from dataclasses import dataclass, asdict
from typing import Optional, List
from datetime import datetime
import polars as pl
import logging
logger = logging.getLogger(__name__)




WMO_CODES = {
    0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
    45: "Fog", 48: "Icy fog", 51: "Light drizzle", 53: "Drizzle",
    55: "Heavy drizzle", 61: "Light rain", 63: "Rain", 65: "Heavy rain",
    71: "Light snow", 73: "Snow", 75: "Heavy snow", 80: "Rain showers",
    85: "Snow showers", 95: "Thunderstorm", 99: "Thunderstorm with hail",
}

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
    'wind_speed': pl.Float32,
    'weather_code': pl.String
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
    weather_code: Optional[str]



def extract_json(weather_list: list):
    logger.debug(f"transforming weather!")
    weather_data = []
    try:
        for data in weather_list:
            weather_obj = Weather(
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
                wind_speed=data['current']['wind_speed_10m'],
                weather_code=WMO_CODES.get(data['current']['weather_code'], '')
            )

            logger.info(f"Parsing weather json. lat {weather_obj.latitude} long {weather_obj.longitude}")
            weather_data.append(weather_obj)

        return weather_data
    
    except Exception as e:
        logger.error(f"Failed to transform data! Error: {e}")



def create_dataframe(data_obj: List[Weather]):
    df = pl.DataFrame(schema=POLARS_SCHEMA)
    for location in data_obj:
        try:
            new_df = pl.DataFrame(asdict(location), schema=POLARS_SCHEMA)
            logger.info(f'Converted to polars at lat {location.latitude} long {location.longitude}')
            df = pl.concat([df, new_df])
        except Exception as e:
            logger.error(f"Dataframe failed! lat {location.latitude} long {location.longitude}. Error: {e}")
    return df


