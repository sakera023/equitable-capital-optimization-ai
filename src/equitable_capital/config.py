"""Shared project configuration and feature definitions."""

RANDOM_SEED = 42
DEFAULT_SAMPLE_SIZE = 1500
DEFAULT_SELECTION_THRESHOLD = 0.50
DEFAULT_EQUITY_WEIGHT = 0.30

NUMERIC_FEATURES = [
    "annual_revenue",
    "revenue_growth_pct",
    "cash_runway_months",
    "employees",
    "years_operating",
    "debt_service_coverage",
    "digital_adoption_score",
    "market_demand_score",
    "management_capacity_score",
    "requested_capital",
]

CATEGORICAL_FEATURES = ["state", "industry"]
MODEL_FEATURES = NUMERIC_FEATURES + CATEGORICAL_FEATURES
TARGET = "funding_success"
