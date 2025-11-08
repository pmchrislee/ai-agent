"""
Weather service for fetching real weather data.

This module provides functionality to fetch current weather conditions
from external weather APIs.
"""

import logging
import os
import re
from typing import Dict, Optional, Tuple
import aiohttp

logger = logging.getLogger(__name__)

# Default location: Queens, NY
DEFAULT_LOCATION = "Queens,NY,US"
DEFAULT_LAT = 40.7282
DEFAULT_LON = -73.7949


def parse_location_from_message(message: str) -> Optional[str]:
    """
    Parse location from a user message.
    
    Looks for patterns like:
    - "weather in [location]"
    - "weather at [location]"
    - "weather for [location]"
    - "[location] weather"
    
    Args:
        message: User's message text
        
    Returns:
        str: Parsed location string, or None if no location found
    """
    message_lower = message.lower()
    
    # Patterns to match location - improved to handle commas and state abbreviations
    # Try to match "weather in/at/for [location]" first, then "[location] weather"
    patterns = [
        # Match "weather in/at/for [location]" - capture everything until end or weather/joke keyword
        # This handles: "What's the weather in Queens, NY?" or "weather in Queens, NY"
        r'(?:what\'?s|what|tell|show|get).*?weather\s+(?:in|at|for)\s+([^?!]*?)(?:\s+(?:weather|joke)|[?!]|$)',
        r'weather\s+(?:in|at|for)\s+([^?!]*?)(?:\s+(?:weather|joke)|[?!]|$)',
        # Match "[location] weather" - capture everything before "weather"
        r'(.+?)\s+weather',
        # Match "weather in/at/for [location]" to end of string
        r'weather\s+(?:in|at|for)\s+(.+?)$',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, message_lower, re.IGNORECASE)
        if match:
            location = match.group(1).strip()
            # Clean up common words
            location = re.sub(r'\s+(weather|joke|like|today|now|current)', '', location, flags=re.IGNORECASE)
            location = location.strip()
            
            # Remove trailing punctuation
            location = location.rstrip('.,!?')
            
            # Normalize location format: "Queens, NY" -> "Queens,NY" for API compatibility
            location = re.sub(r',\s+', ',', location)  # Remove space after comma
            
            # Skip if location is too short or common words
            if len(location) > 2 and location not in ['the', 'a', 'an', 'what', 'how', 'tell', 'me', 'is', 'it']:
                return location
    
    return None


class WeatherService:
    """Service for fetching weather data from OpenWeatherMap API."""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the weather service.

        Args:
            api_key: OpenWeatherMap API key. If not provided, will try to get from env.
        """
        self.api_key = api_key or os.getenv("OPENWEATHER_API_KEY")
        self.base_url = "https://api.openweathermap.org/data/2.5/weather"

    async def get_weather(self, city: str = DEFAULT_LOCATION,
                         lat: Optional[float] = None,
                         lon: Optional[float] = None) -> Dict:
        """
        Get current weather for a location.

        Args:
            city: City name (e.g., "Queens,NY,US" or "Queens,NY")
            lat: Latitude (optional, for more precise location)
            lon: Longitude (optional, for more precise location)

        Returns:
            dict: Weather data with keys:
                - temperature_f: Temperature in Fahrenheit
                - temperature_c: Temperature in Celsius
                - condition: Weather condition (e.g., "Clear", "Clouds")
                - description: Detailed description
                - humidity: Humidity percentage
                - wind_speed: Wind speed in mph
                - location: Location name
        """
        if not self.api_key:
            logger.warning("No OpenWeatherMap API key found. Using fallback weather.")
            return self._get_fallback_weather()

        try:
            # Build query parameters
            params = {
                "appid": self.api_key,
                "units": "imperial"  # Get Fahrenheit
            }

            # Use coordinates if provided, otherwise use city name
            if lat and lon:
                params["lat"] = lat
                params["lon"] = lon
            else:
                # Normalize city format - ensure it's in the right format for API
                # If it's just "Queens,NY", try to use it as-is, API should handle it
                params["q"] = city
                logger.debug(f"Fetching weather for: {city}")

            # Fetch weather data
            async with aiohttp.ClientSession() as session:
                async with session.get(self.base_url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._parse_weather_data(data, city)
                    else:
                        logger.error(f"Weather API error: {response.status}")
                        return self._get_fallback_weather()

        except Exception as e:
            logger.error(f"Error fetching weather: {e}", exc_info=True)
            return self._get_fallback_weather()

    def _parse_weather_data(self, data: Dict, location: str) -> Dict:
        """Parse OpenWeatherMap API response."""
        main = data.get("main", {})
        weather = data.get("weather", [{}])[0]
        wind = data.get("wind", {})

        return {
            "temperature_f": round(main.get("temp", 70)),
            "temperature_c": round((main.get("temp", 70) - 32) * 5 / 9),
            "feels_like_f": round(main.get("feels_like", 70)),
            "condition": weather.get("main", "Clear"),
            "description": weather.get("description", "clear sky").title(),
            "humidity": main.get("humidity", 50),
            "wind_speed": round(wind.get("speed", 0)),
            "location": data.get("name", location)
        }

    def _get_fallback_weather(self) -> Dict:
        """Return fallback weather data when API is unavailable."""
        return {
            "temperature_f": 72,
            "temperature_c": 22,
            "feels_like_f": 72,
            "condition": "Clear",
            "description": "Clear sky",
            "humidity": 50,
            "wind_speed": 5,
            "location": "Queens, NY"
        }

    def format_weather_response(self, weather_data: Dict, include_joke: bool = False) -> str:
        """
        Format weather data into a user-friendly response.

        Args:
            weather_data: Weather data dictionary
            include_joke: Whether to include a weather joke

        Returns:
            str: Formatted weather response
        """
        temp = weather_data["temperature_f"]
        condition = weather_data["condition"]
        description = weather_data["description"]
        feels_like = weather_data["feels_like_f"]
        humidity = weather_data["humidity"]
        wind = weather_data["wind_speed"]
        location = weather_data["location"]

        # Weather emoji mapping
        emoji_map = {
            "Clear": "☀️",
            "Clouds": "☁️",
            "Rain": "🌧️",
            "Drizzle": "🌦️",
            "Thunderstorm": "⛈️",
            "Snow": "❄️",
            "Mist": "🌫️",
            "Fog": "🌫️",
            "Haze": "🌫️"
        }
        emoji = emoji_map.get(condition, "🌤️")

        if include_joke:
            jokes = [
                f"The meteorologist's favorite type of music? Heavy metal - especially when it's hailing! Currently in {location}: {temp}°F with {description.lower()}! {emoji}",
                f"Why do clouds never get lonely? Because they're always in good company - they're quite the cumulus crowd! Right now in {location} it's {temp}°F with {description.lower()}! {emoji}",
                f"What did the barometric pressure say to the thermometer? 'I'm feeling quite under pressure today, but you seem to be rising to the occasion!' In {location}: {temp}°F with {description.lower()}! {emoji}",
                f"The wind's favorite type of literature? Gust-ave Flaubert novels, naturally! Today in {location}: {temp}°F with {description.lower()} and light winds! {emoji}",
                f"Why did the dew point become a philosopher? Because it was always questioning the humidity of existence! Current conditions in {location}: {temp}°F with {description.lower()}! {emoji}",
                f"What's a tornado's favorite dance? The twist, obviously! But don't worry, in {location} it's just {temp}°F with {description.lower()}! {emoji}"
            ]
            import random
            return random.choice(jokes)

        # Regular weather response
        response = f"Current weather in {location}: {temp}°F"
        if feels_like != temp:
            response += f" (feels like {feels_like}°F)"
        response += f" with {description.lower()}. {emoji}"
        
        if humidity > 70:
            response += f" It's quite humid ({humidity}% humidity)."
        elif humidity < 30:
            response += f" The air is dry ({humidity}% humidity)."
        
        if wind > 15:
            response += f" Windy conditions with {wind} mph winds."
        elif wind > 5:
            response += f" Light breeze at {wind} mph."

        return response


# Global weather service instance
_weather_service: Optional[WeatherService] = None


def get_weather_service() -> WeatherService:
    """Get or create the global weather service instance."""
    global _weather_service
    if _weather_service is None:
        _weather_service = WeatherService()
    return _weather_service


