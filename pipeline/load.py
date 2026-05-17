import polars as pl
import os
import logging
from datetime import datetime
from db.connection import engine
from sqlalchemy import text
import json

logger = logging.getLogger(__name__)

PARQUET_DIR = os.path.join('data', 'processed')
RAW_DATA_DIR = os.path.join('data', 'raw')
os.makedirs(PARQUET_DIR, exist_ok=True)
os.makedirs(RAW_DATA_DIR, exist_ok=True)


def load_raw_data(data_list, ingestion_time: datetime):
    partition_dir = os.path.join(RAW_DATA_DIR, f"date={ingestion_time.date()}", f"hour={ingestion_time.hour}")
    os.makedirs(partition_dir, exist_ok=True)
    file_path = os.path.join(partition_dir, 'weather.json')
    if os.path.exists(file_path):
        logger.info('JSON exist appending new data!')
        with open(file_path, 'r', encoding='utf-8') as f:
            weather_json = json.load(f)
        if isinstance(weather_json, list):
            for item in data_list:
                filtered_item = {
                    'latitude': item['latitude'],
                    'longitude': item['longitude'],
                    'time': item['current']['time']
                }
                filtered_weather = [
                    {
                        'latitude': obj['latitude'],
                        'longitude': obj['longitude'],
                        'time': obj['current']['time']
                    } for obj in weather_json
                ]
                if filtered_item not in filtered_weather:
                    logger.info("JSON file update with new data.")
                    weather_json.append(item)
                else:
                    logger.info('Duplicate JSON file!')
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(weather_json, f)
        else:
            logger.warning('Incompatible JSON file!')
    else:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data_list, f)
        logger.info("JSON file created for weather.")




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
    return partition_path



def read_parquet(file_path):
    df = pl.read_parquet(file_path)
    return df


def insert_db(df: pl.DataFrame):
    try:
        with engine.connect() as conn:
            geo_ids = {}
            for row in df.select(["timezone", "latitude", "longitude"]).to_dicts():
                result = conn.execute(text("""
                    INSERT INTO geo_table (timezone, latitude, longitude)
                    VALUES (:timezone, :latitude, :longitude)
                    ON CONFLICT (latitude, longitude) DO UPDATE SET timezone = EXCLUDED.timezone
                    RETURNING id, latitude, longitude
                """), row)
                r = result.fetchone()
                geo_ids[(r.latitude, r.longitude)] = r.id

            measure_rows = [
                {**row, 'geo_id': geo_ids[(row['latitude'], row['longitude'])]}
                for row in df.to_dicts()
            ]

            conn.execute(text("""
                INSERT INTO weather_measures
                    (temperature, humidity, feels_like, is_day, precipitation,
                     cloud_cover, wind_speed, weather_code, updated_at, geo_id)
                VALUES
                    (:temperature, :humidity, :feels_like, :is_day, :precipitation,
                     :cloud_cover, :wind_speed, :weather_code, :time, :geo_id)
                ON CONFLICT (geo_id, updated_at) DO NOTHING
            """), measure_rows)

            conn.commit()
            logger.info("Database insertion success!")
    except Exception as e:
        logger.error(f"Could not insert items to database. Error: {e}")
