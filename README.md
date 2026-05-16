# Weather Update Pipeline

An asynchronous ETL pipeline that fetches real-time weather data for multiple cities on a scheduled interval and stores it locally in both raw JSON and processed Parquet formats.

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
    ├── extract.py  → fetch_multiple_locations()   # async HTTP via httpx
    ├── load.py     → load_raw_data()               # save raw JSON
    ├── transform.py → extract_json(), create_dataframe()  # parse + Polars DataFrame
    └── load.py     → load_parquet()                # save processed Parquet
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

Both raw and processed data are partitioned by date and hour. Duplicate records (same latitude, longitude, time) are detected and skipped on append.

## Setup

**Requirements:** Python 3.13+

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Usage

```bash
python main.py
```

The pipeline runs an initial fetch immediately on startup, then continues on a `0, 15, 30, 45` minute cron schedule. Logs are written to both the terminal and `pipeline.log`.

## Configuration

`config.py` exposes two constants:

| Variable | Default | Description |
|----------|---------|-------------|
| `MAX_RETIES` | `5` | HTTP retry attempts per location |
| `REQUEST_TIMEOUT` | `30` | Seconds before a request times out |

## Key Dependencies

| Package | Purpose |
|---------|---------|
| `httpx` | Async HTTP client for API requests |
| `APScheduler` | Cron-based job scheduling |
| `polars` | Fast DataFrame processing and Parquet I/O |
| `pandas` | General data utilities |
