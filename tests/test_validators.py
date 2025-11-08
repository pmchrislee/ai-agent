"""
Tests for input validation utilities.
"""

import pytest
from utils.validators import (
    validate_message,
    validate_user_id,
    sanitize_html,
    ValidationError
)


class TestValidateMessage:
    """Test cases for message validation."""

    def test_valid_message(self):
        """Test validation of a valid message."""
        valid, result = validate_message("Hello, world!")
        assert valid is True
        assert result == "Hello, world!"

    def test_message_with_whitespace(self):
        """Test message with leading/trailing whitespace."""
        valid, result = validate_message("  Hello  ")
        assert valid is True
        assert result == "Hello"

    def test_empty_message(self):
        """Test empty message raises error."""
        with pytest.raises(ValidationError):
            validate_message("")

    def test_whitespace_only_message(self):
        """Test whitespace-only message raises error."""
        with pytest.raises(ValidationError):
            validate_message("   ")

    def test_none_message(self):
        """Test None message raises error."""
        with pytest.raises(ValidationError):
            validate_message(None)

    def test_non_string_message(self):
        """Test non-string message raises error."""
        with pytest.raises(ValidationError):
            validate_message(123)

    def test_long_message(self):
        """Test message exceeding max length raises error."""
        long_message = "a" * 6000  # Exceeds default max of 5000
        with pytest.raises(ValidationError):
            validate_message(long_message)

    def test_custom_max_length(self):
        """Test custom max length parameter."""
        valid, result = validate_message("Hello", max_length=10)
        assert valid is True

        with pytest.raises(ValidationError):
            validate_message("Hello world!", max_length=5)


class TestValidateUserId:
    """Test cases for user ID validation."""

    def test_valid_user_id(self):
        """Test validation of valid user IDs."""
        valid, result = validate_user_id("user123")
        assert valid is True
        assert result == "user123"

        valid, result = validate_user_id("test-user_01")
        assert valid is True
        assert result == "test-user_01"

    def test_user_id_with_whitespace(self):
        """Test user ID with leading/trailing whitespace."""
        valid, result = validate_user_id("  user123  ")
        assert valid is True
        assert result == "user123"

    def test_empty_user_id(self):
        """Test empty user ID raises error."""
        with pytest.raises(ValidationError):
            validate_user_id("")

    def test_none_user_id(self):
        """Test None user ID raises error."""
        with pytest.raises(ValidationError):
            validate_user_id(None)

    def test_non_string_user_id(self):
        """Test non-string user ID raises error."""
        with pytest.raises(ValidationError):
            validate_user_id(123)

    def test_user_id_too_long(self):
        """Test user ID exceeding max length raises error."""
        long_id = "a" * 300
        with pytest.raises(ValidationError):
            validate_user_id(long_id)

    def test_user_id_invalid_characters(self):
        """Test user ID with invalid characters raises error."""
        with pytest.raises(ValidationError):
            validate_user_id("user@123")

        with pytest.raises(ValidationError):
            validate_user_id("user name")


class TestSanitizeHtml:
    """Test cases for HTML sanitization."""

    def test_sanitize_basic_html(self):
        """Test basic HTML sanitization."""
        result = sanitize_html("<script>alert('xss')</script>")
        assert "<script>" not in result
        assert "&lt;script&gt;" in result

    def test_sanitize_html_entities(self):
        """Test various HTML entities are escaped."""
        test_cases = {
            "<": "&lt;",
            ">": "&gt;",
            "&": "&amp;",
            '"': "&quot;",
            "'": "&#x27;",
            "/": "&#x2F;"
        }

        for char, entity in test_cases.items():
            result = sanitize_html(char)
            assert entity in result

    def test_sanitize_mixed_content(self):
        """Test sanitizing mixed text and HTML."""
        text = 'Hello <b>world</b> & "friends"'
        result = sanitize_html(text)
        assert "<b>" not in result
        assert "&lt;b&gt;" in result
        assert "&quot;" in result

    def test_sanitize_non_string(self):
        """Test sanitizing non-string values."""
        result = sanitize_html(123)
        assert result == "123"

        result = sanitize_html(None)
        assert result == "None"
