# Weather Update Pipeline

An asynchronous ETL pipeline that fetches real-time weather data for multiple cities on a scheduled interval, storing it across three layers: raw JSON, processed Parquet, and a PostgreSQL database.

## Overview

The pipeline runs every 15 minutes and collects current weather conditions from the [Open-Meteo API](https://open-meteo.com/) for 6 cities:

| City | Coordinates |
|------|-------------|
| Toronto, CA | 43.6532, -79.3832 |
| Tehran, IR | 35.6892, 51.3890 |
| Los Angeles, US | 34.0522, -118.2437 |
| Vancouver, CA | 49.2827, -123.1207 |
| Montreal, CA | 45.5017, -73.5673 |
| New York, US | 40.7128, -74.0060 |

## Architecture

```
main.py
└── run_pipeline()
    ├── extract.py   → fetch_multiple_locations()          # concurrent async HTTP via httpx
    ├── load.py      → load_raw_data()                     # bronze: raw JSON
    ├── transform.py → extract_json(), create_dataframe()  # parse + Polars DataFrame
    ├── load.py      → load_parquet()                      # silver: processed Parquet
    └── load.py      → insert_db()                         # gold: PostgreSQL
```

### Data fields collected

`temperature`, `humidity`, `feels_like`, `is_day`, `precipitation`, `cloud_cover`, `wind_speed`, `weather_code` (WMO description), `latitude`, `longitude`, `timezone`, `time`

## Storage Layout

```
data/
├── raw/
│   └── date=YYYY-MM-DD/
│       └── hour=H/
│           └── weather.json       # raw API responses, deduplicated
└── processed/
    └── date=YYYY-MM-DD/
        └── hour=H/
            └── weather.parquet    # typed Polars DataFrame, deduplicated
```

Both raw and processed data are partitioned by date and hour. The PostgreSQL gold layer stores normalized data across two tables:

- **`geo_table`** — unique locations (latitude, longitude, timezone)
- **`weather_measures`** — weather readings linked to a location via foreign key

## Setup

### Local

**Requirements:** Python 3.13+

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and fill in your database credentials:

```
DB_NAME=weather_db
DB_USER=postgres
DB_PASS=yourpassword
DB_PORT=5432
DB_HOST=localhost
```

```bash
python main.py
```

### Docker

```bash
docker compose up -d
```

This starts both the pipeline and a PostgreSQL container. The database schema is applied automatically on first run. Logs and data are persisted via volumes.

### Deploying to a VPS

```bash
# install Docker
sudo apt install docker.io docker-compose-plugin -y

# clone and configure
git clone <your-repo> && cd weather-update
cp .env.example .env  # fill in real values

# run
docker compose up -d

# follow logs
docker compose logs -f pipeline
```

## Configuration

`config.py` exposes two constants:

| Variable | Default | Description |
|----------|---------|-------------|
| `MAX_RETIES` | `5` | HTTP retry attempts per location |
| `REQUEST_TIMEOUT` | `30` | Seconds before a request times out |

Retries use exponential backoff (1s, 2s, 4s, 8s...).

## Key Dependencies

| Package | Purpose |
|---------|---------|
| `httpx` | Async HTTP client for API requests |
| `APScheduler` | Cron-based job scheduling |
| `polars` | Fast DataFrame processing and Parquet I/O |
| `sqlalchemy` | PostgreSQL connection and query execution |
| `psycopg2` | PostgreSQL driver |
