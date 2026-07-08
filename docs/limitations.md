# Project Limitations

This project uses the public Alibaba Cloud Transport System Dataset.

It does not use any private telecom operator data, internal NMS logs or confidential DWDM/OTN records.

## Important Limitations

1. The dataset is not a raw ITU-T G.709 overhead dataset.
2. The project does not decode OPU, ODU or OTU overhead bytes.
3. The dataset does not provide real operator alarms such as TIM, BDI, PLM or TCM defects.
4. The analysis is based on public optical transport telemetry, including Pre-FEC BER, optical channel power and EDFA-related metrics.
5. ITU-T G.709/OTN concepts are used as the technical interpretation framework, not as a claim that all G.709 fields are directly available in the dataset.
6. Health classification rules are based on dataset statistics such as percentiles, not on vendor-specific thresholds.
7. The dashboard is designed for learning, analysis and CV demonstration, not for production NOC operation.

## Correct Positioning

Correct:

> This project applies G.709/OTN concepts to interpret public optical transport telemetry.

Incorrect:

> This project extracts real G.709 TIM, BDI, PLM and TCM alarms from Alibaba's dataset.
