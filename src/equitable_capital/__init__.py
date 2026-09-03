"""Public API for the Equitable Capital Optimization research package."""

from .allocation import allocate_capital, summarize_allocation
from .data import generate_synthetic_startups
from .explainability import explain_applicant
from .fairness import fairness_audit, opportunity_gap
from .modeling import (
    ModelResult,
    build_pipeline,
    global_feature_importance,
    train_model,
)

__all__ = [
    "ModelResult",
    "allocate_capital",
    "build_pipeline",
    "explain_applicant",
    "fairness_audit",
    "generate_synthetic_startups",
    "global_feature_importance",
    "opportunity_gap",
    "summarize_allocation",
    "train_model",
]
