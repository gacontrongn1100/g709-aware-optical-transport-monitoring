# Phase 4 KPI Report

This report summarizes KPI calculation outputs generated from the cleaned Alibaba optical transport telemetry dataset.

All health thresholds in this phase are data-driven percentile thresholds derived from the public dataset. No vendor-specific thresholds are assumed.

## Output Files

| Output File | Rows | Purpose |
|---|---:|---|
| `data/processed/pre_fec_ber_kpi.csv` | 50 | Pre-FEC BER KPI by channel |
| `data/processed/och_power_kpi.csv` | 1,348 | OCH power KPI by channel |
| `data/processed/edfa_kpi.csv` | 103 | EDFA KPI by amplifier/logical component |
| `data/processed/frequency_health_summary.csv` | 42 | Frequency-level health summary |

## 1. Pre-FEC BER KPI

- Clean input rows: **28,900**
- Rows used for KPI calculation: **14,450**
- KPI channel rows: **50**
- BER P90 threshold: `0.0034829`
- BER P99 threshold: `0.00438882`

### BER Status Distribution

| Status | Count |
|---|---:|
| `Normal` | 45 |
| `Warning` | 4 |
| `Critical` | 1 |

## 2. OCH Power KPI

- Clean input rows: **267,508**
- KPI channel rows: **1,348**
- Power range P90 threshold: `2.2583252801999976`
- Power range P99 threshold: `5.91952512661`
- Low power P10 threshold: `1.8347211613`
- Low power P01 threshold: `-0.61529999947`

### OCH Power Status Distribution

| Status | Count |
|---|---:|
| `Normal` | 1,095 |
| `Warning` | 225 |
| `Critical` | 28 |

## 3. EDFA KPI

- Clean input rows: **22,944**
- KPI EDFA rows: **103**
- Gain tilt absolute P90 threshold: `1.5`
- Gain tilt absolute P99 threshold: `1.7`
- Attenuation P90 threshold: `5.442993865030674`
- Attenuation P99 threshold: `11.706040490797559`

### EDFA Status Distribution

| Status | Count |
|---|---:|
| `Normal` | 79 |
| `Warning` | 17 |
| `Critical` | 7 |

## 4. Frequency Health Summary

- Frequency rows: **42**

### Frequency Status Distribution

| Status | Count |
|---|---:|
| `Normal` | 21 |
| `Warning` | 13 |
| `Critical` | 8 |

## G.709/OTN Interpretation

Pre-FEC BER is relevant to OTN/DWDM transport monitoring because it reflects bit error behavior before FEC correction. In this project, high Pre-FEC BER is interpreted as a transport-channel degradation indicator, not as a direct extraction of raw G.709 overhead.

OCH power and EDFA telemetry provide optical-layer context that helps explain BER degradation. This supports a G.709-aware troubleshooting workflow: correlate transponder-side Pre-FEC BER with optical channel power and amplifier behavior.

## Limitation

The KPI outputs are calculated from public telemetry data. They do not represent vendor-specific alarm thresholds or private operator NMS logic.
