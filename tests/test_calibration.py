import numpy as np

from equitable_capital.calibration import (
    calibration_curve_table,
    expected_calibration_error,
    run_calibration_benchmark,
    summarize_calibration,
)
from equitable_capital.data import generate_synthetic_startups


def test_calibration_curve_table_counts_every_observation():
    y_true = np.array([0, 0, 1, 1, 1, 0])
    probabilities = np.array([0.05, 0.20, 0.45, 0.70, 0.95, 1.0])

    table = calibration_curve_table(y_true, probabilities, n_bins=5)

    assert int(table["count"].sum()) == len(y_true)
    assert table["mean_predicted_probability"].between(0, 1).all()
    assert table["observed_rate"].between(0, 1).all()


def test_expected_calibration_error_is_bounded():
    y_true = np.array([0, 0, 1, 1])
    probabilities = np.array([0.10, 0.25, 0.75, 0.90])

    ece = expected_calibration_error(y_true, probabilities, n_bins=4)

    assert 0 <= ece <= 1


def test_calibration_benchmark_is_reproducible_and_complete():
    data = generate_synthetic_startups(n=300, seed=90)
    first = run_calibration_benchmark(data, split_seeds=(42,), n_bins=8)
    second = run_calibration_benchmark(data, split_seeds=(42,), n_bins=8)

    assert set(first["method"]) == {"uncalibrated", "sigmoid", "isotonic"}
    assert first[["roc_auc", "brier", "log_loss", "ece"]].notna().all().all()
    assert np.allclose(
        first[["roc_auc", "brier", "log_loss", "ece"]],
        second[["roc_auc", "brier", "log_loss", "ece"]],
    )


def test_calibration_summary_has_one_row_per_method():
    data = generate_synthetic_startups(n=300, seed=91)
    results = run_calibration_benchmark(data, split_seeds=(42, 43), n_bins=6)
    summary = summarize_calibration(results)

    assert set(summary["method"]) == {"uncalibrated", "sigmoid", "isotonic"}
    assert summary["brier_mean"].between(0, 1).all()
    assert summary["ece_mean"].between(0, 1).all()
