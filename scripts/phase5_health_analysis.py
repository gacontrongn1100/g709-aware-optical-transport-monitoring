from pathlib import Path
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
DOCS_DIR = PROJECT_ROOT / "docs"


INPUT_FILES = {
    "pre_fec_kpi": PROCESSED_DIR / "pre_fec_ber_kpi.csv",
    "och_power_kpi": PROCESSED_DIR / "och_power_kpi.csv",
    "edfa_kpi": PROCESSED_DIR / "edfa_kpi.csv",
    "frequency_summary": PROCESSED_DIR / "frequency_health_summary.csv",
}


STATUS_RANK = {
    "Unknown": 0,
    "Normal": 1,
    "Warning": 2,
    "Critical": 3,
}


PRIORITY_MAP = {
    "Critical": "P1",
    "Warning": "P2",
    "Normal": "P3",
    "Unknown": "P4",
}


def read_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Required file not found: {path}")

    df = pd.read_csv(path)

    if "time_start" in df.columns:
        df["time_start"] = pd.to_datetime(df["time_start"], errors="coerce")

    if "time_end" in df.columns:
        df["time_end"] = pd.to_datetime(df["time_end"], errors="coerce")

    # Normalize identifier columns before merge/groupby.
    # These columns are IDs, not numerical values.
    identifier_columns = [
        "device_name",
        "logical_name",
        "pn",
        "side",
        "och",
        "channel_key",
        "edfa_key",
    ]

    for col in identifier_columns:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()

    return df


def normalize_status(value: object) -> str:
    if pd.isna(value):
        return "Unknown"

    value = str(value).strip()

    if value not in STATUS_RANK:
        return "Unknown"

    return value


def worst_status(values: list[object]) -> str:
    statuses = [normalize_status(value) for value in values]
    return max(statuses, key=lambda status: STATUS_RANK.get(status, 0))


def status_counts(df: pd.DataFrame, column: str) -> str:
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


def priority_counts(df: pd.DataFrame, column: str = "priority") -> str:
    if column not in df.columns:
        return "_Priority column not found._"

    counts = df[column].value_counts(dropna=False)

    lines = [
        "| Priority | Count |",
        "|---|---:|",
    ]

    for priority, count in counts.items():
        lines.append(f"| `{priority}` | {count:,} |")

    return "\n".join(lines)


def build_device_health_summary(
    och_power_kpi: pd.DataFrame,
    edfa_kpi: pd.DataFrame,
) -> pd.DataFrame:
    power = och_power_kpi.copy()
    edfa = edfa_kpi.copy()

    power["power_status"] = power["power_status"].apply(normalize_status)
    edfa["edfa_status"] = edfa["edfa_status"].apply(normalize_status)

    power_device = (
        power
        .groupby("device_name", dropna=False)
        .agg(
            och_channel_count=("channel_key", "count"),
            power_risk_score_max=("power_risk_score", "max"),
            power_critical_count=("power_status", lambda s: (s == "Critical").sum()),
            power_warning_count=("power_status", lambda s: (s == "Warning").sum()),
            power_normal_count=("power_status", lambda s: (s == "Normal").sum()),
        )
        .reset_index()
    )

    def power_device_status(row: pd.Series) -> str:
        if row["power_critical_count"] > 0:
            return "Critical"
        if row["power_warning_count"] > 0:
            return "Warning"
        return "Normal"

    power_device["power_device_status"] = power_device.apply(power_device_status, axis=1)

    edfa_device = (
        edfa
        .groupby("device_name", dropna=False)
        .agg(
            edfa_count=("edfa_key", "count"),
            edfa_risk_score_max=("edfa_risk_score", "max"),
            edfa_critical_count=("edfa_status", lambda s: (s == "Critical").sum()),
            edfa_warning_count=("edfa_status", lambda s: (s == "Warning").sum()),
            edfa_normal_count=("edfa_status", lambda s: (s == "Normal").sum()),
        )
        .reset_index()
    )

    def edfa_device_status(row: pd.Series) -> str:
        if row["edfa_critical_count"] > 0:
            return "Critical"
        if row["edfa_warning_count"] > 0:
            return "Warning"
        return "Normal"

    edfa_device["edfa_device_status"] = edfa_device.apply(edfa_device_status, axis=1)

    summary = power_device.merge(edfa_device, on="device_name", how="outer")

    for col in [
        "och_channel_count",
        "power_critical_count",
        "power_warning_count",
        "power_normal_count",
        "edfa_count",
        "edfa_critical_count",
        "edfa_warning_count",
        "edfa_normal_count",
    ]:
        if col in summary.columns:
            summary[col] = summary[col].fillna(0).astype(int)

    for col in ["power_risk_score_max", "edfa_risk_score_max"]:
        if col in summary.columns:
            summary[col] = pd.to_numeric(summary[col], errors="coerce").fillna(0)

    summary["power_device_status"] = summary["power_device_status"].fillna("Unknown")
    summary["edfa_device_status"] = summary["edfa_device_status"].fillna("Unknown")

    summary["device_status"] = summary.apply(
        lambda row: worst_status([row["power_device_status"], row["edfa_device_status"]]),
        axis=1,
    )

    summary["device_risk_score"] = summary[
        ["power_risk_score_max", "edfa_risk_score_max"]
    ].max(axis=1).round(2)

    summary["priority"] = summary["device_status"].map(PRIORITY_MAP)

    summary["recommended_check"] = summary.apply(build_device_recommendation, axis=1)

    return summary.sort_values(
        ["device_status", "device_risk_score"],
        ascending=[True, False],
    )


def build_device_recommendation(row: pd.Series) -> str:
    power_status = normalize_status(row.get("power_device_status"))
    edfa_status = normalize_status(row.get("edfa_device_status"))

    if power_status == "Critical" and edfa_status == "Critical":
        return "Critical OCH power and EDFA behavior detected. Prioritize checking amplifier gain/tilt, attenuation, optical channel power and physical optical path."

    if power_status == "Critical":
        return "Critical OCH power behavior detected. Check OCH power level, channel equalization, patching, connector condition and optical path."

    if edfa_status == "Critical":
        return "Critical EDFA behavior detected. Check amplifier gain profile, gain tilt, VOA/attenuation and span condition."

    if power_status == "Warning" or edfa_status == "Warning":
        return "Warning-level optical behavior detected. Trend monitoring is recommended before service-impacting degradation."

    if power_status == "Unknown" and edfa_status == "Unknown":
        return "Insufficient device-level data for recommendation."

    return "Device-level optical telemetry is within the normal dataset distribution."


def build_frequency_health_analysis(
    frequency_summary: pd.DataFrame,
    edfa_kpi: pd.DataFrame,
) -> pd.DataFrame:
    freq = frequency_summary.copy()

    freq["frequency_status"] = freq["frequency_status"].apply(normalize_status)
    freq["priority"] = freq["frequency_status"].map(PRIORITY_MAP)

    freq["ber_critical_count"] = pd.to_numeric(freq["ber_critical_count"], errors="coerce").fillna(0).astype(int)
    freq["ber_warning_count"] = pd.to_numeric(freq["ber_warning_count"], errors="coerce").fillna(0).astype(int)
    freq["power_critical_count"] = pd.to_numeric(freq["power_critical_count"], errors="coerce").fillna(0).astype(int)
    freq["power_warning_count"] = pd.to_numeric(freq["power_warning_count"], errors="coerce").fillna(0).astype(int)

    freq["issue_category"] = freq.apply(classify_frequency_issue, axis=1)
    freq["recommended_check"] = freq.apply(build_frequency_recommendation, axis=1)

    return freq.sort_values(
        ["frequency_status", "frequency_risk_score"],
        ascending=[True, False],
    )


def classify_frequency_issue(row: pd.Series) -> str:
    ber_critical = int(row.get("ber_critical_count", 0))
    ber_warning = int(row.get("ber_warning_count", 0))
    power_critical = int(row.get("power_critical_count", 0))
    power_warning = int(row.get("power_warning_count", 0))

    if ber_critical > 0 and power_critical > 0:
        return "BER and optical power critical"

    if ber_critical > 0 and power_warning > 0:
        return "BER critical with power warning"

    if ber_critical > 0:
        return "BER critical only"

    if power_critical > 0 and ber_warning > 0:
        return "Power critical with BER warning"

    if power_critical > 0:
        return "Optical power critical only"

    if ber_warning > 0 and power_warning > 0:
        return "BER and optical power warning"

    if ber_warning > 0:
        return "BER warning only"

    if power_warning > 0:
        return "Optical power warning only"

    return "No abnormal behavior detected"


def build_frequency_recommendation(row: pd.Series) -> str:
    issue = row.get("issue_category", "")

    if issue == "BER and optical power critical":
        return "Highest priority. Correlate Pre-FEC BER with OCH power degradation. Check optical path, channel power, amplifier behavior and transponder condition."

    if issue == "BER critical with power warning":
        return "High priority. BER is critical while optical power is already abnormal. Check channel power trend, OSNR-related degradation and amplifier section."

    if issue == "BER critical only":
        return "High priority. BER is critical but OCH power is not critical. Check transponder, modulation/FEC behavior, non-power optical impairments and side-specific degradation."

    if issue == "Power critical with BER warning":
        return "High priority. Optical power is critical and BER is degraded. Check power equalization, connector/patching and amplifier tilt."

    if issue == "Optical power critical only":
        return "Check OCH power level, channel equalization, ROADM/EDFA behavior and physical optical path. BER may still be protected by FEC."

    if issue == "BER and optical power warning":
        return "Monitor closely. BER and power are both above normal distribution. Investigate before escalation to critical state."

    if issue == "BER warning only":
        return "Monitor Pre-FEC BER trend and compare A/Z side behavior. Check non-power optical impairments if trend worsens."

    if issue == "Optical power warning only":
        return "Monitor optical channel power drift and EDFA gain/tilt. Check equalization if drift continues."

    return "No immediate action. Continue regular monitoring."


def build_channel_health_analysis(
    pre_fec_kpi: pd.DataFrame,
    frequency_health: pd.DataFrame,
    device_health: pd.DataFrame,
) -> pd.DataFrame:
    ber = pre_fec_kpi.copy()

    ber["ber_status"] = ber["ber_status"].apply(normalize_status)

    freq_cols = [
        "center_frequency",
        "frequency_status",
        "frequency_risk_score",
        "issue_category",
        "ber_critical_count",
        "ber_warning_count",
        "power_critical_count",
        "power_warning_count",
    ]

    available_freq_cols = [col for col in freq_cols if col in frequency_health.columns]

    channel = ber.merge(
        frequency_health[available_freq_cols],
        on="center_frequency",
        how="left",
        suffixes=("", "_frequency"),
    )

    device_cols = [
        "device_name",
        "device_status",
        "device_risk_score",
        "power_device_status",
        "edfa_device_status",
    ]

    available_device_cols = [col for col in device_cols if col in device_health.columns]

    channel = channel.merge(
        device_health[available_device_cols],
        on="device_name",
        how="left",
        suffixes=("", "_device"),
    )

    channel["frequency_status"] = channel["frequency_status"].apply(normalize_status)
    channel["device_status"] = channel["device_status"].apply(normalize_status)

    channel["overall_status"] = channel.apply(
        lambda row: worst_status(
            [
                row["ber_status"],
                row["frequency_status"],
                row["device_status"],
            ]
        ),
        axis=1,
    )

    risk_candidates = []

    for col in ["ber_risk_score", "frequency_risk_score", "device_risk_score"]:
        if col in channel.columns:
            channel[col] = pd.to_numeric(channel[col], errors="coerce").fillna(0)
            risk_candidates.append(col)

    if risk_candidates:
        channel["overall_risk_score"] = channel[risk_candidates].max(axis=1).round(2)
    else:
        channel["overall_risk_score"] = 0

    channel["priority"] = channel["overall_status"].map(PRIORITY_MAP)

    channel["issue_category_final"] = channel.apply(classify_channel_issue, axis=1)
    channel["recommended_check"] = channel.apply(build_channel_recommendation, axis=1)

    preferred_cols = [
        "priority",
        "overall_status",
        "overall_risk_score",
        "issue_category_final",
        "recommended_check",
        "time_start",
        "time_end",
        "device_name",
        "logical_name",
        "pn",
        "side",
        "och",
        "och_group",
        "center_frequency",
        "ber_status",
        "ber_risk_score",
        "ber_mean",
        "ber_p95",
        "ber_max",
        "ber_last",
        "frequency_status",
        "frequency_risk_score",
        "issue_category",
        "device_status",
        "device_risk_score",
        "power_device_status",
        "edfa_device_status",
        "channel_key",
    ]

    existing_cols = [col for col in preferred_cols if col in channel.columns]
    other_cols = [col for col in channel.columns if col not in existing_cols]

    channel = channel[existing_cols + other_cols]

    return channel.sort_values(
        ["overall_status", "overall_risk_score"],
        ascending=[True, False],
    )


def classify_channel_issue(row: pd.Series) -> str:
    ber_status = normalize_status(row.get("ber_status"))
    frequency_status = normalize_status(row.get("frequency_status"))
    device_status = normalize_status(row.get("device_status"))
    side = str(row.get("side", "")).strip()

    if ber_status == "Critical" and frequency_status == "Critical":
        return "Critical BER correlated with frequency-level degradation"

    if ber_status == "Critical" and device_status == "Critical":
        return "Critical BER correlated with device-level degradation"

    if ber_status == "Critical":
        return "Critical Pre-FEC BER"

    if ber_status == "Warning" and frequency_status in ["Warning", "Critical"]:
        return "BER warning correlated with frequency-level abnormality"

    if ber_status == "Warning":
        return "Pre-FEC BER warning"

    if frequency_status == "Critical":
        return "Frequency-level critical condition affecting this channel"

    if device_status == "Critical":
        return "Device-level critical condition affecting this channel"

    if side in ["A", "Z"]:
        return "Normal channel with side-specific monitoring available"

    return "Normal channel"


def build_channel_recommendation(row: pd.Series) -> str:
    issue = row.get("issue_category_final", "")

    if issue == "Critical BER correlated with frequency-level degradation":
        return "P1. Check optical channel/frequency, OCH power behavior, EDFA section and transponder Pre-FEC BER trend."

    if issue == "Critical BER correlated with device-level degradation":
        return "P1. Check transponder and local device optical components. Correlate with EDFA and OCH power status on the same device."

    if issue == "Critical Pre-FEC BER":
        return "P1. Check Pre-FEC BER trend, side A/Z behavior, transponder condition and possible optical impairments not visible from power alone."

    if issue == "BER warning correlated with frequency-level abnormality":
        return "P2. Monitor BER and frequency-level OCH power. Investigate early before Post-FEC/service impact."

    if issue == "Pre-FEC BER warning":
        return "P2. Monitor Pre-FEC BER and compare with OCH power/EDFA telemetry."

    if issue == "Frequency-level critical condition affecting this channel":
        return "P1/P2. Frequency has critical power or BER behavior. Check whether this channel shares the affected frequency group."

    if issue == "Device-level critical condition affecting this channel":
        return "P1/P2. Device has critical optical behavior. Check device-level OCH power and EDFA telemetry."

    return "No immediate action. Continue monitoring."


def build_high_risk_recommendations(
    channel_health: pd.DataFrame,
    frequency_health: pd.DataFrame,
    device_health: pd.DataFrame,
) -> pd.DataFrame:
    rows = []

    channel_high = channel_health[channel_health["overall_status"].isin(["Critical", "Warning"])].copy()
    frequency_high = frequency_health[frequency_health["frequency_status"].isin(["Critical", "Warning"])].copy()
    device_high = device_health[device_health["device_status"].isin(["Critical", "Warning"])].copy()

    for _, row in channel_high.iterrows():
        rows.append(
            {
                "source": "channel",
                "priority": row.get("priority"),
                "status": row.get("overall_status"),
                "risk_score": row.get("overall_risk_score"),
                "object_id": row.get("channel_key"),
                "device_name": row.get("device_name"),
                "center_frequency": row.get("center_frequency"),
                "issue_category": row.get("issue_category_final"),
                "recommended_check": row.get("recommended_check"),
            }
        )

    for _, row in frequency_high.iterrows():
        rows.append(
            {
                "source": "frequency",
                "priority": row.get("priority"),
                "status": row.get("frequency_status"),
                "risk_score": row.get("frequency_risk_score"),
                "object_id": row.get("center_frequency"),
                "device_name": "",
                "center_frequency": row.get("center_frequency"),
                "issue_category": row.get("issue_category"),
                "recommended_check": row.get("recommended_check"),
            }
        )

    for _, row in device_high.iterrows():
        rows.append(
            {
                "source": "device",
                "priority": row.get("priority"),
                "status": row.get("device_status"),
                "risk_score": row.get("device_risk_score"),
                "object_id": row.get("device_name"),
                "device_name": row.get("device_name"),
                "center_frequency": "",
                "issue_category": f"Device optical health: power={row.get('power_device_status')}, edfa={row.get('edfa_device_status')}",
                "recommended_check": row.get("recommended_check"),
            }
        )

    result = pd.DataFrame(rows)

    if result.empty:
        return result

    result["risk_score"] = pd.to_numeric(result["risk_score"], errors="coerce").fillna(0)

    priority_order = {
        "P1": 1,
        "P2": 2,
        "P3": 3,
        "P4": 4,
    }

    result["priority_order"] = result["priority"].map(priority_order).fillna(99)

    result = result.sort_values(
        ["priority_order", "risk_score"],
        ascending=[True, False],
    ).drop(columns=["priority_order"])

    return result


def build_health_report(
    channel_health: pd.DataFrame,
    frequency_health: pd.DataFrame,
    device_health: pd.DataFrame,
    high_risk: pd.DataFrame,
) -> str:
    lines = []

    lines.append("# Phase 5 Health Analysis Report")
    lines.append("")
    lines.append("This report summarizes rule-based health analysis built from Phase 4 KPI outputs.")
    lines.append("")
    lines.append("The analysis uses data-driven KPI status values from the public Alibaba optical transport telemetry dataset. It does not use private NMS alarm logic or vendor-specific thresholds.")
    lines.append("")

    lines.append("## Output Files")
    lines.append("")
    lines.append("| Output File | Rows | Purpose |")
    lines.append("|---|---:|---|")
    lines.append(f"| `data/processed/channel_health_analysis.csv` | {len(channel_health):,} | Channel/transponder-level health analysis |")
    lines.append(f"| `data/processed/frequency_health_analysis.csv` | {len(frequency_health):,} | Frequency-level health analysis |")
    lines.append(f"| `data/processed/device_health_analysis.csv` | {len(device_health):,} | Device-level optical health analysis |")
    lines.append(f"| `data/processed/high_risk_recommendations.csv` | {len(high_risk):,} | Prioritized warning/critical objects |")
    lines.append("")

    lines.append("## 1. Channel Health")
    lines.append("")
    lines.append("### Overall Status Distribution")
    lines.append("")
    lines.append(status_counts(channel_health, "overall_status"))
    lines.append("")
    lines.append("### Priority Distribution")
    lines.append("")
    lines.append(priority_counts(channel_health))
    lines.append("")

    lines.append("## 2. Frequency Health")
    lines.append("")
    lines.append("### Frequency Status Distribution")
    lines.append("")
    lines.append(status_counts(frequency_health, "frequency_status"))
    lines.append("")
    lines.append("### Frequency Priority Distribution")
    lines.append("")
    lines.append(priority_counts(frequency_health))
    lines.append("")

    lines.append("## 3. Device Health")
    lines.append("")
    lines.append("### Device Status Distribution")
    lines.append("")
    lines.append(status_counts(device_health, "device_status"))
    lines.append("")
    lines.append("### Device Priority Distribution")
    lines.append("")
    lines.append(priority_counts(device_health))
    lines.append("")

    lines.append("## 4. High-Risk Recommendations")
    lines.append("")
    lines.append(f"- Total high-risk objects: **{len(high_risk):,}**")
    lines.append("")
    if not high_risk.empty:
        lines.append("### High-Risk Source Distribution")
        lines.append("")
        lines.append(status_counts(high_risk, "source"))
        lines.append("")
        lines.append("### High-Risk Priority Distribution")
        lines.append("")
        lines.append(priority_counts(high_risk))
        lines.append("")

    lines.append("## Rule Logic")
    lines.append("")
    lines.append("| Input Condition | Interpretation |")
    lines.append("|---|---|")
    lines.append("| Critical Pre-FEC BER + critical frequency status | Possible optical transport degradation affecting the channel/frequency |")
    lines.append("| Critical Pre-FEC BER + normal frequency status | Possible transponder-side or non-power optical impairment |")
    lines.append("| Critical OCH power behavior | Possible optical power degradation, channel equalization issue or physical path issue |")
    lines.append("| Critical EDFA behavior | Possible amplifier gain, tilt, attenuation or span issue |")
    lines.append("| Warning status | Early degradation indicator requiring trend monitoring |")
    lines.append("")

    lines.append("## G.709/OTN Interpretation")
    lines.append("")
    lines.append("Pre-FEC BER is interpreted as a transport-channel quality indicator before FEC correction. OCH power and EDFA telemetry provide optical-layer context for investigating BER degradation.")
    lines.append("")
    lines.append("This supports a G.709-aware troubleshooting workflow without claiming to decode raw G.709 overhead or extract real TIM/BDI/PLM/TCM alarms.")
    lines.append("")

    lines.append("## Limitation")
    lines.append("")
    lines.append("The health analysis is based on public telemetry and percentile-based KPI status values. It is intended for learning, portfolio demonstration and analysis workflow design, not production NOC deployment.")
    lines.append("")

    return "\n".join(lines)


def main() -> None:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    DOCS_DIR.mkdir(parents=True, exist_ok=True)

    print("Project root:", PROJECT_ROOT)
    print("Processed dir:", PROCESSED_DIR)
    print("-" * 80)

    print("Reading Phase 4 KPI outputs...")
    pre_fec_kpi = read_csv(INPUT_FILES["pre_fec_kpi"])
    och_power_kpi = read_csv(INPUT_FILES["och_power_kpi"])
    edfa_kpi = read_csv(INPUT_FILES["edfa_kpi"])
    frequency_summary = read_csv(INPUT_FILES["frequency_summary"])

    print("Building device health analysis...")
    device_health = build_device_health_summary(och_power_kpi, edfa_kpi)
    device_path = PROCESSED_DIR / "device_health_analysis.csv"
    device_health.to_csv(device_path, index=False, encoding="utf-8-sig")
    print(f"  Saved: {device_path} ({len(device_health):,} rows)")

    print("Building frequency health analysis...")
    frequency_health = build_frequency_health_analysis(frequency_summary, edfa_kpi)
    frequency_path = PROCESSED_DIR / "frequency_health_analysis.csv"
    frequency_health.to_csv(frequency_path, index=False, encoding="utf-8-sig")
    print(f"  Saved: {frequency_path} ({len(frequency_health):,} rows)")

    print("Building channel health analysis...")
    channel_health = build_channel_health_analysis(pre_fec_kpi, frequency_health, device_health)
    channel_path = PROCESSED_DIR / "channel_health_analysis.csv"
    channel_health.to_csv(channel_path, index=False, encoding="utf-8-sig")
    print(f"  Saved: {channel_path} ({len(channel_health):,} rows)")

    print("Building high-risk recommendations...")
    high_risk = build_high_risk_recommendations(channel_health, frequency_health, device_health)
    high_risk_path = PROCESSED_DIR / "high_risk_recommendations.csv"
    high_risk.to_csv(high_risk_path, index=False, encoding="utf-8-sig")
    print(f"  Saved: {high_risk_path} ({len(high_risk):,} rows)")

    print("Writing Phase 5 report...")
    report = build_health_report(channel_health, frequency_health, device_health, high_risk)
    report_path = DOCS_DIR / "phase5_health_analysis_report.md"
    report_path.write_text(report, encoding="utf-8")
    print(f"  Generated: {report_path}")

    print("-" * 80)
    print("Phase 5 health analysis completed.")


if __name__ == "__main__":
    main()