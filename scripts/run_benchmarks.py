"""Run the reproducible benchmark and write CSV outputs."""

from pathlib import Path

import plotly.express as px

from equitable_capital.benchmark import run_model_benchmark, summarize_benchmark
from equitable_capital.calibration import run_calibration_benchmark, summarize_calibration

OUTPUT_DIR = Path("benchmarks")


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)

    results = run_model_benchmark()
    summary = summarize_benchmark(results)
    calibration = run_calibration_benchmark()
    calibration_summary = summarize_calibration(calibration.metrics)

    results.to_csv(OUTPUT_DIR / "latest_runs.csv", index=False)
    summary.to_csv(OUTPUT_DIR / "latest_summary.csv", index=False)
    calibration.metrics.to_csv(OUTPUT_DIR / "calibration_runs.csv", index=False)
    calibration_summary.to_csv(OUTPUT_DIR / "calibration_summary.csv", index=False)
    calibration.reliability.to_csv(OUTPUT_DIR / "reliability_curve.csv", index=False)

    figure = px.line(
        calibration.reliability,
        x="mean_predicted_probability",
        y="observed_success_rate",
        color="model",
        line_dash="calibration_method",
        markers=True,
        title="Reliability Diagram: Synthetic Funding-Success Probabilities",
        labels={
            "mean_predicted_probability": "Mean predicted probability",
            "observed_success_rate": "Observed synthetic success rate",
            "model": "Model",
            "calibration_method": "Calibration method",
        },
    )
    figure.add_shape(
        type="line",
        x0=0,
        y0=0,
        x1=1,
        y1=1,
        line={"color": "gray", "dash": "dot"},
    )
    figure.write_html(OUTPUT_DIR / "reliability_diagram.html")

    print(summary.to_string(index=False))
    print()
    print(calibration_summary.to_string(index=False))


if __name__ == "__main__":
    main()
