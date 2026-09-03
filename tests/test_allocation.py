import pytest

from equitable_capital import (
    allocate_capital,
    generate_synthetic_startups,
    summarize_allocation,
    train_model,
)


def test_allocation_respects_budget():
    data = generate_synthetic_startups(500, seed=14)
    result = train_model(data)
    baseline, equitable = allocate_capital(result.scored_data, budget=500_000)

    assert baseline["allocated_capital"].sum() <= 500_000 + 1e-6
    assert equitable["allocated_capital"].sum() <= 500_000 + 1e-6


def test_allocation_summary_is_bounded():
    data = generate_synthetic_startups(500, seed=15)
    result = train_model(data)
    _, equitable = allocate_capital(result.scored_data, budget=500_000)
    summary = summarize_allocation(equitable, budget=500_000)

    assert 0 <= summary["budget_utilization"] <= 1
    assert 0 <= summary["share_to_higher_barrier_contexts"] <= 1


def test_invalid_budget_is_rejected():
    data = generate_synthetic_startups(500, seed=16)
    result = train_model(data)

    with pytest.raises(ValueError):
        allocate_capital(result.scored_data, budget=0)
