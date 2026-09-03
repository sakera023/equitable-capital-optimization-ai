"""Run the reproducible benchmark and write CSV outputs."""

from pathlib import Path

from equitable_capital.benchmark import run_model_benchmark, summarize_benchmark

OUTPUT_DIR = Path("benchmarks")


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)

    results = run_model_benchmark()
    summary = summarize_benchmark(results)

    results.to_csv(OUTPUT_DIR / "latest_runs.csv", index=False)
    summary.to_csv(OUTPUT_DIR / "latest_summary.csv", index=False)

    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()
