# MobiCommand: Micro-Mobility Analytics Platform with Data Engineering

I developed a data engineering and analytics prototype to how IoT telemetry from micro-mobility vehicles can be collected, processed, and served as insights to operators.

---

## What This Project Does

Micro-mobility vehicles generate continuous telemetry such as location, speed, battery level, trip events. This prototype captures all of that, transforms it into structured data, and makes it queryable through a REST API and visual dashboard. Everything runs on GCP.

---

## Live Links

| Component | URL |
|---|---|
| REST API | https://micromobility-api-115910154602.europe-west2.run.app |
| API Docs (Swagger) | https://micromobility-api-115910154602.europe-west2.run.app/docs |
| Dashboard | https://micromobility-platform-mcnel9immepf4cj5gafyax.streamlit.app/ |

---

## Architecture

```
IoT Vehicle Simulator
        |
        v
Google Cloud Storage        <-- raw JSON telemetry files land here
        |
        v
Apache Airflow (Docker)     <-- orchestrates the ELT pipeline on a schedule
        |
        v
BigQuery: raw dataset       <-- raw telemetry loaded as-is
        |
        v
dbt (data build tool)       <-- transforms raw data into clean analytical models
        |
        v
BigQuery: processed dataset <-- staging views + dimensional mart tables
        |
        v
FastAPI (Cloud Run)         <-- REST API serving processed data publicly
        |
        v
Streamlit Dashboard         <-- visual analytics interface for Toyota stakeholders
```

---

## Data Pipeline: Step by Step

### 1. Data Generation
A Python simulator (`data_generator/`) mimics real IoT vehicle behaviour. It generates trip events (trip_start, location_update, trip_end) for 20 vehicles across a configurable time window and uploads them as JSON files to Cloud Storage.

### 2. Orchestration with Airflow
Airflow runs inside Docker and schedules a DAG with three tasks:

| Task | What it does |
|---|---|
| `check_for_files` | Checks Cloud Storage for new telemetry files |
| `load_to_bigquery` | Loads new files into the raw BigQuery dataset |
| `archive_files` | Moves processed files to an archive bucket to prevent reprocessing |

### 3. Transformation with dbt
dbt reads from the raw BigQuery dataset and builds two layers:

**Staging layer (views)**
| Model | Description |
|---|---|
| `stg_vehicle_telemetry` | Cleans and casts raw telemetry columns |

**Marts layer (tables)**
| Model | Description |
|---|---|
| `dim_vehicles` | One row per vehicle with current status and battery |
| `dim_locations` | Deduplicated location coordinates |
| `dim_date` | Date dimension extracted from telemetry timestamps |
| `fct_trips` | One row per trip with duration, speed, and battery metrics |

### 4. API with FastAPI
A FastAPI application deployed to Cloud Run exposes four endpoints:

| Endpoint | Description |
|---|---|
| `GET /vehicles` | All vehicles with current status and battery level |
| `GET /trips` | Recent trip history with full metrics |
| `GET /analytics/summary` | Platform-wide KPIs (total trips, avg speed, avg duration) |
| `GET /analytics/demand` | Trip count grouped by hour of day |

The API authenticates with BigQuery using a GCP service account locally and Cloud Run's built-in identity in production.

### 5. Dashboard with Streamlit
A four-page Streamlit dashboard calls the live API and visualises the data for Toyota stakeholders:

| Page | What it shows |
|---|---|
| Overview | KPI cards and fleet composition chart |
| Fleet Status | Battery distribution histogram and vehicle table |
| Trip History | Full trip log with metrics |
| Demand Analytics | Hourly demand bar chart with peak detection |

---

## Tech Stack

| Category | Tool |
|---|---|
| Cloud Platform | Google Cloud Platform (GCP) |
| Data Warehouse | BigQuery |
| Object Storage | Cloud Storage |
| Orchestration | Apache Airflow |
| Containerisation | Docker |
| Transformation | dbt (data build tool) |
| Dimensional Model | Kimball Star Schema |
| API Framework | FastAPI |
| API Deployment | Cloud Run |
| Dashboard | Streamlit |
| Infrastructure | Terraform |
| Language | Python, SQL |
| Version Control | Git / GitHub |

---

## Project Structure

```
micromobility-platform/
├── api/
│   └── main.py                  # FastAPI application
├── dashboard/
│   ├── app.py                   # Streamlit dashboard
│   └── .streamlit/
│       └── config.toml          # Dark theme config
├── data_generator/
│   └── simulator.py             # IoT vehicle telemetry simulator
├── dags/
│   └── elt_pipeline.py          # Airflow DAG
├── micromobility_dbt/
│   ├── models/
│   │   ├── staging/             # Staging SQL models
│   │   └── marts/               # Dimensional mart models
│   └── dbt_project.yml
├── infrastructure/
│   ├── main.tf                  # Terraform GCP infrastructure
│   └── variables.tf
├── Dockerfile                   # API container definition
├── requirements.txt
└── README.md
```

---

## Data Model

The processed dataset follows Kimball dimensional modelling principles:

```
dim_vehicles ----+
                 |
dim_locations ---+----- fct_trips
                 |
dim_date --------+
```

`fct_trips` is the fact table at the centre. Each trip record links to vehicle, location, and date dimensions. This structure makes it fast and simple to answer questions like "what was the average trip duration for e-scooters on weekday mornings?"

---

## Running Locally

### Prerequisites
- Python 3.11+
- Docker
- GCP service account with BigQuery and Cloud Storage access

### Setup

```bash
git clone https://github.com/lawal2345/micromobility-platform.git
cd micromobility-platform
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Run the Dashboard

```bash
streamlit run dashboard/app.py
```


---

## Author

Jesutofunmi Lawal
Data & AI Engineer