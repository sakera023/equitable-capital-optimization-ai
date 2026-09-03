# Examples

These notebooks provide reproducible, research-oriented walkthroughs of the core
capabilities in **Equitable Capital Optimization AI**.

| Notebook | Purpose |
| --- | --- |
| [01 Capital Readiness](01_capital_readiness.ipynb) | Generate synthetic businesses, train the model, inspect performance, and review capital-readiness scores. |
| [02 Fairness Audit](02_fairness_audit.ipynb) | Compare model outcomes across structural-access contexts and test multiple selection thresholds. |
| [03 Equitable Allocation](03_equitable_allocation.ipynb) | Compare efficiency-only and equity-aware capital-allocation scenarios. |
| [04 Public U.S. Data Context](04_public_us_data_context.ipynb) | Discover and load official SBA state or metropolitan small-business workbooks. |

## Run locally

From the repository root:

```bash
python -m venv .venv
```

Activate the environment and install the project:

```bash
pip install -e ".[dev]"
pip install jupyter
jupyter lab
```

Then open the notebooks in the `examples/` directory.

## Research boundary

The applicant-level predictive examples use **synthetic data** and are intended for
research and education only. The public-data example accesses aggregate official U.S.
government statistics for contextual analysis. Public aggregate data are not used to
claim real-world validation of the synthetic prediction model.
