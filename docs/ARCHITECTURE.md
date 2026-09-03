# Architecture

## Design goals

The repository is organized around five principles:

1. **Separation of concerns** — data generation, modeling, explainability, fairness,
   and allocation are independent modules.
2. **Reproducibility** — explicit seeds and deterministic tests make results repeatable.
3. **Inspectability** — no hidden external model API is required.
4. **Responsible research** — predictive logic is separated from policy simulation.
5. **Extensibility** — synthetic inputs and the baseline model can be replaced without
   rewriting the dashboard.

## Component map

```text
src/equitable_capital/
├── config.py          Shared constants and model feature definitions
├── data.py            Synthetic dataset generator
├── modeling.py        Pipeline construction, training, metrics, importance
├── explainability.py  Applicant-level local sensitivity
├── fairness.py        Structural-context diagnostic metrics
└── allocation.py      Funding-allocation scenario simulation
```

## Data flow

```text
Synthetic Data
    |
    v
Predictive Model
    |-----------------------> Streamlit UI
    |                         (readiness scores + metrics)
    |
    +--> Explainability ----> Streamlit UI
    |     (local sensitivity)
    |
    +--> Fairness Audit ----> Streamlit UI
    |     (context diagnostics)
    |
    +--> Allocation Engine -> Streamlit UI
          ^
          |
   Structural Context Index
```

## Boundary between prediction and allocation

The predictive model estimates a synthetic funding-success probability from operating
and market features.

The allocation simulator then uses model scores plus an explicit research policy
parameter. This prevents the equity weighting from being hidden inside the predictive
model.

## Deployment

The interactive application is a Streamlit process importing the local Python package.
No database, external API, or secret is required for the default demonstration.

For production-grade research deployment, add:

- authenticated data access;
- model artifact versioning;
- immutable experiment tracking;
- centralized logging;
- environment-specific configuration;
- data validation;
- model monitoring; and
- access controls.
