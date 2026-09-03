# Geographic Visualization

## Purpose

The project includes state-level geographic visualization to make regional patterns easier
to inspect and communicate.

The map layer supports two distinct research contexts:

1. **Synthetic model geography** — state-level summaries of the synthetic capital-readiness
   dataset.
2. **Official SBA geography** — choropleth mapping of numeric state-level indicators loaded
   from the U.S. Small Business Administration public-data workbook.

These two layers remain clearly separated.

## Synthetic geographic indicators

The application aggregates synthetic business records by state and can map:

- average Capital Readiness Score;
- average Structural Barrier Index;
- average requested capital;
- average predicted funding-success probability; and
- number of synthetic businesses.

These results are demonstrations of model behavior, not measured state economic outcomes.

## Official SBA state map

When the SBA State Small Business Statistics workbook is loaded in the **U.S. Public Data**
tab, the application attempts to identify the state field and numeric measures in the
selected worksheet.

Users can choose a numeric measure and render a U.S. state choropleth directly from the
official aggregate worksheet.

The helper module:

`src/equitable_capital/geographic.py`

provides state normalization, state-column detection, numeric-measure discovery, and
map-ready state aggregation.

## Responsible interpretation

Geographic visualization can make patterns visually compelling, but color differences
alone do not demonstrate causation, inequity, discrimination, or policy effectiveness.

The synthetic and official maps should be interpreted as exploratory research tools.
