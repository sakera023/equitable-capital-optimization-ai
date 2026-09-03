# Case Study 2 — Low-Income Metropolitan Entrepreneurship

## Research question

How can the platform explore a business operating in a metropolitan area where economic
opportunity and access to capital may be unevenly distributed?

## Illustrative scenario

Consider a **synthetic young business** in a large metropolitan market. It has promising
revenue growth and market demand but a shorter operating history and limited cash runway.

The business is placed in a higher structural-barrier context for research purposes.
No real applicant or neighborhood is represented.

## Analytical workflow

### 1. Review readiness and uncertainty

Use the Business Assessment tab to inspect the selected synthetic business.

Pay particular attention to the interaction between:

- revenue growth;
- years operating;
- cash runway;
- management capacity; and
- requested capital.

A moderately strong readiness score with weak operating history can be useful for
discussing why a single score should not be treated as a complete decision rule.

### 2. Examine model sensitivity

Use the local sensitivity explanation to identify features that move the predicted
probability most strongly around the selected record.

The explanation is directional and local. It does not establish causal effects.

### 3. Compare fairness diagnostics

Use the Fairness Audit tab at several selection thresholds.

Questions to document include:

- How does the selection rate change for higher-barrier contexts?
- Does the selection-rate ratio remain stable when the threshold changes?
- Are average readiness levels different across context groups?

Threshold sensitivity is useful because fairness conclusions can change when the
operational cutoff changes.

### 4. Add metropolitan public context

Load the SBA Metropolitan Area Small Business Statistics dataset in the
**U.S. Public Data** tab.

The aggregate statistics can help characterize the scale and composition of small
business activity in metropolitan areas. They should not be joined to a synthetic
business in a way that implies individual validation.

### 5. Compare allocation scenarios

Use the Capital Allocation tab to compare an efficiency-only allocation with an
equity-aware scenario.

Document the trade-off between:

- expected successes;
- number of simulated businesses funded; and
- share of capital reaching higher-barrier contexts.

## What this case study demonstrates

This scenario shows how predictive performance, fairness diagnostics, public economic
context, and allocation policy can be examined together without collapsing them into a
single automated decision.

## Limitations

The scenario does not identify a real low-income neighborhood, protected group, or
lending institution. It is a research demonstration only.
