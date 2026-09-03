# Methodology

## 1. Research objective

This prototype operationalizes four parts of an equitable-capital research workflow:

1. predictive capital-readiness modeling;
2. applicant-level model explainability;
3. structural-access and fairness auditing; and
4. capital-allocation scenario simulation.

The system is intentionally modular so each component can be evaluated or replaced
without conflating prediction with policy choice.

## 2. Synthetic data

The repository generates reproducible synthetic startup and small-business records.

Synthetic data is used because it:

- avoids publishing private applicant information;
- makes the repository self-contained;
- supports deterministic tests; and
- prevents the demonstration from implying that a real lender dataset has been validated.

The synthetic distribution is illustrative rather than empirically representative.

## 3. Predictive features

The model uses business-level operating and market characteristics:

- annual revenue;
- revenue growth;
- cash runway;
- employee count;
- years operating;
- debt-service coverage;
- digital adoption;
- market demand;
- management capacity;
- requested capital;
- state; and
- industry.

The predictive model does not use race, ethnicity, gender, religion, disability,
immigration status, or other protected personal traits.

## 4. Structural barrier index

The demonstration index combines:

- low-income-area indicator;
- limited-finance-access indicator;
- rural-area indicator; and
- inverse digital-adoption score.

The index is reserved for post-model diagnostics and allocation simulation. It is not
included in the predictive model's feature set.

This distinction is deliberate: predictive performance and policy prioritization are
separate research questions.

## 5. Predictive model

The baseline model is a Random Forest classifier implemented through a scikit-learn
Pipeline.

Preprocessing:

- numeric variables: standardization;
- categorical variables: one-hot encoding.

Training:

- stratified 75/25 train/test split;
- deterministic random seed;
- balanced class weighting;
- 300 trees;
- bounded tree depth and minimum leaf size.

## 6. Evaluation

The holdout evaluation reports:

- ROC-AUC;
- accuracy;
- precision;
- recall;
- F1 score; and
- Brier score.

Accuracy alone is not used because a single metric can obscure class imbalance,
probability quality, or asymmetric error behavior.

These metrics apply only to the synthetic demonstration.

## 7. Explainability

Applicant-level explanations use local sensitivity analysis:

1. calculate the applicant's base predicted probability;
2. replace one numeric feature with the synthetic reference median;
3. recalculate probability; and
4. report the difference as a directional contribution proxy.

This method is intentionally transparent and lightweight. It is not a causal
explanation.

A future research version can add SHAP while preserving this simpler baseline for
comparison.

## 8. Fairness audit

The audit compares:

- selection rate;
- average predicted probability;
- average requested capital;
- average readiness score; and
- selection-rate ratio

between higher- and lower-barrier structural contexts.

The audit is descriptive and diagnostic. It is not a legal test and does not establish
discrimination or regulatory compliance.

## 9. Capital-allocation simulation

Two scenarios are compared.

### Efficiency-only

Ranks applicants using predicted success relative to requested capital.

### Equity-aware

Combines predicted success with the structural barrier index and a small capital-size
penalty.

The equity weight is a policy-simulation parameter, not a learned model coefficient.

## 10. Validation required before real-world use

A publication-grade or operational study would require substantially more evidence,
including:

- representative real-world data;
- clear outcome definitions;
- temporal holdout validation;
- geographic external validation;
- probability calibration;
- missing-data strategy;
- uncertainty intervals;
- subgroup robustness analysis;
- sensitivity analysis;
- independent replication;
- privacy/governance review; and
- applicable legal and regulatory review.

## 11. Public-data extension

Potential aggregate/public inputs include:

- U.S. Census Bureau Annual Business Survey;
- SBA public datasets;
- CDFI Fund public datasets; and
- regional economic indicators.

Applicant-level financial data should only be introduced with appropriate permissions,
privacy controls, governance, and documented data lineage.
