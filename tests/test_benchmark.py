import pandas as pd

from equitable_capital import generate_synthetic_startups
from equitable_capital.benchmark import (
    benchmark_model_registry,
    run_model_benchmark,
    summarize_benchmark,
)


def test_benchmark_registry_contains_multiple_model_families():
    registry = benchmark_model_registry(42)

    assert {
        "Logistic Regression",
        "Random Forest",
        "Extra Trees",
        "HistGradientBoosting",
    } == set(registry)


def test_benchmark_returns_expected_metrics():
    data = generate_synthetic_startups(n=300, seed=21)
    results = run_model_benchmark(data, split_seeds=(21,))
    summary = summarize_benchmark(results)

    assert len(results) == 4
    assert len(summary) == 4
    assert results["roc_auc"].between(0, 1).all()
    assert results["brier"].between(0, 1).all()
    assert pd.notna(summary["roc_auc_mean"]).all()
