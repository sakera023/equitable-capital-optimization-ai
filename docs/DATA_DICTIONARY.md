# Research Data Dictionary

This dictionary documents the synthetic applicant-level fields used by the demonstration
model. Measured public-data fields are documented separately in the source-specific pages.

| Field | Type | Role | Definition / generation |
| --- | --- | --- | --- |
| `startup_id` | string | identifier | Synthetic sequential ID; not linked to a real business. |
| `state` | category | model feature | Synthetic state category among VA, MD, DC, NC, GA, TX, CA, NY, IL, FL. |
| `industry` | category | model feature | Synthetic industry category. |
| `annual_revenue` | numeric | model feature | Synthetic annual revenue generated from a log-normal distribution. |
| `revenue_growth_pct` | numeric | model feature | Synthetic annual growth percentage, clipped to -40% to 120%. |
| `cash_runway_months` | numeric | model feature | Synthetic months of runway, clipped to 0.5–24 months. |
| `employees` | integer | model feature | Synthetic employee count from 1 to 79. |
| `years_operating` | numeric | model feature | Synthetic operating history, clipped to 0.2–20 years. |
| `debt_service_coverage` | numeric | model feature | Synthetic coverage ratio, clipped to 0.2–3.5. |
| `digital_adoption_score` | numeric | model feature/context | Synthetic 0–100 digital-adoption score. |
| `market_demand_score` | numeric | model feature | Synthetic 0–100 market-demand score. |
| `management_capacity_score` | numeric | model feature | Synthetic 0–100 management-capacity score. |
| `requested_capital` | numeric | model feature | Synthetic requested capital generated from a log-normal distribution. |
| `rural_area` | binary | context only | Synthetic rural-context flag. |
| `low_income_area` | binary | context only | Synthetic low-income-context flag. |
| `limited_finance_access` | binary | context only | Synthetic limited-finance-access flag. |
| `underserved_context_index` | numeric | audit/allocation context | Weighted synthetic context index from 0–1. It is not a protected-class label. |
| `funding_success` | binary | synthetic target | Bernoulli outcome generated from an explicit synthetic logistic probability function. |
| `predicted_success_probability` | numeric | model output | Random-Forest probability estimate produced by the fitted research pipeline. |
| `capital_readiness_score` | numeric | model output | Predicted probability scaled to a 0–100 presentation score. |

## Modeling separation

The three structural binary indicators and the derived `underserved_context_index` are not
included in the predictive model feature list. The context index is used for distributional
analysis and allocation simulations. This separation makes the modeling design explicit,
although it does not itself establish real-world fairness or regulatory compliance.

## Public-data dictionaries

See:

- [PUBLIC_DATA.md](PUBLIC_DATA.md) — SBA public statistics;
- [COUNTY_CONTEXT.md](COUNTY_CONTEXT.md) — Census County Business Patterns;
- [CENSUS_ABS.md](CENSUS_ABS.md) — Census Annual Business Survey; and
- [CDFI_CONTEXT.md](CDFI_CONTEXT.md) — Certified CDFI geography.
