"""U.S. Census County Business Patterns (CBP) public-data integration."""

from __future__ import annotations

import json
import re
from io import BytesIO
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from zipfile import ZipFile

import pandas as pd

from .geographic import US_STATE_NAMES

CENSUS_CBP_2023 = {
    "label": "U.S. Census County Business Patterns 2023",
    "publisher": "U.S. Census Bureau",
    "vintage": "2023",
    "landing_page": "https://www.census.gov/data/datasets/2023/econ/cbp/2023-cbp.html",
    "county_resource_url": (
        "https://www2.census.gov/programs-surveys/cbp/datasets/2023/cbp23co.zip"
    ),
    "description": (
        "Annual establishment statistics including employment and payroll by industry "
        "and county/county-equivalent geography."
    ),
}

CENSUS_TIGER_COUNTY_2023 = {
    "label": "Census TIGERweb 2023 generalized county boundaries",
    "query_url": (
        "https://tigerweb.geo.census.gov/arcgis/rest/services/"
        "Generalized_ACS2023/State_County/MapServer/12/query"
    ),
    "vintage": "2023",
}

STATE_FIPS_TO_ABBR = {
    "01": "AL", "02": "AK", "04": "AZ", "05": "AR", "06": "CA", "08": "CO",
    "09": "CT", "10": "DE", "11": "DC", "12": "FL", "13": "GA", "15": "HI",
    "16": "ID", "17": "IL", "18": "IN", "19": "IA", "20": "KS", "21": "KY",
    "22": "LA", "23": "ME", "24": "MD", "25": "MA", "26": "MI", "27": "MN",
    "28": "MS", "29": "MO", "30": "MT", "31": "NE", "32": "NV", "33": "NH",
    "34": "NJ", "35": "NM", "36": "NY", "37": "NC", "38": "ND", "39": "OH",
    "40": "OK", "41": "OR", "42": "PA", "44": "RI", "45": "SC", "46": "SD",
    "47": "TN", "48": "TX", "49": "UT", "50": "VT", "51": "VA", "53": "WA",
    "54": "WV", "55": "WI", "56": "WY",
}
STATE_ABBR_TO_FIPS = {abbr: fips for fips, abbr in STATE_FIPS_TO_ABBR.items()}


def _fetch_bytes(url: str, timeout: int = 60) -> bytes:
    request = Request(
        url,
        headers={"User-Agent": "equitable-capital-optimization-ai/0.5"},
    )
    with urlopen(request, timeout=timeout) as response:  # noqa: S310
        return response.read()


def _fetch_json(url: str, timeout: int = 60) -> dict:
    return json.loads(_fetch_bytes(url, timeout=timeout).decode("utf-8"))


def _first_data_member(archive: ZipFile) -> str:
    candidates = [
        name
        for name in archive.namelist()
        if not name.endswith("/") and name.lower().endswith((".csv", ".txt"))
    ]
    if not candidates:
        raise ValueError("The Census CBP ZIP archive did not contain a CSV/text file.")
    return candidates[0]


def load_cbp_county_file(fetch_bytes=_fetch_bytes) -> pd.DataFrame:
    """Load the official downloadable CBP county file."""
    raw = fetch_bytes(CENSUS_CBP_2023["county_resource_url"])
    with ZipFile(BytesIO(raw)) as archive:
        frame = pd.read_csv(
            archive.open(_first_data_member(archive)),
            dtype=str,
            low_memory=False,
        )
    frame.columns = [str(column).strip().lower() for column in frame.columns]
    return frame


def _column(frame: pd.DataFrame, *candidates: str) -> str | None:
    for candidate in candidates:
        if candidate in frame.columns:
            return candidate
    return None


def _filter_lfo_and_size_rows(frame: pd.DataFrame) -> pd.DataFrame:
    work = frame.copy()
    lfo_column = _column(work, "lfo")
    if lfo_column and (work[lfo_column].astype(str).str.zfill(3) == "001").any():
        work = work[work[lfo_column].astype(str).str.zfill(3) == "001"]

    size_column = _column(work, "empszes", "empsize")
    if size_column and (work[size_column].astype(str).str.zfill(3) == "001").any():
        work = work[work[size_column].astype(str).str.zfill(3) == "001"]
    return work


def _filter_total_rows(frame: pd.DataFrame) -> pd.DataFrame:
    work = _filter_lfo_and_size_rows(frame)
    naics_column = _column(work, "naics", "naics2017")
    if naics_column:
        values = work[naics_column].astype(str).str.strip()
        match = next(
            (code for code in ("------", "00", "0", "TOTAL", "ALL") if (values == code).any()),
            None,
        )
        if match is not None:
            work = work[values == match]
    return work


def _core_metrics(frame: pd.DataFrame) -> dict[str, pd.Series]:
    candidates = {
        "establishments": ("est", "estab"),
        "employment": ("emp",),
        "annual_payroll_thousands": ("ap", "payann"),
        "q1_payroll_thousands": ("qp1", "payqtr1"),
    }
    output: dict[str, pd.Series] = {}
    for output_name, source_names in candidates.items():
        source = _column(frame, *source_names)
        if source:
            output[output_name] = pd.to_numeric(frame[source], errors="coerce")
    return output


def summarize_cbp_county_totals(frame: pd.DataFrame) -> pd.DataFrame:
    """Return one all-industry total row per county/county equivalent."""
    work = _filter_total_rows(frame)
    state_column = _column(work, "fipstate", "state")
    county_column = _column(work, "fipscty", "county")
    if state_column is None or county_column is None:
        raise ValueError("CBP state/county FIPS columns were not found.")

    state_fips = work[state_column].astype(str).str.replace(".0", "", regex=False).str.zfill(2)
    county_fips = work[county_column].astype(str).str.replace(".0", "", regex=False).str.zfill(3)
    output = pd.DataFrame(
        {
            "state_fips": state_fips,
            "county_fips": county_fips,
            "geoid": state_fips + county_fips,
        }
    )
    output["state"] = output["state_fips"].map(STATE_FIPS_TO_ABBR)
    output["state_name"] = output["state"].map(US_STATE_NAMES)
    for name, values in _core_metrics(work).items():
        output[name] = values

    output = output.dropna(subset=["state"]).drop_duplicates(subset=["geoid"])
    if output.empty:
        raise ValueError("No county-total CBP rows could be prepared.")
    return output.sort_values(["state", "county_fips"]).reset_index(drop=True)


def summarize_county_industry_concentration(
    frame: pd.DataFrame,
    value_column: str = "est",
) -> pd.DataFrame:
    """Calculate county sector concentration on the conventional 0-10,000 HHI scale."""
    work = _filter_lfo_and_size_rows(frame)
    state_column = _column(work, "fipstate", "state")
    county_column = _column(work, "fipscty", "county")
    naics_column = _column(work, "naics", "naics2017")
    if state_column is None or county_column is None or naics_column is None:
        raise ValueError("Required CBP county/NAICS fields were not found.")
    if value_column not in work.columns:
        raise ValueError(f"Unknown CBP value column: {value_column}")

    naics = work[naics_column].astype(str).str.strip()
    sector_mask = naics.map(
        lambda value: bool(re.fullmatch(r"(?:\d{2}----|\d{2}-\d{2}-)", value))
    )
    work = work[sector_mask].copy()
    work["sector"] = naics[sector_mask]
    work["state_fips"] = (
        work[state_column].astype(str).str.replace(".0", "", regex=False).str.zfill(2)
    )
    work["county_fips"] = (
        work[county_column].astype(str).str.replace(".0", "", regex=False).str.zfill(3)
    )
    work["geoid"] = work["state_fips"] + work["county_fips"]
    work["value"] = pd.to_numeric(work[value_column], errors="coerce")
    work = work.dropna(subset=["value"])

    grouped = work.groupby(["geoid", "sector"], as_index=False)["value"].sum()
    if grouped.empty:
        raise ValueError("No high-level county industry rows were available.")
    grouped["county_total"] = grouped.groupby("geoid")["value"].transform("sum")
    grouped["share"] = grouped["value"] / grouped["county_total"].replace(0, pd.NA)
    grouped["share_squared"] = grouped["share"] ** 2
    return (
        grouped.groupby("geoid", as_index=False)
        .agg(
            industry_hhi=("share_squared", lambda values: float(values.sum() * 10000)),
            sector_count=("sector", "nunique"),
            top_sector_share=("share", "max"),
        )
        .sort_values("industry_hhi", ascending=False)
        .reset_index(drop=True)
    )


def load_county_geojson(state_fips: str, fetch_json=_fetch_json) -> dict:
    """Load generalized Census TIGERweb county boundaries for one state."""
    state_fips = str(state_fips).zfill(2)
    if state_fips not in STATE_FIPS_TO_ABBR:
        raise ValueError(f"Unknown state FIPS code: {state_fips}")

    params = {
        "where": f"STATE='{state_fips}'",
        "outFields": "GEOID,STATE,COUNTY,BASENAME,NAME",
        "returnGeometry": "true",
        "outSR": "4326",
        "f": "geojson",
    }
    payload = fetch_json(f"{CENSUS_TIGER_COUNTY_2023['query_url']}?{urlencode(params)}")
    if payload.get("error"):
        raise RuntimeError(f"Census TIGERweb returned an error: {payload['error']}")
    if payload.get("type") != "FeatureCollection" or not payload.get("features"):
        raise ValueError("No county boundary features were returned for the selected state.")
    return payload


def county_name_lookup(geojson: dict) -> dict[str, str]:
    """Return GEOID-to-county-name labels from a TIGERweb GeoJSON response."""
    labels: dict[str, str] = {}
    for feature in geojson.get("features", []):
        properties = feature.get("properties", {})
        geoid = str(properties.get("GEOID", "")).zfill(5)
        name = properties.get("NAME") or properties.get("BASENAME")
        if geoid and name:
            labels[geoid] = str(name)
    return labels
