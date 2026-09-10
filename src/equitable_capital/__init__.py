"""Public API for the Equitable Capital Optimization research package."""

from .allocation import allocate_capital, summarize_allocation
from .benchmark import (
    benchmark_model_registry,
    run_model_benchmark,
    summarize_benchmark,
)
from .calibration import (
    calibration_curve_table,
    expected_calibration_error,
    run_calibration_benchmark,
    summarize_calibration,
)
from .cdfi import (
    CDFI_CERTIFICATION,
    load_cdfi_certification_workbook,
    summarize_cdfi_by_state,
)
from .census_abs import (
    ABS_2022_COMPANY_SUMMARY,
    build_abs_query_url,
    load_abs_county_data,
    load_abs_state_data,
    total_population_rows,
)
from .census_cbp import (
    CENSUS_CBP_2023,
    STATE_ABBR_TO_FIPS,
    county_name_lookup,
    load_cbp_county_file,
    load_county_geojson,
    summarize_cbp_county_totals,
    summarize_county_industry_concentration,
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
    "ABS_2022_COMPANY_SUMMARY",
    "CDFI_CERTIFICATION",
    "CENSUS_CBP_2023",
    "ModelResult",
    "PUBLIC_DATASETS",
    "STATE_ABBR_TO_FIPS",
    "allocate_capital",
    "benchmark_model_registry",
    "build_abs_query_url",
    "build_pipeline",
    "calibration_curve_table",
    "county_name_lookup",
    "expected_calibration_error",
    "explain_applicant",
    "fairness_audit",
    "generate_synthetic_startups",
    "get_sba_dataset_metadata",
    "global_feature_importance",
    "load_abs_county_data",
    "load_abs_state_data",
    "load_cbp_county_file",
    "load_cdfi_certification_workbook",
    "load_county_geojson",
    "load_sba_public_workbook",
    "opportunity_gap",
    "prepare_public_state_map",
    "public_state_metric_options",
    "run_calibration_benchmark",
    "run_model_benchmark",
    "summarize_allocation",
    "summarize_benchmark",
    "summarize_calibration",
    "summarize_cbp_county_totals",
    "summarize_cdfi_by_state",
    "summarize_county_industry_concentration",
    "summarize_synthetic_states",
    "total_population_rows",
    "train_model",
]
