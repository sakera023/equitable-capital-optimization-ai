"""Reproducible model benchmarking for the synthetic research prototype."""

from __future__ import annotations

from time import perf_counter

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import (
    ExtraTreesClassifier,
    HistGradientBoostingClassifier,
    RandomForestClassifier,
)
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    brier_score_loss,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from .config import (
    CATEGORICAL_FEATURES,
    MODEL_FEATURES,
    NUMERIC_FEATURES,
    RANDOM_SEED,
    TARGET,
)
from .data import generate_synthetic_startups

BENCHMARK_PROTOCOL_VERSION = "1.0"
DEFAULT_BENCHMARK_SPLIT_SEEDS = (42, 43, 44, 45, 46)


def _benchmark_preprocessor() -> ColumnTransformer:
    """Build a dense preprocessor so all benchmark models use the same inputs."""
    return ColumnTransformer(
        [
            ("num", StandardScaler(), NUMERIC_FEATURES),
            (
                "cat",
                OneHotEncoder(handle_unknown="ignore", sparse_output=False),
                CATEGORICAL_FEATURES,
            ),
        ]
    )


def benchmark_model_registry(random_state: int = RANDOM_SEED) -> dict[str, object]:
    """Return the model families compared by the benchmark."""
    return {
        "Logistic Regression": LogisticRegression(
            max_iter=1500,
            class_weight="balanced",
            random_state=random_state,
        ),
        "Random Forest": RandomForestClassifier(
            n_estimators=300,
            max_depth=9,
            min_samples_leaf=5,
            class_weight="balanced",
            random_state=random_state,
            n_jobs=-1,
        ),
        "Extra Trees": ExtraTreesClassifier(
            n_estimators=300,
            max_depth=10,
            min_samples_leaf=3,
            class_weight="balanced",
            random_state=random_state,
            n_jobs=-1,
        ),
        "HistGradientBoosting": HistGradientBoostingClassifier(
            max_iter=200,
            learning_rate=0.06,
            max_leaf_nodes=31,
            l2_regularization=0.5,
            random_state=random_state,
        ),
    }


def run_model_benchmark(
    data: pd.DataFrame | None = None,
    split_seeds: tuple[int, ...] = DEFAULT_BENCHMARK_SPLIT_SEEDS,
) -> pd.DataFrame:
    """Run repeated stratified holdout comparisons on the synthetic dataset."""
    if data is None:
        data = generate_synthetic_startups(seed=RANDOM_SEED)

    missing = sorted(set(MODEL_FEATURES + [TARGET]) - set(data.columns))
    if missing:
        raise ValueError(f"Missing required columns: {missing}")
    if not split_seeds:
        raise ValueError("split_seeds must contain at least one random seed")

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

        for model_name, estimator in benchmark_model_registry(split_seed).items():
            pipeline = Pipeline(
                [
                    ("preprocess", _benchmark_preprocessor()),
                    ("model", estimator),
                ]
            )

            started = perf_counter()
            pipeline.fit(x_train, y_train)
            fit_seconds = perf_counter() - started

            started = perf_counter()
            probabilities = pipeline.predict_proba(x_test)[:, 1]
            inference_seconds = perf_counter() - started
            predictions = (probabilities >= 0.50).astype(int)

            rows.append(
                {
                    "split_seed": split_seed,
                    "model": model_name,
                    "roc_auc": float(roc_auc_score(y_test, probabilities)),
                    "accuracy": float(accuracy_score(y_test, predictions)),
                    "precision": float(
                        precision_score(y_test, predictions, zero_division=0)
                    ),
                    "recall": float(recall_score(y_test, predictions, zero_division=0)),
                    "f1": float(f1_score(y_test, predictions, zero_division=0)),
                    "brier": float(brier_score_loss(y_test, probabilities)),
                    "fit_seconds": float(fit_seconds),
                    "inference_ms_per_1000": float(
                        inference_seconds * 1_000_000 / len(x_test)
                    ),
                }
            )

    return pd.DataFrame(rows)


def summarize_benchmark(results: pd.DataFrame) -> pd.DataFrame:
    """Aggregate repeated benchmark runs into mean and standard-deviation metrics."""
    required = {
        "model",
        "roc_auc",
        "accuracy",
        "precision",
        "recall",
        "f1",
        "brier",
        "fit_seconds",
        "inference_ms_per_1000",
    }
    missing = sorted(required - set(results.columns))
    if missing:
        raise ValueError(f"Missing benchmark result columns: {missing}")

    summary = (
        results.groupby("model", as_index=False)
        .agg(
            roc_auc_mean=("roc_auc", "mean"),
            roc_auc_std=("roc_auc", "std"),
            accuracy_mean=("accuracy", "mean"),
            precision_mean=("precision", "mean"),
            recall_mean=("recall", "mean"),
            f1_mean=("f1", "mean"),
            brier_mean=("brier", "mean"),
            fit_seconds_mean=("fit_seconds", "mean"),
            inference_ms_per_1000_mean=("inference_ms_per_1000", "mean"),
        )
        .sort_values(["roc_auc_mean", "f1_mean"], ascending=False)
        .reset_index(drop=True)
    )
    return summary
