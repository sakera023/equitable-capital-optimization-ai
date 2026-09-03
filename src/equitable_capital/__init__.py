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
from .public_data import PUBLIC_DATASETS, get_sba_dataset_metadata, load_sba_public_workbook

__all__ = [
    "ModelResult",
    "PUBLIC_DATASETS",
    "allocate_capital",
    "build_pipeline",
    "explain_applicant",
    "fairness_audit",
    "generate_synthetic_startups",
    "get_sba_dataset_metadata",
    "global_feature_importance",
    "load_sba_public_workbook",
    "opportunity_gap",
    "summarize_allocation",
    "train_model",
]
