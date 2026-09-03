"""Fairness and structural-opportunity diagnostic utilities."""

from __future__ import annotations

import pandas as pd

from .config import DEFAULT_SELECTION_THRESHOLD


def fairness_audit(
    scored: pd.DataFrame,
    threshold: float = DEFAULT_SELECTION_THRESHOLD,
    underserved_cutoff: float = 0.50,
) -> pd.DataFrame:
    """Compare model outcomes across higher- and lower-barrier contexts."""
    if not 0 <= threshold <= 1:
        raise ValueError("threshold must be between 0 and 1")

    data = scored.copy()
    data["context_group"] = data["underserved_context_index"].ge(underserved_cutoff).map(
        {
            True: "Higher structural barriers",
            False: "Lower structural barriers",
        }
    )
    data["selected"] = data["predicted_success_probability"].ge(threshold).astype(int)

    rows: list[dict[str, float | int | str]] = []
    for group, frame in data.groupby("context_group", observed=True):
        rows.append(
            {
                "context_group": group,
                "n": int(len(frame)),
                "selection_rate": float(frame["selected"].mean()),
                "avg_predicted_success": float(
                    frame["predicted_success_probability"].mean()
                ),
                "avg_requested_capital": float(frame["requested_capital"].mean()),
                "avg_readiness_score": float(frame["capital_readiness_score"].mean()),
            }
        )

    audit = pd.DataFrame(rows)
    if len(audit) == 2:
        maximum = float(audit["selection_rate"].max())
        minimum = float(audit["selection_rate"].min())
        ratio = minimum / maximum if maximum > 0 else 1.0
    else:
        ratio = 1.0

    audit["selection_rate_ratio"] = ratio
    return audit


def opportunity_gap(scored: pd.DataFrame, cutoff: float = 0.50) -> dict[str, float]:
    """Summarize readiness and requested-capital gaps across contexts."""
    higher = scored[scored["underserved_context_index"] >= cutoff]
    lower = scored[scored["underserved_context_index"] < cutoff]

    return {
        "readiness_gap_points": float(
            lower["capital_readiness_score"].mean()
            - higher["capital_readiness_score"].mean()
        ),
        "requested_capital_gap": float(
            higher["requested_capital"].mean() - lower["requested_capital"].mean()
        ),
    }
