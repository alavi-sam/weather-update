import httpx
import logging
from datetime import datetime
from config import MAX_RETIES, REQUEST_TIMEOUT


logger = logging.getLogger(__name__)


async def fetch_weather(lat=43.78, long=-79.41):
    for retry in range(MAX_RETIES):
        try:
            logger.debug(f"fetching weather. Try {retry}/{MAX_RETIES}")
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={long}&current=temperature_2m,relative_humidity_2m,apparent_temperature,is_day,precipitation,cloud_cover,wind_speed_10m,weather_code",
                    timeout=REQUEST_TIMEOUT
                )
                response.raise_for_status()
            data = response.json()
            logger.info(f"✓ weather extracted for lat {lat} long {long}")
            return data
        
        except httpx.HTTPStatusError as e:
            logger.exception(f"failed extraction with error code {e.response.status_code} for lat {lat} long {long}, error {e}")

        except (httpx.RequestError, httpx.TimeoutException) as e:
            logger.exception(f"Network error for lat {lat} long {long} on attempt {retry}: {e}")


    return response



async def fetch_multiple_locations(locations: list[tuple]):
    weather_list = []
    for location in locations:
        response = await fetch_weather(location[0], location[1])
        weather_list.append(response)
    logger.info('Fetched all locations.')
    return weather_list, datetime.now()
