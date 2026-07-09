import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="G.709-Aware Optical Transport Monitoring",
    layout="wide"
)

st.title("G.709-Aware Optical Transport Monitoring Dashboard")

st.success("Phase 1 test: Streamlit is running successfully.")

st.markdown("""
## Project Status

This dashboard is currently a placeholder for Phase 1.

Next phases will load and analyze the Alibaba Cloud Transport System Dataset, including:

- Pre-FEC BER from `performance_elec.csv`
- Optical channel power from `ocm.csv`
- EDFA telemetry from `performance_optical.csv`
- G.709/OTN-aware interpretation of transport channel quality
""")

sample = pd.DataFrame(
    {
        "Dataset File": [
            "performance_elec.csv",
            "ocm.csv",
            "performance_optical.csv"
        ],
        "Planned Analysis": [
            "Pre-FEC BER / transponder-side performance",
            "Optical channel power / center frequency",
            "EDFA input-output power / gain / tilt / attenuation"
        ],
        "Status": [
            "Pending Phase 2",
            "Pending Phase 2",
            "Pending Phase 2"
        ]
    }
)

st.dataframe(sample, use_container_width=True)
