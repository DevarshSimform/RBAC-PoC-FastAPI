"""
Unit tests for security module.
"""

from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

import pytest

from app.core.security import (
    ALGORITHM,
    SECRET_KEY,
    create_access_token,
    decode_access_token,
    get_password_hash,
    verify_password,
)


class TestPasswordHashing:
    """Test password hashing and verification."""

    def test_get_password_hash_returns_string(self):
        """Test that password hashing returns a string."""
        password = "testpassword123"
        hashed = get_password_hash(password)

        assert isinstance(hashed, str)
        assert len(hashed) > 0
        assert hashed != password

    def test_get_password_hash_different_for_same_password(self):
        """Test that the same password generates different hashes (due to salt)."""
        password = "testpassword123"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)

        assert hash1 != hash2

    def test_verify_password_correct_password(self):
        """Test password verification with correct password."""
        password = "testpassword123"
        hashed = get_password_hash(password)

        assert verify_password(password, hashed) is True

    def test_verify_password_incorrect_password(self):
        """Test password verification with incorrect password."""
        password = "testpassword123"
        wrong_password = "wrongpassword"
        hashed = get_password_hash(password)

        assert verify_password(wrong_password, hashed) is False

    def test_verify_password_empty_password(self):
        """Test password verification with empty password."""
        password = "testpassword123"
        hashed = get_password_hash(password)

        assert verify_password("", hashed) is False


class TestJWTTokens:
    """Test JWT token creation and validation."""

    def test_create_access_token_returns_string(self):
        """Test that token creation returns a string."""
        data = {"sub": "test@example.com"}
        token = create_access_token(data)

        assert isinstance(token, str)
        assert len(token) > 0

    def test_create_access_token_with_expiration(self):
        """Test token creation with custom expiration."""
        data = {"sub": "test@example.com"}
        expires_delta = timedelta(minutes=30)
        token = create_access_token(data, expires_delta)

        assert isinstance(token, str)
        assert len(token) > 0

    def test_decode_access_token_valid_token(self):
        """Test decoding a valid token."""
        data = {"sub": "test@example.com"}
        token = create_access_token(data)

        decoded_data = decode_access_token(token)

        assert decoded_data["sub"] == "test@example.com"
        assert "exp" in decoded_data

    def test_decode_access_token_invalid_token(self):
        """Test decoding an invalid token."""
        invalid_token = "invalid.token.here"

        decoded_data = decode_access_token(invalid_token)

        assert decoded_data is None

    def test_decode_access_token_expired_token(self):
        """Test decoding an expired token."""
        data = {"sub": "test@example.com"}
        expires_delta = timedelta(seconds=-1)  # Already expired
        token = create_access_token(data, expires_delta)

        decoded_data = decode_access_token(token)

        assert decoded_data is None

    @patch("app.core.security.jwt.decode")
    def test_decode_access_token_jwt_error(self, mock_decode):
        """Test decoding token with JWT error."""
        mock_decode.side_effect = Exception("JWT Error")
        token = "some.token.here"

        decoded_data = decode_access_token(token)

        assert decoded_data is None

    def test_token_contains_expiration(self):
        """Test that created token contains expiration claim."""
        data = {"sub": "test@example.com"}
        token = create_access_token(data)
        decoded_data = decode_access_token(token)

        assert "exp" in decoded_data
        assert isinstance(decoded_data["exp"], int)

        # Check that expiration is in the future
        current_time = datetime.utcnow().timestamp()
        assert decoded_data["exp"] > current_time
