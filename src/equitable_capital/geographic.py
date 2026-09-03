"""Geographic aggregation helpers for state-level research visualization."""

from __future__ import annotations

import re

import pandas as pd

US_STATE_NAMES = {
    "AL": "Alabama",
    "AK": "Alaska",
    "AZ": "Arizona",
    "AR": "Arkansas",
    "CA": "California",
    "CO": "Colorado",
    "CT": "Connecticut",
    "DE": "Delaware",
    "DC": "District of Columbia",
    "FL": "Florida",
    "GA": "Georgia",
    "HI": "Hawaii",
    "ID": "Idaho",
    "IL": "Illinois",
    "IN": "Indiana",
    "IA": "Iowa",
    "KS": "Kansas",
    "KY": "Kentucky",
    "LA": "Louisiana",
    "ME": "Maine",
    "MD": "Maryland",
    "MA": "Massachusetts",
    "MI": "Michigan",
    "MN": "Minnesota",
    "MS": "Mississippi",
    "MO": "Missouri",
    "MT": "Montana",
    "NE": "Nebraska",
    "NV": "Nevada",
    "NH": "New Hampshire",
    "NJ": "New Jersey",
    "NM": "New Mexico",
    "NY": "New York",
    "NC": "North Carolina",
    "ND": "North Dakota",
    "OH": "Ohio",
    "OK": "Oklahoma",
    "OR": "Oregon",
    "PA": "Pennsylvania",
    "RI": "Rhode Island",
    "SC": "South Carolina",
    "SD": "South Dakota",
    "TN": "Tennessee",
    "TX": "Texas",
    "UT": "Utah",
    "VT": "Vermont",
    "VA": "Virginia",
    "WA": "Washington",
    "WV": "West Virginia",
    "WI": "Wisconsin",
    "WY": "Wyoming",
}

STATE_NAME_TO_ABBR = {name.lower(): abbr for abbr, name in US_STATE_NAMES.items()}
STATE_NAME_TO_ABBR["washington dc"] = "DC"
STATE_NAME_TO_ABBR["washington, dc"] = "DC"
STATE_NAME_TO_ABBR["district of columbia"] = "DC"


def normalize_state_abbreviation(value: object) -> str | None:
    """Normalize a U.S. state name or abbreviation to a two-letter code."""
    if pd.isna(value):
        return None

    text = str(value).strip()
    if not text:
        return None

    upper = text.upper()
    if upper in US_STATE_NAMES:
        return upper

    normalized = re.sub(r"\s+", " ", text.lower()).strip(" .")
    return STATE_NAME_TO_ABBR.get(normalized)


def summarize_synthetic_states(scored: pd.DataFrame) -> pd.DataFrame:
    """Aggregate scored synthetic records into state-level research indicators."""
    required = {
        "state",
        "startup_id",
        "capital_readiness_score",
        "underserved_context_index",
        "requested_capital",
        "predicted_success_probability",
    }
    missing = sorted(required - set(scored.columns))
    if missing:
        raise ValueError(f"Missing columns for geographic summary: {missing}")

    summary = (
        scored.groupby("state", as_index=False)
        .agg(
            avg_readiness=("capital_readiness_score", "mean"),
            avg_barrier_index=("underserved_context_index", "mean"),
            avg_requested_capital=("requested_capital", "mean"),
            avg_predicted_success=("predicted_success_probability", "mean"),
            businesses=("startup_id", "count"),
        )
        .copy()
    )
    summary["state"] = summary["state"].map(normalize_state_abbreviation)
    summary = summary.dropna(subset=["state"])
    summary["state_name"] = summary["state"].map(US_STATE_NAMES)
    return summary


def detect_state_column(frame: pd.DataFrame) -> str | None:
    """Identify a column that predominantly contains U.S. state names/codes."""
    if frame.empty:
        return None

    best_column: str | None = None
    best_score = 0.0

    for column in frame.columns:
        series = frame[column].dropna().head(200)
        if len(series) < 3:
            continue

        recognized = series.map(normalize_state_abbreviation).notna()
        score = float(recognized.mean())
        column_hint = str(column).strip().lower()
        if "state" in column_hint:
            score += 0.15

        if score > best_score:
            best_score = score
            best_column = str(column)

    return best_column if best_score >= 0.45 else None


def _coerce_numeric_series(series: pd.Series) -> pd.Series:
    text = series.astype(str).str.strip()
    text = text.str.replace(",", "", regex=False)
    text = text.str.replace("$", "", regex=False)
    text = text.str.replace("%", "", regex=False)
    text = text.str.replace(r"^\((.*)\)$", r"-\1", regex=True)
    text = text.replace({"nan": None, "None": None, "": None, "—": None, "-": None})
    return pd.to_numeric(text, errors="coerce")


def public_state_metric_options(frame: pd.DataFrame) -> tuple[str | None, list[str]]:
    """Return the detected state column and numeric columns suitable for mapping."""
    state_column = detect_state_column(frame)
    if state_column is None:
        return None, []

    options: list[str] = []
    for column in frame.columns:
        column_name = str(column)
        if column_name == state_column:
            continue

        numeric = _coerce_numeric_series(frame[column])
        valid_count = int(numeric.notna().sum())
        if valid_count >= 3:
            options.append(column_name)

    return state_column, options


def prepare_public_state_map(
    frame: pd.DataFrame,
    metric_column: str,
    state_column: str | None = None,
) -> pd.DataFrame:
    """Prepare one official aggregate metric for a Plotly USA-states choropleth."""
    resolved_state_column = state_column or detect_state_column(frame)
    if resolved_state_column is None:
        raise ValueError("No U.S. state column could be detected in this worksheet.")
    if metric_column not in frame.columns:
        raise ValueError(f"Unknown metric column: {metric_column}")

    mapped = pd.DataFrame(
        {
            "state": frame[resolved_state_column].map(normalize_state_abbreviation),
            "value": _coerce_numeric_series(frame[metric_column]),
        }
    ).dropna(subset=["state", "value"])

    if mapped.empty:
        raise ValueError("No state-level numeric values were available for this metric.")

    mapped = mapped.groupby("state", as_index=False)["value"].mean()
    mapped["state_name"] = mapped["state"].map(US_STATE_NAMES)
    mapped["metric"] = metric_column
    return mapped
