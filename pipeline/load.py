import polars as pl
import os
import logging
from datetime import datetime
import json

logger = logging.getLogger(__name__)

PARQUET_DIR = os.path.join('data', 'processed')
RAW_DATA_DIR = os.path.join('data', 'raw')
os.makedirs(PARQUET_DIR, exist_ok=True)
os.makedirs(RAW_DATA_DIR, exist_ok=True)


def load_raw_data(data_list, ingestion_time: datetime):
    partition_dir = os.path.join(RAW_DATA_DIR, f"date={ingestion_time.date}", f"hour={ingestion_time.hour}")
    os.makedirs(partition_dir, exist_ok=True)
    file_path = os.path.join(partition_dir, 'weather.json')
    if os.path.exists(file_path):
        weather_json = json.load(file_path)
        if isinstance(weather_json, list):
            weather_json.extend(data_list)
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(weather_json, f)
        else:
            logger.warning('Incompatible JSON file!')
    else:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(weather_json, f)




def load_parquet(df):
    date = df[0]['time'].dt.date()[0]
    hour = df[0]['time'].dt.hour()[0]
    partition_dir = os.path.join(PARQUET_DIR, f"date={date}", f"hour={hour}")
    os.makedirs(partition_dir, exist_ok=True)
    partition_path = os.path.join(partition_dir, 'weather.parquet')
    if os.path.exists(partition_path):
        logger.info('Parquet exist appending new data!')
        existing_df = pl.read_parquet(partition_path)
        final_df = pl.concat([existing_df, df]).unique(subset=['latitude', 'longitude', 'time'], keep='last')
    else:
        logger.info('New parquet created!')
        final_df = df

    print(final_df)
    final_df.write_parquet(partition_path)



