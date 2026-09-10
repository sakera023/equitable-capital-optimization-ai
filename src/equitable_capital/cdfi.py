"""CDFI Fund public-data integration for capital-support context."""

from __future__ import annotations

import re
from io import BytesIO
from urllib.parse import urljoin
from urllib.request import Request, urlopen

import pandas as pd

from .geographic import US_STATE_NAMES, detect_state_column, normalize_state_abbreviation

CDFI_CERTIFICATION = {
    "label": "List of Currently Certified CDFIs",
    "publisher": "Community Development Financial Institutions Fund, U.S. Treasury",
    "landing_page": "https://www.cdfifund.gov/programs-training/certification/cdfi",
    "fallback_resource_url": "https://www.cdfifund.gov/media/8018681/download?inline=",
    "description": (
        "Official current list of organizations certified as Community Development "
        "Financial Institutions (CDFIs)."
    ),
}

_CDFI_LINK_PATTERN = re.compile(
    r"""href=["']([^"']*/media/\d+/download\?inline=?[^"']*)["'][^>]*>
        \s*List\s+of\s+Currently\s+Certified\s+CDFIs\s*</a>""",
    re.IGNORECASE | re.VERBOSE,
)


def _fetch_bytes(url: str, timeout: int = 60) -> bytes:
    request = Request(url, headers={"User-Agent": "equitable-capital-optimization-ai/0.5"})
    with urlopen(request, timeout=timeout) as response:  # noqa: S310
        return response.read()


def discover_cdfi_workbook_url(fetch_bytes=_fetch_bytes) -> str:
    """Discover the current official Certified CDFI workbook from the source page."""
    html = fetch_bytes(CDFI_CERTIFICATION["landing_page"]).decode("utf-8", errors="ignore")
    match = _CDFI_LINK_PATTERN.search(html)
    if match:
        return urljoin(CDFI_CERTIFICATION["landing_page"], match.group(1))
    return CDFI_CERTIFICATION["fallback_resource_url"]


def _normalized_label(value: object) -> str:
    text = re.sub(r"[^a-z0-9]+", " ", str(value).strip().lower())
    return re.sub(r"\s+", " ", text).strip()


def _find_column(frame: pd.DataFrame, candidates: tuple[str, ...]) -> str | None:
    normalized = {_normalized_label(column): str(column) for column in frame.columns}
    for candidate in candidates:
        if candidate in normalized:
            return normalized[candidate]
    for normalized_name, original in normalized.items():
        if any(candidate in normalized_name for candidate in candidates):
            return original
    return None


def _find_header_row(raw: pd.DataFrame) -> int:
    terms = {
        "state",
        "organization name",
        "cdfi name",
        "institution name",
        "city",
        "organization type",
        "cdfi type",
    }
    best_row = 0
    best_score = -1
    for row_index in range(min(25, len(raw))):
        labels = {_normalized_label(value) for value in raw.iloc[row_index].tolist()}
        score = sum(
            1
            for label in labels
            if label in terms or label.endswith(" state") or "organization name" in label
        )
        if score > best_score:
            best_row, best_score = row_index, score
    return best_row


def _unique_columns(values: list[object]) -> list[str]:
    counts: dict[str, int] = {}
    output: list[str] = []
    for index, value in enumerate(values):
        base = str(value).strip() if pd.notna(value) else f"column_{index + 1}"
        base = base or f"column_{index + 1}"
        count = counts.get(base, 0)
        counts[base] = count + 1
        output.append(base if count == 0 else f"{base}_{count + 1}")
    return output


def _clean_sheet(raw: pd.DataFrame) -> pd.DataFrame:
    if raw.empty:
        return raw
    header_row = _find_header_row(raw)
    frame = raw.iloc[header_row + 1 :].copy()
    frame.columns = _unique_columns(raw.iloc[header_row].tolist())
    return frame.dropna(axis=0, how="all").dropna(axis=1, how="all").reset_index(drop=True)


def load_cdfi_certification_workbook(fetch_bytes=_fetch_bytes) -> tuple[dict, pd.DataFrame]:
    """Load the current official CDFI institution roster with summary-sheet safeguards."""
    resource_url = discover_cdfi_workbook_url(fetch_bytes=fetch_bytes)
    sheets = pd.read_excel(BytesIO(fetch_bytes(resource_url)), sheet_name=None, header=None)
    candidates = []

    for sheet_name, raw in sheets.items():
        frame = _clean_sheet(raw)
        state_column = detect_state_column(frame)
        if not state_column:
            continue
        organization_column = _find_column(
            frame,
            ("organization name", "cdfi name", "institution name", "organization"),
        )
        states = frame[state_column].map(normalize_state_abbreviation)
        recognized_count = int(states.notna().sum())
        candidates.append(
            (
                organization_column is not None,
                recognized_count,
                str(sheet_name),
                frame,
                state_column,
            )
        )

    if not candidates:
        raise ValueError("No state-level Certified CDFI worksheet could be identified.")

    has_org, recognized_count, sheet_name, frame, state_column = max(
        candidates, key=lambda item: (item[0], item[1])
    )
    if not has_org:
        raise ValueError("No organization-name column was found in the candidate CDFI sheet.")
    if recognized_count < 100:
        raise ValueError(
            "The selected CDFI worksheet contains fewer than 100 recognized institution "
            "rows; refusing to treat a state summary as the institution roster."
        )

    return (
        {
            **CDFI_CERTIFICATION,
            "resource_url": resource_url,
            "worksheet": sheet_name,
            "state_column": state_column,
        },
        frame,
    )


def summarize_cdfi_by_state(frame: pd.DataFrame) -> pd.DataFrame:
    """Summarize institution locations by state without implying service-area coverage."""
    state_column = detect_state_column(frame)
    if state_column is None:
        raise ValueError("No state column could be identified in the Certified CDFI list.")
    organization_column = _find_column(
        frame,
        ("organization name", "cdfi name", "institution name", "organization"),
    )
    if organization_column is None:
        raise ValueError("No organization-name column could be identified.")
    type_column = _find_column(
        frame,
        ("organization type", "cdfi type", "institution type", "type"),
    )

    work = pd.DataFrame(
        {
            "state": frame[state_column].map(normalize_state_abbreviation),
            "organization": frame[organization_column].astype(str).str.strip(),
        }
    )
    if type_column:
        work["institution_type"] = frame[type_column].astype(str).str.strip()
    work = work.dropna(subset=["state"])
    work = work[work["organization"].ne("") & work["organization"].ne("nan")]

    aggregations: dict[str, tuple[str, str]] = {
        "certified_cdfis": ("organization", "nunique")
    }
    if "institution_type" in work.columns:
        aggregations["institution_type_count"] = ("institution_type", "nunique")

    result = work.groupby("state", as_index=False).agg(**aggregations)
    if "institution_type_count" not in result.columns:
        result["institution_type_count"] = pd.NA
    result["state_name"] = result["state"].map(US_STATE_NAMES)
    return result.sort_values("certified_cdfis", ascending=False).reset_index(drop=True)
