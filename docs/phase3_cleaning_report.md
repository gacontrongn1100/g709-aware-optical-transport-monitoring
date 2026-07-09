# Phase 3 Cleaning Report

This report summarizes the cleaning and standardization outputs generated from the public Alibaba Cloud Transport System Dataset.

## Output Files

| Output File | Rows | Purpose |
|---|---:|---|
| `data/processed/pre_fec_ber_clean.csv` | 28,900 | Clean Pre-FEC BER records |
| `data/processed/och_power_clean.csv` | 267,508 | Clean OCH power records |
| `data/processed/edfa_telemetry_long_clean.csv` | 154,935 | Clean EDFA telemetry in long format |
| `data/processed/edfa_telemetry_wide_clean.csv` | 22,944 | Clean EDFA telemetry in wide format |

## 1. Pre-FEC BER Cleaning

- Raw rows in `performance_elec.csv`: **29,276**
- Rows with `item = preFecBer` before dropping invalid values: **28,900**
- Clean Pre-FEC BER rows: **28,900**
- Dropped rows after filtering invalid time/value: **0**
- Invalid timestamp rows in raw file: **376**

### `item` distribution

| Value | Count |
|---|---:|
| `preFecBer` | 28,900 |
| `nan` | 376 |

### `stats_type` distribution

| Value | Count |
|---|---:|
| `avg` | 10,322 |
| `max` | 10,322 |
| `instant` | 4,128 |
| `min` | 4,128 |
| `nan` | 376 |

### `side` distribution

| Value | Count |
|---|---:|
| `Z` | 14,450 |
| `A` | 14,450 |
| `nan` | 376 |

## 2. OCH Power Cleaning

- Raw rows in `ocm.csv`: **267,508**
- Clean OCH power rows: **267,508**
- Dropped rows after filtering invalid time/frequency/power: **0**
- Invalid timestamp rows in raw file: **0**
- Missing power rows in raw file: **0**

### Top `device_name` values

| Value | Count |
|---|---:|
| `19` | 9,780 |
| `1` | 8,256 |
| `10` | 8,256 |
| `13` | 8,256 |
| `2` | 8,256 |
| `40` | 5,542 |
| `20` | 4,890 |
| `21` | 4,890 |
| `22` | 4,890 |
| `23` | 4,890 |
| `24` | 4,890 |
| `25` | 4,890 |
| `26` | 4,890 |
| `27` | 4,890 |
| `28` | 4,890 |
| `29` | 4,890 |
| `30` | 4,890 |
| `31` | 4,890 |
| `32` | 4,890 |
| `33` | 4,890 |
| `34` | 4,890 |
| `35` | 4,890 |
| `36` | 4,890 |
| `37` | 4,890 |
| `38` | 4,890 |
| `39` | 4,890 |
| `41` | 4,890 |
| `42` | 4,890 |
| `43` | 4,890 |
| `44` | 4,890 |

### Top `logical_name` values

| Value | Count |
|---|---:|
| `/TO_EAST_OCM` | 103,008 |
| `/TO_WEST_OCM` | 103,008 |
| `/D1/OA-W/EGR_OCM` | 19,283 |
| `/D1/OA-W/IGR_OCM` | 19,283 |
| `/D2/OA-W/EGR_OCM` | 11,463 |
| `/D2/OA-W/IGR_OCM` | 11,463 |

## 3. EDFA Telemetry Cleaning

- Raw rows in `performance_optical.csv`: **154,935**
- Clean long-format EDFA rows: **154,935**
- Clean wide-format EDFA rows: **22,944**
- Dropped rows after filtering invalid time/item/stats/value: **0**
- Invalid timestamp rows in raw file: **0**
- Missing measurement value rows in raw file: **0**

### `item` distribution

| Value | Count |
|---|---:|
| `outputTPM` | 77,469 |
| `inputTPM` | 77,466 |

### `stats_type` distribution

| Value | Count |
|---|---:|
| `min` | 51,645 |
| `max` | 51,645 |
| `avg` | 48,893 |
| `instant` | 2,752 |

### `pn` distribution

| Value | Count |
|---|---:|
| `EDFA3` | 75,843 |
| `EDFA2` | 70,836 |
| `EDFA1` | 8,256 |

## Technical Note

The cleaned datasets are derived directly from the public Alibaba dataset. No private operator data is used, and no synthetic optical telemetry is fabricated.

The cleaned data will be used in Phase 4 for KPI calculation, including Pre-FEC BER behavior, OCH power distribution, EDFA gain/tilt/attenuation analysis and G.709-aware transport health interpretation.
