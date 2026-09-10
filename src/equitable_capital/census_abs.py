"""U.S. Census Annual Business Survey (ABS) API integration.

The module exposes the official aggregate ABS table without joining it to the synthetic
applicant-level model. Census API keys are supplied at runtime and are never stored in the
repository.
"""

from __future__ import annotations

import json
import os
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import pandas as pd

ABS_2022_COMPANY_SUMMARY = {
    "label": "Annual Business Survey: Company Summary 2022",
    "publisher": "U.S. Census Bureau",
    "reference_year": "2022",
    "api_base": "https://api.census.gov/data/2022/abscs",
    "documentation": "https://www.census.gov/data/developers/data-sets/abs.html",
    "examples": "https://api.census.gov/data/2022/abscs/examples.html",
    "variables": "https://api.census.gov/data/2022/abscs/variables.html",
}

DEFAULT_ABS_FIELDS = (
    "NAME",
    "GEO_ID",
    "NAICS2022_LABEL",
    "SEX",
    "SEX_LABEL",
    "ETH_GROUP",
    "ETH_GROUP_LABEL",
    "RACE_GROUP",
    "RACE_GROUP_LABEL",
    "VET_GROUP",
    "VET_GROUP_LABEL",
    "FIRMPDEMP",
    "EMP",
    "RCPPDEMP",
    "PAYANN",
)


def _resolve_api_key(api_key: str | None) -> str:
    key = (api_key or os.getenv("CENSUS_API_KEY") or "").strip()
    if not key:
        raise ValueError(
            "A Census API key is required. Pass api_key=... or set CENSUS_API_KEY. "
            "Do not commit API keys to the repository."
        )
    return key


def build_abs_query_url(
    *,
    geography: str = "state:*",
    in_geography: str | None = None,
    fields: tuple[str, ...] = DEFAULT_ABS_FIELDS,
    naics: str = "00",
    api_key: str | None = None,
) -> str:
    """Build an official Census ABS API query URL."""
    if not fields:
        raise ValueError("At least one ABS field must be requested")
    key = _resolve_api_key(api_key)

    params: list[tuple[str, str]] = [
        ("get", ",".join(fields)),
        ("for", geography),
    ]
    if in_geography:
        params.append(("in", in_geography))
    params.extend([("NAICS2022", str(naics)), ("key", key)])
    return f"{ABS_2022_COMPANY_SUMMARY['api_base']}?{urlencode(params)}"


def parse_census_api_payload(payload: list[list[object]]) -> pd.DataFrame:
    """Convert Census API header-plus-rows JSON into a typed DataFrame."""
    if not payload or len(payload) < 2:
        raise ValueError("The Census API response did not contain data rows.")

    columns = [str(value) for value in payload[0]]
    frame = pd.DataFrame(payload[1:], columns=columns)
    for column in ("FIRMPDEMP", "EMP", "RCPPDEMP", "PAYANN"):
        if column in frame.columns:
            frame[column] = pd.to_numeric(frame[column], errors="coerce")
    return frame


def _fetch_json(url: str, timeout: int = 60) -> list[list[object]]:
    request = Request(
        url,
        headers={"User-Agent": "equitable-capital-optimization-ai/0.5"},
    )
    with urlopen(request, timeout=timeout) as response:  # noqa: S310
        return json.loads(response.read().decode("utf-8"))


def load_abs_state_data(
    *,
    api_key: str | None = None,
    fields: tuple[str, ...] = DEFAULT_ABS_FIELDS,
    fetch_json=_fetch_json,
) -> tuple[dict, pd.DataFrame]:
    """Load official state-level ABS aggregate rows for all industries (NAICS 00)."""
    url = build_abs_query_url(
        geography="state:*",
        fields=fields,
        naics="00",
        api_key=api_key,
    )
    frame = parse_census_api_payload(fetch_json(url))
    metadata = {
        **ABS_2022_COMPANY_SUMMARY,
        "geography": "state",
        "query_scope": "all industries (NAICS2022=00)",
    }
    return metadata, frame


def load_abs_county_data(
    state_fips: str,
    *,
    api_key: str | None = None,
    fields: tuple[str, ...] = DEFAULT_ABS_FIELDS,
    fetch_json=_fetch_json,
) -> tuple[dict, pd.DataFrame]:
    """Load official county-level ABS aggregate rows for one selected state."""
    state_fips = str(state_fips).zfill(2)
    if not state_fips.isdigit() or len(state_fips) != 2:
        raise ValueError("state_fips must be a two-digit Census state FIPS code")

    url = build_abs_query_url(
        geography="county:*",
        in_geography=f"state:{state_fips}",
        fields=fields,
        naics="00",
        api_key=api_key,
    )
    frame = parse_census_api_payload(fetch_json(url))
    if "state" in frame.columns and "county" in frame.columns:
        frame["geoid"] = frame["state"].astype(str).str.zfill(2) + frame["county"].astype(
            str
        ).str.zfill(3)
    metadata = {
        **ABS_2022_COMPANY_SUMMARY,
        "geography": "county",
        "state_fips": state_fips,
        "query_scope": "all industries (NAICS2022=00)",
    }
    return metadata, frame


def total_population_rows(frame: pd.DataFrame) -> pd.DataFrame:
    """Select rows whose available demographic labels explicitly identify totals.

    The function deliberately refuses to infer total-category codes. If the requested ABS
    table does not include label fields or no explicit total rows can be identified, an
    empty frame is returned instead of silently double-counting demographic categories.
    """
    label_columns = [
        column
        for column in (
            "SEX_LABEL",
            "ETH_GROUP_LABEL",
            "RACE_GROUP_LABEL",
            "VET_GROUP_LABEL",
        )
        if column in frame.columns
    ]
    if not label_columns:
        return frame.iloc[0:0].copy()

    work = frame.copy()
    mask = pd.Series(True, index=work.index)
    for column in label_columns:
        labels = work[column].fillna("").astype(str).str.strip().str.lower()
        total_mask = labels.str.contains(r"\btotal\b|\ball firms\b|\ball owners\b", regex=True)
        mask &= total_mask
    return work[mask].copy().reset_index(drop=True)
