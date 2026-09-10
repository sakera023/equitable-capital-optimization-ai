# Independent Replication Protocol

## Goal

This protocol gives an external researcher, reviewer, instructor, or developer a short and
verifiable way to reproduce the core methodology without relying on screenshots or claims
from the maintainer.

## Environment

Recommended:

- Python 3.11 or 3.12;
- a clean virtual environment; and
- internet access only for optional official public-data layers.

## Install

```bash
pip install equitable-capital-optimization-ai
```

For the newest repository code:

```bash
git clone https://github.com/sakera023/equitable-capital-optimization-ai.git
cd equitable-capital-optimization-ai
pip install -r requirements-dev.txt
```

## Reproduce the synthetic research workflow

```bash
python scripts/run_benchmark.py
python scripts/run_calibration_analysis.py
python scripts/run_robustness_analysis.py
```

The workflow covers:

- multi-model repeated holdout benchmarking;
- probability calibration;
- repeated stratified cross-validation;
- threshold sensitivity;
- missing-data stress testing;
- permutation importance; and
- synthetic geographic holdout validation.

## Run automated tests

```bash
ruff check src tests scripts app.py pages
python -m pytest -q
```

## Public-data replication

The separate public-data modules can be used to reproduce:

- SBA aggregate small-business statistics;
- Census County Business Patterns county context;
- current Certified CDFI organization geography; and
- Census Annual Business Survey state/county queries with a user-provided API key.

Public data are not used as labels for the synthetic applicant-level model.

## Report an independent replication

A useful report should include:

- date;
- operating system and Python version;
- GitHub commit SHA or released package version;
- commands or notebooks run;
- whether results reproduced successfully;
- discrepancies or limitations; and
- a public link to a repository, notebook, report, syllabus, or presentation when
  available.

Critical findings are welcome. A reproducible failure or methodological disagreement is
valid independent evidence and should not be suppressed.
