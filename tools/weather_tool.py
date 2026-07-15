import logging
import requests
from config.settings import settings

logger = logging.getLogger(__name__)

BASE_URL = "https://api.openweathermap.org/data/2.5/weather"


class WeatherTool:

    def get_weather(self, location: str) -> str:
        logger.info(f"[Weather] Fetching weather for: {location}")

        try:
            response = requests.get(
                BASE_URL,
                params={
                    "q":     location,
                    "appid": settings.openweathermap_api_key,
                    "units": "metric",
                },
                timeout=10,
            )

            if response.status_code == 404:
                return f"Location '{location}' not found."

            if response.status_code == 401:
                return "Invalid OpenWeatherMap API key."

            response.raise_for_status()
            data = response.json()

            name        = data["name"]
            country     = data["sys"]["country"]
            temp        = data["main"]["temp"]
            feels_like  = data["main"]["feels_like"]
            humidity    = data["main"]["humidity"]
            description = data["weather"][0]["description"].capitalize()
            wind_speed  = data["wind"]["speed"]

            return (
                f"Weather in {name}, {country}\n"
                f"Condition:   {description}\n"
                f"Temperature: {temp}°C (feels like {feels_like}°C)\n"
                f"Humidity:    {humidity}%\n"
                f"Wind Speed:  {wind_speed} m/s"
            )

        except requests.Timeout:
            return "Weather request timed out."
        except Exception as e:
            logger.error(f"[Weather] Failed: {e}")
            return f"Could not fetch weather for '{location}': {str(e)}"

    def extract_location(self, query: str) -> str:
        """
        Extract location from query.
        Defaults to Mumbai if no location found.
        """
        query_lower = query.lower()

        cities = [
            "mumbai", "delhi", "bangalore", "hyderabad", "chennai",
            "kolkata", "pune", "london", "new york", "tokyo", "dubai",
            "paris", "singapore", "sydney", "los angeles", "chicago",
        ]

        for city in cities:
            if city in query_lower:
                return city.title()

        return "Mumbai"


# Singleton
_weather_instance = None


def get_weather_tool() -> WeatherTool:
    global _weather_instance
    if _weather_instance is None:
        _weather_instance = WeatherTool()
    return _weather_instance