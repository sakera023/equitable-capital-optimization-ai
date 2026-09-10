from equitable_capital.data import generate_synthetic_startups
from equitable_capital.robustness import (
    geographic_holdout_validation,
    missing_data_stress_test,
    permutation_feature_importance,
    repeated_cross_validation,
    threshold_sensitivity,
)


def test_repeated_cross_validation_returns_fold_metrics():
    data = generate_synthetic_startups(n=300, seed=101)
    results = repeated_cross_validation(data, n_splits=3, n_repeats=1)

    assert len(results) == 3
    assert results["roc_auc"].between(0, 1).all()
    assert results["brier"].between(0, 1).all()


def test_threshold_sensitivity_reports_tradeoffs():
    data = generate_synthetic_startups(n=300, seed=102)
    results = threshold_sensitivity(data, thresholds=(0.3, 0.5, 0.7))

    assert list(results["threshold"]) == [0.3, 0.5, 0.7]
    assert results["selection_rate"].between(0, 1).all()
    assert results["f1"].between(0, 1).all()


def test_missing_data_stress_is_reproducible():
    data = generate_synthetic_startups(n=300, seed=103)
    first = missing_data_stress_test(data, missing_rates=(0.0, 0.1), repeats=1)
    second = missing_data_stress_test(data, missing_rates=(0.0, 0.1), repeats=1)

    assert first.equals(second)
    assert first["roc_auc"].between(0, 1).all()


def test_permutation_importance_returns_original_features():
    data = generate_synthetic_startups(n=300, seed=104)
    importance = permutation_feature_importance(data, n_repeats=2)

    assert {"feature", "importance_mean", "importance_std"}.issubset(importance.columns)
    assert len(importance) > 5


def test_geographic_holdout_reports_multiple_states():
    data = generate_synthetic_startups(n=500, seed=105)
    results = geographic_holdout_validation(data)

    assert len(results) >= 5
    assert results["roc_auc"].between(0, 1).all()
    assert results["brier"].between(0, 1).all()
