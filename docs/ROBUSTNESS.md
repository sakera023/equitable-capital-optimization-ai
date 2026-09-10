# Model Robustness Protocol

## Purpose

The baseline holdout metrics are supplemented with multiple diagnostics so that model
behavior is not represented by a single random split or a single classification
threshold.

## Diagnostics

### Repeated stratified cross-validation

The baseline pipeline is evaluated across repeated stratified folds using ROC-AUC, Brier
score, F1, and accuracy. This measures sensitivity to partition choice within the
synthetic dataset.

### Threshold sensitivity

Precision, recall, F1, accuracy, and the share of observations classified positive are
reported across multiple probability thresholds. A threshold is therefore treated as a
policy/design choice rather than an intrinsic property of the model.

### Missing-data stress test

The trained pipeline is evaluated after deterministic random masking of held-out feature
values at increasing rates. The pipeline's existing imputers handle missing values while
the resulting ROC-AUC and Brier score show performance degradation.

### Permutation importance

Holdout permutation importance is calculated at the original input-feature level using
ROC-AUC as the scoring metric. This complements tree impurity-based feature importance.

### Geographic holdout

Each synthetic state is held out in turn while the model is trained on all other states.
The resulting state-level ROC-AUC and Brier scores reveal geographic sensitivity in the
synthetic generator.

## Reproduce

```bash
python scripts/run_robustness_analysis.py
```

Outputs are written to `benchmarks/`:

- `repeated_cross_validation.csv`
- `threshold_sensitivity.csv`
- `missing_data_stress.csv`
- `permutation_importance.csv`
- `geographic_holdout.csv`

## Limits

These tests strengthen internal reproducibility and methodological transparency. They do
not convert synthetic outcomes into real-world evidence. Temporal holdout validation and
external criterion validation remain future work because the current demonstration data
do not contain a genuine longitudinal outcome process or representative external labels.
