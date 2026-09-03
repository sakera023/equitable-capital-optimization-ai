"""Public API for the Equitable Capital Optimization research package."""

from .allocation import allocate_capital, summarize_allocation
from .benchmark import (
    benchmark_model_registry,
    run_model_benchmark,
    summarize_benchmark,
)
from .data import generate_synthetic_startups
from .explainability import explain_applicant
from .fairness import fairness_audit, opportunity_gap
from .geographic import (
    prepare_public_state_map,
    public_state_metric_options,
    summarize_synthetic_states,
)
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
    "benchmark_model_registry",
    "build_pipeline",
    "explain_applicant",
    "fairness_audit",
    "generate_synthetic_startups",
    "get_sba_dataset_metadata",
    "global_feature_importance",
    "load_sba_public_workbook",
    "opportunity_gap",
    "prepare_public_state_map",
    "public_state_metric_options",
    "run_model_benchmark",
    "summarize_allocation",
    "summarize_synthetic_states",
    "summarize_benchmark",
    "train_model",
]
