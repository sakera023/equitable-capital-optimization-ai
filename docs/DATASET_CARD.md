# Synthetic Dataset Card

## Dataset name

**Equitable Capital Optimization Synthetic Startup Dataset**

## Purpose

The dataset is generated in code to support reproducible demonstrations of predictive
modeling, explainability, distributional diagnostics, allocation simulation, and
robustness testing without exposing real applicant or business records.

It is **not** a survey, administrative dataset, lender portfolio, or historical record of
real funding decisions.

## Generation

The default generator creates 1,500 synthetic observations using NumPy's deterministic
random generator with seed 42. A minimum sample size of 100 is enforced for the standard
demonstration workflow.

Generated geography is limited to ten synthetic state categories: VA, MD, DC, NC, GA, TX,
CA, NY, IL, and FL. Industry categories include Technology, Retail, Professional Services,
Food, Healthcare, Manufacturing, Education, and Logistics.

## Feature families

### Business and operating characteristics

- annual revenue;
- revenue growth;
- cash runway;
- employee count;
- years operating;
- debt-service coverage;
- digital adoption;
- market demand;
- management capacity; and
- requested capital.

### Structural-context indicators

- rural-area flag;
- low-income-area flag;
- limited-finance-access flag; and
- a derived underserved-context index.

The context index is a synthetic analytical construct. Its components and weights are
explicitly defined in `src/equitable_capital/data.py`.

## Synthetic target

`funding_success` is sampled from a synthetic logistic probability function using selected
business features. It does not reproduce the underwriting rules, approval process, or
outcomes of any lender, investor, government program, or financial institution.

## Privacy

No personal information, credit files, bank records, tax records, applications, protected
characteristics, or confidential company records are used to construct the synthetic
dataset.

## Appropriate uses

- software testing;
- reproducible machine-learning demonstrations;
- calibration and robustness experiments;
- model-explanation research;
- distributional diagnostic examples; and
- capital-allocation simulation research.

## Inappropriate uses

Do not use synthetic scores or outputs to:

- approve or deny financing;
- rank real applicants;
- represent real approval probabilities;
- infer legal or regulatory compliance;
- claim discrimination or causal disadvantage; or
- claim measured national, state, county, or demographic economic conditions.

For measured geographic context, use the separately documented SBA, Census CBP, Census
ABS, and CDFI Fund public-data modules.
