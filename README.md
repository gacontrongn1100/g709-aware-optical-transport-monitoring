# G.709-Aware Optical Transport Monitoring

> An end-to-end Python workflow for analyzing public DWDM/OTN telemetry and presenting transport-health insights in an interactive Streamlit dashboard.

[English](#english) · [Tiếng Việt](#tiếng-việt)

---

## English

### Overview

This project analyzes public optical transport telemetry from the Alibaba Cloud Transport System Dataset. It processes Pre-FEC BER, optical channel monitor (OCM) power, and EDFA telemetry, then produces channel-, frequency-, and device-level health assessments through a Streamlit dashboard.

ITU-T G.709/OTN concepts are used as a technical interpretation framework. The project does **not** decode raw OPU/ODU/OTU overhead bytes and does not claim to extract real TIM, BDI, PLM, or TCM alarms.

### Who is this for?

- Network and transmission engineers exploring optical telemetry analytics
- Data analysts learning how to build a reproducible monitoring pipeline
- Students and researchers studying DWDM, OTN, Pre-FEC BER, or EDFA behavior
- Recruiters and reviewers evaluating a practical Python network-engineering project

### Key capabilities

- Validate the required public dataset files
- Profile and document the source telemetry
- Clean and standardize optical transport records
- Calculate data-driven Pre-FEC BER, OCH power, and EDFA KPIs
- Classify channel, frequency, and device health using percentile-based rules
- Generate prioritized warning and critical recommendations
- Explore results through nine interactive Streamlit views
- Correlate transport-channel quality with optical-layer context

### Architecture and workflow

```text
Public Alibaba telemetry
        │
        ▼
Dataset validation
        │
        ▼
Exploration and profiling
        │
        ▼
Cleaning and standardization
        │
        ▼
KPI calculation
        │
        ▼
Rule-based health analysis
        │
        ▼
Streamlit dashboard
```

The workflow uses three primary input files:

| File | Main use |
|---|---|
| `performance_elec.csv` | Pre-FEC BER and transponder-side performance |
| `ocm.csv` | Optical channel power and center frequency |
| `performance_optical.csv` | EDFA input/output power, gain, tilt, and attenuation |

### Project structure

```text
g709-aware-optical-transport-monitoring/
├── dashboard/
│   └── app.py
├── data/
│   ├── raw/                 # Public source dataset (not committed)
│   └── processed/           # Generated datasets (not committed)
├── docs/                    # Scope, data, limitations, and phase reports
├── notebooks/               # Exploration notebook area
├── scripts/
│   ├── check_dataset.py
│   ├── phase2_explore_data.py
│   ├── phase3_clean_data.py
│   ├── phase4_calculate_kpi.py
│   └── phase5_health_analysis.py
├── src/
├── requirements.txt
└── README.md
```

### Quick start

#### Prerequisites

- Python 3 with `venv` support
- Git
- Enough local storage for the public dataset and generated CSV files

The commands below use PowerShell. Equivalent commands can be used on Linux or macOS.

#### 1. Clone the project

```powershell
git clone https://github.com/gacontrongn1100/g709-aware-optical-transport-monitoring.git
cd g709-aware-optical-transport-monitoring
```

#### 2. Create and activate a virtual environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

#### 3. Download the public dataset

```powershell
git clone https://github.com/alibaba/alibaba-cloud-transport-system.git .\data\raw\alibaba-cloud-transport-system
```

Expected dataset location:

```text
data/raw/alibaba-cloud-transport-system/data/
```

#### 4. Run the pipeline in order

```powershell
python .\scripts\check_dataset.py
python .\scripts\phase2_explore_data.py
python .\scripts\phase3_clean_data.py
python .\scripts\phase4_calculate_kpi.py
python .\scripts\phase5_health_analysis.py
```

#### 5. Start the dashboard

```powershell
python -m streamlit run .\dashboard\app.py
```

Open `http://localhost:8501` in a browser.

### Dashboard views

| View | Purpose |
|---|---|
| Overview | Summary of health results and core indicators |
| High-Risk Recommendations | Prioritized warning and critical objects |
| Channel Health | Channel/transponder-level analysis |
| Frequency Health | Center-frequency-level analysis |
| Device Health | Optical-device-level analysis |
| Pre-FEC BER KPI | Pre-FEC BER distribution and status |
| OCH Power KPI | Optical channel power behavior |
| EDFA KPI | Amplifier gain, tilt, and attenuation behavior |
| G.709 / OTN Notes | Interpretation scope and technical context |

### Generated outputs

All generated CSV files are written to `data/processed/`.

| Stage | Outputs |
|---|---|
| Cleaned data | `pre_fec_ber_clean.csv`, `och_power_clean.csv`, `edfa_telemetry_long_clean.csv`, `edfa_telemetry_wide_clean.csv` |
| KPI data | `pre_fec_ber_kpi.csv`, `och_power_kpi.csv`, `edfa_kpi.csv`, `frequency_health_summary.csv` |
| Health analysis | `channel_health_analysis.csv`, `frequency_health_analysis.csv`, `device_health_analysis.csv`, `high_risk_recommendations.csv` |

### Health-model interpretation

The health model uses thresholds derived from the dataset's percentile distributions. It does not use undisclosed vendor thresholds or private operator alarm logic.

| Signal | Interpretation in this project |
|---|---|
| Pre-FEC BER | Transport-channel quality before FEC correction |
| OCH power | Optical channel power level and variation |
| Center frequency | DWDM frequency/channel dimension |
| EDFA gain | Amplifier behavior |
| EDFA gain tilt | Gain-profile imbalance indicator |
| Attenuation | Optical section attenuation context |

### Documentation

- [Project scope](docs/project_scope.md)
- [Data source](docs/data_source.md)
- [Data dictionary](docs/data_dictionary.md)
- [Known limitations](docs/limitations.md)
- [Phase 2 findings](docs/phase2_findings.md)
- [Phase 3 cleaning report](docs/phase3_cleaning_report.md)
- [Phase 4 KPI report](docs/phase4_kpi_report.md)
- [Phase 5 health-analysis report](docs/phase5_health_analysis_report.md)

### Limitations and responsible use

- The project uses public, historical telemetry; it is not connected to a live network.
- Health statuses are data-driven analytical labels, not production NOC alarms.
- Results are not based on vendor-specific engineering limits.
- The dataset does not expose raw G.709 overhead bytes.
- The project is intended for learning, portfolio demonstration, and workflow design—not direct production deployment without validation.

### Technology stack

Python, pandas, NumPy, Streamlit, Plotly, Matplotlib, scikit-learn, PyArrow, Jupyter, and tabulate.

---

## Tiếng Việt

### Tổng quan

Dự án phân tích dữ liệu giám sát truyền dẫn quang công khai từ Alibaba Cloud Transport System Dataset. Hệ thống xử lý Pre-FEC BER, công suất kênh quang từ OCM và telemetry EDFA, sau đó đánh giá sức khỏe theo cấp kênh, tần số và thiết bị thông qua dashboard Streamlit.

Các khái niệm ITU-T G.709/OTN được sử dụng làm khung diễn giải kỹ thuật. Dự án **không** giải mã trực tiếp byte overhead OPU/ODU/OTU và không tuyên bố trích xuất các cảnh báo TIM, BDI, PLM hoặc TCM thực tế.

### Dự án phù hợp với ai?

- Kỹ sư truyền dẫn và kỹ sư mạng muốn tìm hiểu phân tích telemetry quang
- Chuyên viên dữ liệu muốn xây dựng pipeline giám sát có thể tái lập
- Sinh viên và nhà nghiên cứu về DWDM, OTN, Pre-FEC BER hoặc EDFA
- Nhà tuyển dụng và người đánh giá dự án Python ứng dụng trong kỹ thuật mạng

### Khả năng chính

- Kiểm tra sự hiện diện và cấu trúc của các tệp dữ liệu nguồn
- Khảo sát, lập hồ sơ và tài liệu hóa telemetry
- Làm sạch và chuẩn hóa bản ghi truyền dẫn quang
- Tính KPI Pre-FEC BER, công suất OCH và EDFA dựa trên dữ liệu
- Phân loại sức khỏe kênh, tần số và thiết bị bằng quy tắc percentile
- Sinh danh sách khuyến nghị Warning/Critical theo mức ưu tiên
- Khám phá kết quả qua chín màn hình Streamlit tương tác
- Liên hệ chất lượng kênh truyền dẫn với trạng thái lớp quang

### Kiến trúc và quy trình

```text
Telemetry công khai từ Alibaba
        │
        ▼
Kiểm tra dataset
        │
        ▼
Khảo sát và lập hồ sơ dữ liệu
        │
        ▼
Làm sạch và chuẩn hóa
        │
        ▼
Tính toán KPI
        │
        ▼
Phân tích sức khỏe theo quy tắc
        │
        ▼
Dashboard Streamlit
```

Ba tệp đầu vào chính:

| Tệp | Mục đích chính |
|---|---|
| `performance_elec.csv` | Pre-FEC BER và hiệu năng phía transponder |
| `ocm.csv` | Công suất kênh quang và tần số trung tâm |
| `performance_optical.csv` | Công suất vào/ra, gain, tilt và suy hao EDFA |

### Cấu trúc dự án

```text
g709-aware-optical-transport-monitoring/
├── dashboard/               # Ứng dụng Streamlit
├── data/
│   ├── raw/                 # Dataset công khai, không commit
│   └── processed/           # Dữ liệu sinh ra, không commit
├── docs/                    # Phạm vi, dữ liệu, giới hạn và báo cáo
├── notebooks/               # Khu vực notebook khảo sát
├── scripts/                 # Pipeline xử lý theo từng giai đoạn
├── src/
├── requirements.txt
└── README.md
```

### Cài đặt nhanh

#### Yêu cầu môi trường

- Python 3 có hỗ trợ `venv`
- Git
- Đủ dung lượng lưu dataset công khai và các tệp CSV được sinh ra

Các lệnh dưới đây sử dụng PowerShell. Người dùng Linux hoặc macOS có thể dùng lệnh tương đương.

#### 1. Clone dự án

```powershell
git clone https://github.com/gacontrongn1100/g709-aware-optical-transport-monitoring.git
cd g709-aware-optical-transport-monitoring
```

#### 2. Tạo môi trường ảo và cài thư viện

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

#### 3. Tải dataset công khai

```powershell
git clone https://github.com/alibaba/alibaba-cloud-transport-system.git .\data\raw\alibaba-cloud-transport-system
```

Vị trí dữ liệu mong đợi:

```text
data/raw/alibaba-cloud-transport-system/data/
```

#### 4. Chạy pipeline theo đúng thứ tự

```powershell
python .\scripts\check_dataset.py
python .\scripts\phase2_explore_data.py
python .\scripts\phase3_clean_data.py
python .\scripts\phase4_calculate_kpi.py
python .\scripts\phase5_health_analysis.py
```

#### 5. Khởi động dashboard

```powershell
python -m streamlit run .\dashboard\app.py
```

Mở `http://localhost:8501` trên trình duyệt.

### Các màn hình dashboard

| Màn hình | Chức năng |
|---|---|
| Overview | Tổng quan kết quả sức khỏe và chỉ số chính |
| High-Risk Recommendations | Các đối tượng Warning/Critical theo mức ưu tiên |
| Channel Health | Phân tích theo kênh/transponder |
| Frequency Health | Phân tích theo tần số trung tâm |
| Device Health | Phân tích theo thiết bị quang |
| Pre-FEC BER KPI | Phân bố và trạng thái Pre-FEC BER |
| OCH Power KPI | Hành vi công suất kênh quang |
| EDFA KPI | Gain, tilt và suy hao bộ khuếch đại |
| G.709 / OTN Notes | Phạm vi diễn giải và ngữ cảnh kỹ thuật |

### Dữ liệu đầu ra

Tất cả tệp CSV được sinh vào `data/processed/`.

| Giai đoạn | Tệp đầu ra |
|---|---|
| Dữ liệu sạch | `pre_fec_ber_clean.csv`, `och_power_clean.csv`, `edfa_telemetry_long_clean.csv`, `edfa_telemetry_wide_clean.csv` |
| KPI | `pre_fec_ber_kpi.csv`, `och_power_kpi.csv`, `edfa_kpi.csv`, `frequency_health_summary.csv` |
| Phân tích sức khỏe | `channel_health_analysis.csv`, `frequency_health_analysis.csv`, `device_health_analysis.csv`, `high_risk_recommendations.csv` |

### Cách diễn giải mô hình sức khỏe

Mô hình sử dụng các ngưỡng được suy ra từ phân bố percentile của dataset. Dự án không sử dụng ngưỡng bí mật của nhà cung cấp hoặc logic cảnh báo nội bộ của nhà khai thác.

| Tín hiệu | Cách diễn giải trong dự án |
|---|---|
| Pre-FEC BER | Chất lượng kênh truyền dẫn trước khi FEC sửa lỗi |
| Công suất OCH | Mức và độ biến thiên công suất kênh quang |
| Tần số trung tâm | Chiều phân tích tần số/kênh DWDM |
| EDFA gain | Hoạt động khuếch đại |
| EDFA gain tilt | Chỉ báo mất cân bằng phổ gain |
| Attenuation | Ngữ cảnh suy hao đoạn quang |

### Tài liệu

- [Phạm vi dự án](docs/project_scope.md)
- [Nguồn dữ liệu](docs/data_source.md)
- [Từ điển dữ liệu](docs/data_dictionary.md)
- [Các giới hạn đã biết](docs/limitations.md)
- [Kết quả khảo sát Phase 2](docs/phase2_findings.md)
- [Báo cáo làm sạch Phase 3](docs/phase3_cleaning_report.md)
- [Báo cáo KPI Phase 4](docs/phase4_kpi_report.md)
- [Báo cáo phân tích sức khỏe Phase 5](docs/phase5_health_analysis_report.md)

### Giới hạn và cách sử dụng phù hợp

- Dự án dùng telemetry lịch sử công khai, không kết nối mạng đang vận hành.
- Các trạng thái sức khỏe là nhãn phân tích dựa trên dữ liệu, không phải cảnh báo NOC thực tế.
- Kết quả không dựa trên giới hạn kỹ thuật riêng của nhà cung cấp thiết bị.
- Dataset không cung cấp byte overhead G.709 thô.
- Dự án phục vụ học tập, trình bày năng lực và thiết kế quy trình; cần được kiểm chứng thêm trước khi áp dụng vào production.

### Công nghệ sử dụng

Python, pandas, NumPy, Streamlit, Plotly, Matplotlib, scikit-learn, PyArrow, Jupyter và tabulate.

---

## License and data attribution / Giấy phép và ghi nhận dữ liệu

This repository does not currently include a project license file. Review the upstream dataset repository and its terms before redistributing source data or using the project beyond evaluation and learning.

Repository này hiện chưa có tệp giấy phép riêng. Hãy kiểm tra repository dataset nguồn và các điều khoản liên quan trước khi phân phối lại dữ liệu hoặc sử dụng dự án ngoài mục đích đánh giá và học tập.

- Dataset source / Nguồn dataset: [Alibaba Cloud Transport System Dataset](https://github.com/alibaba/alibaba-cloud-transport-system)
- Project repository / Repository dự án: [g709-aware-optical-transport-monitoring](https://github.com/gacontrongn1100/g709-aware-optical-transport-monitoring)

## Keywords

`G.709` · `OTN` · `DWDM` · `Pre-FEC BER` · `EDFA` · `OCM` · `Optical Transport Monitoring` · `Python` · `pandas` · `Streamlit` · `Plotly`
