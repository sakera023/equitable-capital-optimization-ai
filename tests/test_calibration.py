import pandas as pd
import pytest

from equitable_capital import generate_synthetic_startups
from equitable_capital.calibration import (
    expected_calibration_error,
    reliability_curve_frame,
    run_calibration_benchmark,
    summarize_calibration,
)


def test_reliability_curve_frame_builds_probability_bins():
    curve = reliability_curve_frame(
        y_true=pd.Series([0, 0, 1, 1]),
        probabilities=pd.Series([0.05, 0.25, 0.70, 0.95]),
        n_bins=4,
    )

    assert set(curve.columns) == {
        "bin",
        "bin_lower",
        "bin_upper",
        "mean_predicted_probability",
        "observed_success_rate",
        "count",
    }
    assert int(curve["count"].sum()) == 4
    assert curve["mean_predicted_probability"].between(0, 1).all()
    assert curve["observed_success_rate"].between(0, 1).all()


def test_expected_calibration_error_is_count_weighted():
    reliability = pd.DataFrame(
        {
            "mean_predicted_probability": [0.20, 0.80],
            "observed_success_rate": [0.10, 0.50],
            "count": [3, 1],
        }
    )

    assert expected_calibration_error(reliability) == pytest.approx(0.15)


def test_calibration_benchmark_returns_methods_and_summary():
    data = generate_synthetic_startups(n=300, seed=22)
    result = run_calibration_benchmark(
        data,
        split_seeds=(22,),
        methods=("uncalibrated", "sigmoid"),
        n_bins=5,
    )
    summary = summarize_calibration(result.metrics)

    assert len(result.metrics) == 8
    assert set(result.metrics["calibration_method"]) == {"uncalibrated", "sigmoid"}
    assert result.metrics["brier"].between(0, 1).all()
    assert result.metrics["expected_calibration_error"].between(0, 1).all()
    assert not result.reliability.empty
    assert len(summary) == 8
