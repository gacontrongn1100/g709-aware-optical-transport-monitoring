from pathlib import Path
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data" / "raw" / "alibaba-cloud-transport-system" / "data"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
DOCS_DIR = PROJECT_ROOT / "docs"


RAW_FILES = {
    "performance_optical": DATA_DIR / "performance_optical.csv",
    "ocm": DATA_DIR / "ocm.csv",
    "performance_elec": DATA_DIR / "performance_elec.csv",
}


def read_raw_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Raw file not found: {path}")

    df = pd.read_csv(path)

    if "time" in df.columns:
        df["time"] = pd.to_datetime(df["time"], errors="coerce")

    return df


def clean_text(series: pd.Series) -> pd.Series:
    return series.astype(str).str.strip()


def to_number(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series, errors="coerce")


def make_key(df: pd.DataFrame, columns: list[str]) -> pd.Series:
    parts = []
    for col in columns:
        if col in df.columns:
            parts.append(df[col].astype(str).fillna("NA"))
    if not parts:
        return pd.Series(["NA"] * len(df), index=df.index)
    return parts[0].str.cat(parts[1:], sep="|")


def value_counts_markdown(series: pd.Series, max_rows: int = 30) -> str:
    counts = series.value_counts(dropna=False).head(max_rows)

    lines = [
        "| Value | Count |",
        "|---|---:|",
    ]

    for value, count in counts.items():
        lines.append(f"| `{value}` | {count:,} |")

    return "\n".join(lines)


def clean_pre_fec_ber(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    raw_rows = len(df)

    work = df.copy()

    work["item_clean"] = clean_text(work["item"])
    work["stats_type"] = clean_text(work["stats_type"])
    work["device_name"] = clean_text(work["device_name"])
    work["logical_name"] = clean_text(work["logical_name"])
    work["side"] = clean_text(work["side"]).str.upper()
    work["pn"] = clean_text(work["pn"])

    pre = work[work["item_clean"].str.lower() == "prefecber"].copy()

    pre["pre_fec_ber"] = to_number(pre["value"])
    pre["center_frequency"] = to_number(pre["center_frequency"])
    pre["och_group"] = to_number(pre["och_group"])

    before_drop = len(pre)

    pre = pre.dropna(subset=["time", "pre_fec_ber"]).copy()

    pre["channel_key"] = make_key(
        pre,
        [
            "device_name",
            "logical_name",
            "och",
            "och_group",
            "center_frequency",
            "side",
            "pn",
        ],
    )

    output_columns = [
        "time",
        "device_name",
        "logical_name",
        "pn",
        "side",
        "och",
        "och_group",
        "center_frequency",
        "stats_type",
        "pre_fec_ber",
        "channel_key",
    ]

    pre = pre[output_columns].sort_values(["time", "device_name", "logical_name"])

    report = {
        "raw_rows": raw_rows,
        "prefec_rows_before_drop": before_drop,
        "clean_rows": len(pre),
        "dropped_rows": before_drop - len(pre),
        "invalid_time_rows": int(work["time"].isna().sum()),
        "missing_prefec_value_rows": int(pd.to_numeric(work["value"], errors="coerce").isna().sum()),
        "item_counts": value_counts_markdown(work["item_clean"]),
        "stats_type_counts": value_counts_markdown(work["stats_type"]),
        "side_counts": value_counts_markdown(work["side"]),
    }

    return pre, report


def clean_ocm_power(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    raw_rows = len(df)

    work = df.copy()

    work["device_name"] = clean_text(work["device_name"])
    work["logical_name"] = clean_text(work["logical_name"])
    work["online_channel_num"] = to_number(work["online_channel_num"])
    work["center_frequency"] = to_number(work["center_frequency"])
    work["och_power"] = to_number(work["power"])

    before_drop = len(work)

    work = work.dropna(subset=["time", "center_frequency", "och_power"]).copy()

    work["channel_key"] = make_key(
        work,
        [
            "device_name",
            "logical_name",
            "online_channel_num",
            "center_frequency",
        ],
    )

    output_columns = [
        "time",
        "device_name",
        "logical_name",
        "online_channel_num",
        "center_frequency",
        "och_power",
        "channel_key",
    ]

    work = work[output_columns].sort_values(["time", "device_name", "logical_name", "center_frequency"])

    report = {
        "raw_rows": raw_rows,
        "clean_rows": len(work),
        "dropped_rows": before_drop - len(work),
        "invalid_time_rows": int(df["time"].isna().sum()),
        "missing_power_rows": int(to_number(df["power"]).isna().sum()),
        "device_counts": value_counts_markdown(work["device_name"]),
        "logical_name_counts": value_counts_markdown(work["logical_name"]),
    }

    return work, report


def clean_edfa_telemetry(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    raw_rows = len(df)

    work = df.copy()

    work["device_name"] = clean_text(work["device_name"])
    work["logical_name"] = clean_text(work["logical_name"])
    work["item"] = clean_text(work["item"])
    work["stats_type"] = clean_text(work["stats_type"])
    work["pn"] = clean_text(work["pn"])

    work["value"] = to_number(work["value"])
    work["actual_gain"] = to_number(work["actual_gain"])
    work["actual_gain_tilt"] = to_number(work["actual_gain_tilt"])
    work["attenuation"] = to_number(work["attenuation"])

    before_drop = len(work)

    long_df = work.dropna(subset=["time", "item", "stats_type", "value"]).copy()

    long_df["edfa_key"] = make_key(
        long_df,
        [
            "device_name",
            "logical_name",
            "pn",
        ],
    )

    long_columns = [
        "time",
        "device_name",
        "logical_name",
        "pn",
        "item",
        "stats_type",
        "value",
        "actual_gain",
        "actual_gain_tilt",
        "attenuation",
        "edfa_key",
    ]

    long_df = long_df[long_columns].sort_values(["time", "device_name", "logical_name", "item", "stats_type"])

    wide_source = long_df.copy()
    wide_source["metric"] = wide_source["item"] + "_" + wide_source["stats_type"]

    index_columns = [
        "time",
        "device_name",
        "logical_name",
        "pn",
        "actual_gain",
        "actual_gain_tilt",
        "attenuation",
        "edfa_key",
    ]

    wide_df = (
        wide_source
        .pivot_table(
            index=index_columns,
            columns="metric",
            values="value",
            aggfunc="mean",
        )
        .reset_index()
    )

    wide_df.columns.name = None
    wide_df = wide_df.sort_values(["time", "device_name", "logical_name"])

    report = {
        "raw_rows": raw_rows,
        "long_clean_rows": len(long_df),
        "wide_clean_rows": len(wide_df),
        "dropped_rows": before_drop - len(long_df),
        "invalid_time_rows": int(df["time"].isna().sum()),
        "missing_value_rows": int(to_number(df["value"]).isna().sum()),
        "item_counts": value_counts_markdown(work["item"]),
        "stats_type_counts": value_counts_markdown(work["stats_type"]),
        "pn_counts": value_counts_markdown(work["pn"]),
    }

    return long_df, wide_df, report


def build_cleaning_report(
    pre_fec_report: dict,
    ocm_report: dict,
    edfa_report: dict,
    pre_fec_df: pd.DataFrame,
    ocm_df: pd.DataFrame,
    edfa_long_df: pd.DataFrame,
    edfa_wide_df: pd.DataFrame,
) -> str:
    lines = []

    lines.append("# Phase 3 Cleaning Report")
    lines.append("")
    lines.append("This report summarizes the cleaning and standardization outputs generated from the public Alibaba Cloud Transport System Dataset.")
    lines.append("")
    lines.append("## Output Files")
    lines.append("")
    lines.append("| Output File | Rows | Purpose |")
    lines.append("|---|---:|---|")
    lines.append(f"| `data/processed/pre_fec_ber_clean.csv` | {len(pre_fec_df):,} | Clean Pre-FEC BER records |")
    lines.append(f"| `data/processed/och_power_clean.csv` | {len(ocm_df):,} | Clean OCH power records |")
    lines.append(f"| `data/processed/edfa_telemetry_long_clean.csv` | {len(edfa_long_df):,} | Clean EDFA telemetry in long format |")
    lines.append(f"| `data/processed/edfa_telemetry_wide_clean.csv` | {len(edfa_wide_df):,} | Clean EDFA telemetry in wide format |")
    lines.append("")

    lines.append("## 1. Pre-FEC BER Cleaning")
    lines.append("")
    lines.append(f"- Raw rows in `performance_elec.csv`: **{pre_fec_report['raw_rows']:,}**")
    lines.append(f"- Rows with `item = preFecBer` before dropping invalid values: **{pre_fec_report['prefec_rows_before_drop']:,}**")
    lines.append(f"- Clean Pre-FEC BER rows: **{pre_fec_report['clean_rows']:,}**")
    lines.append(f"- Dropped rows after filtering invalid time/value: **{pre_fec_report['dropped_rows']:,}**")
    lines.append(f"- Invalid timestamp rows in raw file: **{pre_fec_report['invalid_time_rows']:,}**")
    lines.append("")
    lines.append("### `item` distribution")
    lines.append("")
    lines.append(pre_fec_report["item_counts"])
    lines.append("")
    lines.append("### `stats_type` distribution")
    lines.append("")
    lines.append(pre_fec_report["stats_type_counts"])
    lines.append("")
    lines.append("### `side` distribution")
    lines.append("")
    lines.append(pre_fec_report["side_counts"])
    lines.append("")

    lines.append("## 2. OCH Power Cleaning")
    lines.append("")
    lines.append(f"- Raw rows in `ocm.csv`: **{ocm_report['raw_rows']:,}**")
    lines.append(f"- Clean OCH power rows: **{ocm_report['clean_rows']:,}**")
    lines.append(f"- Dropped rows after filtering invalid time/frequency/power: **{ocm_report['dropped_rows']:,}**")
    lines.append(f"- Invalid timestamp rows in raw file: **{ocm_report['invalid_time_rows']:,}**")
    lines.append(f"- Missing power rows in raw file: **{ocm_report['missing_power_rows']:,}**")
    lines.append("")
    lines.append("### Top `device_name` values")
    lines.append("")
    lines.append(ocm_report["device_counts"])
    lines.append("")
    lines.append("### Top `logical_name` values")
    lines.append("")
    lines.append(ocm_report["logical_name_counts"])
    lines.append("")

    lines.append("## 3. EDFA Telemetry Cleaning")
    lines.append("")
    lines.append(f"- Raw rows in `performance_optical.csv`: **{edfa_report['raw_rows']:,}**")
    lines.append(f"- Clean long-format EDFA rows: **{edfa_report['long_clean_rows']:,}**")
    lines.append(f"- Clean wide-format EDFA rows: **{edfa_report['wide_clean_rows']:,}**")
    lines.append(f"- Dropped rows after filtering invalid time/item/stats/value: **{edfa_report['dropped_rows']:,}**")
    lines.append(f"- Invalid timestamp rows in raw file: **{edfa_report['invalid_time_rows']:,}**")
    lines.append(f"- Missing measurement value rows in raw file: **{edfa_report['missing_value_rows']:,}**")
    lines.append("")
    lines.append("### `item` distribution")
    lines.append("")
    lines.append(edfa_report["item_counts"])
    lines.append("")
    lines.append("### `stats_type` distribution")
    lines.append("")
    lines.append(edfa_report["stats_type_counts"])
    lines.append("")
    lines.append("### `pn` distribution")
    lines.append("")
    lines.append(edfa_report["pn_counts"])
    lines.append("")

    lines.append("## Technical Note")
    lines.append("")
    lines.append("The cleaned datasets are derived directly from the public Alibaba dataset. No private operator data is used, and no synthetic optical telemetry is fabricated.")
    lines.append("")
    lines.append("The cleaned data will be used in Phase 4 for KPI calculation, including Pre-FEC BER behavior, OCH power distribution, EDFA gain/tilt/attenuation analysis and G.709-aware transport health interpretation.")
    lines.append("")

    return "\n".join(lines)


def main() -> None:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    DOCS_DIR.mkdir(parents=True, exist_ok=True)

    print("Project root:", PROJECT_ROOT)
    print("Data dir:", DATA_DIR)
    print("Processed dir:", PROCESSED_DIR)
    print("-" * 80)

    print("Reading raw files...")
    performance_optical = read_raw_csv(RAW_FILES["performance_optical"])
    ocm = read_raw_csv(RAW_FILES["ocm"])
    performance_elec = read_raw_csv(RAW_FILES["performance_elec"])

    print("Cleaning Pre-FEC BER...")
    pre_fec_df, pre_fec_report = clean_pre_fec_ber(performance_elec)
    pre_fec_path = PROCESSED_DIR / "pre_fec_ber_clean.csv"
    pre_fec_df.to_csv(pre_fec_path, index=False, encoding="utf-8-sig")
    print(f"  Saved: {pre_fec_path} ({len(pre_fec_df):,} rows)")

    print("Cleaning OCH power...")
    ocm_df, ocm_report = clean_ocm_power(ocm)
    ocm_path = PROCESSED_DIR / "och_power_clean.csv"
    ocm_df.to_csv(ocm_path, index=False, encoding="utf-8-sig")
    print(f"  Saved: {ocm_path} ({len(ocm_df):,} rows)")

    print("Cleaning EDFA telemetry...")
    edfa_long_df, edfa_wide_df, edfa_report = clean_edfa_telemetry(performance_optical)

    edfa_long_path = PROCESSED_DIR / "edfa_telemetry_long_clean.csv"
    edfa_wide_path = PROCESSED_DIR / "edfa_telemetry_wide_clean.csv"

    edfa_long_df.to_csv(edfa_long_path, index=False, encoding="utf-8-sig")
    edfa_wide_df.to_csv(edfa_wide_path, index=False, encoding="utf-8-sig")

    print(f"  Saved: {edfa_long_path} ({len(edfa_long_df):,} rows)")
    print(f"  Saved: {edfa_wide_path} ({len(edfa_wide_df):,} rows)")

    report = build_cleaning_report(
        pre_fec_report=pre_fec_report,
        ocm_report=ocm_report,
        edfa_report=edfa_report,
        pre_fec_df=pre_fec_df,
        ocm_df=ocm_df,
        edfa_long_df=edfa_long_df,
        edfa_wide_df=edfa_wide_df,
    )

    report_path = DOCS_DIR / "phase3_cleaning_report.md"
    report_path.write_text(report, encoding="utf-8")

    print("-" * 80)
    print("Phase 3 cleaning completed.")
    print(f"Generated report: {report_path}")


if __name__ == "__main__":
    main()