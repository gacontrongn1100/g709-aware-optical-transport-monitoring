from pathlib import Path
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATASET_ROOT = PROJECT_ROOT / "data" / "raw" / "alibaba-cloud-transport-system"
DATA_DIR = DATASET_ROOT / "data"

DOCS_DIR = PROJECT_ROOT / "docs"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

FILES = {
    "performance_optical": "performance_optical.csv",
    "ocm": "ocm.csv",
    "performance_elec": "performance_elec.csv",
}


def read_csv_file(filename: str) -> pd.DataFrame:
    path = DATA_DIR / filename
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    df = pd.read_csv(path)

    if "time" in df.columns:
        df["time"] = pd.to_datetime(df["time"], errors="coerce")

    return df


def markdown_table_from_series(series: pd.Series, max_rows: int = 50) -> str:
    if series.empty:
        return "_No data_\n"

    rows = []
    for index, value in series.head(max_rows).items():
        rows.append(f"| `{index}` | {value} |")

    table = "| Value | Count |\n|---|---:|\n" + "\n".join(rows) + "\n"

    if len(series) > max_rows:
        table += f"\n_Showing first {max_rows} of {len(series)} values._\n"

    return table


def profile_dataframe(name: str, df: pd.DataFrame) -> str:
    lines = []

    lines.append(f"# Data Profile: `{name}`")
    lines.append("")
    lines.append("## Basic Information")
    lines.append("")
    lines.append(f"- Rows: **{df.shape[0]:,}**")
    lines.append(f"- Columns: **{df.shape[1]:,}**")
    lines.append("")

    lines.append("## Columns")
    lines.append("")
    lines.append("| Column | Dtype | Missing Count | Missing Rate | Unique Count |")
    lines.append("|---|---|---:|---:|---:|")

    for col in df.columns:
        missing_count = int(df[col].isna().sum())
        missing_rate = missing_count / len(df) if len(df) else 0
        unique_count = int(df[col].nunique(dropna=True))
        dtype = str(df[col].dtype)
        lines.append(
            f"| `{col}` | `{dtype}` | {missing_count:,} | {missing_rate:.2%} | {unique_count:,} |"
        )

    lines.append("")

    if "time" in df.columns:
        lines.append("## Time Range")
        lines.append("")
        lines.append(f"- Min time: `{df['time'].min()}`")
        lines.append(f"- Max time: `{df['time'].max()}`")
        lines.append(f"- Invalid time rows: `{df['time'].isna().sum():,}`")
        lines.append("")

    lines.append("## Key Categorical Values")
    lines.append("")

    categorical_candidates = [
        "device_name",
        "logical_name",
        "item",
        "stats_type",
        "pn",
        "side",
        "och",
        "och_group",
        "online_channel_num",
        "center_frequency",
    ]

    for col in categorical_candidates:
        if col in df.columns:
            lines.append(f"### `{col}`")
            lines.append("")
            counts = df[col].value_counts(dropna=False)
            lines.append(markdown_table_from_series(counts, max_rows=30))
            lines.append("")

    numeric_cols = df.select_dtypes(include="number").columns.tolist()

    if numeric_cols:
        lines.append("## Numeric Summary")
        lines.append("")
        desc = df[numeric_cols].describe().T
        lines.append(desc.to_markdown())
        lines.append("")

    lines.append("## Sample Rows")
    lines.append("")
    lines.append(df.head(10).to_markdown(index=False))
    lines.append("")

    return "\n".join(lines)


def build_data_dictionary() -> str:
    return """# Data Dictionary

This document is generated in Phase 2 based on the actual columns found in the public Alibaba Cloud Transport System Dataset.

The project uses three primary CSV files:

1. `performance_optical.csv`
2. `ocm.csv`
3. `performance_elec.csv`

---

## 1. `performance_optical.csv`

Observed shape from Phase 1:

- Rows: 154,935
- Columns: 10

Observed columns:

| Column | Initial Meaning in This Project |
|---|---|
| `device_name` | Optical device identifier |
| `logical_name` | Logical component or interface name |
| `item` | Measured optical performance item, for example input/output optical power |
| `stats_type` | Statistical type of the measurement, for example avg/min/max if present |
| `value` | Measurement value |
| `actual_gain` | Actual EDFA gain |
| `actual_gain_tilt` | EDFA gain tilt |
| `pn` | Equipment/card/module identifier |
| `attenuation` | Attenuation value |
| `time` | Timestamp of the measurement |

Planned use:

- EDFA input/output power analysis
- Gain and gain tilt analysis
- Attenuation analysis
- Optical section health interpretation

---

## 2. `ocm.csv`

Observed shape from Phase 1:

- Rows: 267,508
- Columns: 6

Observed columns:

| Column | Initial Meaning in This Project |
|---|---|
| `device_name` | Optical device identifier |
| `logical_name` | Logical OCM component/interface name |
| `online_channel_num` | Online optical channel number |
| `center_frequency` | Optical channel center frequency |
| `power` | Optical channel power |
| `time` | Timestamp of the measurement |

Planned use:

- OCH power monitoring
- Channel power distribution
- Power drift analysis
- Channel flatness analysis

---

## 3. `performance_elec.csv`

Observed shape from Phase 1:

- Rows: 29,276
- Columns: 11

Observed columns:

| Column | Initial Meaning in This Project |
|---|---|
| `device_name` | Transponder or terminal device identifier |
| `logical_name` | Logical transponder/client/line interface name |
| `item` | Electrical/transponder-side performance item |
| `stats_type` | Statistical type of the measurement |
| `value` | Measurement value, used for Pre-FEC BER when `item = preFecBer` |
| `och` | Optical channel identifier |
| `center_frequency` | Optical channel center frequency |
| `och_group` | Optical channel group |
| `time` | Timestamp of the measurement |
| `side` | Direction or side of the optical channel, for example A/Z |
| `pn` | Equipment/card/module identifier |

Planned use:

- Pre-FEC BER analysis
- A/Z side comparison
- Transponder-side channel health monitoring
- G.709/OTN-aware FEC degradation interpretation

---

## Important Note

This data dictionary documents observed dataset columns. It does not claim that the dataset contains full raw G.709 OPU/ODU/OTU overhead fields or real NMS alarms such as TIM, BDI, PLM or TCM defects.
"""


def build_findings_report(dfs: dict[str, pd.DataFrame]) -> str:
    perf_optical = dfs["performance_optical"]
    ocm = dfs["ocm"]
    perf_elec = dfs["performance_elec"]

    lines = []

    lines.append("# Phase 2 Findings")
    lines.append("")
    lines.append("## Confirmed Dataset Files")
    lines.append("")
    lines.append("| File | Rows | Columns | Main Use |")
    lines.append("|---|---:|---:|---|")
    lines.append(f"| `performance_optical.csv` | {perf_optical.shape[0]:,} | {perf_optical.shape[1]} | EDFA / optical performance |")
    lines.append(f"| `ocm.csv` | {ocm.shape[0]:,} | {ocm.shape[1]} | Optical channel power |")
    lines.append(f"| `performance_elec.csv` | {perf_elec.shape[0]:,} | {perf_elec.shape[1]} | Pre-FEC BER / transponder performance |")
    lines.append("")

    lines.append("## Key Observations")
    lines.append("")
    lines.append("1. The dataset provides real public optical transport telemetry suitable for DWDM/OTN monitoring analysis.")
    lines.append("2. `performance_elec.csv` contains the `item` field and the observed sample from Phase 1 shows `preFecBer`, which is directly relevant to FEC-related channel quality monitoring.")
    lines.append("3. `ocm.csv` contains optical channel power and center frequency, useful for OCH power monitoring.")
    lines.append("4. `performance_optical.csv` contains EDFA-related fields such as gain, gain tilt and attenuation.")
    lines.append("5. The dataset does not expose raw G.709 OPU/ODU/OTU overhead bytes, so G.709 is used as an interpretation framework, not as raw decoded overhead data.")
    lines.append("")

    lines.append("## Next Phase")
    lines.append("")
    lines.append("Phase 3 will clean and standardize the three datasets:")
    lines.append("")
    lines.append("- Parse and validate timestamps.")
    lines.append("- Filter Pre-FEC BER records from `performance_elec.csv`.")
    lines.append("- Prepare OCH power records from `ocm.csv`.")
    lines.append("- Prepare EDFA telemetry records from `performance_optical.csv`.")
    lines.append("- Export clean processed CSV files for KPI calculation.")
    lines.append("")

    return "\n".join(lines)


def main() -> None:
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    print("Project root:", PROJECT_ROOT)
    print("Dataset root:", DATASET_ROOT)
    print("Data dir:", DATA_DIR)
    print("-" * 80)

    dfs: dict[str, pd.DataFrame] = {}

    for name, filename in FILES.items():
        print(f"Reading {filename}...")
        df = read_csv_file(filename)
        dfs[name] = df

        sample_path = PROCESSED_DIR / f"sample_{name}.csv"
        df.head(20).to_csv(sample_path, index=False, encoding="utf-8-sig")
        print(f"  Saved sample: {sample_path}")

    profile_parts = []
    for name, df in dfs.items():
        print(f"Profiling {name}...")
        profile_parts.append(profile_dataframe(name, df))
        profile_parts.append("\n---\n")

    data_profile_path = DOCS_DIR / "phase2_data_profile.md"
    data_profile_path.write_text("\n".join(profile_parts), encoding="utf-8")

    data_dictionary_path = DOCS_DIR / "data_dictionary.md"
    data_dictionary_path.write_text(build_data_dictionary(), encoding="utf-8")

    findings_path = DOCS_DIR / "phase2_findings.md"
    findings_path.write_text(build_findings_report(dfs), encoding="utf-8")

    print("-" * 80)
    print("Phase 2 exploration completed.")
    print(f"Generated: {data_profile_path}")
    print(f"Generated: {data_dictionary_path}")
    print(f"Generated: {findings_path}")


if __name__ == "__main__":
    main()