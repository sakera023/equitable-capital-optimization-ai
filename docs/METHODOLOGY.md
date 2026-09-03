# Methodology

## Research objective

This software prototype operationalizes an AI-powered framework for studying equitable
capital optimization in underserved U.S. entrepreneurial ecosystems.

It separates four analytical tasks:

1. Predictive capital-readiness modeling
2. Applicant-level model explainability
3. Structural-access and fairness auditing
4. Capital-allocation scenario simulation

## Synthetic data

The repository generates synthetic startup and small-business records so the full
workflow can be reproduced without exposing private financial information.

Features include revenue, growth, cash runway, employees, years operating,
debt-service coverage, digital adoption, market demand, management capacity,
requested capital, industry, and state.

## Protected characteristics

Race, ethnicity, gender, religion, disability, immigration status, and other protected
personal characteristics are excluded from the predictive model.

The structural barrier index is built from contextual indicators such as low-income
area, rural area, limited finance access, and digital adoption. It is used for
research auditing and allocation simulation rather than model training.

## Predictive model

The baseline model is a Random Forest classifier in a scikit-learn pipeline.
Categorical features are one-hot encoded and numeric features are standardized.

The dashboard reports holdout ROC-AUC and accuracy.

## Explainability

The prototype uses a transparent local sensitivity method. Each numeric feature is
replaced with the dataset median and the change in predicted probability is measured.
This is a directional contribution proxy, not a causal explanation.

## Fairness audit

The audit compares selection rates and average scores between higher- and lower-barrier
business contexts. These metrics are diagnostic and do not constitute a legal
determination of discrimination or compliance.

## Capital allocation

Two research scenarios are simulated:

- **Efficiency-only:** prioritizes expected success relative to requested capital.
- **Equity-aware:** blends predicted success with structural-access context.

The simulator is for academic and policy research only and must not be used for real
underwriting, lending, investing, or eligibility decisions.

## Future empirical extension

A publication-grade version could integrate public or aggregate data from the
U.S. Census Bureau Annual Business Survey, SBA datasets, CDFI Fund data, and regional
economic indicators, together with calibration, temporal validation, SHAP analysis,
robustness testing, and constrained optimization.
