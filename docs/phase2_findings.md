# Phase 2 Findings

## Confirmed Dataset Files

| File | Rows | Columns | Main Use |
|---|---:|---:|---|
| `performance_optical.csv` | 154,935 | 10 | EDFA / optical performance |
| `ocm.csv` | 267,508 | 6 | Optical channel power |
| `performance_elec.csv` | 29,276 | 11 | Pre-FEC BER / transponder performance |

## Key Observations

1. The dataset provides real public optical transport telemetry suitable for DWDM/OTN monitoring analysis.
2. `performance_elec.csv` contains the `item` field and the observed sample from Phase 1 shows `preFecBer`, which is directly relevant to FEC-related channel quality monitoring.
3. `ocm.csv` contains optical channel power and center frequency, useful for OCH power monitoring.
4. `performance_optical.csv` contains EDFA-related fields such as gain, gain tilt and attenuation.
5. The dataset does not expose raw G.709 OPU/ODU/OTU overhead bytes, so G.709 is used as an interpretation framework, not as raw decoded overhead data.

## Next Phase

Phase 3 will clean and standardize the three datasets:

- Parse and validate timestamps.
- Filter Pre-FEC BER records from `performance_elec.csv`.
- Prepare OCH power records from `ocm.csv`.
- Prepare EDFA telemetry records from `performance_optical.csv`.
- Export clean processed CSV files for KPI calculation.
