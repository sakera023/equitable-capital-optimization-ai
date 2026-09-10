# County-Level Public Business Context

## Purpose

This layer extends the project beyond state-only geography with authoritative county-level
business measures from the U.S. Census Bureau. It remains separate from the synthetic
applicant-level model.

## Sources

### County Business Patterns 2023

- Publisher: U.S. Census Bureau
- Dataset page: https://www.census.gov/data/datasets/2023/econ/cbp/2023-cbp.html
- County archive: https://www2.census.gov/programs-surveys/cbp/datasets/2023/cbp23co.zip

The integration prepares all-industry county totals for:

- establishments;
- employment;
- annual payroll (thousands of dollars); and
- first-quarter payroll (thousands of dollars).

It creates the standard five-digit county GEOID from two-digit state FIPS and three-digit
county FIPS.

### Census TIGERweb 2023

Generalized county geometry is retrieved state-by-state from the official Census TIGERweb
State/County service. State-scoped retrieval reduces response size and makes an interactive
county research workflow practical.

## Industry concentration

The optional county industry-concentration calculation uses high-level NAICS sector
establishment shares and reports a Herfindahl-Hirschman Index on a 0–10,000 scale together
with the top-sector share and number of observed sectors.

This is a descriptive local business-structure measure. It is not a measure of lender
competition, credit availability, or entrepreneurial quality.

## Interpretation boundary

County business measures describe establishments and payroll in published geographic
aggregates. They should not be treated as applicant-level predictors, causal evidence of
capital constraints, or proof of discrimination. Suppression, classification, vintage,
and geographic-definition limitations in the underlying public data still apply.
