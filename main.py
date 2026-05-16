from pipeline.extract import fetch_weather, fetch_multiple_locations
from pipeline.transform import extract_json, create_dataframe
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

response = asyncio.run(fetch_multiple_locations([(12, 12), (0,0)]))
# print(response)
weather_obj = extract_json(response)
df = create_dataframe(weather_obj)
print(df)