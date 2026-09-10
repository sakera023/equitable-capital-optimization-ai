"""Reproducible robustness diagnostics for the synthetic research model."""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.inspection import permutation_importance
from sklearn.metrics import (
    accuracy_score,
    brier_score_loss,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import RepeatedStratifiedKFold, cross_validate, train_test_split

from .config import MODEL_FEATURES, RANDOM_SEED, TARGET
from .data import generate_synthetic_startups
from .modeling import build_pipeline


def _validated_data(data: pd.DataFrame | None) -> pd.DataFrame:
    frame = generate_synthetic_startups(seed=RANDOM_SEED) if data is None else data.copy()
    missing = sorted(set(MODEL_FEATURES + [TARGET]) - set(frame.columns))
    if missing:
        raise ValueError(f"Missing required columns: {missing}")
    return frame


def repeated_cross_validation(
    data: pd.DataFrame | None = None,
    *,
    n_splits: int = 5,
    n_repeats: int = 2,
    random_state: int = RANDOM_SEED,
) -> pd.DataFrame:
    """Evaluate the baseline pipeline under repeated stratified cross-validation."""
    if n_splits < 2 or n_repeats < 1:
        raise ValueError("n_splits must be >= 2 and n_repeats must be >= 1")
    frame = _validated_data(data)
    cv = RepeatedStratifiedKFold(
        n_splits=n_splits,
        n_repeats=n_repeats,
        random_state=random_state,
    )
    results = cross_validate(
        build_pipeline(random_state=random_state),
        frame[MODEL_FEATURES],
        frame[TARGET].astype(int),
        cv=cv,
        scoring={
            "roc_auc": "roc_auc",
            "brier": "neg_brier_score",
            "f1": "f1",
            "accuracy": "accuracy",
        },
        return_train_score=False,
    )
    output = pd.DataFrame(
        {
            "fold": np.arange(1, len(results["test_roc_auc"]) + 1),
            "roc_auc": results["test_roc_auc"],
            "brier": -results["test_brier"],
            "f1": results["test_f1"],
            "accuracy": results["test_accuracy"],
            "fit_seconds": results["fit_time"],
        }
    )
    return output


def threshold_sensitivity(
    data: pd.DataFrame | None = None,
    *,
    thresholds: tuple[float, ...] = (0.20, 0.30, 0.40, 0.50, 0.60, 0.70, 0.80),
    random_state: int = RANDOM_SEED,
) -> pd.DataFrame:
    """Measure holdout classification trade-offs across probability thresholds."""
    frame = _validated_data(data)
    x_train, x_test, y_train, y_test = train_test_split(
        frame[MODEL_FEATURES],
        frame[TARGET].astype(int),
        test_size=0.25,
        stratify=frame[TARGET].astype(int),
        random_state=random_state,
    )
    model = build_pipeline(random_state=random_state)
    model.fit(x_train, y_train)
    probabilities = model.predict_proba(x_test)[:, 1]
    rows = []
    for threshold in thresholds:
        if not 0 < threshold < 1:
            raise ValueError("thresholds must be strictly between 0 and 1")
        predictions = (probabilities >= threshold).astype(int)
        rows.append(
            {
                "threshold": float(threshold),
                "selection_rate": float(predictions.mean()),
                "precision": float(precision_score(y_test, predictions, zero_division=0)),
                "recall": float(recall_score(y_test, predictions, zero_division=0)),
                "f1": float(f1_score(y_test, predictions, zero_division=0)),
                "accuracy": float(accuracy_score(y_test, predictions)),
            }
        )
    return pd.DataFrame(rows)


def missing_data_stress_test(
    data: pd.DataFrame | None = None,
    *,
    missing_rates: tuple[float, ...] = (0.0, 0.05, 0.10, 0.20),
    repeats: int = 5,
    random_state: int = RANDOM_SEED,
) -> pd.DataFrame:
    """Stress held-out inputs with deterministic missingness and report ROC-AUC."""
    if repeats < 1:
        raise ValueError("repeats must be at least 1")
    frame = _validated_data(data)
    x_train, x_test, y_train, y_test = train_test_split(
        frame[MODEL_FEATURES],
        frame[TARGET].astype(int),
        test_size=0.25,
        stratify=frame[TARGET].astype(int),
        random_state=random_state,
    )
    model = build_pipeline(random_state=random_state)
    model.fit(x_train, y_train)
    rows = []

    for rate in missing_rates:
        if not 0 <= rate < 1:
            raise ValueError("missing_rates must be in [0, 1)")
        for repeat in range(repeats):
            stressed = x_test.copy()
            if rate > 0:
                rng = np.random.default_rng(random_state + repeat + int(rate * 1000))
                mask = rng.random(stressed.shape) < rate
                stressed = stressed.mask(mask)
            probabilities = model.predict_proba(stressed)[:, 1]
            rows.append(
                {
                    "missing_rate": float(rate),
                    "repeat": repeat + 1,
                    "roc_auc": float(roc_auc_score(y_test, probabilities)),
                    "brier": float(brier_score_loss(y_test, probabilities)),
                }
            )
    return pd.DataFrame(rows)


def permutation_feature_importance(
    data: pd.DataFrame | None = None,
    *,
    n_repeats: int = 8,
    random_state: int = RANDOM_SEED,
) -> pd.DataFrame:
    """Compute holdout permutation importance at the original input-feature level."""
    frame = _validated_data(data)
    x_train, x_test, y_train, y_test = train_test_split(
        frame[MODEL_FEATURES],
        frame[TARGET].astype(int),
        test_size=0.25,
        stratify=frame[TARGET].astype(int),
        random_state=random_state,
    )
    model = build_pipeline(random_state=random_state)
    model.fit(x_train, y_train)
    result = permutation_importance(
        model,
        x_test,
        y_test,
        scoring="roc_auc",
        n_repeats=n_repeats,
        random_state=random_state,
    )
    return (
        pd.DataFrame(
            {
                "feature": MODEL_FEATURES,
                "importance_mean": result.importances_mean,
                "importance_std": result.importances_std,
            }
        )
        .sort_values("importance_mean", ascending=False)
        .reset_index(drop=True)
    )


def geographic_holdout_validation(
    data: pd.DataFrame | None = None,
    *,
    random_state: int = RANDOM_SEED,
) -> pd.DataFrame:
    """Train on all other synthetic states and evaluate each state as a held-out geography."""
    frame = _validated_data(data)
    rows = []
    for state in sorted(frame["state"].dropna().unique()):
        train = frame[frame["state"] != state]
        test = frame[frame["state"] == state]
        y_train = train[TARGET].astype(int)
        y_test = test[TARGET].astype(int)
        if y_train.nunique() < 2 or y_test.nunique() < 2:
            continue
        model = build_pipeline(random_state=random_state)
        model.fit(train[MODEL_FEATURES], y_train)
        probabilities = model.predict_proba(test[MODEL_FEATURES])[:, 1]
        rows.append(
            {
                "held_out_state": state,
                "n_test": len(test),
                "observed_rate": float(y_test.mean()),
                "mean_probability": float(probabilities.mean()),
                "roc_auc": float(roc_auc_score(y_test, probabilities)),
                "brier": float(brier_score_loss(y_test, probabilities)),
            }
        )
    return pd.DataFrame(rows).sort_values("held_out_state").reset_index(drop=True)
