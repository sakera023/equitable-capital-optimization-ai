# Case Study 3 — Growth-Stage Small Business With Constrained Capital

## Research question

How can the platform examine a business that appears operationally strong but is asking
for a relatively large amount of growth capital?

## Illustrative scenario

Consider a **synthetic growth-stage business** with established revenue, positive growth,
a capable management profile, and meaningful market demand. Its requested-capital amount
is large relative to many other records in the synthetic dataset.

## Analytical workflow

### 1. Inspect capital readiness

Select a synthetic record with relatively strong operating metrics and a high requested
capital amount.

Review:

- Capital Readiness Score;
- predicted funding-success probability;
- requested capital; and
- structural-barrier context.

### 2. Explain the score

Use the local model-sensitivity chart to examine whether strong operating indicators
offset the effect of a large capital request.

This is useful for demonstrating how multiple variables contribute to a nonlinear model
rather than relying on a single rule.

### 3. Compare model families

Review the [Model Benchmark Report](../BENCHMARKS.md).

The repository's benchmark shows that the most complex model is not automatically the
best performer on the synthetic dataset. This case study can therefore be repeated with
different model families in future work to test robustness.

### 4. Examine allocation constraints

A strong business can still face an allocation constraint when the total simulated
capital pool is limited.

Use the Capital Allocation tab to test multiple budgets and equity/context weights.

Document how funding one large request affects:

- the number of businesses funded;
- capital utilization;
- expected successes; and
- distribution to higher-barrier contexts.

### 5. Geographic comparison

Use the Geographic Insights tab to compare the selected state with other states in the
synthetic research sample.

If official SBA state data are loaded, keep those aggregate measures clearly separated
from the synthetic applicant-level model.

## What this case study demonstrates

Capital allocation is not identical to prediction. Even a relatively strong predicted
business can compete with other requests under a fixed budget, making the allocation
objective itself an important research question.

## Limitations

The scenario does not estimate investment returns, default risk, or real funding
eligibility. It is an educational simulation.
