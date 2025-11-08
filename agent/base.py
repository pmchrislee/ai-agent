"""
Base AI Agent implementation.

This module provides the core AIAgent class with message processing,
conversation history management, and extensible response handling.
"""

import logging
from collections import deque
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Callable, Awaitable

from agent.responses import ResponseGenerator
from utils.weather import get_weather_service, parse_location_from_message, DEFAULT_LOCATION

logger = logging.getLogger(__name__)


class MessageHandler:
    """Handler for pattern matching and response generation."""

    def __init__(self, keywords: List[str], handler: Callable[[str], str],
                 require_all: bool = False):
        """
        Initialize a message handler.

        Args:
            keywords: List of keywords to match in the message
            handler: Function to call when pattern matches
            require_all: If True, all keywords must be present; if False, any keyword
        """
        self.keywords = keywords
        self.handler = handler
        self.require_all = require_all

    def matches(self, message: str) -> bool:
        """Check if this handler matches the given message."""
        message_lower = message.lower()
        if self.require_all:
            return all(keyword in message_lower for keyword in self.keywords)
        else:
            return any(keyword in message_lower for keyword in self.keywords)

    def handle(self, message: str) -> str:
        """Execute the handler and return the response."""
        return self.handler(message)


class AIAgent:
    """
    Core AI Agent with conversation management and response generation.

    This agent uses a pattern-matching system to generate appropriate responses
    based on user input. It maintains conversation history and status tracking.

    Attributes:
        name: The agent's name
        version: The agent's version
        status: Current status (idle, processing, error)
        max_history: Maximum number of conversation entries to retain
    """

    def __init__(self, name: str = "AI Assistant", version: str = "2.0.0",
                 max_history: int = 1000):
        """
        Initialize the AI Agent.

        Args:
            name: Name of the agent
            version: Version string
            max_history: Maximum conversation history entries to keep
        """
        self.name = name
        self.version = version
        self.status = "idle"
        self.max_history = max_history
        self.conversation_history = deque(maxlen=max_history)
        self.response_gen = ResponseGenerator()

        # Initialize message handlers in priority order
        self._init_handlers()

        logger.info(f"Initialized {self.name} v{self.version}")

    def _init_handlers(self):
        """Initialize the message handlers in priority order."""
        self.handlers = [
            # Weather + joke combination (check first - most specific)
            MessageHandler(
                keywords=['weather', 'joke'],
                handler=self._handle_weather_joke,
                require_all=True
            ),
            # Weather only
            MessageHandler(
                keywords=['weather', 'forecast', 'temperature'],
                handler=self._handle_weather_info,
                require_all=False
            ),
            # Jokes
            MessageHandler(
                keywords=['joke', 'funny', 'humor', 'laugh'],
                handler=lambda msg: self.response_gen.get_general_joke(),
                require_all=False
            ),
            # Greetings
            MessageHandler(
                keywords=['hello', 'hi', 'hey', 'greetings'],
                handler=lambda msg: self.response_gen.get_greeting(),
                require_all=False
            ),
            # Help
            MessageHandler(
                keywords=['help', 'commands', 'what can you do'],
                handler=lambda msg: self.response_gen.get_help_text(),
                require_all=False
            ),
            # News
            MessageHandler(
                keywords=['news', 'headlines', 'current events'],
                handler=lambda msg: self.response_gen.get_news_response(),
                require_all=False
            ),
        ]

    async def process_message(self, message: str, user_id: str = "default") -> Dict:
        """
        Process a user message and generate a response.

        Args:
            message: The user's message text
            user_id: Unique identifier for the user

        Returns:
            dict: Response object with keys:
                - content: The response text
                - type: Response type ("chat")
                - timestamp: ISO format timestamp
                - user_id: The user's ID

        Raises:
            ValueError: If message is invalid
        """
        if not message or not isinstance(message, str):
            raise ValueError("Message must be a non-empty string")

        self.status = "processing"
        logger.info(f"Processing message from user {user_id}: {message[:50]}...")

        try:
            # Generate response using handler chain
            response_content = await self._generate_response(message)

            # Create response object
            response = {
                "content": response_content,
                "type": "chat",
                "timestamp": datetime.utcnow().isoformat(),
                "user_id": user_id
            }

            # Add to conversation history
            self._add_to_history(message, response_content, user_id)

            self.status = "idle"
            logger.debug(f"Generated response: {response_content[:50]}...")

            return response

        except Exception as e:
            self.status = "error"
            logger.error(f"Error processing message: {e}", exc_info=True)
            return {
                "content": "I encountered an error processing your message. Please try again.",
                "type": "error",
                "timestamp": datetime.utcnow().isoformat(),
                "user_id": user_id
            }

    async def _generate_response(self, message: str) -> str:
        """
        Generate a response using the handler chain.

        Args:
            message: The user's message

        Returns:
            str: The generated response
        """
        # Try each handler in order
        for handler in self.handlers:
            if handler.matches(message):
                result = handler.handle(message)
                # Handle async handlers
                if hasattr(result, '__await__'):
                    return await result
                return result

        # No handler matched - use default response
        return self.response_gen.get_default_response()

    async def _handle_weather_joke(self, message: str) -> str:
        """Handle weather joke request with real weather data."""
        weather_service = get_weather_service()
        # Parse location from message, default to Queens, NY
        location = parse_location_from_message(message) or DEFAULT_LOCATION
        # Format location name for display
        display_location = self._format_location_name(location)
        weather_data = await weather_service.get_weather(city=location)
        return weather_service.format_weather_response(weather_data, include_joke=True, 
                                                      requested_location=display_location)

    async def _handle_weather_info(self, message: str) -> str:
        """Handle weather info request with real weather data."""
        weather_service = get_weather_service()
        # Parse location from message, default to Queens, NY
        location = parse_location_from_message(message) or DEFAULT_LOCATION
        # Format location name for display
        display_location = self._format_location_name(location)
        weather_data = await weather_service.get_weather(city=location)
        return weather_service.format_weather_response(weather_data, include_joke=False,
                                                      requested_location=display_location)
    
    def _format_location_name(self, location: str) -> str:
        """Format location name for display."""
        location_lower = location.lower().strip()
        location_names = {
            "queens,ny": "Queens, NY",
            "queens": "Queens, NY",
            "new york,ny": "New York, NY",
            "new york": "New York, NY",
            "manhattan,ny": "Manhattan, NY",
            "manhattan": "Manhattan, NY",
            "brooklyn,ny": "Brooklyn, NY",
            "brooklyn": "Brooklyn, NY",
            "bronx,ny": "Bronx, NY",
            "bronx": "Bronx, NY",
            "staten island,ny": "Staten Island, NY",
            "staten island": "Staten Island, NY",
        }
        
        if location_lower in location_names:
            return location_names[location_lower]
        
        # Otherwise, capitalize properly
        parts = location.split(',')
        formatted_parts = []
        for part in parts:
            words = part.strip().split()
            formatted_words = [word.capitalize() for word in words]
            formatted_parts.append(' '.join(formatted_words))
        return ', '.join(formatted_parts)

    def _add_to_history(self, message: str, response: str, user_id: str):
        """
        Add a conversation entry to history.

        Args:
            message: User's message
            response: Agent's response
            user_id: User identifier
        """
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": user_id,
            "message": message,
            "response": response
        }
        self.conversation_history.append(entry)
        logger.debug(f"Added entry to history (total: {len(self.conversation_history)})")

    def get_status(self) -> Dict:
        """
        Get the current status of the agent.

        Returns:
            dict: Status information including name, version, status, and history count
        """
        return {
            "name": self.name,
            "version": self.version,
            "status": self.status,
            "conversation_count": len(self.conversation_history),
            "max_history": self.max_history
        }

    def get_conversation_history(self, user_id: Optional[str] = None,
                                 limit: Optional[int] = None) -> List[Dict]:
        """
        Retrieve conversation history.

        Args:
            user_id: Optional filter by user ID
            limit: Optional limit on number of entries to return

        Returns:
            list: List of conversation history entries
        """
        history = list(self.conversation_history)

        # Filter by user_id if provided
        if user_id:
            history = [entry for entry in history if entry.get("user_id") == user_id]

        # Apply limit if provided
        if limit:
            history = history[-limit:]

        logger.debug(f"Retrieved {len(history)} history entries")
        return history

    def clear_history(self, user_id: Optional[str] = None):
        """
        Clear conversation history.

        Args:
            user_id: Optional user ID to clear history for specific user only
        """
        if user_id:
            # Remove entries for specific user
            self.conversation_history = deque(
                (entry for entry in self.conversation_history
                 if entry.get("user_id") != user_id),
                maxlen=self.max_history
            )
            logger.info(f"Cleared history for user {user_id}")
        else:
            # Clear all history
            self.conversation_history.clear()
            logger.info("Cleared all conversation history")
