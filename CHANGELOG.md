# Changelog

All notable changes to this project are documented here.

## [0.3.0] - 2026-09-03

### Added

- live public U.S. data browser in the Streamlit application;
- runtime access to SBA Office of Advocacy state small-business statistics;
- runtime access to SBA metropolitan-area small-business statistics;
- public-data source documentation and provenance metadata;
- tests for public-data resource discovery;
- reproducible Jupyter examples for capital readiness, fairness auditing, capital allocation, and SBA public-data context.

### Changed

- added `openpyxl` for reading official SBA Excel workbooks;
- kept public aggregate data separate from the synthetic predictive model.

## [0.2.0] - 2026-09-03

### Added

- professional `src/` package structure;
- multi-metric model evaluation;
- global feature-importance reporting;
- improved Streamlit research dashboard;
- architecture, methodology, model-card, and roadmap documents;
- `pyproject.toml` packaging metadata;
- development requirements and Makefile;
- linting in CI;
- split unit-test modules;
- citation metadata;
- contributing and security policies;
- GitHub issue and pull-request templates.

### Changed

- increased the Random Forest baseline to 300 estimators;
- separated prediction logic from fairness and allocation modules;
- documented synthetic-data and responsible-use limitations more explicitly.

## [0.1.0] - 2026-09-03

### Added

- initial Streamlit dashboard;
- synthetic business-data generator;
- Random Forest funding-success model;
- fairness audit;
- local sensitivity explanation;
- capital-allocation simulator;
- basic automated tests.
