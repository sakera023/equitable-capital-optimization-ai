"""Predictive modeling and model-evaluation utilities."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
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


@dataclass(frozen=True)
class ModelResult:
    """Container for the trained pipeline, evaluation metrics, and scored data."""

    pipeline: Pipeline
    metrics: dict[str, float]
    scored_data: pd.DataFrame

    @property
    def auc(self) -> float:
        return self.metrics["roc_auc"]

    @property
    def accuracy(self) -> float:
        return self.metrics["accuracy"]


def build_pipeline(random_state: int = RANDOM_SEED) -> Pipeline:
    """Build the preprocessing and Random Forest classification pipeline."""
    preprocess = ColumnTransformer(
        [
            ("num", StandardScaler(), NUMERIC_FEATURES),
            ("cat", OneHotEncoder(handle_unknown="ignore"), CATEGORICAL_FEATURES),
        ]
    )
    model = RandomForestClassifier(
        n_estimators=300,
        max_depth=9,
        min_samples_leaf=5,
        class_weight="balanced",
        random_state=random_state,
        n_jobs=-1,
    )
    return Pipeline([("preprocess", preprocess), ("model", model)])


def train_model(data: pd.DataFrame, random_state: int = RANDOM_SEED) -> ModelResult:
    """Train the model and score the complete synthetic dataset."""
    missing = sorted(set(MODEL_FEATURES + [TARGET]) - set(data.columns))
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    features = data[MODEL_FEATURES].copy()
    target = data[TARGET].astype(int)

    x_train, x_test, y_train, y_test = train_test_split(
        features,
        target,
        test_size=0.25,
        stratify=target,
        random_state=random_state,
    )

    pipeline = build_pipeline(random_state=random_state)
    pipeline.fit(x_train, y_train)

    predictions = pipeline.predict(x_test)
    probabilities = pipeline.predict_proba(x_test)[:, 1]

    metrics = {
        "roc_auc": float(roc_auc_score(y_test, probabilities)),
        "accuracy": float(accuracy_score(y_test, predictions)),
        "precision": float(precision_score(y_test, predictions, zero_division=0)),
        "recall": float(recall_score(y_test, predictions, zero_division=0)),
        "f1": float(f1_score(y_test, predictions, zero_division=0)),
        "brier": float(brier_score_loss(y_test, probabilities)),
    }

    scored = data.copy()
    scored["predicted_success_probability"] = pipeline.predict_proba(features)[:, 1]
    scored["capital_readiness_score"] = (
        100 * scored["predicted_success_probability"]
    ).round(1)

    return ModelResult(pipeline=pipeline, metrics=metrics, scored_data=scored)


def global_feature_importance(result: ModelResult) -> pd.DataFrame:
    """Return transformed-model feature importances in descending order."""
    preprocess = result.pipeline.named_steps["preprocess"]
    model = result.pipeline.named_steps["model"]
    feature_names = preprocess.get_feature_names_out()

    importance = pd.DataFrame(
        {"feature": feature_names, "importance": model.feature_importances_}
    )
    importance["feature"] = (
        importance["feature"]
        .str.replace("num__", "", regex=False)
        .str.replace("cat__", "", regex=False)
    )
    return importance.sort_values("importance", ascending=False).reset_index(drop=True)
