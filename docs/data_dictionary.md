# Data Dictionary

This document is generated in Phase 2 based on the actual columns found in the public Alibaba Cloud Transport System Dataset.

The project uses three primary CSV files:

1. `performance_optical.csv`
2. `ocm.csv`
3. `performance_elec.csv`

---

## 1. `performance_optical.csv`

Observed shape from Phase 1:

- Rows: 154,935
- Columns: 10

Observed columns:

| Column | Initial Meaning in This Project |
|---|---|
| `device_name` | Optical device identifier |
| `logical_name` | Logical component or interface name |
| `item` | Measured optical performance item, for example input/output optical power |
| `stats_type` | Statistical type of the measurement, for example avg/min/max if present |
| `value` | Measurement value |
| `actual_gain` | Actual EDFA gain |
| `actual_gain_tilt` | EDFA gain tilt |
| `pn` | Equipment/card/module identifier |
| `attenuation` | Attenuation value |
| `time` | Timestamp of the measurement |

Planned use:

- EDFA input/output power analysis
- Gain and gain tilt analysis
- Attenuation analysis
- Optical section health interpretation

---

## 2. `ocm.csv`

Observed shape from Phase 1:

- Rows: 267,508
- Columns: 6

Observed columns:

| Column | Initial Meaning in This Project |
|---|---|
| `device_name` | Optical device identifier |
| `logical_name` | Logical OCM component/interface name |
| `online_channel_num` | Online optical channel number |
| `center_frequency` | Optical channel center frequency |
| `power` | Optical channel power |
| `time` | Timestamp of the measurement |

Planned use:

- OCH power monitoring
- Channel power distribution
- Power drift analysis
- Channel flatness analysis

---

## 3. `performance_elec.csv`

Observed shape from Phase 1:

- Rows: 29,276
- Columns: 11

Observed columns:

| Column | Initial Meaning in This Project |
|---|---|
| `device_name` | Transponder or terminal device identifier |
| `logical_name` | Logical transponder/client/line interface name |
| `item` | Electrical/transponder-side performance item |
| `stats_type` | Statistical type of the measurement |
| `value` | Measurement value, used for Pre-FEC BER when `item = preFecBer` |
| `och` | Optical channel identifier |
| `center_frequency` | Optical channel center frequency |
| `och_group` | Optical channel group |
| `time` | Timestamp of the measurement |
| `side` | Direction or side of the optical channel, for example A/Z |
| `pn` | Equipment/card/module identifier |

Planned use:

- Pre-FEC BER analysis
- A/Z side comparison
- Transponder-side channel health monitoring
- G.709/OTN-aware FEC degradation interpretation

---

## Important Note

This data dictionary documents observed dataset columns. It does not claim that the dataset contains full raw G.709 OPU/ODU/OTU overhead fields or real NMS alarms such as TIM, BDI, PLM or TCM defects.
