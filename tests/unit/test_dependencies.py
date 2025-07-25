"""
Unit tests for dependencies module.
"""

from unittest.mock import Mock, patch

import pytest
from fastapi import HTTPException
from jose import JWTError

from app.core.dependencies import check_permission, get_current_user_with_db
from app.models.user import User


class TestGetCurrentUser:
    """Test get_current_user dependency."""

    @pytest.fixture
    def mock_db_session(self):
        """Mock database session."""
        return Mock()

    @pytest.fixture
    def sample_user(self):
        """Sample user object."""
        return User(
            id=1,
            firstname="John",
            lastname="Doe",
            email="john.doe@example.com",
            is_active=True,
        )

    @patch("app.core.dependencies.decode_access_token")
    def test_get_current_user_valid_token(
        self, mock_decode, mock_db_session, sample_user
    ):
        """Test getting current user with valid token."""
        token = "valid_token"
        mock_decode.return_value = {"sub": "john.doe@example.com"}
        mock_db_session.query.return_value.filter.return_value.first.return_value = (
            sample_user
        )

        result = get_current_user_with_db(token, mock_db_session)

        assert result == sample_user
        mock_decode.assert_called_once_with(token)

    @patch("app.core.dependencies.decode_access_token")
    def test_get_current_user_invalid_token(self, mock_decode, mock_db_session):
        """Test getting current user with invalid token."""
        token = "invalid_token"
        mock_decode.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            get_current_user_with_db(token, mock_db_session)

        assert exc_info.value.status_code == 401
        assert "Could not validate credentials" in str(exc_info.value.detail)

    @patch("app.core.dependencies.decode_access_token")
    def test_get_current_user_no_email_in_token(self, mock_decode, mock_db_session):
        """Test getting current user when token has no email."""
        token = "token_without_email"
        mock_decode.return_value = {"other_field": "value"}

        with pytest.raises(HTTPException) as exc_info:
            get_current_user_with_db(token, mock_db_session)

        assert exc_info.value.status_code == 401
        assert "Could not validate credentials" in str(exc_info.value.detail)

    @patch("app.core.dependencies.decode_access_token")
    def test_get_current_user_user_not_found(self, mock_decode, mock_db_session):
        """Test getting current user when user doesn't exist in database."""
        token = "valid_token"
        mock_decode.return_value = {"sub": "nonexistent@example.com"}
        mock_db_session.query.return_value.filter.return_value.first.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            get_current_user_with_db(token, mock_db_session)

        assert exc_info.value.status_code == 401
        assert "Could not validate credentials" in str(exc_info.value.detail)

    @patch("app.core.dependencies.decode_access_token")
    def test_get_current_user_inactive_user(self, mock_decode, mock_db_session):
        """Test getting current user when user is inactive."""
        token = "valid_token"
        mock_decode.return_value = {"sub": "john.doe@example.com"}
        inactive_user = User(
            id=1,
            firstname="John",
            lastname="Doe",
            email="john.doe@example.com",
            is_active=False,
        )
        mock_db_session.query.return_value.filter.return_value.first.return_value = (
            inactive_user
        )

        with pytest.raises(HTTPException) as exc_info:
            get_current_user_with_db(token, mock_db_session)

        assert exc_info.value.status_code == 400
        assert "Inactive user" in str(exc_info.value.detail)


class TestCheckPermissions:
    """Test check_permissions dependency."""

    @pytest.fixture
    def mock_db_session(self):
        """Mock database session."""
        return Mock()

    @pytest.fixture
    def sample_user(self):
        """Sample user object."""
        return User(
            id=1,
            firstname="John",
            lastname="Doe",
            email="john.doe@example.com",
            is_active=True,
        )

    def test_check_permissions_with_permissions(self, mock_db_session, sample_user):
        """Test permission checking when user has permissions."""
        # Mock the permission checking logic
        with patch("app.core.dependencies.has_permission") as mock_has_permission:
            mock_has_permission.return_value = True

            result = check_permission(["read_users"], mock_db_session)(sample_user)

            assert result == sample_user

    def test_check_permissions_without_permissions(self, mock_db_session, sample_user):
        """Test permission checking when user lacks permissions."""
        with patch("app.core.dependencies.has_permission") as mock_has_permission:
            mock_has_permission.return_value = False

            permission_checker = check_permission(["admin_access"], mock_db_session)

            with pytest.raises(HTTPException) as exc_info:
                permission_checker(sample_user)

            assert exc_info.value.status_code == 403
            assert "Insufficient permissions" in str(exc_info.value.detail)
