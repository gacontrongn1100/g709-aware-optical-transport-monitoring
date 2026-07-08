# Data Source

## Primary Dataset

Alibaba Cloud Transport System Dataset

## Dataset Role in This Project

The dataset is used as the primary source of optical transport telemetry. It contains data related to optical transport network performance estimation, including optical-layer and electrical/transponder-side performance records.

## Expected Data Files

The project will focus on the following CSV files:

1. `performance_optical.csv`
   - EDFA-related optical performance data
   - Input/output optical power
   - Gain
   - Tilt
   - Attenuation
   - Time-based statistics

2. `ocm.csv`
   - Optical Channel Monitor data
   - Online channel information
   - Center frequency
   - Channel power
   - Time

3. `performance_elec.csv`
   - Transponder or optical terminal performance data
   - Pre-FEC BER
   - OCH group
   - Center frequency
   - Side A/Z
   - Time-based statistics

## Data Usage Principle

This project will not fabricate optical transport data.

Any derived KPI must be calculated from the public dataset or clearly marked as an analytical feature derived from the dataset.
