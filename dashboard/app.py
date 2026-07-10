from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


# =========================
# Path configuration
# =========================

PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

FILES = {
    "channel_health": PROCESSED_DIR / "channel_health_analysis.csv",
    "frequency_health": PROCESSED_DIR / "frequency_health_analysis.csv",
    "device_health": PROCESSED_DIR / "device_health_analysis.csv",
    "high_risk": PROCESSED_DIR / "high_risk_recommendations.csv",
    "pre_fec_kpi": PROCESSED_DIR / "pre_fec_ber_kpi.csv",
    "och_power_kpi": PROCESSED_DIR / "och_power_kpi.csv",
    "edfa_kpi": PROCESSED_DIR / "edfa_kpi.csv",
}


# =========================
# Streamlit config
# =========================

st.set_page_config(
    page_title="G.709-Aware Optical Transport Monitoring",
    page_icon="📡",
    layout="wide",
)


# =========================
# Data loading
# =========================

@st.cache_data
def load_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()

    df = pd.read_csv(path)

    for col in ["time", "time_start", "time_end"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    return df


@st.cache_data
def load_all_data() -> dict:
    return {
        name: load_csv(path)
        for name, path in FILES.items()
    }


# =========================
# Common helpers
# =========================

def status_order() -> list:
    return ["Critical", "Warning", "Normal", "Unknown"]


def priority_order() -> list:
    return ["P1", "P2", "P3", "P4"]


def show_table(df: pd.DataFrame, title: str, height: int = 550) -> None:
    st.subheader(title)

    if df.empty:
        st.warning("No data available.")
        return

    st.dataframe(df, width='stretch', height=height)


def show_status_chart(df: pd.DataFrame, status_col: str, title: str) -> None:
    if df.empty or status_col not in df.columns:
        st.info(f"No data available for {title}.")
        return

    counts = (
        df[status_col]
        .fillna("Unknown")
        .value_counts()
        .reindex(status_order(), fill_value=0)
        .reset_index()
    )

    counts.columns = ["Status", "Count"]

    fig = px.bar(
        counts,
        x="Status",
        y="Count",
        text="Count",
        title=title,
    )

    fig.update_layout(
        xaxis_title="Status",
        yaxis_title="Count",
        showlegend=False,
    )

    st.plotly_chart(fig, width='stretch')


def show_priority_chart(df: pd.DataFrame, title: str) -> None:
    if df.empty or "priority" not in df.columns:
        st.info(f"No priority data available for {title}.")
        return

    counts = (
        df["priority"]
        .fillna("P4")
        .value_counts()
        .reindex(priority_order(), fill_value=0)
        .reset_index()
    )

    counts.columns = ["Priority", "Count"]

    fig = px.bar(
        counts,
        x="Priority",
        y="Count",
        text="Count",
        title=title,
    )

    fig.update_layout(
        xaxis_title="Priority",
        yaxis_title="Count",
        showlegend=False,
    )

    st.plotly_chart(fig, width='stretch')


def sidebar_filter(df: pd.DataFrame, column: str, label: str) -> pd.DataFrame:
    if df.empty or column not in df.columns:
        return df

    values = sorted(df[column].dropna().astype(str).unique().tolist())

    selected = st.sidebar.multiselect(label, values)

    if not selected:
        return df

    return df[df[column].astype(str).isin(selected)]


def sort_by_numeric(df: pd.DataFrame, column: str) -> pd.DataFrame:
    if df.empty or column not in df.columns:
        return df

    df = df.copy()
    df[column] = pd.to_numeric(df[column], errors="coerce")
    return df.sort_values(column, ascending=False)


# =========================
# Pages
# =========================

def overview_page(data: dict) -> None:
    st.header("Overview")

    channel_df = data["channel_health"]
    frequency_df = data["frequency_health"]
    device_df = data["device_health"]
    high_risk_df = data["high_risk"]

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Channels", len(channel_df))
    col2.metric("Frequencies", len(frequency_df))
    col3.metric("Devices", len(device_df))
    col4.metric("High-risk objects", len(high_risk_df))

    st.markdown("---")

    col1, col2, col3 = st.columns(3)

    with col1:
        show_status_chart(
            channel_df,
            "overall_status",
            "Channel Health Status",
        )

    with col2:
        show_status_chart(
            frequency_df,
            "frequency_status",
            "Frequency Health Status",
        )

    with col3:
        show_status_chart(
            device_df,
            "device_status",
            "Device Health Status",
        )

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        show_priority_chart(
            high_risk_df,
            "High-Risk Priority Distribution",
        )

    with col2:
        if not high_risk_df.empty and "source" in high_risk_df.columns:
            source_counts = (
                high_risk_df["source"]
                .value_counts()
                .reset_index()
            )
            source_counts.columns = ["Source", "Count"]

            fig = px.pie(
                source_counts,
                names="Source",
                values="Count",
                title="High-Risk Source Distribution",
                hole=0.35,
            )

            st.plotly_chart(fig, width='stretch')
        else:
            st.info("No high-risk source data available.")

    st.markdown("---")

    if not high_risk_df.empty:
        columns = [
            "source",
            "priority",
            "status",
            "risk_score",
            "object_id",
            "device_name",
            "center_frequency",
            "issue_category",
            "recommended_check",
        ]

        columns = [
            col for col in columns
            if col in high_risk_df.columns
        ]

        show_table(
            high_risk_df[columns].head(20),
            "Top 20 High-Risk Recommendations",
            height=420,
        )


def high_risk_page(data: dict) -> None:
    st.header("High-Risk Recommendations")

    df = data["high_risk"].copy()

    if df.empty:
        st.warning("No high-risk recommendation data found.")
        return

    df = sidebar_filter(df, "priority", "Filter priority")
    df = sidebar_filter(df, "source", "Filter source")
    df = sidebar_filter(df, "status", "Filter status")

    df = sort_by_numeric(df, "risk_score")

    show_table(
        df,
        "Prioritized Warning/Critical Objects",
        height=650,
    )


def channel_health_page(data: dict) -> None:
    st.header("Channel Health Analysis")

    df = data["channel_health"].copy()

    if df.empty:
        st.warning("No channel health data found.")
        return

    df = sidebar_filter(df, "priority", "Filter priority")
    df = sidebar_filter(df, "overall_status", "Filter overall status")
    df = sidebar_filter(df, "device_name", "Filter device")
    df = sidebar_filter(df, "side", "Filter side")

    df = sort_by_numeric(df, "overall_risk_score")

    col1, col2 = st.columns(2)

    with col1:
        show_status_chart(
            df,
            "overall_status",
            "Filtered Channel Status",
        )

    with col2:
        show_priority_chart(
            df,
            "Filtered Channel Priority",
        )

    show_table(
        df,
        "Channel Health Table",
        height=650,
    )


def frequency_health_page(data: dict) -> None:
    st.header("Frequency Health Analysis")

    df = data["frequency_health"].copy()

    if df.empty:
        st.warning("No frequency health data found.")
        return

    df = sidebar_filter(df, "priority", "Filter priority")
    df = sidebar_filter(df, "frequency_status", "Filter frequency status")
    df = sidebar_filter(df, "issue_category", "Filter issue category")

    col1, col2 = st.columns(2)

    with col1:
        show_status_chart(
            df,
            "frequency_status",
            "Frequency Status",
        )

    with col2:
        show_priority_chart(
            df,
            "Frequency Priority",
        )

    if "frequency_risk_score" in df.columns:
        plot_df = sort_by_numeric(df, "frequency_risk_score")

        fig = px.bar(
            plot_df,
            x="center_frequency",
            y="frequency_risk_score",
            color="frequency_status",
            title="Frequency Risk Score",
            hover_data=[
                col for col in [
                    "issue_category",
                    "recommended_check",
                ]
                if col in plot_df.columns
            ],
        )

        fig.update_layout(
            xaxis_title="Center Frequency",
            yaxis_title="Risk Score",
        )

        st.plotly_chart(fig, width='stretch')

    show_table(
        df,
        "Frequency Health Table",
        height=600,
    )


def device_health_page(data: dict) -> None:
    st.header("Device Health Analysis")

    df = data["device_health"].copy()

    if df.empty:
        st.warning("No device health data found.")
        return

    df = sidebar_filter(df, "priority", "Filter priority")
    df = sidebar_filter(df, "device_status", "Filter device status")
    df = sidebar_filter(df, "device_name", "Filter device name")

    col1, col2 = st.columns(2)

    with col1:
        show_status_chart(
            df,
            "device_status",
            "Device Status",
        )

    with col2:
        show_priority_chart(
            df,
            "Device Priority",
        )

    if "device_risk_score" in df.columns:
        plot_df = sort_by_numeric(df, "device_risk_score").head(30)

        fig = px.bar(
            plot_df,
            x="device_name",
            y="device_risk_score",
            color="device_status",
            title="Top Device Risk Scores",
        )

        fig.update_layout(
            xaxis_title="Device",
            yaxis_title="Risk Score",
        )

        st.plotly_chart(fig, width='stretch')

    show_table(
        df,
        "Device Health Table",
        height=600,
    )


def pre_fec_page(data: dict) -> None:
    st.header("Pre-FEC BER KPI")

    df = data["pre_fec_kpi"].copy()

    if df.empty:
        st.warning("No Pre-FEC BER KPI data found.")
        return

    df = sidebar_filter(df, "ber_status", "Filter BER status")
    df = sidebar_filter(df, "device_name", "Filter device")
    df = sidebar_filter(df, "side", "Filter side")

    col1, col2 = st.columns(2)

    with col1:
        show_status_chart(
            df,
            "ber_status",
            "BER Status",
        )

    with col2:
        if "ber_risk_score" in df.columns:
            plot_df = sort_by_numeric(df, "ber_risk_score").head(20)

            fig = px.bar(
                plot_df,
                x="channel_key",
                y="ber_risk_score",
                color="ber_status",
                title="Top Pre-FEC BER Risk Scores",
            )

            fig.update_layout(
                xaxis_title="Channel",
                yaxis_title="Risk Score",
            )

            st.plotly_chart(fig, width='stretch')

    show_table(
        df,
        "Pre-FEC BER KPI Table",
        height=600,
    )


def och_power_page(data: dict) -> None:
    st.header("OCH Power KPI")

    df = data["och_power_kpi"].copy()

    if df.empty:
        st.warning("No OCH Power KPI data found.")
        return

    df = sidebar_filter(df, "power_status", "Filter power status")
    df = sidebar_filter(df, "device_name", "Filter device")

    col1, col2 = st.columns(2)

    with col1:
        show_status_chart(
            df,
            "power_status",
            "OCH Power Status",
        )

    with col2:
        if "power_risk_score" in df.columns:
            plot_df = sort_by_numeric(df, "power_risk_score").head(30)

            fig = px.bar(
                plot_df,
                x="channel_key",
                y="power_risk_score",
                color="power_status",
                title="Top OCH Power Risk Scores",
            )

            fig.update_layout(
                xaxis_title="OCH Channel",
                yaxis_title="Risk Score",
            )

            st.plotly_chart(fig, width='stretch')

    show_table(
        df,
        "OCH Power KPI Table",
        height=600,
    )


def edfa_page(data: dict) -> None:
    st.header("EDFA KPI")

    df = data["edfa_kpi"].copy()

    if df.empty:
        st.warning("No EDFA KPI data found.")
        return

    df = sidebar_filter(df, "edfa_status", "Filter EDFA status")
    df = sidebar_filter(df, "device_name", "Filter device")
    df = sidebar_filter(df, "pn", "Filter PN")

    col1, col2 = st.columns(2)

    with col1:
        show_status_chart(
            df,
            "edfa_status",
            "EDFA Status",
        )

    with col2:
        if "edfa_risk_score" in df.columns:
            plot_df = sort_by_numeric(df, "edfa_risk_score").head(30)

            fig = px.bar(
                plot_df,
                x="edfa_key",
                y="edfa_risk_score",
                color="edfa_status",
                title="Top EDFA Risk Scores",
            )

            fig.update_layout(
                xaxis_title="EDFA",
                yaxis_title="Risk Score",
            )

            st.plotly_chart(fig, width='stretch')

    show_table(
        df,
        "EDFA KPI Table",
        height=600,
    )


def g709_notes_page() -> None:
    st.header("G.709 / OTN Interpretation Notes")

    st.markdown(
        """
## Scope

This dashboard uses public optical transport telemetry from the Alibaba Cloud Transport System Dataset.

It does **not** decode raw G.709 OPU/ODU/OTU overhead bytes and does **not** extract real NMS alarms such as TIM, BDI, PLM or TCM defects.

## Simplified OTN/DWDM interpretation model

```text
Client Signal
    ↓
OPUk
    ↓
ODUk
    ↓
OTUk / FEC
    ↓
Optical Channel / DWDM Lambda
    ↓
EDFA / Optical Section
    ↓
Fiber Route
```

## How this project interprets telemetry

| Dataset Signal | Interpretation |
|---|---|
| Pre-FEC BER | Transport-channel quality before FEC correction |
| OCH power | Optical channel power behavior |
| Center frequency | DWDM frequency/channel dimension |
| EDFA gain | Amplifier behavior |
| EDFA gain tilt | Gain profile imbalance indicator |
| Attenuation | Optical section attenuation context |

## Troubleshooting logic

| Condition | Possible interpretation |
|---|---|
| High Pre-FEC BER + abnormal OCH power | Possible optical path degradation |
| High Pre-FEC BER + normal OCH power | Possible transponder-side or non-power impairment |
| Abnormal EDFA tilt + OCH power imbalance | Possible amplifier/equalization issue |
| Warning status | Early degradation indicator |
| Critical status | Prioritized object for investigation |
"""
    )


# =========================
# Main app
# =========================

def main() -> None:
    st.title("G.709-Aware Optical Transport Monitoring Dashboard")

    data = load_all_data()

    missing_files = [
        name
        for name, df in data.items()
        if df.empty
    ]

    if missing_files:
        st.warning(
            "Some processed files are missing or empty: "
            + ", ".join(missing_files)
            + ". Please run Phase 4 and Phase 5 scripts first."
        )

    page = st.sidebar.radio(
        "Navigation",
        [
            "Overview",
            "High-Risk Recommendations",
            "Channel Health",
            "Frequency Health",
            "Device Health",
            "Pre-FEC BER KPI",
            "OCH Power KPI",
            "EDFA KPI",
            "G.709 / OTN Notes",
        ],
    )

    st.sidebar.markdown("---")
    st.sidebar.caption(
        "G.709-aware analysis using public Alibaba optical transport telemetry."
    )

    if page == "Overview":
        overview_page(data)
    elif page == "High-Risk Recommendations":
        high_risk_page(data)
    elif page == "Channel Health":
        channel_health_page(data)
    elif page == "Frequency Health":
        frequency_health_page(data)
    elif page == "Device Health":
        device_health_page(data)
    elif page == "Pre-FEC BER KPI":
        pre_fec_page(data)
    elif page == "OCH Power KPI":
        och_power_page(data)
    elif page == "EDFA KPI":
        edfa_page(data)
    elif page == "G.709 / OTN Notes":
        g709_notes_page()


if __name__ == "__main__":
    main()
