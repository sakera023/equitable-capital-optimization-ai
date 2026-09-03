# Model Card

## Intended use
Research demonstration of business capital-readiness modeling, explainability, and fairness auditing.

## Not intended for
Real lending, credit underwriting, investment selection, or eligibility decisions.

## Model
Random Forest classifier using business-level operating and market features.

## Training data
Synthetic startup and small-business records generated reproducibly by this repository.

## Excluded features
Protected personal characteristics and highly sensitive personal data are excluded from predictive features.

## Evaluation
The dashboard reports holdout ROC-AUC and accuracy.

## Limitations
Synthetic data cannot establish real-world validity. Model outputs are not causal.
Fairness metrics are diagnostic and do not establish legal compliance.
