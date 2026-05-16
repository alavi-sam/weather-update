from dataclasses import dataclass
from typing import Optional
from datetime import datetime
import polars as pl
import logging
logger = logging.getLogger(__name__)



POLARS_SCHEMA = {
    'latitude': pl.Float32,
    'longitude': pl.Float32,
    'timezone': pl.String,
    'time': pl.Datetime,
    'temperature': pl.Float32,
    'humidity': pl.Float32,
    'feels_like': pl.Float32,
    'is_day': pl.Boolean,
    'precipitation': pl.Float32,
    'cloud_cover': pl.Float32,
    'wind_speed': pl.Float32
}


@dataclass
class Weather:
    latitude: str
    longitude: str
    timezone: str
    time: datetime
    temperature: float
    humidity: float
    feels_like: float
    is_day: bool
    precipitation: Optional[float]
    cloud_cover: Optional[float]
    wind_speed: float



def extract_json(data):
    logger.debug(f"transforming weather!")
    try:
        weather_data = Weather(
            latitude=data['latitude'],
            longitude=data['longitude'],
            timezone=data['timezone'],
            time=data['current']['time'],
            temperature=data['current']['temperature_2m'],
            humidity=data['current']['relative_humidity_2m'],
            feels_like=data['current']['apparent_temperature'],
            is_day=bool(data['current']['is_day']),
            precipitation=data['current']['precipitation'],
            cloud_cover=data['current']['cloud_cover']/100,
            wind_speed=data['current']['wind_speed_10m']
        )
        
        logger.info(f"Parsing weather json. lat {weather_data.latitude} long {weather_data.longitude}")

        return weather_data
    
    except Exception as e:
        logger.error(f"Failed to transform data! Error: {e}")


