"""Lightweight, transparent local explanation utilities."""

from __future__ import annotations

import pandas as pd
from sklearn.pipeline import Pipeline

from .config import MODEL_FEATURES, NUMERIC_FEATURES


def explain_applicant(
    pipeline: Pipeline,
    applicant: pd.Series,
    reference: pd.DataFrame,
) -> pd.DataFrame:
    """Estimate local directional sensitivity for numeric model features."""
    base = applicant[MODEL_FEATURES].to_frame().T.copy()
    base_probability = float(pipeline.predict_proba(base)[:, 1][0])
    rows: list[dict[str, float | str]] = []

    for feature in NUMERIC_FEATURES:
        perturbed = base.copy()
        perturbed[feature] = reference[feature].median()
        probability = float(pipeline.predict_proba(perturbed)[:, 1][0])
        rows.append(
            {
                "feature": feature,
                "applicant_value": float(base.iloc[0][feature]),
                "reference_median": float(reference[feature].median()),
                "contribution_proxy": base_probability - probability,
            }
        )

    return pd.DataFrame(rows).sort_values(
        "contribution_proxy",
        key=lambda series: series.abs(),
        ascending=False,
    )
