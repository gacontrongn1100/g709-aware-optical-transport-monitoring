@'
# G.709-Aware Optical Transport Monitoring Dashboard

## Overview

This project builds a monitoring and analysis dashboard for optical transport network telemetry using the public Alibaba Cloud Transport System Dataset.

The project focuses on analyzing key optical transport indicators such as Pre-FEC BER, optical channel power, EDFA input/output power, gain, tilt and attenuation.

ITU-T G.709/OTN concepts are used as the technical interpretation framework for understanding transport-channel quality, FEC-related degradation and DWDM/OTN monitoring workflows.

## Dataset

Primary dataset:

- Alibaba Cloud Transport System Dataset

Main data files planned for this project:

- `performance_elec.csv`: transponder-side performance data, including Pre-FEC BER.
- `ocm.csv`: optical channel monitor data, including center frequency and optical channel power.
- `performance_optical.csv`: EDFA-related optical performance data, including input/output power, gain, tilt and attenuation.

## Technical Scope

This project includes:

- Data exploration and data dictionary creation.
- Pre-FEC BER analysis.
- Optical channel power analysis.
- EDFA telemetry analysis.
- Data-driven health classification using percentile-based rules.
- Streamlit dashboard visualization.
- Technical documentation connecting optical telemetry to G.709/OTN concepts.

## Project Limitation

This project does not use private telecom operator data.

This project does not decode raw G.709 overhead bytes.

This project does not claim to extract real TIM, BDI, PLM or TCM alarms from the dataset.

The project applies G.709/OTN concepts to interpret public optical transport telemetry.

## Project Structure

```text
g709-aware-optical-transport-monitoring/
├── dashboard/
├── data/
│   ├── raw/
│   └── processed/
├── docs/
├── notebooks/
├── screenshots/
├── src/
├── .gitignore
├── README.md
└── requirements.txt