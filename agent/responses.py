"""
Response data for the AI agent.

This module contains all hardcoded responses, jokes, and other static data
used by the AI agent for generating responses.
"""

import random
from typing import List

# Weather jokes combining humor with weather information
WEATHER_JOKES: List[str] = [
    "I checked the weather for you! It's partly cloudy with a 100% chance of dad jokes! 🌤️ (Currently 72°F)",
    "The forecast shows sunny with occasional puns! ☀️ (Temperature: 68°F)",
    "Weather update: High chance of laughter, low chance of rain! 🌈 (Feels like 70°F)",
    "Breaking news: It's a beautiful day for terrible weather puns! ⛅ (75°F and rising)",
    "Meteorologically speaking, it's perfect joke-telling weather! 🌡️ (A comfortable 71°F)",
    "The weather is so nice, even my jokes are getting warmer! 🌞 (73°F)",
    "Forecast: Clear skies with a slight chance of groaning at my jokes! 🌅 (69°F)"
]

# Weather information responses
WEATHER_CONDITIONS: List[str] = [
    "It's a beautiful sunny day! Perfect for outdoor activities! ☀️ (Temperature: 75°F)",
    "Looks like partly cloudy skies today. Great weather for a walk! ⛅ (Currently 68°F)",
    "A bit overcast, but no rain expected. Don't forget your sunglasses just in case! 🌤️ (72°F)",
    "Clear skies and comfortable temperatures! Enjoy your day! 🌞 (70°F)",
    "Mild and pleasant weather conditions today! 🌈 (Temperature: 71°F)",
    "Beautiful weather outside! Time to get some fresh air! 🌸 (73°F)"
]

# General jokes and puns
GENERAL_JOKES: List[str] = [
    "Why don't scientists trust atoms? Because they make up everything! 🔬",
    "I told my computer I needed a break, and now it won't stop sending me Kit-Kats! 🍫",
    "Why did the programmer quit his job? Because he didn't get arrays! 💻",
    "What do you call a bear with no teeth? A gummy bear! 🐻",
    "Why did the scarecrow win an award? He was outstanding in his field! 🌾",
    "I'm reading a book about anti-gravity. It's impossible to put down! 📚",
    "Why don't eggs tell jokes? They'd crack each other up! 🥚",
    "What do you call a fake noodle? An impasta! 🍝",
    "Why did the math book look so sad? Because it had too many problems! 📖",
    "What did the ocean say to the beach? Nothing, it just waved! 🌊"
]

# Greeting responses
GREETINGS: List[str] = [
    "Hello! How can I help you today? 👋",
    "Hi there! What can I do for you? 😊",
    "Hey! Great to see you! How can I assist? 🌟",
    "Greetings! I'm here to help! 🤖",
    "Hello! Ready to chat? What's on your mind? 💬"
]

# Default/fallback responses
DEFAULT_RESPONSES: List[str] = [
    "I'm not sure I understand. Could you try asking differently?",
    "That's interesting! Tell me more about that.",
    "I'm still learning! Could you rephrase your question?",
    "Hmm, I'm not quite sure how to respond to that yet.",
    "I appreciate your message! Could you clarify what you'd like help with?"
]

# Help text
HELP_TEXT: str = """
I'm an AI assistant that can help you with:
- General conversation and questions
- Weather information (try asking about the weather!)
- Jokes and humor (ask me for a joke!)
- Fun weather jokes (combine both!)

Try asking me:
- "What's the weather like?"
- "Tell me a joke"
- "Tell me a weather joke"
- "Hello" or "Hi"

I'm always learning and improving! 🚀
"""

# News-related responses
NEWS_RESPONSES: List[str] = [
    "I don't have access to real-time news, but I'm here to chat about anything else!",
    "I can't fetch live news updates, but feel free to share what's on your mind!",
    "News is constantly changing! I recommend checking a reliable news source for the latest updates.",
    "While I don't have current news access, I'm happy to discuss other topics!"
]


class ResponseGenerator:
    """Centralized response generation with various strategies."""

    @staticmethod
    def get_weather_joke() -> str:
        """Return a random weather joke."""
        return random.choice(WEATHER_JOKES)

    @staticmethod
    def get_weather_info() -> str:
        """Return random weather information."""
        return random.choice(WEATHER_CONDITIONS)

    @staticmethod
    def get_general_joke() -> str:
        """Return a random general joke."""
        return random.choice(GENERAL_JOKES)

    @staticmethod
    def get_greeting() -> str:
        """Return a random greeting."""
        return random.choice(GREETINGS)

    @staticmethod
    def get_help_text() -> str:
        """Return the help text."""
        return HELP_TEXT

    @staticmethod
    def get_news_response() -> str:
        """Return a news-related response."""
        return random.choice(NEWS_RESPONSES)

    @staticmethod
    def get_default_response() -> str:
        """Return a random default/fallback response."""
        return random.choice(DEFAULT_RESPONSES)
