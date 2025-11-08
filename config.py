"""
Configuration management for the AI Agent.

This module handles all configuration settings, supporting both environment
variables and default values.
"""

import os
from typing import Optional


class Config:
    """Application configuration with environment variable support."""

    # Agent configuration
    AGENT_NAME: str = os.getenv('AGENT_NAME', 'AI Assistant')
    AGENT_VERSION: str = os.getenv('AGENT_VERSION', '2.0.0')
    MAX_CONVERSATION_HISTORY: int = int(os.getenv('MAX_CONVERSATION_HISTORY', '1000'))

    # Web server configuration
    WEB_HOST: str = os.getenv('WEB_HOST', '0.0.0.0')
    WEB_PORT: int = int(os.getenv('WEB_PORT', '8080'))
    DEBUG: bool = os.getenv('DEBUG', 'False').lower() in ('true', '1', 'yes')
    CORS_ORIGINS: str = os.getenv('CORS_ORIGINS', '*')

    # Message validation
    MAX_MESSAGE_LENGTH: int = int(os.getenv('MAX_MESSAGE_LENGTH', '5000'))

    # Logging configuration
    LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FORMAT: str = os.getenv(
        'LOG_FORMAT',
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    @classmethod
    def get_cors_origins(cls) -> list:
        """
        Parse CORS origins from configuration.

        Returns:
            list: List of allowed CORS origins
        """
        if cls.CORS_ORIGINS == '*':
            return ['*']
        return [origin.strip() for origin in cls.CORS_ORIGINS.split(',')]

    @classmethod
    def validate(cls) -> bool:
        """
        Validate configuration settings.

        Returns:
            bool: True if configuration is valid

        Raises:
            ValueError: If configuration is invalid
        """
        if cls.WEB_PORT < 1 or cls.WEB_PORT > 65535:
            raise ValueError(f"Invalid port number: {cls.WEB_PORT}")

        if cls.MAX_MESSAGE_LENGTH < 1:
            raise ValueError(f"Invalid max message length: {cls.MAX_MESSAGE_LENGTH}")

        if cls.MAX_CONVERSATION_HISTORY < 1:
            raise ValueError(f"Invalid max history: {cls.MAX_CONVERSATION_HISTORY}")

        valid_log_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if cls.LOG_LEVEL.upper() not in valid_log_levels:
            raise ValueError(f"Invalid log level: {cls.LOG_LEVEL}")

        return True

    @classmethod
    def summary(cls) -> dict:
        """
        Get a summary of current configuration.

        Returns:
            dict: Configuration summary
        """
        return {
            'agent': {
                'name': cls.AGENT_NAME,
                'version': cls.AGENT_VERSION,
                'max_history': cls.MAX_CONVERSATION_HISTORY
            },
            'web': {
                'host': cls.WEB_HOST,
                'port': cls.WEB_PORT,
                'debug': cls.DEBUG,
                'cors_origins': cls.get_cors_origins()
            },
            'validation': {
                'max_message_length': cls.MAX_MESSAGE_LENGTH
            },
            'logging': {
                'level': cls.LOG_LEVEL,
                'format': cls.LOG_FORMAT
            }
        }
