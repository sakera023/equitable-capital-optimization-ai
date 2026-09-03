# Equitable Capital Optimization AI v0.4.0

This release turns the project into a more complete research-software package with
public-data context, reproducible examples, benchmarking, geographic visualization,
documented case studies, and clearer pathways for citation and legitimate external use.

## Highlights

### Public U.S. data

- SBA State Small Business Statistics integration
- SBA Metropolitan Area Small Business Statistics integration
- runtime source discovery from the official SBA catalog
- documented separation between aggregate public data and synthetic applicant-level modeling

### Reproducible research examples

Five Jupyter notebooks now cover:

1. capital-readiness analysis;
2. fairness auditing;
3. equity-aware allocation;
4. official U.S. public-data context; and
5. geographic visualization.

### Model benchmark

The repository includes a reproducible four-model comparison across:

- Logistic Regression
- Random Forest
- Extra Trees
- HistGradientBoosting

The benchmark reports ROC-AUC, accuracy, precision, recall, F1, Brier score, and
machine-readable outputs.

### Geographic analysis

A dedicated Geographic Insights tab provides interactive U.S. state choropleths for
synthetic research indicators. The public-data workflow can also map suitable official
SBA state-level measures.

### Documented case studies

Three synthetic case studies demonstrate the end-to-end research workflow for:

- rural small-business capital access;
- low-income metropolitan entrepreneurship; and
- growth-stage businesses with constrained capital.

### Academic citation visibility

This release adds or updates:

- CITATION.cff
- CITATION.md
- codemeta.json
- Google Scholar and publication links
- PyPI and live-application links

No DOI is claimed unless a verified DOI is minted by an external research-software archive.

### External use and contribution

The repository now includes:

- ADOPTION.md;
- a Research / Adoption Report issue template;
- a Public Data Source Request template;
- community conduct guidance; and
- public contribution issues for Census data, county mapping, calibration, and verified use feedback.

## Responsible-use boundary

The applicant-level model uses synthetic data and is intended for research and education.
This release must not be used to make real credit, lending, investment, employment,
housing, insurance, benefits, or eligibility decisions.

Official SBA statistics are aggregate contextual data and are not presented as validation
of individual predictions.

## Installation

```bash
pip install equitable-capital-optimization-ai==0.4.0
```

## Live application

https://equitable-capital-ai-sakera.streamlit.app
