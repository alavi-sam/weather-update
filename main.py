from pipeline.extract import fetch_multiple_locations
from pipeline.transform import extract_json, create_dataframe
from pipeline.load import load_parquet, load_raw_data, read_parquet, insert_db
from apscheduler.triggers.cron import CronTrigger
from apscheduler.schedulers.asyncio import AsyncIOScheduler

import logging
import asyncio


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s",
    datefmt="%H:%M:%S",
    handlers=[
        logging.StreamHandler(),                           # terminal
        logging.FileHandler("pipeline.log", mode="a"),    # file
    ]
)

logger = logging.getLogger(__name__)


async def run_pipeline(locations: list[tuple]):
    try:
        logger.info("── Pipeline run starting ──")
        response, ingestion_time = await fetch_multiple_locations(locations)
        load_raw_data(response, ingestion_time)
        weather_obj = extract_json(response)
        df = create_dataframe(weather_obj)
        path = load_parquet(df)
        df_parquet = read_parquet(path)
        insert_db(df_parquet)
        logger.info(f"── Pipeline run complete: {df.shape[0]} rows written ──")
    except Exception as e:
        logger.exception(f"Pipeline run failed: {e}")


CITIES = [
    (43.6532,  -79.3832),
    (35.6892,   51.3890),
    (34.0522, -118.2437),
    (49.2827, -123.1207),
    (45.5017,  -73.5673),
    (40.7128,  -74.0060),
]

scheduler = AsyncIOScheduler()
scheduler.add_job(
    run_pipeline,
    trigger=CronTrigger(minute="0,15,30,45"),
    kwargs={'locations': CITIES}
)

async def main():
    scheduler.start()
    await run_pipeline(CITIES)     
    await asyncio.Event().wait()

asyncio.run(main())

