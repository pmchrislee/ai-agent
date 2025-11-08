"""
Input validation utilities for the AI Agent.

This module provides validation functions for user input and data sanitization.
"""

from typing import Tuple
from config import Config


class ValidationError(Exception):
    """Exception raised for validation errors."""
    pass


def validate_message(message: str, max_length: int = None) -> Tuple[bool, str]:
    """
    Validate a user message.

    Args:
        message: The message to validate
        max_length: Optional maximum length (defaults to Config.MAX_MESSAGE_LENGTH)

    Returns:
        tuple: (is_valid, processed_message or error_message)

    Raises:
        ValidationError: If validation fails
    """
    if max_length is None:
        max_length = Config.MAX_MESSAGE_LENGTH

    # Check if message exists
    if message is None:
        raise ValidationError("Message cannot be None")

    # Check if message is a string
    if not isinstance(message, str):
        raise ValidationError("Message must be a string")

    # Trim whitespace
    message = message.strip()

    # Check if message is empty after stripping
    if not message:
        raise ValidationError("Message cannot be empty")

    # Check length
    if len(message) > max_length:
        raise ValidationError(f"Message exceeds maximum length of {max_length} characters")

    # Return validated message
    return True, message


def sanitize_html(text: str) -> str:
    """
    Basic HTML sanitization for text output.

    Args:
        text: Text to sanitize

    Returns:
        str: Sanitized text with HTML entities escaped
    """
    if not isinstance(text, str):
        return str(text)

    replacements = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#x27;',
        '/': '&#x2F;'
    }

    for char, entity in replacements.items():
        text = text.replace(char, entity)

    return text


def validate_user_id(user_id: str) -> Tuple[bool, str]:
    """
    Validate a user ID.

    Args:
        user_id: The user ID to validate

    Returns:
        tuple: (is_valid, processed_user_id or error_message)

    Raises:
        ValidationError: If validation fails
    """
    if not user_id or not isinstance(user_id, str):
        raise ValidationError("User ID must be a non-empty string")

    user_id = user_id.strip()

    if not user_id:
        raise ValidationError("User ID cannot be empty")

    if len(user_id) > 255:
        raise ValidationError("User ID exceeds maximum length of 255 characters")

    # Allow only alphanumeric, dash, underscore
    if not all(c.isalnum() or c in ('-', '_') for c in user_id):
        raise ValidationError("User ID contains invalid characters")

    return True, user_id
