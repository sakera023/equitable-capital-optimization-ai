# Model Benchmark Report

## Purpose

This benchmark compares several supervised-learning model families under a common,
reproducible preprocessing and evaluation protocol for the **synthetic** capital-readiness
research dataset.

The goal is not to declare a production underwriting model. The goal is to document
baseline behavior, trade-offs, and reproducibility before external validation is attempted.

## Benchmark design

- Dataset: 1,500 reproducible synthetic small-business records generated with seed 42.
- Features: the same operating, market, capital-request, state, and industry features used
  by the research prototype.
- Target: synthetic `funding_success`.
- Evaluation: five repeated stratified 75/25 train/test splits.
- Split seeds: 42, 43, 44, 45, and 46.
- Decision threshold: 0.50.
- Shared preprocessing:
  - numeric features standardized;
  - categorical features one-hot encoded;
  - identical feature set supplied to every model.
- Metrics:
  - ROC-AUC;
  - accuracy;
  - precision;
  - recall;
  - F1;
  - Brier score.
- Probability-calibration diagnostics:
  - uncalibrated probabilities;
  - sigmoid calibration;
  - isotonic calibration;
  - reliability-curve bins;
  - expected calibration error.

The benchmark implementation is in
[`src/equitable_capital/benchmark.py`](../src/equitable_capital/benchmark.py), and the
command-line runner is
[`scripts/run_benchmarks.py`](../scripts/run_benchmarks.py).

The probability-calibration implementation is in
[`src/equitable_capital/calibration.py`](../src/equitable_capital/calibration.py). The
same command-line runner writes calibration outputs in addition to the model benchmark.

## Models compared

| Model | Role in benchmark |
| --- | --- |
| Logistic Regression | Interpretable linear baseline |
| Random Forest | Current nonlinear ensemble baseline used by the application |
| Extra Trees | Highly randomized tree ensemble comparison |
| HistGradientBoosting | Gradient-boosted nonlinear comparison |

## Reference results

The table below reports the mean across five repeated stratified holdouts. ROC-AUC also
includes the sample standard deviation across the five runs.

| Model | ROC-AUC | Accuracy | Precision | Recall | F1 | Brier ↓ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Logistic Regression | **0.663 ± 0.028** | 0.600 | **0.641** | 0.570 | 0.603 | **0.232** |
| Random Forest | 0.653 ± 0.023 | **0.612** | 0.635 | **0.646** | **0.640** | 0.233 |
| Extra Trees | 0.623 ± 0.023 | 0.597 | 0.627 | 0.603 | 0.614 | 0.239 |
| HistGradientBoosting | 0.606 ± 0.013 | 0.584 | 0.605 | 0.641 | 0.622 | 0.279 |

A machine-readable copy of these reference values is available in
[`benchmarks/reference_summary.csv`](../benchmarks/reference_summary.csv).

## Probability calibration analysis

Probability calibration asks whether predicted probabilities behave like probabilities.
For example, among synthetic businesses assigned a predicted success probability near
0.70, roughly 70% should have the synthetic success label if the model is well calibrated.
This matters because the application presents a probability-derived readiness score, not
only a binary prediction.

The calibration protocol uses the same five stratified holdout splits as the model
benchmark. For each split and model family, it compares:

| Method | Description |
| --- | --- |
| Uncalibrated | The model's native `predict_proba` output |
| Sigmoid | Platt-style calibration learned by cross-validation on the training fold |
| Isotonic | Non-parametric monotonic calibration learned by cross-validation on the training fold |

The table below reports the mean across five repeated stratified holdouts.

| Model | Method | ROC-AUC | Brier ↓ | ECE ↓ |
| --- | --- | ---: | ---: | ---: |
| Logistic Regression | Sigmoid | 0.664 ± 0.030 | **0.230** | 0.048 |
| Logistic Regression | Isotonic | **0.666 ± 0.028** | 0.231 | 0.055 |
| Logistic Regression | Uncalibrated | 0.663 ± 0.028 | 0.231 | 0.067 |
| Random Forest | Sigmoid | **0.655 ± 0.023** | **0.233** | **0.046** |
| Random Forest | Uncalibrated | 0.653 ± 0.023 | 0.233 | 0.048 |
| Random Forest | Isotonic | 0.652 ± 0.028 | 0.235 | 0.058 |
| Extra Trees | Isotonic | **0.630 ± 0.032** | **0.237** | 0.052 |
| Extra Trees | Sigmoid | 0.627 ± 0.032 | 0.238 | **0.046** |
| Extra Trees | Uncalibrated | 0.623 ± 0.023 | 0.239 | 0.056 |
| HistGradientBoosting | Sigmoid | **0.627 ± 0.014** | **0.238** | **0.040** |
| HistGradientBoosting | Isotonic | 0.623 ± 0.015 | 0.240 | 0.051 |
| HistGradientBoosting | Uncalibrated | 0.606 ± 0.013 | 0.279 | 0.174 |

Machine-readable outputs are available in:

- [`benchmarks/calibration_summary.csv`](../benchmarks/calibration_summary.csv)
- [`benchmarks/calibration_runs.csv`](../benchmarks/calibration_runs.csv)
- [`benchmarks/reliability_curve.csv`](../benchmarks/reliability_curve.csv)

Running `python scripts/run_benchmarks.py` also creates
`benchmarks/reliability_diagram.html`, an interactive reliability diagram comparing
observed synthetic success rates with mean predicted probabilities.

## Calibration interpretation

Sigmoid calibration modestly improved the Brier score for Logistic Regression and
Random Forest, and materially improved the HistGradientBoosting probability quality in
this synthetic experiment. Isotonic calibration helped some ranking metrics but also
produced larger maximum bin-level calibration errors for several models, which is a useful
reminder that a more flexible calibration method can overfit small validation folds.

The main practical conclusion is conservative: calibration diagnostics should accompany
any probability-derived readiness score. The results support treating Logistic Regression
and Random Forest as useful probability baselines for this synthetic prototype, while
flagging HistGradientBoosting's uncalibrated probabilities as weaker in this setting.

## Interpretation

No model dominates every metric.

**Logistic Regression** achieved the highest mean ROC-AUC and the lowest mean Brier score
in this synthetic experiment. That suggests the synthetic target-generation process has a
substantial linear signal and that a simpler model is competitive when ranking and
probability quality are emphasized.

**Random Forest** achieved the highest mean accuracy, recall, and F1 score at the default
0.50 threshold. This supports retaining it as the current interactive application baseline
when threshold-level classification balance is the main demonstration objective.

**Extra Trees** and **HistGradientBoosting** did not improve ROC-AUC over the two leading
baselines in this particular synthetic setting. Their inclusion remains useful because it
shows that additional model complexity does not automatically improve performance.

## Why the result is scientifically useful

A benchmark is valuable even when the most complex model does not win. The comparison
reduces the risk of selecting a model merely because it is more sophisticated. It also
creates a documented baseline against which future improvements can be tested.

For this project, the benchmark suggests two complementary baselines:

1. **Logistic Regression** for ranking/calibration-oriented comparison.
2. **Random Forest** for the current application workflow and threshold-based F1/recall.

## Reproduce the benchmark

From the repository root:

```bash
pip install -e ".[dev]"
python scripts/run_benchmarks.py
```

The command writes:

```text
benchmarks/latest_runs.csv
benchmarks/latest_summary.csv
```

Runtime measurements are also produced by the script, but they are intentionally omitted
from the fixed reference table because timing is hardware-dependent.

## Limitations

These numbers are **not evidence of real-world lending performance**.

The benchmark uses a synthetic dataset whose target is generated by a known simulated
process. It therefore cannot establish external validity, policy effectiveness, causal
impact, fairness in real credit markets, or performance for any real applicant population.

Additional work required before stronger claims would include:

- temporal validation;
- geographic holdout validation;
- external public or appropriately governed private datasets;
- probability calibration analysis;
- subgroup calibration analysis;
- subgroup stability analysis;
- uncertainty estimation;
- comparison with domain-specific operational baselines;
- documented data-quality and leakage checks.

## Responsible research conclusion

The benchmark strengthens the repository by making model selection transparent and
reproducible. It should be treated as a **research baseline**, not as a production model
selection exercise or a recommendation for real lending decisions.
