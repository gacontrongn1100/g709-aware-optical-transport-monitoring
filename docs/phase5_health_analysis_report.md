# Phase 5 Health Analysis Report

This report summarizes rule-based health analysis built from Phase 4 KPI outputs.

The analysis uses data-driven KPI status values from the public Alibaba optical transport telemetry dataset. It does not use private NMS alarm logic or vendor-specific thresholds.

## Output Files

| Output File | Rows | Purpose |
|---|---:|---|
| `data/processed/channel_health_analysis.csv` | 50 | Channel/transponder-level health analysis |
| `data/processed/frequency_health_analysis.csv` | 42 | Frequency-level health analysis |
| `data/processed/device_health_analysis.csv` | 53 | Device-level optical health analysis |
| `data/processed/high_risk_recommendations.csv` | 89 | Prioritized warning/critical objects |

## 1. Channel Health

### Overall Status Distribution

| Status | Count |
|---|---:|
| `Normal` | 32 |
| `Warning` | 14 |
| `Critical` | 4 |

### Priority Distribution

| Priority | Count |
|---|---:|
| `P3` | 32 |
| `P2` | 14 |
| `P1` | 4 |

## 2. Frequency Health

### Frequency Status Distribution

| Status | Count |
|---|---:|
| `Normal` | 21 |
| `Warning` | 13 |
| `Critical` | 8 |

### Frequency Priority Distribution

| Priority | Count |
|---|---:|
| `P3` | 21 |
| `P2` | 13 |
| `P1` | 8 |

## 3. Device Health

### Device Status Distribution

| Status | Count |
|---|---:|
| `Critical` | 26 |
| `Warning` | 24 |
| `Normal` | 3 |

### Device Priority Distribution

| Priority | Count |
|---|---:|
| `P1` | 26 |
| `P2` | 24 |
| `P3` | 3 |

## 4. High-Risk Recommendations

- Total high-risk objects: **89**

### High-Risk Source Distribution

| Status | Count |
|---|---:|
| `device` | 50 |
| `frequency` | 21 |
| `channel` | 18 |

### High-Risk Priority Distribution

| Priority | Count |
|---|---:|
| `P2` | 51 |
| `P1` | 38 |

## Rule Logic

| Input Condition | Interpretation |
|---|---|
| Critical Pre-FEC BER + critical frequency status | Possible optical transport degradation affecting the channel/frequency |
| Critical Pre-FEC BER + normal frequency status | Possible transponder-side or non-power optical impairment |
| Critical OCH power behavior | Possible optical power degradation, channel equalization issue or physical path issue |
| Critical EDFA behavior | Possible amplifier gain, tilt, attenuation or span issue |
| Warning status | Early degradation indicator requiring trend monitoring |

## G.709/OTN Interpretation

Pre-FEC BER is interpreted as a transport-channel quality indicator before FEC correction. OCH power and EDFA telemetry provide optical-layer context for investigating BER degradation.

This supports a G.709-aware troubleshooting workflow without claiming to decode raw G.709 overhead or extract real TIM/BDI/PLM/TCM alarms.

## Limitation

The health analysis is based on public telemetry and percentile-based KPI status values. It is intended for learning, portfolio demonstration and analysis workflow design, not production NOC deployment.
