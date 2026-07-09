from pathlib import Path
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATASET_ROOT = PROJECT_ROOT / "data" / "raw" / "alibaba-cloud-transport-system"

EXPECTED_FILES = [
    "performance_optical.csv",
    "ocm.csv",
    "performance_elec.csv",
]


def find_file(root: Path, filename: str) -> Path | None:
    matches = list(root.rglob(filename))
    if not matches:
        return None
    return matches[0]


def main() -> None:
    print("Project root:", PROJECT_ROOT)
    print("Dataset root:", DATASET_ROOT)
    print("-" * 80)

    if not DATASET_ROOT.exists():
        raise FileNotFoundError(
            f"Dataset folder not found: {DATASET_ROOT}\n"
            "Please clone the Alibaba repository into data/raw/alibaba-cloud-transport-system."
        )

    for filename in EXPECTED_FILES:
        path = find_file(DATASET_ROOT, filename)
        print(f"\nChecking: {filename}")

        if path is None:
            print("  STATUS: NOT FOUND")
            continue

        print("  STATUS: FOUND")
        print(f"  PATH: {path}")

        df = pd.read_csv(path)
        print(f"  SHAPE: {df.shape[0]} rows x {df.shape[1]} columns")
        print(f"  COLUMNS: {list(df.columns)}")
        print("  HEAD:")
        print(df.head(3))

    print("\nDataset check completed.")


if __name__ == "__main__":
    main()