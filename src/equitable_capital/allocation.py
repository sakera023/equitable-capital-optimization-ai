"""Capital-allocation scenario simulation."""

from __future__ import annotations

import pandas as pd

from .config import DEFAULT_EQUITY_WEIGHT


def _greedy_allocate(
    data: pd.DataFrame,
    budget: float,
    score_column: str,
) -> pd.DataFrame:
    ranked = data.sort_values(
        [score_column, "predicted_success_probability"], ascending=False
    ).copy()
    remaining = float(budget)
    allocations: list[dict] = []

    for _, row in ranked.iterrows():
        if remaining <= 0:
            break
        requested = float(row["requested_capital"])
        allocated = min(requested, remaining)
        if allocated <= 0:
            continue
        item = row.to_dict()
        item["allocated_capital"] = allocated
        allocations.append(item)
        remaining -= allocated

    return pd.DataFrame(allocations)


def allocate_capital(
    scored: pd.DataFrame,
    budget: float,
    equity_weight: float = DEFAULT_EQUITY_WEIGHT,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Compare efficiency-only and equity-aware research scenarios."""
    if budget <= 0:
        raise ValueError("budget must be greater than zero")
    if not 0 <= equity_weight <= 1:
        raise ValueError("equity_weight must be between 0 and 1")

    data = scored.copy()
    data["efficiency_priority"] = (
        data["predicted_success_probability"] / data["requested_capital"].clip(lower=1)
    )

    request_norm = data["requested_capital"] / data["requested_capital"].max()
    data["equity_priority"] = (
        (1 - equity_weight) * data["predicted_success_probability"]
        + equity_weight * data["underserved_context_index"]
        - 0.05 * request_norm
    )

    baseline = _greedy_allocate(data, budget, "efficiency_priority")
    equitable = _greedy_allocate(data, budget, "equity_priority")
    return baseline, equitable


def summarize_allocation(
    allocated: pd.DataFrame,
    budget: float,
) -> dict[str, float | int]:
    """Summarize a simulated allocation result."""
    if allocated.empty:
        return {
            "businesses_funded": 0,
            "capital_allocated": 0.0,
            "budget_utilization": 0.0,
            "share_to_higher_barrier_contexts": 0.0,
            "expected_successes": 0.0,
        }

    total = float(allocated["allocated_capital"].sum())
    higher_barrier = allocated["underserved_context_index"] >= 0.5

    return {
        "businesses_funded": int(len(allocated)),
        "capital_allocated": total,
        "budget_utilization": total / budget if budget else 0.0,
        "share_to_higher_barrier_contexts": float(
            allocated.loc[higher_barrier, "allocated_capital"].sum() / total
            if total
            else 0.0
        ),
        "expected_successes": float(
            (
                allocated["predicted_success_probability"]
                * (allocated["allocated_capital"] / allocated["requested_capital"])
            ).sum()
        ),
    }
