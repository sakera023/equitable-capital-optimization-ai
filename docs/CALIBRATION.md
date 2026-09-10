# Probability Calibration Analysis

## Purpose

A discrimination metric such as ROC-AUC measures ranking quality, but it does not show
whether a predicted probability is numerically well calibrated. This module therefore
adds a separate reliability analysis for the synthetic research model.

## Protocol

The analysis uses five deterministic stratified holdout splits. For every split it
compares:

1. the existing uncalibrated Random Forest pipeline;
2. sigmoid calibration with three-fold internal cross-validation; and
3. isotonic calibration with three-fold internal cross-validation.

Calibration is fit only on the training partition. The untouched holdout partition is
used to report:

- ROC-AUC;
- Brier score;
- log loss; and
- expected calibration error (ECE) across equal-width probability bins.

Run the analysis with:

```bash
python scripts/run_calibration_analysis.py
```

Machine-readable outputs are written to:

- `benchmarks/calibration_runs.csv`
- `benchmarks/calibration_summary.csv`

## Interpretation

Lower Brier score, log loss, and ECE indicate better probability reliability under this
synthetic experiment. A calibration method can improve reliability without improving
ranking discrimination, so ROC-AUC is reported separately.

## Research boundary

The underlying observations and funding-success labels are synthetic. Calibration results
therefore demonstrate methodology and software behavior; they do **not** establish that
the resulting probabilities are calibrated for real applicants, lenders, investors, or
capital programs. Real-world calibration would require representative external data,
temporal validation, governance review, and domain-appropriate outcome definitions.
