"""
Tests for configuration management.
"""

import pytest
from config import Config


class TestConfig:
    """Test cases for Config class."""

    def test_default_values(self):
        """Test default configuration values."""
        assert Config.AGENT_NAME == "AI Assistant"
        assert Config.AGENT_VERSION == "2.0.0"
        assert Config.WEB_HOST == "0.0.0.0"
        assert Config.WEB_PORT == 8080
        assert Config.MAX_MESSAGE_LENGTH == 5000
        assert Config.MAX_CONVERSATION_HISTORY == 1000

    def test_get_cors_origins_wildcard(self):
        """Test CORS origins with wildcard."""
        # Save original value
        original = Config.CORS_ORIGINS
        Config.CORS_ORIGINS = '*'

        origins = Config.get_cors_origins()
        assert origins == ['*']

        # Restore original
        Config.CORS_ORIGINS = original

    def test_get_cors_origins_multiple(self):
        """Test CORS origins with multiple domains."""
        # Save original value
        original = Config.CORS_ORIGINS
        Config.CORS_ORIGINS = 'http://localhost:3000, http://example.com'

        origins = Config.get_cors_origins()
        assert len(origins) == 2
        assert 'http://localhost:3000' in origins
        assert 'http://example.com' in origins

        # Restore original
        Config.CORS_ORIGINS = original

    def test_validate_success(self):
        """Test successful validation."""
        assert Config.validate() is True

    def test_validate_invalid_port(self):
        """Test validation with invalid port."""
        # Save original value
        original = Config.WEB_PORT
        Config.WEB_PORT = 70000

        with pytest.raises(ValueError):
            Config.validate()

        # Restore original
        Config.WEB_PORT = original

    def test_validate_invalid_max_message_length(self):
        """Test validation with invalid max message length."""
        original = Config.MAX_MESSAGE_LENGTH
        Config.MAX_MESSAGE_LENGTH = -1

        with pytest.raises(ValueError):
            Config.validate()

        Config.MAX_MESSAGE_LENGTH = original

    def test_config_summary(self):
        """Test configuration summary."""
        summary = Config.summary()

        assert 'agent' in summary
        assert 'web' in summary
        assert 'validation' in summary
        assert 'logging' in summary

        assert summary['agent']['name'] == Config.AGENT_NAME
        assert summary['web']['port'] == Config.WEB_PORT
