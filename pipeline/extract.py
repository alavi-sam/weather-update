import httpx
import logging
from config import MAX_RETIES, REQUEST_TIMEOUT



logging.basicConfig(filename='app.log', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')


def fetch_weather(lat=43.78, long=-79.41):
    for retry in range(MAX_RETIES):
        try:
            logging.debug(f"fetching weather. Try {retry}/{MAX_RETIES}")
            response = httpx.get(
                f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={long}&current=temperature_2m,relative_humidity_2m,apparent_temperature,is_day,precipitation,cloud_cover,wind_speed_10m",
                timeout=REQUEST_TIMEOUT
            )
            response.raise_for_status()
            data = response.json()
            logging.info(f"✓ weather extracted for lat {lat} long {long}")
            return data
        
        except httpx.HTTPStatusError as e:
            logging.warning(f"failed extraction with error code {e.response.status_code} for lat {lat} long {long}, error {e}")

        except (httpx.RequestError, httpx.TimeoutException) as e:
            logging.warning(f"Network error for lat {lat} long {long} on attempt {retry}: {e}")


    return response
