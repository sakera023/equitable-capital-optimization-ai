# Contributing

Thank you for considering a contribution.

## Development setup

```bash
git clone https://github.com/sakera023/equitable-capital-optimization-ai.git
cd equitable-capital-optimization-ai
python -m venv .venv
pip install -r requirements-dev.txt
```

## Before opening a pull request

Run:

```bash
ruff check src tests scripts app.py
python -m pytest -q
```

A pull request should:

- describe the research or engineering problem;
- explain the implementation choice;
- include tests for new behavior;
- update documentation when behavior changes; and
- avoid committing secrets or private applicant data.

## Research contributions

For changes to fairness metrics, allocation objectives, or model features, include the
methodological reasoning and expected trade-offs in the pull request.

## Data contributions

Do not submit private, proprietary, or personally identifiable applicant data.

Public-data integrations should document source, license/terms, retrieval date, field
definitions, transformation steps, and known limitations.

## Community and external use

Before contributing, review [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) and
[ADOPTION.md](ADOPTION.md).

External contributors are especially welcome to work on public-data integrations,
geographic validation, calibration, reproducibility, documentation, and independent
testing. If your work uses the software in a public paper, repository, course, or report,
consider sharing a verifiable link through the Research / Adoption Report issue template.

Please do not create artificial stars, fabricated testimonials, or unsupported claims of
impact.
