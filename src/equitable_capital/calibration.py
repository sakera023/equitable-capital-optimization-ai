"""Probability-calibration diagnostics for the synthetic benchmark."""

from __future__ import annotations

from dataclasses import dataclass
from time import perf_counter

import numpy as np
import pandas as pd
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import brier_score_loss, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

from .benchmark import (
    DEFAULT_BENCHMARK_SPLIT_SEEDS,
    _benchmark_preprocessor,
    benchmark_model_registry,
)
from .config import MODEL_FEATURES, RANDOM_SEED, TARGET
from .data import generate_synthetic_startups

CALIBRATION_PROTOCOL_VERSION = "1.0"
DEFAULT_CALIBRATION_METHODS = ("uncalibrated", "sigmoid", "isotonic")


@dataclass(frozen=True)
class CalibrationResult:
    """Container for calibration metrics and reliability-curve points."""

    metrics: pd.DataFrame
    reliability: pd.DataFrame
    predictions: pd.DataFrame


def _validate_calibration_inputs(
    data: pd.DataFrame,
    split_seeds: tuple[int, ...],
    methods: tuple[str, ...],
    n_bins: int,
) -> None:
    missing = sorted(set(MODEL_FEATURES + [TARGET]) - set(data.columns))
    if missing:
        raise ValueError(f"Missing required columns: {missing}")
    if not split_seeds:
        raise ValueError("split_seeds must contain at least one random seed")
    if n_bins < 2:
        raise ValueError("n_bins must be at least 2")

    allowed = set(DEFAULT_CALIBRATION_METHODS)
    unsupported = sorted(set(methods) - allowed)
    if unsupported:
        raise ValueError(f"Unsupported calibration methods: {unsupported}")


def _new_pipeline(model_name: str, random_state: int) -> Pipeline:
    estimator = benchmark_model_registry(random_state)[model_name]
    return Pipeline(
        [
            ("preprocess", _benchmark_preprocessor()),
            ("model", estimator),
        ]
    )


def reliability_curve_frame(
    y_true: pd.Series | np.ndarray,
    probabilities: pd.Series | np.ndarray,
    n_bins: int = 10,
) -> pd.DataFrame:
    """Return equal-width reliability bins for observed vs predicted probability."""
    truth = np.asarray(y_true, dtype=int)
    probs = np.asarray(probabilities, dtype=float)
    if truth.shape[0] != probs.shape[0]:
        raise ValueError("y_true and probabilities must have the same length")
    if n_bins < 2:
        raise ValueError("n_bins must be at least 2")
    if np.any((probs < 0) | (probs > 1)):
        raise ValueError("probabilities must be within [0, 1]")

    edges = np.linspace(0.0, 1.0, n_bins + 1)
    bin_ids = np.clip(np.digitize(probs, edges, right=True) - 1, 0, n_bins - 1)
    rows: list[dict[str, float | int]] = []

    for bin_id in range(n_bins):
        mask = bin_ids == bin_id
        if not mask.any():
            continue
        rows.append(
            {
                "bin": bin_id + 1,
                "bin_lower": float(edges[bin_id]),
                "bin_upper": float(edges[bin_id + 1]),
                "mean_predicted_probability": float(probs[mask].mean()),
                "observed_success_rate": float(truth[mask].mean()),
                "count": int(mask.sum()),
            }
        )

    return pd.DataFrame(rows)


def expected_calibration_error(reliability: pd.DataFrame) -> float:
    """Compute count-weighted expected calibration error from reliability bins."""
    required = {"mean_predicted_probability", "observed_success_rate", "count"}
    missing = sorted(required - set(reliability.columns))
    if missing:
        raise ValueError(f"Missing reliability columns: {missing}")
    if reliability.empty:
        return 0.0

    total = float(reliability["count"].sum())
    if total <= 0:
        return 0.0

    gaps = (
        reliability["mean_predicted_probability"] - reliability["observed_success_rate"]
    ).abs()
    return float((gaps * reliability["count"] / total).sum())


def run_calibration_benchmark(
    data: pd.DataFrame | None = None,
    split_seeds: tuple[int, ...] = DEFAULT_BENCHMARK_SPLIT_SEEDS,
    methods: tuple[str, ...] = DEFAULT_CALIBRATION_METHODS,
    n_bins: int = 10,
) -> CalibrationResult:
    """Run repeated holdout probability-calibration analysis on synthetic data."""
    if data is None:
        data = generate_synthetic_startups(seed=RANDOM_SEED)

    _validate_calibration_inputs(data, split_seeds, methods, n_bins)

    features = data[MODEL_FEATURES].copy()
    target = data[TARGET].astype(int)
    metric_rows: list[dict[str, float | int | str]] = []
    prediction_rows: list[pd.DataFrame] = []

    for split_seed in split_seeds:
        x_train, x_test, y_train, y_test = train_test_split(
            features,
            target,
            test_size=0.25,
            stratify=target,
            random_state=split_seed,
        )

        for model_name in benchmark_model_registry(split_seed):
            fitted_models: dict[str, Pipeline | CalibratedClassifierCV] = {}

            if "uncalibrated" in methods:
                base_pipeline = _new_pipeline(model_name, split_seed)
                base_pipeline.fit(x_train, y_train)
                fitted_models["uncalibrated"] = base_pipeline

            for method in methods:
                if method == "uncalibrated":
                    continue
                calibrated = CalibratedClassifierCV(
                    estimator=_new_pipeline(model_name, split_seed),
                    method=method,
                    cv=3,
                )
                calibrated.fit(x_train, y_train)
                fitted_models[method] = calibrated

            for method, estimator in fitted_models.items():
                started = perf_counter()
                probabilities = estimator.predict_proba(x_test)[:, 1]
                inference_seconds = perf_counter() - started
                reliability = reliability_curve_frame(y_test, probabilities, n_bins=n_bins)
                calibration_gaps = (
                    reliability["mean_predicted_probability"]
                    - reliability["observed_success_rate"]
                ).abs()

                metric_rows.append(
                    {
                        "split_seed": split_seed,
                        "model": model_name,
                        "calibration_method": method,
                        "roc_auc": float(roc_auc_score(y_test, probabilities)),
                        "brier": float(brier_score_loss(y_test, probabilities)),
                        "expected_calibration_error": expected_calibration_error(
                            reliability
                        ),
                        "max_calibration_error": float(calibration_gaps.max()),
                        "n_test": int(len(y_test)),
                        "inference_ms_per_1000": float(
                            inference_seconds * 1_000_000 / len(x_test)
                        ),
                    }
                )

                scored = pd.DataFrame(
                    {
                        "split_seed": split_seed,
                        "model": model_name,
                        "calibration_method": method,
                        "y_true": y_test.to_numpy(),
                        "predicted_probability": probabilities,
                    }
                )
                prediction_rows.append(scored)

    predictions = pd.concat(prediction_rows, ignore_index=True)
    reliability_rows: list[pd.DataFrame] = []
    for (model_name, method), group in predictions.groupby(
        ["model", "calibration_method"],
        sort=True,
    ):
        curve = reliability_curve_frame(
            group["y_true"],
            group["predicted_probability"],
            n_bins=n_bins,
        )
        curve.insert(0, "calibration_method", method)
        curve.insert(0, "model", model_name)
        reliability_rows.append(curve)

    reliability = pd.concat(reliability_rows, ignore_index=True)
    metrics = pd.DataFrame(metric_rows)
    return CalibrationResult(metrics=metrics, reliability=reliability, predictions=predictions)


def summarize_calibration(metrics: pd.DataFrame) -> pd.DataFrame:
    """Aggregate repeated calibration runs into mean and standard-deviation metrics."""
    required = {
        "model",
        "calibration_method",
        "roc_auc",
        "brier",
        "expected_calibration_error",
        "max_calibration_error",
        "inference_ms_per_1000",
    }
    missing = sorted(required - set(metrics.columns))
    if missing:
        raise ValueError(f"Missing calibration result columns: {missing}")

    return (
        metrics.groupby(["model", "calibration_method"], as_index=False)
        .agg(
            roc_auc_mean=("roc_auc", "mean"),
            roc_auc_std=("roc_auc", "std"),
            brier_mean=("brier", "mean"),
            brier_std=("brier", "std"),
            expected_calibration_error_mean=("expected_calibration_error", "mean"),
            max_calibration_error_mean=("max_calibration_error", "mean"),
            inference_ms_per_1000_mean=("inference_ms_per_1000", "mean"),
        )
        .sort_values(["brier_mean", "expected_calibration_error_mean"], ascending=True)
        .reset_index(drop=True)
    )
