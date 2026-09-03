import pandas as pd
import pytest

from equitable_capital import generate_synthetic_startups, train_model
from equitable_capital.geographic import (
    detect_state_column,
    normalize_state_abbreviation,
    prepare_public_state_map,
    public_state_metric_options,
    summarize_synthetic_states,
)


def test_state_normalization_supports_names_and_codes():
    assert normalize_state_abbreviation("Virginia") == "VA"
    assert normalize_state_abbreviation("va") == "VA"
    assert normalize_state_abbreviation("District of Columbia") == "DC"
    assert normalize_state_abbreviation("Not a state") is None


def test_detect_state_column_and_map_numeric_values():
    frame = pd.DataFrame(
        {
            "State": ["Virginia", "Maryland", "Texas", "California"],
            "Small Businesses": ["820,000", "640,000", "3,100,000", "4,200,000"],
            "Share": ["99.5%", "99.4%", "99.8%", "99.8%"],
        }
    )

    state_column, options = public_state_metric_options(frame)
    mapped = prepare_public_state_map(frame, "Small Businesses", state_column)

    assert state_column == "State"
    assert "Small Businesses" in options
    assert set(mapped["state"]) == {"VA", "MD", "TX", "CA"}
    assert mapped.loc[mapped["state"] == "VA", "value"].iloc[0] == 820000


def test_detect_state_column_rejects_unrelated_table():
    frame = pd.DataFrame({"Industry": ["Tech", "Retail", "Food"], "Value": [1, 2, 3]})

    assert detect_state_column(frame) is None


def test_synthetic_state_summary_contains_geographic_metrics():
    data = generate_synthetic_startups(n=300, seed=17)
    scored = train_model(data).scored_data
    summary = summarize_synthetic_states(scored)

    assert not summary.empty
    assert {
        "state",
        "state_name",
        "avg_readiness",
        "avg_barrier_index",
        "avg_requested_capital",
        "avg_predicted_success",
        "businesses",
    }.issubset(summary.columns)


def test_public_map_rejects_unknown_metric():
    frame = pd.DataFrame({"State": ["VA", "MD", "TX"], "Value": [1, 2, 3]})

    with pytest.raises(ValueError):
        prepare_public_state_map(frame, "Missing")
