# G.709-Aware Optical Transport Monitoring

A Python-based optical transport monitoring project using the public Alibaba Cloud Transport System Dataset, with ITU-T G.709/OTN concepts used as the technical interpretation framework.

## Overview

This project analyzes public DWDM/OTN-related telemetry to evaluate optical transport channel health.

Main telemetry groups:

- Pre-FEC BER
- Optical channel power
- Center frequency
- EDFA input/output power
- EDFA gain
- EDFA gain tilt
- Optical attenuation

The goal is to build a clean data pipeline, KPI calculation layer, and dashboard for optical transport monitoring analysis.

## Dataset

Primary dataset:

- Alibaba Cloud Transport System Dataset

Local dataset path:

```text
data/raw/alibaba-cloud-transport-system/
```

Main files used:

| File | Purpose |
|---|---|
| `performance_elec.csv` | Pre-FEC BER / transponder performance |
| `ocm.csv` | Optical channel power / center frequency |
| `performance_optical.csv` | EDFA / optical performance |

## Current Status

| Phase | Description | Status |
|---|---|---|
| Phase 1 | Dataset verification | Completed |
| Phase 2 | Data exploration | Completed |
| Phase 3 | Data cleaning and standardization | Completed |
| Phase 4 | KPI calculation | In progress |
| Phase 5 | Rule-based health analysis | Planned |
| Phase 6 | Streamlit dashboard | Planned |
| Phase 7 | Final documentation and CV packaging | Planned |

## Verified Dataset Files

| File | Rows | Columns |
|---|---:|---:|
| `performance_optical.csv` | 154,935 | 10 |
| `ocm.csv` | 267,508 | 6 |
| `performance_elec.csv` | 29,276 | 11 |

## Processed Data

Phase 3 generated the following cleaned datasets:

| Output File | Rows | Purpose |
|---|---:|---|
| `pre_fec_ber_clean.csv` | 28,900 | Clean Pre-FEC BER records |
| `och_power_clean.csv` | 267,508 | Clean OCH power records |
| `edfa_telemetry_long_clean.csv` | 154,935 | Clean EDFA telemetry in long format |
| `edfa_telemetry_wide_clean.csv` | 22,944 | Clean EDFA telemetry in wide format |

Processed CSV files are stored locally under:

```text
data/processed/
```

They are not committed to GitHub because raw and processed datasets are ignored by `.gitignore`.

## Project Structure

```text
g709-aware-optical-transport-monitoring/
├── dashboard/
│   └── app.py
├── data/
│   ├── raw/
│   └── processed/
├── docs/
│   ├── data_dictionary.md
│   ├── phase2_data_profile.md
│   ├── phase2_findings.md
│   └── phase3_cleaning_report.md
├── notebooks/
├── scripts/
│   ├── check_dataset.py
│   ├── phase2_explore_data.py
│   └── phase3_clean_data.py
├── screenshots/
├── src/
├── README.md
└── requirements.txt
```

## Setup

Create a virtual environment:

```powershell
python -m venv .venv
```

Activate the environment on Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

Clone the Alibaba dataset:

```powershell
git clone https://github.com/alibaba/alibaba-cloud-transport-system.git .\data\raw\alibaba-cloud-transport-system
```

## Usage

Verify the dataset:

```powershell
python .\scripts\check_dataset.py
```

Run Phase 2 data exploration:

```powershell
python .\scripts\phase2_explore_data.py
```

Run Phase 3 data cleaning:

```powershell
python .\scripts\phase3_clean_data.py
```

Run the Streamlit dashboard placeholder:

```powershell
python -m streamlit run .\dashboard\app.py
```

## Technical Scope

This project focuses on:

- Public optical transport telemetry analysis
- Pre-FEC BER monitoring
- Optical channel power monitoring
- EDFA telemetry analysis
- Data cleaning and standardization
- KPI calculation
- G.709/OTN-aware interpretation of DWDM transport quality

## Limitations

This project does not use private telecom operator data, internal NMS logs, or confidential DWDM/OTN records.

G.709/OTN is used as an interpretation framework. This project does not decode raw G.709 OPU/ODU/OTU overhead bytes and does not extract real TIM, BDI, PLM, or TCM alarms from the dataset.

## CV Positioning

Suggested CV title:

```text
G.709-Aware Optical Transport Monitoring Dashboard
```

Suggested CV description:

```text
Built a Python-based optical transport monitoring pipeline using the public Alibaba Cloud Transport System Dataset to analyze Pre-FEC BER, optical channel power, EDFA input/output power, gain tilt, and attenuation. Applied ITU-T G.709/OTN concepts to interpret DWDM/OTN transport-channel quality and build a data-driven monitoring workflow.
```

## Keywords

`G.709` `OTN` `DWDM` `Pre-FEC BER` `EDFA` `Optical Channel Monitoring` `Transport Network` `Python` `Streamlit`