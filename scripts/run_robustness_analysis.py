"""Run model robustness diagnostics and write machine-readable results."""

from pathlib import Path

from equitable_capital.robustness import (
    geographic_holdout_validation,
    missing_data_stress_test,
    permutation_feature_importance,
    repeated_cross_validation,
    threshold_sensitivity,
)

OUTPUT_DIR = Path("benchmarks")


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    cv = repeated_cross_validation()
    threshold = threshold_sensitivity()
    missing = missing_data_stress_test()
    importance = permutation_feature_importance()
    geography = geographic_holdout_validation()

    cv.to_csv(OUTPUT_DIR / "repeated_cross_validation.csv", index=False)
    threshold.to_csv(OUTPUT_DIR / "threshold_sensitivity.csv", index=False)
    missing.to_csv(OUTPUT_DIR / "missing_data_stress.csv", index=False)
    importance.to_csv(OUTPUT_DIR / "permutation_importance.csv", index=False)
    geography.to_csv(OUTPUT_DIR / "geographic_holdout.csv", index=False)

    print("Repeated cross-validation")
    print(cv.describe().to_string())
    print("\nGeographic holdout")
    print(geography.to_string(index=False))
    print(f"\nWrote robustness outputs to {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
