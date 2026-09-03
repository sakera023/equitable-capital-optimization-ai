# Equitable Capital Optimization AI

[![CI](https://github.com/sakera023/equitable-capital-optimization-ai/actions/workflows/ci.yml/badge.svg)](https://github.com/sakera023/equitable-capital-optimization-ai/actions/workflows/ci.yml)
[![Live App](https://img.shields.io/badge/Live%20App-Streamlit-FF4B4B?logo=streamlit&logoColor=white)](https://equitable-capital-ai-sakera.streamlit.app)
[![PyPI](https://img.shields.io/pypi/v/equitable-capital-optimization-ai.svg)](https://pypi.org/project/equitable-capital-optimization-ai/)
![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)

A reproducible research prototype for **predictive capital-readiness analysis, model
explainability, fairness auditing, and equity-aware capital-allocation simulation** for
underserved U.S. entrepreneurial ecosystems.

The project is inspired by:

> **An AI-Powered Framework for Equitable Capital Optimization: Leveraging Predictive
> Intelligence to Empower Underserved Entrepreneurial Ecosystems in the U.S.**

Related publication:
[ResearchGate](https://www.researchgate.net/publication/410866072_An_AI-Powered_Framework_for_Equitable_Capital_Optimization_Leveraging_Predictive_Intelligence_to_Empower_Underserved_Entrepreneurial_Ecosystems_in_the_US)

## Live demo

**Public research dashboard:** [Launch the Streamlit application](https://equitable-capital-ai-sakera.streamlit.app)

The live application provides an interactive demonstration of capital-readiness scoring,
local model explanation, fairness auditing, and equity-aware allocation simulation using
reproducible synthetic business data. No login or API key is required.

## Why this project exists

Access to capital is not only a prediction problem. It is also an allocation,
transparency, and measurement problem. This repository separates those concerns into
four independently testable components:

| Component | Purpose |
| --- | --- |
| Predictive modeling | Estimate funding-success probability from business and market features |
| Explainability | Show how applicant-level features influence the model locally |
| Fairness auditing | Compare outcomes across structural-access contexts |
| Capital allocation | Compare efficiency-only and equity-aware funding scenarios |

## Responsible-use boundary

> **Research and educational use only.**
>
> This project must not be used to make real lending, credit, investment, employment,
> housing, insurance, benefits, or eligibility decisions.

The predictive model intentionally excludes protected personal characteristics.
Structural context indicators are used for research auditing and allocation simulation,
not as protected-trait proxies for real-world underwriting.

## Architecture

```text
Synthetic Business Data
          |
          v
   Feature Pipeline
          |
          v
  Random Forest Model
      /          \
     v            v
Readiness      Local
 Scores      Explanation
   |              |
   v              |
Fairness Audit    |
   |              |
   +-------> Research Dashboard
   |
   v
Allocation Simulator
   |
   +-------> Research Dashboard
```

See [Architecture](docs/ARCHITECTURE.md) and [Methodology](docs/METHODOLOGY.md).

## Key capabilities

- Reproducible synthetic U.S. small-business/startup data generation
- Scikit-learn preprocessing and Random Forest classification pipeline
- Holdout evaluation with ROC-AUC, accuracy, precision, recall, F1, and Brier score
- Capital Readiness Score derived from predicted funding-success probability
- Global feature-importance reporting
- Applicant-level local sensitivity explanations
- Structural-context fairness audit and selection-rate comparison
- Efficiency-only and equity-aware capital-allocation simulation
- Interactive Streamlit research dashboard
- Live browser for official SBA state and metropolitan small-business datasets
- Automated tests and linting in GitHub Actions
- Model card, citation metadata, contribution guide, and security policy

## Python package

The reusable research code lives in the `equitable_capital` Python package.

After a release is published to PyPI, install it with:

```bash
pip install equitable-capital-optimization-ai
```

Example:

```python
from equitable_capital import (
    allocate_capital,
    fairness_audit,
    generate_synthetic_startups,
    train_model,
)

data = generate_synthetic_startups()
result = train_model(data)
audit = fairness_audit(result.scored_data)
```

For local development, install the repository in editable mode:

```bash
pip install -e ".[dev]"
```

## Reproducible examples

The repository includes four Jupyter notebooks that walk through the research workflow
from prediction to fairness, allocation, and official U.S. public-data context:

1. [Capital Readiness Analysis](examples/01_capital_readiness.ipynb)
2. [Fairness and Opportunity Audit](examples/02_fairness_audit.ipynb)
3. [Equity-Aware Capital Allocation](examples/03_equitable_allocation.ipynb)
4. [Official U.S. Small-Business Data Context](examples/04_public_us_data_context.ipynb)

See the [examples guide](examples/README.md) for local setup and research-use notes.

## Quick start

```bash
git clone https://github.com/sakera023/equitable-capital-optimization-ai.git
cd equitable-capital-optimization-ai
python -m venv .venv
```

Activate the environment.

**Windows**

```bash
.venv\Scripts\activate
```

**macOS/Linux**

```bash
source .venv/bin/activate
```

Install and run:

```bash
pip install -r requirements.txt
streamlit run app.py
```

Development checks:

```bash
pip install -r requirements-dev.txt
ruff check src tests app.py
python -m pytest -q
```

## Repository structure

```text
.
├── app.py
├── pyproject.toml
├── requirements.txt
├── requirements-dev.txt
├── Makefile
├── src/
│   └── equitable_capital/
│       ├── __init__.py
│       ├── allocation.py
│       ├── config.py
│       ├── data.py
│       ├── explainability.py
│       ├── fairness.py
│       └── modeling.py
├── tests/
├── examples/
│   ├── 01_capital_readiness.ipynb
│   ├── 02_fairness_audit.ipynb
│   ├── 03_equitable_allocation.ipynb
│   └── 04_public_us_data_context.ipynb
├── docs/
├── .github/
├── CITATION.cff
├── CONTRIBUTING.md
├── SECURITY.md
├── CHANGELOG.md
└── LICENSE
```

## Data design

The predictive model uses **synthetic business-level data by default**. This avoids
exposing private financial records, makes the project reproducible, and prevents the
demonstration from implying real-world applicant-level predictive validity.

Predictive features include revenue, growth, cash runway, employees, operating history,
debt-service coverage, digital adoption, market demand, management capacity, requested
capital, industry, and state.

### Official U.S. public-data layer

The live application also provides a separate browser for authoritative aggregate
small-business statistics from the **U.S. Small Business Administration Office of
Advocacy**:

- [State Small Business Statistics 2025](https://data.sba.gov/dataset/state-small-business-statistics-2025)
- [Metropolitan Area Small Business Statistics 2025](https://data.sba.gov/dataset/metropolitan-area-small-business-statistics-2025)

The application resolves the current official workbook through the SBA open-data CKAN
catalog at runtime, so the repository does not need to store a stale government-data
copy. Public aggregate statistics are displayed for geographic and economic context;
they are **not mixed into the synthetic applicant-level model**.

See [Public U.S. Data Layer](docs/PUBLIC_DATA.md) for provenance and research-use notes.

## Model evaluation

The application reports ROC-AUC, accuracy, precision, recall, F1 score, and Brier score.
These metrics evaluate the synthetic demonstration only.

## Fairness and equity analysis

A **structural barrier index** is built from contextual variables such as low-income
area, rural area, limited finance access, and digital adoption.

The index is reserved for post-model fairness diagnostics and research simulation of
equity-aware allocation policies. It is not included in the predictive training
features.

## Reproducibility

The synthetic data generator and model pipeline use explicit random seeds. Tests verify
data ranges, prediction bounds, allocation-budget constraints, and fairness-audit
outputs. CI runs on every push and pull request.

## Research roadmap

Planned extensions include gradient-boosted model benchmarks, probability calibration,
SHAP, temporal/geographic validation, county-level opportunity maps, Census and CDFI
public-data integrations, constrained optimization, and uncertainty analysis.

See [Research Roadmap](docs/RESEARCH_ROADMAP.md).

## Citation

If you use the software, cite the repository metadata in [CITATION.cff](CITATION.cff).
If you use the associated research concept, cite the publication separately and clearly
distinguish research findings from this software prototype.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

## Security

Do not publish secrets, private financial information, or real applicant records in
issues or pull requests. See [SECURITY.md](SECURITY.md).

## License

MIT License. See [LICENSE](LICENSE).

## Maintainer

**Sakera Begum**
