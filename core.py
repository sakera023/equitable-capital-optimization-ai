from __future__ import annotations

from dataclasses import dataclass
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

NUMERIC_FEATURES = [
    "annual_revenue", "revenue_growth_pct", "cash_runway_months",
    "employees", "years_operating", "debt_service_coverage",
    "digital_adoption_score", "market_demand_score",
    "management_capacity_score", "requested_capital"
]
CATEGORICAL_FEATURES = ["state", "industry"]
MODEL_FEATURES = NUMERIC_FEATURES + CATEGORICAL_FEATURES
TARGET = "funding_success"

@dataclass
class ModelResult:
    pipeline: Pipeline
    auc: float
    accuracy: float
    scored_data: pd.DataFrame

def generate_synthetic_startups(n: int = 1500, seed: int = 42) -> pd.DataFrame:
    """Generate privacy-safe synthetic startup and small-business records."""
    rng = np.random.default_rng(seed)
    states = np.array(["VA", "MD", "DC", "NC", "GA", "TX", "CA", "NY", "IL", "FL"])
    industries = np.array([
        "Technology", "Retail", "Professional Services", "Food",
        "Healthcare", "Manufacturing", "Education", "Logistics"
    ])

    df = pd.DataFrame({
        "startup_id": [f"BUS-{i:04d}" for i in range(1, n + 1)],
        "state": rng.choice(states, n),
        "industry": rng.choice(industries, n),
        "annual_revenue": np.round(rng.lognormal(12.0, 0.9, n), 2),
        "revenue_growth_pct": np.round(rng.normal(18, 18, n).clip(-40, 120), 2),
        "cash_runway_months": np.round(rng.gamma(3.2, 2.0, n).clip(0.5, 24), 2),
        "employees": rng.integers(1, 80, n),
        "years_operating": np.round(rng.gamma(2.5, 1.8, n).clip(0.2, 20), 2),
        "debt_service_coverage": np.round(rng.normal(1.35, 0.45, n).clip(0.2, 3.5), 2),
        "digital_adoption_score": np.round(rng.normal(62, 20, n).clip(0, 100), 1),
        "market_demand_score": np.round(rng.normal(66, 18, n).clip(0, 100), 1),
        "management_capacity_score": np.round(rng.normal(64, 17, n).clip(0, 100), 1),
        "requested_capital": np.round(rng.lognormal(11.3, 0.75, n), 2),
        "rural_area": rng.binomial(1, 0.28, n),
        "low_income_area": rng.binomial(1, 0.35, n),
        "limited_finance_access": rng.binomial(1, 0.33, n),
    })

    df["underserved_context_index"] = np.round(
        (
            0.35 * df["low_income_area"]
            + 0.30 * df["limited_finance_access"]
            + 0.20 * df["rural_area"]
            + 0.15 * (1 - df["digital_adoption_score"] / 100)
        ).clip(0, 1),
        3
    )

    logit = (
        -2.6
        + 0.0000022 * df["annual_revenue"]
        + 0.018 * df["revenue_growth_pct"]
        + 0.075 * df["cash_runway_months"]
        + 0.30 * df["debt_service_coverage"]
        + 0.010 * df["market_demand_score"]
        + 0.008 * df["management_capacity_score"]
        - 0.0000013 * df["requested_capital"]
    )
    probability = 1 / (1 + np.exp(-logit))
    df[TARGET] = rng.binomial(1, probability.clip(0.03, 0.97))
    return df

def train_model(df: pd.DataFrame, random_state: int = 42) -> ModelResult:
    X = df[MODEL_FEATURES].copy()
    y = df[TARGET].astype(int)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, stratify=y, random_state=random_state
    )

    preprocess = ColumnTransformer([
        ("num", StandardScaler(), NUMERIC_FEATURES),
        ("cat", OneHotEncoder(handle_unknown="ignore"), CATEGORICAL_FEATURES),
    ])

    model = RandomForestClassifier(
        n_estimators=250,
        max_depth=9,
        min_samples_leaf=5,
        class_weight="balanced",
        random_state=random_state,
        n_jobs=-1,
    )

    pipeline = Pipeline([("preprocess", preprocess), ("model", model)])
    pipeline.fit(X_train, y_train)

    predictions = pipeline.predict(X_test)
    probabilities = pipeline.predict_proba(X_test)[:, 1]

    scored = df.copy()
    scored["predicted_success_probability"] = pipeline.predict_proba(X)[:, 1]
    scored["capital_readiness_score"] = (
        100 * scored["predicted_success_probability"]
    ).round(1)

    return ModelResult(
        pipeline=pipeline,
        auc=float(roc_auc_score(y_test, probabilities)),
        accuracy=float(accuracy_score(y_test, predictions)),
        scored_data=scored,
    )

def fairness_audit(scored: pd.DataFrame, threshold: float = 0.50) -> pd.DataFrame:
    x = scored.copy()
    x["context_group"] = x["underserved_context_index"].ge(0.50).map({
        True: "Higher structural barriers",
        False: "Lower structural barriers",
    })
    x["selected"] = x["predicted_success_probability"].ge(threshold).astype(int)

    rows = []
    for group, g in x.groupby("context_group", observed=True):
        rows.append({
            "context_group": group,
            "n": len(g),
            "selection_rate": g["selected"].mean(),
            "avg_predicted_success": g["predicted_success_probability"].mean(),
            "avg_requested_capital": g["requested_capital"].mean(),
            "avg_readiness_score": g["capital_readiness_score"].mean(),
        })

    audit = pd.DataFrame(rows)
    if len(audit) == 2:
        maximum = audit["selection_rate"].max()
        minimum = audit["selection_rate"].min()
        audit["selection_rate_ratio"] = minimum / maximum if maximum > 0 else 1.0
    else:
        audit["selection_rate_ratio"] = 1.0
    return audit

def explain_applicant(pipeline, applicant: pd.Series, reference: pd.DataFrame) -> pd.DataFrame:
    """Transparent local sensitivity explanation, not a causal explanation."""
    base = applicant[MODEL_FEATURES].to_frame().T.copy()
    base_probability = float(pipeline.predict_proba(base)[:, 1][0])
    rows = []

    for feature in NUMERIC_FEATURES:
        perturbed = base.copy()
        perturbed[feature] = reference[feature].median()
        probability = float(pipeline.predict_proba(perturbed)[:, 1][0])
        rows.append({
            "feature": feature,
            "contribution_proxy": base_probability - probability,
        })

    return pd.DataFrame(rows).sort_values(
        "contribution_proxy", key=lambda s: s.abs(), ascending=False
    )

def _greedy_allocate(df: pd.DataFrame, budget: float, score_col: str) -> pd.DataFrame:
    ranked = df.sort_values(
        [score_col, "predicted_success_probability"], ascending=False
    ).copy()
    remaining = float(budget)
    rows = []

    for _, row in ranked.iterrows():
        if remaining <= 0:
            break
        requested = float(row["requested_capital"])
        allocated = min(requested, remaining)
        if allocated <= 0:
            continue
        item = row.to_dict()
        item["allocated_capital"] = allocated
        rows.append(item)
        remaining -= allocated

    return pd.DataFrame(rows)

def allocate_capital(
    scored: pd.DataFrame,
    budget: float,
    equity_weight: float = 0.30,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    x = scored.copy()

    x["efficiency_priority"] = (
        x["predicted_success_probability"] /
        x["requested_capital"].clip(lower=1)
    )

    request_norm = x["requested_capital"] / x["requested_capital"].max()
    x["equity_priority"] = (
        (1 - equity_weight) * x["predicted_success_probability"]
        + equity_weight * x["underserved_context_index"]
        - 0.05 * request_norm
    )

    baseline = _greedy_allocate(x, budget, "efficiency_priority")
    equitable = _greedy_allocate(x, budget, "equity_priority")
    return baseline, equitable

def summarize_allocation(allocated: pd.DataFrame, budget: float) -> dict:
    if allocated.empty:
        return {
            "businesses_funded": 0,
            "capital_allocated": 0.0,
            "budget_utilization": 0.0,
            "share_to_higher_barrier_contexts": 0.0,
            "expected_successes": 0.0,
        }

    total = allocated["allocated_capital"].sum()
    higher = allocated["underserved_context_index"] >= 0.5

    return {
        "businesses_funded": int(len(allocated)),
        "capital_allocated": float(total),
        "budget_utilization": float(total / budget if budget else 0),
        "share_to_higher_barrier_contexts": float(
            allocated.loc[higher, "allocated_capital"].sum() / total if total else 0
        ),
        "expected_successes": float(
            (
                allocated["predicted_success_probability"]
                * (allocated["allocated_capital"] / allocated["requested_capital"])
            ).sum()
        ),
    }
