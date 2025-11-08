"""
Tests for the AI Agent core functionality.
"""

import pytest
from agent import AIAgent
from agent.responses import ResponseGenerator


class TestAIAgent:
    """Test cases for AIAgent class."""

    @pytest.fixture
    def agent(self):
        """Create a test agent instance."""
        return AIAgent(name="Test Agent", version="1.0.0", max_history=100)

    @pytest.mark.asyncio
    async def test_agent_initialization(self, agent):
        """Test agent initializes correctly."""
        assert agent.name == "Test Agent"
        assert agent.version == "1.0.0"
        assert agent.status == "idle"
        assert agent.max_history == 100
        assert len(agent.conversation_history) == 0

    @pytest.mark.asyncio
    async def test_process_message_basic(self, agent):
        """Test basic message processing."""
        response = await agent.process_message("Hello", "test-user")

        assert response is not None
        assert "content" in response
        assert "type" in response
        assert "timestamp" in response
        assert response["type"] == "chat"
        assert len(response["content"]) > 0

    @pytest.mark.asyncio
    async def test_process_weather_request(self, agent):
        """Test weather information request."""
        response = await agent.process_message("What's the weather like?", "test-user")

        assert response["type"] == "chat"
        assert "°F" in response["content"] or "weather" in response["content"].lower()

    @pytest.mark.asyncio
    async def test_process_joke_request(self, agent):
        """Test joke request."""
        response = await agent.process_message("Tell me a joke", "test-user")

        assert response["type"] == "chat"
        assert len(response["content"]) > 0

    @pytest.mark.asyncio
    async def test_process_weather_joke_request(self, agent):
        """Test combined weather + joke request."""
        response = await agent.process_message("Tell me a weather joke", "test-user")

        assert response["type"] == "chat"
        assert len(response["content"]) > 0

    @pytest.mark.asyncio
    async def test_conversation_history(self, agent):
        """Test conversation history tracking."""
        await agent.process_message("Hello", "user1")
        await agent.process_message("How are you?", "user1")
        await agent.process_message("Tell me a joke", "user2")

        # Check total history
        history = agent.get_conversation_history()
        assert len(history) == 3

        # Check filtered history
        user1_history = agent.get_conversation_history(user_id="user1")
        assert len(user1_history) == 2

        user2_history = agent.get_conversation_history(user_id="user2")
        assert len(user2_history) == 1

    @pytest.mark.asyncio
    async def test_conversation_history_limit(self, agent):
        """Test conversation history respects max limit."""
        # Send more messages than the max_history
        for i in range(150):
            await agent.process_message(f"Message {i}", "test-user")

        history = agent.get_conversation_history()
        assert len(history) <= agent.max_history

    @pytest.mark.asyncio
    async def test_get_status(self, agent):
        """Test status retrieval."""
        status = agent.get_status()

        assert "name" in status
        assert "version" in status
        assert "status" in status
        assert "conversation_count" in status
        assert status["name"] == "Test Agent"
        assert status["version"] == "1.0.0"

    @pytest.mark.asyncio
    async def test_clear_history_all(self, agent):
        """Test clearing all conversation history."""
        await agent.process_message("Hello", "user1")
        await agent.process_message("Hi", "user2")

        agent.clear_history()
        history = agent.get_conversation_history()
        assert len(history) == 0

    @pytest.mark.asyncio
    async def test_clear_history_specific_user(self, agent):
        """Test clearing history for specific user."""
        await agent.process_message("Hello", "user1")
        await agent.process_message("Hi", "user2")

        agent.clear_history(user_id="user1")

        history = agent.get_conversation_history()
        assert len(history) == 1
        assert history[0]["user_id"] == "user2"

    @pytest.mark.asyncio
    async def test_invalid_message(self, agent):
        """Test handling of invalid messages."""
        with pytest.raises(ValueError):
            await agent.process_message("", "test-user")

        with pytest.raises(ValueError):
            await agent.process_message(None, "test-user")


class TestResponseGenerator:
    """Test cases for ResponseGenerator class."""

    def test_get_weather_joke(self):
        """Test weather joke generation."""
        joke = ResponseGenerator.get_weather_joke()
        assert isinstance(joke, str)
        assert len(joke) > 0

    def test_get_weather_info(self):
        """Test weather info generation."""
        info = ResponseGenerator.get_weather_info()
        assert isinstance(info, str)
        assert len(info) > 0

    def test_get_general_joke(self):
        """Test general joke generation."""
        joke = ResponseGenerator.get_general_joke()
        assert isinstance(joke, str)
        assert len(joke) > 0

    def test_get_greeting(self):
        """Test greeting generation."""
        greeting = ResponseGenerator.get_greeting()
        assert isinstance(greeting, str)
        assert len(greeting) > 0

    def test_get_help_text(self):
        """Test help text generation."""
        help_text = ResponseGenerator.get_help_text()
        assert isinstance(help_text, str)
        assert len(help_text) > 0

    def test_get_news_response(self):
        """Test news response generation."""
        news = ResponseGenerator.get_news_response()
        assert isinstance(news, str)
        assert len(news) > 0

    def test_get_default_response(self):
        """Test default response generation."""
        response = ResponseGenerator.get_default_response()
        assert isinstance(response, str)
        assert len(response) > 0
