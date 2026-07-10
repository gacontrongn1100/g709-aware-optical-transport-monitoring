# G.709-Aware Optical Transport Monitoring Dashboard

A Python-based optical transport monitoring project using public DWDM/OTN telemetry from the Alibaba Cloud Transport System Dataset.

The project analyzes Pre-FEC BER, optical channel power, EDFA telemetry, gain tilt and attenuation, then presents channel, frequency and device health through a Streamlit dashboard.

## Overview

This project provides an end-to-end monitoring workflow for optical transport telemetry:

1. Verify raw dataset files
2. Explore and profile telemetry data
3. Clean and standardize optical transport records
4. Calculate transport KPIs
5. Build rule-based health analysis
6. Visualize results in a Streamlit dashboard

The analysis uses ITU-T G.709/OTN concepts as the technical interpretation framework.

## Dataset

Primary public dataset:

- Alibaba Cloud Transport System Dataset

Main input files:

| File | Purpose |
|---|---|
| `performance_elec.csv` | Pre-FEC BER and electrical-side performance |
| `ocm.csv` | Optical channel power and center frequency |
| `performance_optical.csv` | EDFA and optical performance telemetry |

Local dataset path:

```text
data/raw/alibaba-cloud-transport-system/
```

Raw and processed data are not committed to this repository.

## Main Features

- Public optical transport telemetry analysis
- Pre-FEC BER KPI calculation
- Optical channel power monitoring
- EDFA gain and gain tilt analysis
- Frequency-level health summary
- Device-level optical health analysis
- Rule-based high-risk recommendation table
- Streamlit dashboard with interactive filtering
- G.709/OTN-aware interpretation notes

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
│   ├── phase3_cleaning_report.md
│   ├── phase4_kpi_report.md
│   ├── phase5_health_analysis_report.md
│   ├── phase6_dashboard_report.md
│   ├── phase7_final_packaging_report.md
│   ├── project_summary.md
│   └── runbook.md
├── notebooks/
├── screenshots/
├── scripts/
│   ├── check_dataset.py
│   ├── phase2_explore_data.py
│   ├── phase3_clean_data.py
│   ├── phase4_calculate_kpi.py
│   └── phase5_health_analysis.py
├── src/
├── .gitignore
├── README.md
└── requirements.txt
```

## Current Status

| Phase | Description | Status |
|---|---|---|
| Phase 1 | Dataset verification | Completed |
| Phase 2 | Data exploration | Completed |
| Phase 3 | Data cleaning and standardization | Completed |
| Phase 4 | KPI calculation | Completed |
| Phase 5 | Rule-based health analysis | Completed |
| Phase 6 | Streamlit dashboard | Completed |
| Phase 7 | Final documentation and packaging | Completed |

## Setup

### 1. Clone this repository

```powershell
git clone <repository-url>
cd g709-aware-optical-transport-monitoring
```

### 2. Create virtual environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```powershell
python -m pip install -r requirements.txt
```

### 4. Clone the public dataset

```powershell
git clone https://github.com/alibaba/alibaba-cloud-transport-system.git .\data\raw\alibaba-cloud-transport-system
```

## Usage

Run each phase in order.

### Verify dataset

```powershell
python .\scripts\check_dataset.py
```

### Explore data

```powershell
python .\scripts\phase2_explore_data.py
```

### Clean data

```powershell
python .\scripts\phase3_clean_data.py
```

### Calculate KPIs

```powershell
python .\scripts\phase4_calculate_kpi.py
```

### Run health analysis

```powershell
python .\scripts\phase5_health_analysis.py
```

### Launch dashboard

```powershell
python -m streamlit run .\dashboard\app.py
```

Open in browser:

```text
http://localhost:8501
```

## Dashboard Pages

The Streamlit dashboard includes:

- Overview
- High-Risk Recommendations
- Channel Health
- Frequency Health
- Device Health
- Pre-FEC BER KPI
- OCH Power KPI
- EDFA KPI
- G.709 / OTN Notes

## Generated Outputs

### Cleaned Data

| Output File | Purpose |
|---|---|
| `pre_fec_ber_clean.csv` | Clean Pre-FEC BER records |
| `och_power_clean.csv` | Clean optical channel power records |
| `edfa_telemetry_long_clean.csv` | EDFA telemetry in long format |
| `edfa_telemetry_wide_clean.csv` | EDFA telemetry in wide format |

### KPI Data

| Output File | Purpose |
|---|---|
| `pre_fec_ber_kpi.csv` | Pre-FEC BER KPI by channel |
| `och_power_kpi.csv` | OCH power KPI by channel |
| `edfa_kpi.csv` | EDFA KPI by amplifier/logical component |
| `frequency_health_summary.csv` | Frequency-level health summary |

### Health Analysis

| Output File | Purpose |
|---|---|
| `channel_health_analysis.csv` | Channel/transponder-level health analysis |
| `frequency_health_analysis.csv` | Frequency-level health analysis |
| `device_health_analysis.csv` | Device-level optical health analysis |
| `high_risk_recommendations.csv` | Prioritized warning/critical objects |

## Technical Interpretation

This project uses G.709/OTN concepts to interpret optical transport quality.

| Telemetry Signal | Interpretation |
|---|---|
| Pre-FEC BER | Transport-channel quality before FEC correction |
| OCH power | Optical channel power behavior |
| Center frequency | DWDM frequency/channel dimension |
| EDFA gain | Amplifier behavior |
| EDFA gain tilt | Gain profile imbalance indicator |
| Attenuation | Optical section attenuation context |

The dashboard correlates Pre-FEC BER, OCH power and EDFA behavior to support a structured optical transport troubleshooting workflow.

## Limitations

This project uses public telemetry data only.

It does not use private operator data, internal NMS logs, vendor-specific thresholds or confidential network records.

G.709/OTN is used as an interpretation framework. The project does not decode raw G.709 OPU/ODU/OTU overhead bytes and does not extract real TIM, BDI, PLM or TCM alarms.

## Requirements

Main Python packages:

```text
pandas
numpy
streamlit
plotly
tabulate
```

## Documentation

| Document | Purpose |
|---|---|
| `docs/project_summary.md` | Project overview |
| `docs/runbook.md` | Local execution guide |
| `docs/phase2_findings.md` | Data exploration findings |
| `docs/phase3_cleaning_report.md` | Data cleaning report |
| `docs/phase4_kpi_report.md` | KPI calculation report |
| `docs/phase5_health_analysis_report.md` | Health analysis report |
| `docs/phase6_dashboard_report.md` | Dashboard report |
| `docs/phase7_final_packaging_report.md` | Final packaging report |

## Keywords

`G.709` `OTN` `DWDM` `Pre-FEC BER` `EDFA` `Optical Channel Monitoring` `Transport Network Monitoring` `Python` `pandas` `Streamlit` `Plotly`