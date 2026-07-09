from pathlib import Path
import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
DOCS_DIR = PROJECT_ROOT / "docs"


INPUT_FILES = {
    "pre_fec": PROCESSED_DIR / "pre_fec_ber_clean.csv",
    "och_power": PROCESSED_DIR / "och_power_clean.csv",
    "edfa_wide": PROCESSED_DIR / "edfa_telemetry_wide_clean.csv",
}


def read_processed_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Processed file not found: {path}")

    df = pd.read_csv(path)

    if "time" in df.columns:
        df["time"] = pd.to_datetime(df["time"], errors="coerce")

    return df


def to_number(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series, errors="coerce")


def safe_quantile(series: pd.Series, q: float) -> float:
    clean = pd.to_numeric(series, errors="coerce").dropna()
    if clean.empty:
        return float("nan")
    return float(clean.quantile(q))


def classify_high_is_bad(value: float, warn_threshold: float, critical_threshold: float) -> str:
    if pd.isna(value):
        return "Unknown"

    if not pd.isna(critical_threshold) and value >= critical_threshold:
        return "Critical"

    if not pd.isna(warn_threshold) and value >= warn_threshold:
        return "Warning"

    return "Normal"


def classify_low_is_bad(value: float, warn_threshold: float, critical_threshold: float) -> str:
    if pd.isna(value):
        return "Unknown"

    if not pd.isna(critical_threshold) and value <= critical_threshold:
        return "Critical"

    if not pd.isna(warn_threshold) and value <= warn_threshold:
        return "Warning"

    return "Normal"


def combine_status(statuses: list[str]) -> str:
    if "Critical" in statuses:
        return "Critical"
    if "Warning" in statuses:
        return "Warning"
    if all(status == "Unknown" for status in statuses):
        return "Unknown"
    return "Normal"


def percentile_score_high_is_bad(series: pd.Series) -> pd.Series:
    numeric = pd.to_numeric(series, errors="coerce")
    return numeric.rank(pct=True) * 100


def percentile_score_low_is_bad(series: pd.Series) -> pd.Series:
    numeric = pd.to_numeric(series, errors="coerce")
    return (1 - numeric.rank(pct=True)) * 100


def calculate_pre_fec_kpi(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    work = df.copy()

    work["pre_fec_ber"] = to_number(work["pre_fec_ber"])
    work["center_frequency"] = to_number(work["center_frequency"])
    work["stats_type"] = work["stats_type"].astype(str).str.strip().str.lower()

    # Ưu tiên avg và instant cho KPI xu hướng/chất lượng kênh.
    # max/min vẫn hữu ích nhưng sẽ dùng ở báo cáo mở rộng sau.
    base = work[work["stats_type"].isin(["avg", "instant"])].copy()

    group_cols = [
        "channel_key",
        "device_name",
        "logical_name",
        "pn",
        "side",
        "och",
        "och_group",
        "center_frequency",
    ]

    grouped = (
        base
        .groupby(group_cols, dropna=False)
        .agg(
            record_count=("pre_fec_ber", "count"),
            time_start=("time", "min"),
            time_end=("time", "max"),
            ber_mean=("pre_fec_ber", "mean"),
            ber_median=("pre_fec_ber", "median"),
            ber_p95=("pre_fec_ber", lambda s: s.quantile(0.95)),
            ber_max=("pre_fec_ber", "max"),
            ber_min=("pre_fec_ber", "min"),
        )
        .reset_index()
    )

    last_rows = (
        base
        .sort_values("time")
        .groupby("channel_key", dropna=False)
        .tail(1)[["channel_key", "pre_fec_ber"]]
        .rename(columns={"pre_fec_ber": "ber_last"})
    )

    grouped = grouped.merge(last_rows, on="channel_key", how="left")

    warn = safe_quantile(grouped["ber_p95"], 0.90)
    critical = safe_quantile(grouped["ber_p95"], 0.99)

    grouped["ber_status"] = grouped["ber_p95"].apply(
        lambda value: classify_high_is_bad(value, warn, critical)
    )

    grouped["ber_risk_score"] = percentile_score_high_is_bad(grouped["ber_p95"]).round(2)

    grouped["recommended_check"] = grouped["ber_status"].map(
        {
            "Normal": "No immediate action. Continue monitoring Pre-FEC BER.",
            "Warning": "Pre-FEC BER is above dataset P90. Check optical quality trend, OCH power and EDFA telemetry.",
            "Critical": "Pre-FEC BER is above dataset P99. Prioritize checking optical path quality, power level, OSNR-related degradation and transponder condition.",
            "Unknown": "Insufficient data for BER classification.",
        }
    )

    thresholds = {
        "pre_fec_ber_p90_threshold": warn,
        "pre_fec_ber_p99_threshold": critical,
        "input_rows": len(df),
        "kpi_rows": len(grouped),
        "base_rows_used": len(base),
    }

    return grouped.sort_values(["ber_status", "ber_risk_score"], ascending=[True, False]), thresholds


def calculate_och_power_kpi(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    work = df.copy()

    work["och_power"] = to_number(work["och_power"])
    work["center_frequency"] = to_number(work["center_frequency"])
    work["online_channel_num"] = to_number(work["online_channel_num"])

    group_cols = [
        "channel_key",
        "device_name",
        "logical_name",
        "online_channel_num",
        "center_frequency",
    ]

    grouped = (
        work
        .groupby(group_cols, dropna=False)
        .agg(
            record_count=("och_power", "count"),
            time_start=("time", "min"),
            time_end=("time", "max"),
            power_mean=("och_power", "mean"),
            power_median=("och_power", "median"),
            power_min=("och_power", "min"),
            power_max=("och_power", "max"),
            power_std=("och_power", "std"),
        )
        .reset_index()
    )

    grouped["power_range"] = grouped["power_max"] - grouped["power_min"]

    last_rows = (
        work
        .sort_values("time")
        .groupby("channel_key", dropna=False)
        .tail(1)[["channel_key", "och_power"]]
        .rename(columns={"och_power": "power_last"})
    )

    grouped = grouped.merge(last_rows, on="channel_key", how="left")

    drift_warn = safe_quantile(grouped["power_range"], 0.90)
    drift_critical = safe_quantile(grouped["power_range"], 0.99)

    low_power_warn = safe_quantile(grouped["power_min"], 0.10)
    low_power_critical = safe_quantile(grouped["power_min"], 0.01)

    grouped["power_drift_status"] = grouped["power_range"].apply(
        lambda value: classify_high_is_bad(value, drift_warn, drift_critical)
    )

    grouped["low_power_status"] = grouped["power_min"].apply(
        lambda value: classify_low_is_bad(value, low_power_warn, low_power_critical)
    )

    grouped["power_status"] = grouped.apply(
        lambda row: combine_status([row["power_drift_status"], row["low_power_status"]]),
        axis=1,
    )

    grouped["drift_risk_score"] = percentile_score_high_is_bad(grouped["power_range"])
    grouped["low_power_risk_score"] = percentile_score_low_is_bad(grouped["power_min"])

    grouped["power_risk_score"] = grouped[
        ["drift_risk_score", "low_power_risk_score"]
    ].max(axis=1).round(2)

    grouped["recommended_check"] = grouped["power_status"].map(
        {
            "Normal": "OCH power behavior is within the normal dataset distribution.",
            "Warning": "OCH power is outside normal distribution. Check channel equalization, amplifier tilt and wavelength-specific power drift.",
            "Critical": "OCH power is in the extreme dataset range. Prioritize checking optical channel power, EDFA behavior, connector/patching and channel path.",
            "Unknown": "Insufficient data for OCH power classification.",
        }
    )

    thresholds = {
        "power_range_p90_threshold": drift_warn,
        "power_range_p99_threshold": drift_critical,
        "power_min_p10_threshold": low_power_warn,
        "power_min_p01_threshold": low_power_critical,
        "input_rows": len(df),
        "kpi_rows": len(grouped),
    }

    return grouped.sort_values(["power_status", "power_risk_score"], ascending=[True, False]), thresholds


def flatten_columns(df: pd.DataFrame) -> pd.DataFrame:
    new_columns = []

    for col in df.columns:
        if isinstance(col, tuple):
            clean_parts = [str(part) for part in col if str(part) != ""]
            new_columns.append("_".join(clean_parts))
        else:
            new_columns.append(str(col))

    df.columns = new_columns
    return df


def calculate_edfa_kpi(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    work = df.copy()

    for col in work.columns:
        if col not in ["time", "device_name", "logical_name", "pn", "edfa_key"]:
            work[col] = to_number(work[col])

    group_cols = [
        "edfa_key",
        "device_name",
        "logical_name",
        "pn",
    ]

    candidate_cols = [
        "actual_gain",
        "actual_gain_tilt",
        "attenuation",
        "inputTPM_avg",
        "inputTPM_max",
        "inputTPM_min",
        "outputTPM_avg",
        "outputTPM_max",
        "outputTPM_min",
    ]

    numeric_cols = [col for col in candidate_cols if col in work.columns]

    agg_dict = {
        "time": ["min", "max"],
    }

    for col in numeric_cols:
        agg_dict[col] = ["mean", "min", "max", "std"]

    grouped = work.groupby(group_cols, dropna=False).agg(agg_dict).reset_index()
    grouped = flatten_columns(grouped)

    grouped = grouped.rename(
        columns={
            "time_min": "time_start",
            "time_max": "time_end",
        }
    )

    if "actual_gain_tilt_max" in grouped.columns and "actual_gain_tilt_min" in grouped.columns:
        grouped["gain_tilt_abs_max"] = grouped[["actual_gain_tilt_max", "actual_gain_tilt_min"]].abs().max(axis=1)
    elif "actual_gain_tilt_mean" in grouped.columns:
        grouped["gain_tilt_abs_max"] = grouped["actual_gain_tilt_mean"].abs()
    else:
        grouped["gain_tilt_abs_max"] = np.nan

    if "attenuation_mean" not in grouped.columns:
        grouped["attenuation_mean"] = np.nan

    tilt_warn = safe_quantile(grouped["gain_tilt_abs_max"], 0.90)
    tilt_critical = safe_quantile(grouped["gain_tilt_abs_max"], 0.99)

    attenuation_warn = safe_quantile(grouped["attenuation_mean"], 0.90)
    attenuation_critical = safe_quantile(grouped["attenuation_mean"], 0.99)

    grouped["gain_tilt_status"] = grouped["gain_tilt_abs_max"].apply(
        lambda value: classify_high_is_bad(value, tilt_warn, tilt_critical)
    )

    grouped["attenuation_status"] = grouped["attenuation_mean"].apply(
        lambda value: classify_high_is_bad(value, attenuation_warn, attenuation_critical)
    )

    grouped["edfa_status"] = grouped.apply(
        lambda row: combine_status([row["gain_tilt_status"], row["attenuation_status"]]),
        axis=1,
    )

    grouped["gain_tilt_risk_score"] = percentile_score_high_is_bad(grouped["gain_tilt_abs_max"])
    grouped["attenuation_risk_score"] = percentile_score_high_is_bad(grouped["attenuation_mean"])

    grouped["edfa_risk_score"] = grouped[
        ["gain_tilt_risk_score", "attenuation_risk_score"]
    ].max(axis=1).round(2)

    grouped["recommended_check"] = grouped["edfa_status"].map(
        {
            "Normal": "EDFA telemetry is within the normal dataset distribution.",
            "Warning": "EDFA tilt or attenuation is above dataset P90. Check amplifier gain profile and optical section behavior.",
            "Critical": "EDFA tilt or attenuation is above dataset P99. Prioritize checking amplifier configuration, attenuation and span condition.",
            "Unknown": "Insufficient data for EDFA classification.",
        }
    )

    thresholds = {
        "gain_tilt_abs_p90_threshold": tilt_warn,
        "gain_tilt_abs_p99_threshold": tilt_critical,
        "attenuation_p90_threshold": attenuation_warn,
        "attenuation_p99_threshold": attenuation_critical,
        "input_rows": len(df),
        "kpi_rows": len(grouped),
    }

    return grouped.sort_values(["edfa_status", "edfa_risk_score"], ascending=[True, False]), thresholds


def build_frequency_health_summary(
    pre_fec_kpi: pd.DataFrame,
    och_power_kpi: pd.DataFrame,
) -> pd.DataFrame:
    pre = pre_fec_kpi.copy()
    power = och_power_kpi.copy()

    pre_summary = (
        pre
        .groupby("center_frequency", dropna=False)
        .agg(
            ber_channel_count=("channel_key", "count"),
            ber_p95_mean=("ber_p95", "mean"),
            ber_p95_max=("ber_p95", "max"),
            ber_risk_score_max=("ber_risk_score", "max"),
            ber_critical_count=("ber_status", lambda s: (s == "Critical").sum()),
            ber_warning_count=("ber_status", lambda s: (s == "Warning").sum()),
        )
        .reset_index()
    )

    power_summary = (
        power
        .groupby("center_frequency", dropna=False)
        .agg(
            power_channel_count=("channel_key", "count"),
            power_mean=("power_mean", "mean"),
            power_min=("power_min", "min"),
            power_range_mean=("power_range", "mean"),
            power_risk_score_max=("power_risk_score", "max"),
            power_critical_count=("power_status", lambda s: (s == "Critical").sum()),
            power_warning_count=("power_status", lambda s: (s == "Warning").sum()),
        )
        .reset_index()
    )

    summary = pre_summary.merge(power_summary, on="center_frequency", how="outer")

    for col in [
        "ber_critical_count",
        "ber_warning_count",
        "power_critical_count",
        "power_warning_count",
    ]:
        summary[col] = summary[col].fillna(0).astype(int)

    def row_status(row: pd.Series) -> str:
        if row["ber_critical_count"] > 0 or row["power_critical_count"] > 0:
            return "Critical"
        if row["ber_warning_count"] > 0 or row["power_warning_count"] > 0:
            return "Warning"
        return "Normal"

    summary["frequency_status"] = summary.apply(row_status, axis=1)

    risk_cols = ["ber_risk_score_max", "power_risk_score_max"]
    summary["frequency_risk_score"] = summary[risk_cols].max(axis=1).round(2)

    summary["recommended_check"] = summary["frequency_status"].map(
        {
            "Normal": "Frequency-level BER and OCH power behavior are within normal dataset distribution.",
            "Warning": "Frequency has BER or power warning. Check corresponding transponder/channel and optical power behavior.",
            "Critical": "Frequency has critical BER or power behavior. Prioritize checking OCH, transponder, EDFA and optical path quality.",
        }
    )

    return summary.sort_values(["frequency_status", "frequency_risk_score"], ascending=[True, False])


def status_count_table(df: pd.DataFrame, column: str) -> str:
    if column not in df.columns:
        return "_Status column not found._"

    counts = df[column].value_counts(dropna=False)

    lines = [
        "| Status | Count |",
        "|---|---:|",
    ]

    for status, count in counts.items():
        lines.append(f"| `{status}` | {count:,} |")

    return "\n".join(lines)


def build_kpi_report(
    pre_fec_kpi: pd.DataFrame,
    pre_fec_thresholds: dict,
    och_power_kpi: pd.DataFrame,
    och_thresholds: dict,
    edfa_kpi: pd.DataFrame,
    edfa_thresholds: dict,
    frequency_summary: pd.DataFrame,
) -> str:
    lines = []

    lines.append("# Phase 4 KPI Report")
    lines.append("")
    lines.append("This report summarizes KPI calculation outputs generated from the cleaned Alibaba optical transport telemetry dataset.")
    lines.append("")
    lines.append("All health thresholds in this phase are data-driven percentile thresholds derived from the public dataset. No vendor-specific thresholds are assumed.")
    lines.append("")

    lines.append("## Output Files")
    lines.append("")
    lines.append("| Output File | Rows | Purpose |")
    lines.append("|---|---:|---|")
    lines.append(f"| `data/processed/pre_fec_ber_kpi.csv` | {len(pre_fec_kpi):,} | Pre-FEC BER KPI by channel |")
    lines.append(f"| `data/processed/och_power_kpi.csv` | {len(och_power_kpi):,} | OCH power KPI by channel |")
    lines.append(f"| `data/processed/edfa_kpi.csv` | {len(edfa_kpi):,} | EDFA KPI by amplifier/logical component |")
    lines.append(f"| `data/processed/frequency_health_summary.csv` | {len(frequency_summary):,} | Frequency-level health summary |")
    lines.append("")

    lines.append("## 1. Pre-FEC BER KPI")
    lines.append("")
    lines.append(f"- Clean input rows: **{pre_fec_thresholds['input_rows']:,}**")
    lines.append(f"- Rows used for KPI calculation: **{pre_fec_thresholds['base_rows_used']:,}**")
    lines.append(f"- KPI channel rows: **{pre_fec_thresholds['kpi_rows']:,}**")
    lines.append(f"- BER P90 threshold: `{pre_fec_thresholds['pre_fec_ber_p90_threshold']}`")
    lines.append(f"- BER P99 threshold: `{pre_fec_thresholds['pre_fec_ber_p99_threshold']}`")
    lines.append("")
    lines.append("### BER Status Distribution")
    lines.append("")
    lines.append(status_count_table(pre_fec_kpi, "ber_status"))
    lines.append("")

    lines.append("## 2. OCH Power KPI")
    lines.append("")
    lines.append(f"- Clean input rows: **{och_thresholds['input_rows']:,}**")
    lines.append(f"- KPI channel rows: **{och_thresholds['kpi_rows']:,}**")
    lines.append(f"- Power range P90 threshold: `{och_thresholds['power_range_p90_threshold']}`")
    lines.append(f"- Power range P99 threshold: `{och_thresholds['power_range_p99_threshold']}`")
    lines.append(f"- Low power P10 threshold: `{och_thresholds['power_min_p10_threshold']}`")
    lines.append(f"- Low power P01 threshold: `{och_thresholds['power_min_p01_threshold']}`")
    lines.append("")
    lines.append("### OCH Power Status Distribution")
    lines.append("")
    lines.append(status_count_table(och_power_kpi, "power_status"))
    lines.append("")

    lines.append("## 3. EDFA KPI")
    lines.append("")
    lines.append(f"- Clean input rows: **{edfa_thresholds['input_rows']:,}**")
    lines.append(f"- KPI EDFA rows: **{edfa_thresholds['kpi_rows']:,}**")
    lines.append(f"- Gain tilt absolute P90 threshold: `{edfa_thresholds['gain_tilt_abs_p90_threshold']}`")
    lines.append(f"- Gain tilt absolute P99 threshold: `{edfa_thresholds['gain_tilt_abs_p99_threshold']}`")
    lines.append(f"- Attenuation P90 threshold: `{edfa_thresholds['attenuation_p90_threshold']}`")
    lines.append(f"- Attenuation P99 threshold: `{edfa_thresholds['attenuation_p99_threshold']}`")
    lines.append("")
    lines.append("### EDFA Status Distribution")
    lines.append("")
    lines.append(status_count_table(edfa_kpi, "edfa_status"))
    lines.append("")

    lines.append("## 4. Frequency Health Summary")
    lines.append("")
    lines.append(f"- Frequency rows: **{len(frequency_summary):,}**")
    lines.append("")
    lines.append("### Frequency Status Distribution")
    lines.append("")
    lines.append(status_count_table(frequency_summary, "frequency_status"))
    lines.append("")

    lines.append("## G.709/OTN Interpretation")
    lines.append("")
    lines.append("Pre-FEC BER is relevant to OTN/DWDM transport monitoring because it reflects bit error behavior before FEC correction. In this project, high Pre-FEC BER is interpreted as a transport-channel degradation indicator, not as a direct extraction of raw G.709 overhead.")
    lines.append("")
    lines.append("OCH power and EDFA telemetry provide optical-layer context that helps explain BER degradation. This supports a G.709-aware troubleshooting workflow: correlate transponder-side Pre-FEC BER with optical channel power and amplifier behavior.")
    lines.append("")
    lines.append("## Limitation")
    lines.append("")
    lines.append("The KPI outputs are calculated from public telemetry data. They do not represent vendor-specific alarm thresholds or private operator NMS logic.")
    lines.append("")

    return "\n".join(lines)


def main() -> None:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    DOCS_DIR.mkdir(parents=True, exist_ok=True)

    print("Project root:", PROJECT_ROOT)
    print("Processed dir:", PROCESSED_DIR)
    print("-" * 80)

    print("Reading cleaned data...")
    pre_fec = read_processed_csv(INPUT_FILES["pre_fec"])
    och_power = read_processed_csv(INPUT_FILES["och_power"])
    edfa_wide = read_processed_csv(INPUT_FILES["edfa_wide"])

    print("Calculating Pre-FEC BER KPI...")
    pre_fec_kpi, pre_fec_thresholds = calculate_pre_fec_kpi(pre_fec)
    pre_fec_kpi_path = PROCESSED_DIR / "pre_fec_ber_kpi.csv"
    pre_fec_kpi.to_csv(pre_fec_kpi_path, index=False, encoding="utf-8-sig")
    print(f"  Saved: {pre_fec_kpi_path} ({len(pre_fec_kpi):,} rows)")

    print("Calculating OCH power KPI...")
    och_power_kpi, och_thresholds = calculate_och_power_kpi(och_power)
    och_power_kpi_path = PROCESSED_DIR / "och_power_kpi.csv"
    och_power_kpi.to_csv(och_power_kpi_path, index=False, encoding="utf-8-sig")
    print(f"  Saved: {och_power_kpi_path} ({len(och_power_kpi):,} rows)")

    print("Calculating EDFA KPI...")
    edfa_kpi, edfa_thresholds = calculate_edfa_kpi(edfa_wide)
    edfa_kpi_path = PROCESSED_DIR / "edfa_kpi.csv"
    edfa_kpi.to_csv(edfa_kpi_path, index=False, encoding="utf-8-sig")
    print(f"  Saved: {edfa_kpi_path} ({len(edfa_kpi):,} rows)")

    print("Building frequency health summary...")
    frequency_summary = build_frequency_health_summary(pre_fec_kpi, och_power_kpi)
    frequency_summary_path = PROCESSED_DIR / "frequency_health_summary.csv"
    frequency_summary.to_csv(frequency_summary_path, index=False, encoding="utf-8-sig")
    print(f"  Saved: {frequency_summary_path} ({len(frequency_summary):,} rows)")

    report = build_kpi_report(
        pre_fec_kpi=pre_fec_kpi,
        pre_fec_thresholds=pre_fec_thresholds,
        och_power_kpi=och_power_kpi,
        och_thresholds=och_thresholds,
        edfa_kpi=edfa_kpi,
        edfa_thresholds=edfa_thresholds,
        frequency_summary=frequency_summary,
    )

    report_path = DOCS_DIR / "phase4_kpi_report.md"
    report_path.write_text(report, encoding="utf-8")
    print(f"Generated report: {report_path}")

    print("-" * 80)
    print("Phase 4 KPI calculation completed.")


if __name__ == "__main__":
    main()