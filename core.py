"""Backward-compatible imports.

The implementation now lives in the `equitable_capital` package under `src/`.
New code should import from `equitable_capital` directly.
"""

from equitable_capital import (
    allocate_capital,
    explain_applicant,
    fairness_audit,
    generate_synthetic_startups,
    global_feature_importance,
    opportunity_gap,
    summarize_allocation,
    train_model,
)

__all__ = [
    "allocate_capital",
    "explain_applicant",
    "fairness_audit",
    "generate_synthetic_startups",
    "global_feature_importance",
    "opportunity_gap",
    "summarize_allocation",
    "train_model",
]
