"""
Unit tests for User Service.
"""

from unittest.mock import Mock, patch

import pytest
from fastapi import HTTPException

from app.models.user import User
from app.schemas.user_schema import LoginUser, RegisterUser, UserUpdate
from app.services.user_service import UserService


class TestUserService:
    """Test User Service operations."""

    @pytest.fixture
    def mock_user_repo(self):
        """Mock user repository."""
        return Mock()

    @pytest.fixture
    def user_service(self, mock_user_repo):
        """Create UserService instance with mock repository."""
        return UserService(mock_user_repo)

    @pytest.fixture
    def sample_user(self):
        """Sample user object."""
        return User(
            id=1,
            firstname="John",
            lastname="Doe",
            email="john.doe@example.com",
            password_hash="hashed_password",
        )

    @pytest.fixture
    def register_user_data(self):
        """Sample registration data."""
        return RegisterUser(
            firstname="Jane",
            lastname="Smith",
            email="jane.smith@example.com",
            password="securepassword123",
        )

    def test_register_user_success(
        self, user_service, mock_user_repo, register_user_data, sample_user
    ):
        """Test successful user registration."""
        mock_user_repo.get_user_by_email.return_value = None
        mock_user_repo.create_user.return_value = sample_user

        result = user_service.register_user(register_user_data)

        assert result == sample_user
        mock_user_repo.get_user_by_email.assert_called_once_with(
            "jane.smith@example.com"
        )
        mock_user_repo.create_user.assert_called_once()

    def test_register_user_email_already_exists(
        self, user_service, mock_user_repo, register_user_data, sample_user
    ):
        """Test registration with existing email."""
        mock_user_repo.get_user_by_email.return_value = sample_user

        with pytest.raises(HTTPException) as exc_info:
            user_service.register_user(register_user_data)

        assert exc_info.value.status_code == 400
        assert "Email already registered" in str(exc_info.value.detail)
        mock_user_repo.create_user.assert_not_called()

    def test_login_user_success(self, user_service, mock_user_repo, sample_user):
        """Test successful user login."""
        login_data = LoginUser(
            email="john.doe@example.com", password="correct_password"
        )
        mock_user_repo.authenticate_user.return_value = sample_user

        with patch(
            "app.services.user_service.create_access_token"
        ) as mock_create_token:
            mock_create_token.return_value = "test_token"

            result = user_service.login_user(login_data)

            assert result == {"access_token": "test_token", "token_type": "bearer"}
            mock_user_repo.authenticate_user.assert_called_once_with(login_data)
            mock_create_token.assert_called_once_with(data={"sub": sample_user.email})

    def test_login_user_invalid_credentials(self, user_service, mock_user_repo):
        """Test login with invalid credentials."""
        login_data = LoginUser(email="john.doe@example.com", password="wrong_password")
        mock_user_repo.authenticate_user.return_value = False

        with pytest.raises(HTTPException) as exc_info:
            user_service.login_user(login_data)

        assert exc_info.value.status_code == 401
        assert "Incorrect email or password" in str(exc_info.value.detail)

    def test_get_all_users(self, user_service, mock_user_repo, sample_user):
        """Test getting all users."""
        mock_user_repo.get_all_users.return_value = [sample_user]

        result = user_service.get_all_users()

        assert result == [sample_user]
        mock_user_repo.get_all_users.assert_called_once()

    def test_get_user_by_id_found(self, user_service, mock_user_repo, sample_user):
        """Test getting user by ID when user exists."""
        mock_user_repo.get_user_by_id.return_value = sample_user

        result = user_service.get_user_by_id(1)

        assert result == sample_user
        mock_user_repo.get_user_by_id.assert_called_once_with(1)

    def test_get_user_by_id_not_found(self, user_service, mock_user_repo):
        """Test getting user by ID when user doesn't exist."""
        mock_user_repo.get_user_by_id.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            user_service.get_user_by_id(999)

        assert exc_info.value.status_code == 404
        assert "User not found" in str(exc_info.value.detail)

    def test_update_user_success(self, user_service, mock_user_repo, sample_user):
        """Test successful user update."""
        update_data = UserUpdate(firstname="Updated Name")
        mock_user_repo.update_user_by_id.return_value = sample_user

        result = user_service.update_user(1, update_data)

        assert result == sample_user
        mock_user_repo.update_user_by_id.assert_called_once_with(
            1, {"firstname": "Updated Name"}
        )

    def test_update_user_not_found(self, user_service, mock_user_repo):
        """Test updating non-existent user."""
        update_data = UserUpdate(firstname="Updated Name")
        mock_user_repo.update_user_by_id.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            user_service.update_user(999, update_data)

        assert exc_info.value.status_code == 404
        assert "User not found" in str(exc_info.value.detail)

    def test_delete_user_success(self, user_service, mock_user_repo):
        """Test successful user deletion."""
        mock_user_repo.delete_user_by_id.return_value = True

        result = user_service.delete_user(1)

        assert result == {"message": "User deleted successfully"}
        mock_user_repo.delete_user_by_id.assert_called_once_with(1)

    def test_delete_user_not_found(self, user_service, mock_user_repo):
        """Test deleting non-existent user."""
        mock_user_repo.delete_user_by_id.return_value = False

        with pytest.raises(HTTPException) as exc_info:
            user_service.delete_user(999)

        assert exc_info.value.status_code == 404
        assert "User not found" in str(exc_info.value.detail)
