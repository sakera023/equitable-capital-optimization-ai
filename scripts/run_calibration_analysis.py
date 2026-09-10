"""Run probability-calibration diagnostics and write machine-readable outputs."""

from pathlib import Path

from equitable_capital.calibration import run_calibration_benchmark, summarize_calibration

OUTPUT_DIR = Path("benchmarks")


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    results = run_calibration_benchmark()
    summary = summarize_calibration(results)

    results.to_csv(OUTPUT_DIR / "calibration_runs.csv", index=False)
    summary.to_csv(OUTPUT_DIR / "calibration_summary.csv", index=False)

    print(summary.to_string(index=False))
    print(f"Wrote {OUTPUT_DIR / 'calibration_runs.csv'}")
    print(f"Wrote {OUTPUT_DIR / 'calibration_summary.csv'}")


if __name__ == "__main__":
    main()
