"""Probability-calibration diagnostics for the synthetic research prototype.

Calibration analysis is intentionally evaluated on held-out synthetic observations. The
results describe the behavior of the demonstration model only and do not establish
real-world lending or investment validity.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import brier_score_loss, log_loss, roc_auc_score
from sklearn.model_selection import train_test_split

from .config import MODEL_FEATURES, RANDOM_SEED, TARGET
from .data import generate_synthetic_startups
from .modeling import build_pipeline

DEFAULT_CALIBRATION_SPLIT_SEEDS = (42, 43, 44, 45, 46)
CALIBRATION_METHODS = ("uncalibrated", "sigmoid", "isotonic")


def calibration_curve_table(
    y_true: pd.Series | np.ndarray,
    probabilities: pd.Series | np.ndarray,
    n_bins: int = 10,
) -> pd.DataFrame:
    """Return a reliability table with counts, mean probability, and observed rate."""
    if n_bins < 2:
        raise ValueError("n_bins must be at least 2")

    y = np.asarray(y_true, dtype=float)
    p = np.asarray(probabilities, dtype=float)
    if len(y) != len(p) or len(y) == 0:
        raise ValueError("y_true and probabilities must have the same non-zero length")
    if np.any((p < 0) | (p > 1)):
        raise ValueError("probabilities must be between 0 and 1")

    edges = np.linspace(0.0, 1.0, n_bins + 1)
    bin_ids = np.digitize(p, edges[1:-1], right=False)
    rows: list[dict[str, float | int]] = []

    for bin_id in range(n_bins):
        mask = bin_ids == bin_id
        if not mask.any():
            continue
        rows.append(
            {
                "bin": bin_id + 1,
                "lower_bound": float(edges[bin_id]),
                "upper_bound": float(edges[bin_id + 1]),
                "count": int(mask.sum()),
                "mean_predicted_probability": float(p[mask].mean()),
                "observed_rate": float(y[mask].mean()),
                "absolute_gap": float(abs(p[mask].mean() - y[mask].mean())),
            }
        )

    return pd.DataFrame(rows)


def expected_calibration_error(
    y_true: pd.Series | np.ndarray,
    probabilities: pd.Series | np.ndarray,
    n_bins: int = 10,
) -> float:
    """Compute count-weighted expected calibration error (ECE)."""
    table = calibration_curve_table(y_true, probabilities, n_bins=n_bins)
    total = int(table["count"].sum())
    return float((table["absolute_gap"] * table["count"] / total).sum())


def run_calibration_benchmark(
    data: pd.DataFrame | None = None,
    split_seeds: tuple[int, ...] = DEFAULT_CALIBRATION_SPLIT_SEEDS,
    n_bins: int = 10,
) -> pd.DataFrame:
    """Compare uncalibrated, sigmoid, and isotonic probabilities on holdout data."""
    if data is None:
        data = generate_synthetic_startups(seed=RANDOM_SEED)
    if not split_seeds:
        raise ValueError("split_seeds must contain at least one random seed")

    missing = sorted(set(MODEL_FEATURES + [TARGET]) - set(data.columns))
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    features = data[MODEL_FEATURES].copy()
    target = data[TARGET].astype(int)
    rows: list[dict[str, float | int | str]] = []

    for split_seed in split_seeds:
        x_train, x_test, y_train, y_test = train_test_split(
            features,
            target,
            test_size=0.25,
            stratify=target,
            random_state=split_seed,
        )

        for method in CALIBRATION_METHODS:
            if method == "uncalibrated":
                estimator = build_pipeline(random_state=split_seed)
            else:
                estimator = CalibratedClassifierCV(
                    estimator=build_pipeline(random_state=split_seed),
                    method=method,
                    cv=3,
                )

            estimator.fit(x_train, y_train)
            probabilities = estimator.predict_proba(x_test)[:, 1]

            rows.append(
                {
                    "split_seed": split_seed,
                    "method": method,
                    "roc_auc": float(roc_auc_score(y_test, probabilities)),
                    "brier": float(brier_score_loss(y_test, probabilities)),
                    "log_loss": float(log_loss(y_test, probabilities)),
                    "ece": expected_calibration_error(
                        y_test.to_numpy(), probabilities, n_bins=n_bins
                    ),
                    "mean_probability": float(probabilities.mean()),
                    "observed_rate": float(y_test.mean()),
                }
            )

    return pd.DataFrame(rows)


def summarize_calibration(results: pd.DataFrame) -> pd.DataFrame:
    """Aggregate repeated calibration runs into mean and standard-deviation metrics."""
    required = {"method", "roc_auc", "brier", "log_loss", "ece"}
    missing = sorted(required - set(results.columns))
    if missing:
        raise ValueError(f"Missing calibration result columns: {missing}")

    return (
        results.groupby("method", as_index=False)
        .agg(
            roc_auc_mean=("roc_auc", "mean"),
            roc_auc_std=("roc_auc", "std"),
            brier_mean=("brier", "mean"),
            brier_std=("brier", "std"),
            log_loss_mean=("log_loss", "mean"),
            ece_mean=("ece", "mean"),
            ece_std=("ece", "std"),
        )
        .sort_values(["brier_mean", "ece_mean"])
        .reset_index(drop=True)
    )
