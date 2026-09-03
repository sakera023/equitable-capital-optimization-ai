# AI-Powered Equitable Capital Optimization

A research-oriented Python and Streamlit prototype inspired by:

**An AI-Powered Framework for Equitable Capital Optimization: Leveraging Predictive Intelligence to Empower Underserved Entrepreneurial Ecosystems in the U.S.**

The project demonstrates how predictive analytics can be combined with explainability, structural-access auditing, and funding-allocation simulation to study capital access for underserved entrepreneurial ecosystems.

## Core capabilities

- Generates reproducible synthetic U.S. startup and small-business records
- Trains a Random Forest funding-success model
- Produces a Capital Readiness Score
- Provides applicant-level model sensitivity explanations
- Audits outcomes across higher- and lower-barrier business contexts
- Compares efficiency-only and equity-aware capital allocation scenarios
- Presents results in an interactive Streamlit dashboard

## Responsible use

> **Research and educational use only.**
>
> This prototype must not be used to make real lending, credit, investment, employment, housing, insurance, benefits, or eligibility decisions.

The predictive model excludes protected personal characteristics. Structural/geographic indicators are used only for research auditing and allocation simulation.

## Project files

```text
equitable-capital-optimization-ai/
├── app.py
├── core.py
├── requirements.txt
├── .gitignore
├── LICENSE
├── docs/
│   └── METHODOLOGY.md
└── tests/
    └── test_core.py
```

## Run locally

```bash
python -m venv .venv
pip install -r requirements.txt
streamlit run app.py
```

Run tests:

```bash
pytest -q
```

## Model inputs

The predictive prototype uses business-level characteristics including revenue, revenue growth, cash runway, employee count, years operating, debt-service coverage, digital adoption, market demand, management capacity, requested capital, industry, and state.

It does **not** use race, ethnicity, gender, religion, disability, immigration status, or other protected personal traits.

## Research extensions

Future versions can add:

- XGBoost / LightGBM benchmark models
- SHAP explainability
- probability calibration
- U.S. Census Annual Business Survey data
- SBA and CDFI public datasets
- county-level capital-access maps
- constrained optimization
- robustness and bias stress testing
- model cards and dataset documentation

## Author

Sakera Begum

## License

MIT
