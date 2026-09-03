# Case Study 1 — Rural Small-Business Capital Access

## Research question

How can the platform be used to examine a small business operating in a rural context
where access to traditional finance may be limited?

## Illustrative scenario

Consider a **synthetic established service business** operating in a rural U.S. community.
The business has positive revenue, a modest employee base, an active request for growth
capital, and a higher structural-barrier context in the simulation.

This scenario is not based on a real applicant.

## Analytical workflow

### 1. Capital-readiness assessment

Use the **Business Assessment** tab to select a synthetic business with:

- a rural-context indicator;
- a comparatively high structural-barrier index; and
- a non-trivial requested-capital amount.

Review the Capital Readiness Score and predicted funding-success probability.

The score should be interpreted as a model output from the synthetic research dataset,
not as a real approval probability.

### 2. Explainability review

Inspect the local model-sensitivity chart to identify which operating and market features
are associated with upward or downward changes in the model output.

Useful questions include:

- Does cash runway materially affect the score?
- Is debt-service coverage influential?
- How much does management capacity affect the local prediction?
- Is requested capital large relative to the business profile?

### 3. Structural-context audit

Use the **Fairness Audit** tab to compare the selected business's context with the
higher- and lower-barrier synthetic groups.

This helps separate two ideas:

- what the predictive model estimates from operating features; and
- what the research framework observes about the broader access context.

### 4. Geographic context

Use the **Geographic Insights** tab to inspect state-level synthetic indicators.

Then load the official SBA State Small Business Statistics dataset in the
**U.S. Public Data** tab for aggregate context. Public SBA statistics should be treated
as contextual evidence, not as validation of the synthetic applicant prediction.

### 5. Allocation scenario

Compare the efficiency-only allocation with an equity-aware scenario.

A useful research question is whether changing the explicit equity/context weight changes
the share of simulated capital reaching higher-barrier contexts while preserving a
reasonable expected-success profile.

## What this case study demonstrates

This scenario illustrates why the project separates prediction from allocation policy.
A business can have one model score while the allocation simulator separately explores
how a funder might study structural access constraints.

## Limitations

The rural indicator and structural-barrier index are synthetic constructs. No conclusion
about real rural credit access, discrimination, or policy effectiveness should be drawn
from this example alone.
