# Project Scope

## Project Name

G.709-Aware Optical Transport Monitoring Dashboard

## Objective

This project builds a monitoring and analysis dashboard for optical transport network telemetry using the public Alibaba Cloud Transport System Dataset.

The project focuses on analyzing transport-channel health indicators such as Pre-FEC BER, optical channel power, EDFA input/output power, gain, tilt and attenuation.

The project applies ITU-T G.709/OTN concepts as the technical interpretation framework for understanding transport-layer monitoring, FEC-related degradation and DWDM channel quality.

## Main Goals

1. Use a public optical transport dataset instead of private operator data.
2. Explore and document the Alibaba Cloud Transport System Dataset.
3. Analyze Pre-FEC BER, OCH power and EDFA telemetry.
4. Build rule-based channel health classification using data-driven thresholds.
5. Visualize optical transport KPIs in a Streamlit dashboard.
6. Document the relationship between optical telemetry and G.709/OTN concepts.
7. Produce a GitHub-ready project suitable for a transmission/network engineering CV.

## In Scope

- Public Alibaba optical transport telemetry dataset.
- Pre-FEC BER analysis.
- Optical channel power analysis.
- EDFA input/output power analysis.
- Gain, tilt and attenuation analysis.
- Percentile-based health classification.
- Streamlit dashboard.
- Technical documentation.
- CV-ready project explanation.

## Out of Scope

- No private operator data.
- No real NMS alarm logs.
- No live network data collection.
- No decoding of raw G.709 overhead bytes.
- No claim of real TIM, BDI, PLM or TCM alarm extraction from the dataset.
- No vendor-specific threshold unless explicitly documented from public sources.
