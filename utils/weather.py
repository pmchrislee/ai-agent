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

# Known location coordinates for better accuracy
# Note: More specific locations (neighborhoods) should be checked first
LOCATION_COORDINATES = {
    # Specific neighborhoods (check these first for accuracy)
    "little neck,ny": (40.7756, -73.7400),
    "little neck": (40.7756, -73.7400),
    "huntington,ny": (40.8682, -73.4257),
    "huntington": (40.8682, -73.4257),
    # Boroughs
    "queens,ny": (40.7282, -73.7949),
    "queens": (40.7282, -73.7949),
    "manhattan,ny": (40.7831, -73.9712),
    "manhattan": (40.7831, -73.9712),
    "brooklyn,ny": (40.6782, -73.9442),
    "brooklyn": (40.6782, -73.9442),
    "bronx,ny": (40.8448, -73.8648),
    "bronx": (40.8448, -73.8648),
    "staten island,ny": (40.5795, -74.1502),
    "staten island": (40.5795, -74.1502),
    # General city (check last to avoid overriding specific neighborhoods)
    "new york,ny": (40.7128, -74.0060),  # Manhattan coordinates
    "new york": (40.7128, -74.0060),
}


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
        # Check if we have coordinates for this location
        # Normalize city name for lookup (remove spaces after commas, lowercase)
        city_normalized = city.lower().strip()
        city_normalized = re.sub(r',\s+', ',', city_normalized)  # "Little Neck, NY" -> "little neck,ny"
        
        # Try exact match first
        if city_normalized in LOCATION_COORDINATES:
            lat, lon = LOCATION_COORDINATES[city_normalized]
            logger.debug(f"Using known coordinates for {city}: {lat}, {lon}")
        else:
            # Try matching without state abbreviation
            city_no_state = city_normalized.split(',')[0].strip()
            if city_no_state in LOCATION_COORDINATES:
                lat, lon = LOCATION_COORDINATES[city_no_state]
                logger.debug(f"Using known coordinates for {city_no_state}: {lat}, {lon}")
        
        # Try OpenWeatherMap API first if key is available
        if self.api_key:
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
                    logger.debug(f"Fetching weather using coordinates: {lat}, {lon}")
                else:
                    # Normalize city format - ensure it's in the right format for API
                    params["q"] = city
                    logger.debug(f"Fetching weather for: {city}")

                # Fetch weather data with optimized timeout
                timeout = aiohttp.ClientTimeout(total=5, connect=3)  # Faster timeout
                async with aiohttp.ClientSession(timeout=timeout) as session:
                    async with session.get(self.base_url, params=params, timeout=timeout) as response:
                        if response.status == 200:
                            data = await response.json()
                            return self._parse_weather_data(data, city)
                        else:
                            logger.warning(f"OpenWeatherMap API error: {response.status}, falling back to wttr.in")
            except Exception as e:
                logger.warning(f"Error fetching from OpenWeatherMap: {e}, falling back to wttr.in")
        
        # Fallback to wttr.in (free, no API key required)
        try:
            return await self._fetch_from_wttr(city, lat, lon)
        except Exception as e:
            logger.error(f"Error fetching weather from wttr.in: {e}", exc_info=True)
            return self._get_fallback_weather()

    def _parse_weather_data(self, data: Dict, location: str) -> Dict:
        """Parse OpenWeatherMap API response."""
        main = data.get("main", {})
        weather = data.get("weather", [{}])[0]
        wind = data.get("wind", {})

        # Format the location name based on what was requested
        # This ensures we use the correct location name even if API returns something else
        location_lower = location.lower().strip()
        location_normalized = re.sub(r',\s+', ',', location_lower)
        
        # Format the location name properly (prioritize specific neighborhoods)
        display_location = None
        if location_normalized in LOCATION_COORDINATES or location_lower.split(',')[0].strip() in LOCATION_COORDINATES:
            if location_normalized in ["little neck,ny", "little neck"] or location_lower.startswith("little neck"):
                display_location = "Little Neck, NY"
            elif location_normalized in ["huntington,ny", "huntington"] or location_lower.startswith("huntington"):
                display_location = "Huntington, NY"
            elif location_normalized in ["queens,ny", "queens"] or location_lower.startswith("queens"):
                display_location = "Queens, NY"
            elif location_normalized in ["manhattan,ny", "manhattan"] or location_lower.startswith("manhattan"):
                display_location = "Manhattan, NY"
            elif location_normalized in ["brooklyn,ny", "brooklyn"] or location_lower.startswith("brooklyn"):
                display_location = "Brooklyn, NY"
            elif location_normalized in ["bronx,ny", "bronx"] or location_lower.startswith("bronx"):
                display_location = "Bronx, NY"
            elif location_normalized in ["staten island,ny", "staten island"] or location_lower.startswith("staten island"):
                display_location = "Staten Island, NY"
            elif location_normalized in ["new york,ny", "new york"] or location_lower.startswith("new york"):
                display_location = "New York, NY"
        
        # If we couldn't format it, use API's returned name or the original location
        if not display_location:
            api_location_name = data.get("name", "")
            if api_location_name:
                display_location = api_location_name
            elif location:
                display_location = location
            else:
                # If no location provided, try to construct from coordinates if available
                # This shouldn't happen often, but handle gracefully
                display_location = "Unknown Location"

        return {
            "temperature_f": round(main.get("temp", 70)),
            "temperature_c": round((main.get("temp", 70) - 32) * 5 / 9),
            "feels_like_f": round(main.get("feels_like", 70)),
            "condition": weather.get("main", "Clear"),
            "description": weather.get("description", "clear sky").title(),
            "humidity": main.get("humidity", 50),
            "wind_speed": round(wind.get("speed", 0)),
            "location": display_location
        }

    async def _fetch_from_wttr(self, city: str, lat: Optional[float] = None, 
                               lon: Optional[float] = None) -> Dict:
        """Fetch weather from wttr.in (free, no API key required)."""
        import ssl
        try:
            # Format location for wttr.in
            if lat and lon:
                # Use coordinates for more accurate results
                location_query = f"{lat},{lon}"
            else:
                # Format city name for wttr.in
                # Remove spaces and format as "City,State" or "City,State,Country"
                location_query = city.replace(" ", "")
            
            # wttr.in API endpoint - format=j1 returns JSON
            url = f"https://wttr.in/{location_query}?format=j1"
            
            # Create SSL context that doesn't verify certificates
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            # Use shorter timeout for faster response
            connector = aiohttp.TCPConnector(ssl=ssl_context, limit=10)
            timeout = aiohttp.ClientTimeout(total=5, connect=3)  # Reduced from 10s to 5s
            async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
                async with session.get(url, timeout=timeout) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._parse_wttr_data(data, city, lat, lon)
                    else:
                        raise Exception(f"wttr.in returned status {response.status}")
        except Exception as e:
            logger.error(f"Error fetching from wttr.in: {e}")
            raise

    def _parse_wttr_data(self, data: Dict, city: str, lat: Optional[float] = None,
                        lon: Optional[float] = None) -> Dict:
        """Parse wttr.in API response."""
        try:
            current = data.get("current_condition", [{}])[0]
            location_info = data.get("nearest_area", [{}])[0]
            
            # Get location name
            area_name = location_info.get("areaName", [{}])[0].get("value", "")
            region = location_info.get("region", [{}])[0].get("value", "")
            country = location_info.get("country", [{}])[0].get("value", "")
            
            # Format location name based on requested city (prioritize our database over API response)
            city_lower = city.lower().strip()
            city_normalized = re.sub(r',\s+', ',', city_lower)
            
            # Check if we have this location in our database (prioritize specific neighborhoods)
            location_name = None
            if city_normalized in LOCATION_COORDINATES or city_lower.split(',')[0].strip() in LOCATION_COORDINATES:
                if city_normalized in ["little neck,ny", "little neck"] or city_lower.startswith("little neck"):
                    location_name = "Little Neck, NY"
                elif city_normalized in ["huntington,ny", "huntington"] or city_lower.startswith("huntington"):
                    location_name = "Huntington, NY"
                elif city_normalized in ["queens,ny", "queens"] or city_lower.startswith("queens"):
                    location_name = "Queens, NY"
                elif city_normalized in ["manhattan,ny", "manhattan"] or city_lower.startswith("manhattan"):
                    location_name = "Manhattan, NY"
                elif city_normalized in ["brooklyn,ny", "brooklyn"] or city_lower.startswith("brooklyn"):
                    location_name = "Brooklyn, NY"
                elif city_normalized in ["bronx,ny", "bronx"] or city_lower.startswith("bronx"):
                    location_name = "Bronx, NY"
                elif city_normalized in ["staten island,ny", "staten island"] or city_lower.startswith("staten island"):
                    location_name = "Staten Island, NY"
                elif city_normalized in ["new york,ny", "new york"] or city_lower.startswith("new york"):
                    location_name = "New York, NY"
            
            # If we couldn't format from our database, use API response or fallback
            if not location_name:
                if area_name:
                    if region and region != area_name:
                        location_name = f"{area_name}, {region}"
                    else:
                        location_name = area_name
                elif city:
                    location_name = city
                else:
                    # If no city provided and we have coordinates, use area name from API
                    # This handles the case where only coordinates are provided
                    if area_name:
                        location_name = f"{area_name}, {region}" if region else area_name
                    else:
                        location_name = f"{lat:.2f}, {lon:.2f}" if lat and lon else "Unknown Location"
            
            # Get temperature (wttr.in provides in both F and C)
            temp_f = int(current.get("temp_F", 70))
            temp_c = int(current.get("temp_C", 21))
            feels_like_f = int(current.get("FeelsLikeF", temp_f))
            
            # Get condition
            weather_desc = current.get("weatherDesc", [{}])[0].get("value", "Clear")
            # Map wttr.in descriptions to our condition types
            condition_map = {
                "sunny": "Clear",
                "clear": "Clear",
                "partly cloudy": "Clouds",
                "cloudy": "Clouds",
                "overcast": "Clouds",
                "mist": "Mist",
                "fog": "Fog",
                "light rain": "Rain",
                "moderate rain": "Rain",
                "heavy rain": "Rain",
                "light snow": "Snow",
                "moderate snow": "Snow",
                "heavy snow": "Snow",
            }
            condition = "Clear"
            for key, value in condition_map.items():
                if key in weather_desc.lower():
                    condition = value
                    break
            
            humidity = int(current.get("humidity", 50))
            wind_speed = int(float(current.get("windspeedMiles", 0)))
            
            return {
                "temperature_f": temp_f,
                "temperature_c": temp_c,
                "feels_like_f": feels_like_f,
                "condition": condition,
                "description": weather_desc,
                "humidity": humidity,
                "wind_speed": wind_speed,
                "location": location_name
            }
        except Exception as e:
            logger.error(f"Error parsing wttr.in data: {e}")
            raise

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

    def format_weather_response(self, weather_data: Dict, include_joke: bool = False, 
                                requested_location: Optional[str] = None) -> str:
        """
        Format weather data into a user-friendly response.

        Args:
            weather_data: Weather data dictionary
            include_joke: Whether to include a weather joke
            requested_location: The location name the user requested (for display)

        Returns:
            str: Formatted weather response
        """
        temp = weather_data["temperature_f"]
        condition = weather_data["condition"]
        description = weather_data["description"]
        feels_like = weather_data["feels_like_f"]
        humidity = weather_data["humidity"]
        wind = weather_data["wind_speed"]
        # ALWAYS use requested location if provided - this ensures we show the correct location name
        # even if the API returns a different name (e.g., API returns "New York" for Little Neck coordinates)
        if requested_location:
            location = requested_location
        else:
            location = weather_data.get("location", "Unknown location")

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


