"""Synthetic data generation for the research prototype."""

from __future__ import annotations

import numpy as np
import pandas as pd

from .config import DEFAULT_SAMPLE_SIZE, RANDOM_SEED, TARGET


def generate_synthetic_startups(
    n: int = DEFAULT_SAMPLE_SIZE,
    seed: int = RANDOM_SEED,
) -> pd.DataFrame:
    """Generate reproducible, privacy-safe synthetic small-business records."""
    if n < 100:
        raise ValueError("n must be at least 100 for a stable demonstration dataset")

    rng = np.random.default_rng(seed)
    states = np.array(["VA", "MD", "DC", "NC", "GA", "TX", "CA", "NY", "IL", "FL"])
    industries = np.array(
        [
            "Technology",
            "Retail",
            "Professional Services",
            "Food",
            "Healthcare",
            "Manufacturing",
            "Education",
            "Logistics",
        ]
    )

    data = pd.DataFrame(
        {
            "startup_id": [f"BUS-{i:04d}" for i in range(1, n + 1)],
            "state": rng.choice(states, n),
            "industry": rng.choice(industries, n),
            "annual_revenue": np.round(rng.lognormal(12.0, 0.9, n), 2),
            "revenue_growth_pct": np.round(rng.normal(18, 18, n).clip(-40, 120), 2),
            "cash_runway_months": np.round(rng.gamma(3.2, 2.0, n).clip(0.5, 24), 2),
            "employees": rng.integers(1, 80, n),
            "years_operating": np.round(rng.gamma(2.5, 1.8, n).clip(0.2, 20), 2),
            "debt_service_coverage": np.round(
                rng.normal(1.35, 0.45, n).clip(0.2, 3.5), 2
            ),
            "digital_adoption_score": np.round(rng.normal(62, 20, n).clip(0, 100), 1),
            "market_demand_score": np.round(rng.normal(66, 18, n).clip(0, 100), 1),
            "management_capacity_score": np.round(
                rng.normal(64, 17, n).clip(0, 100), 1
            ),
            "requested_capital": np.round(rng.lognormal(11.3, 0.75, n), 2),
            "rural_area": rng.binomial(1, 0.28, n),
            "low_income_area": rng.binomial(1, 0.35, n),
            "limited_finance_access": rng.binomial(1, 0.33, n),
        }
    )

    data["underserved_context_index"] = np.round(
        (
            0.35 * data["low_income_area"]
            + 0.30 * data["limited_finance_access"]
            + 0.20 * data["rural_area"]
            + 0.15 * (1 - data["digital_adoption_score"] / 100)
        ).clip(0, 1),
        3,
    )

    logit = (
        -2.6
        + 0.0000022 * data["annual_revenue"]
        + 0.018 * data["revenue_growth_pct"]
        + 0.075 * data["cash_runway_months"]
        + 0.30 * data["debt_service_coverage"]
        + 0.010 * data["market_demand_score"]
        + 0.008 * data["management_capacity_score"]
        - 0.0000013 * data["requested_capital"]
    )
    probability = 1 / (1 + np.exp(-logit))
    data[TARGET] = rng.binomial(1, probability.clip(0.03, 0.97))
    return data
