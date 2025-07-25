"""
Unit tests for User Repository.
"""

from datetime import datetime
from unittest.mock import Mock, patch

import pytest

from app.models.user import User
from app.repositories.user_repo import UserRepository
from app.schemas.user_schema import LoginUser


class TestUserRepository:
    """Test User Repository operations."""

    @pytest.fixture
    def mock_db_session(self):
        """Mock database session."""
        return Mock()

    @pytest.fixture
    def user_repo(self, mock_db_session):
        """Create UserRepository instance with mock session."""
        return UserRepository(mock_db_session)

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

    def test_get_user_by_email_found(self, user_repo, mock_db_session, sample_user):
        """Test getting user by email when user exists."""
        mock_db_session.query.return_value.filter.return_value.first.return_value = (
            sample_user
        )

        result = user_repo.get_user_by_email("john.doe@example.com")

        assert result == sample_user
        mock_db_session.query.assert_called_once_with(User)

    def test_get_user_by_email_not_found(self, user_repo, mock_db_session):
        """Test getting user by email when user doesn't exist."""
        mock_db_session.query.return_value.filter.return_value.first.return_value = None

        result = user_repo.get_user_by_email("nonexistent@example.com")

        assert result is None
        mock_db_session.query.assert_called_once_with(User)

    @patch("app.repositories.user_repo.get_password_hash")
    @patch("app.repositories.user_repo.datetime")
    def test_create_user(self, mock_datetime, mock_hash, user_repo, mock_db_session):
        """Test creating a new user."""
        mock_datetime.utcnow.return_value = datetime(2023, 1, 1, 12, 0, 0)
        mock_hash.return_value = "hashed_password"

        user_data = User(
            firstname="Jane",
            lastname="Smith",
            email="jane.smith@example.com",
            password="plaintext_password",
        )

        result = user_repo.create_user(user_data)

        mock_db_session.add.assert_called_once()
        mock_db_session.commit.assert_called_once()
        mock_db_session.refresh.assert_called_once()
        mock_hash.assert_called_once_with("plaintext_password")

    @patch("app.repositories.user_repo.verify_password")
    def test_authenticate_user_success(
        self, mock_verify, user_repo, mock_db_session, sample_user
    ):
        """Test successful user authentication."""
        mock_db_session.query.return_value.filter_by.return_value.first.return_value = (
            sample_user
        )
        mock_verify.return_value = True

        login_data = LoginUser(
            email="john.doe@example.com", password="correct_password"
        )

        result = user_repo.authenticate_user(login_data)

        assert result == sample_user
        assert sample_user.last_login is not None
        mock_db_session.commit.assert_called_once()

    @patch("app.repositories.user_repo.verify_password")
    def test_authenticate_user_wrong_password(
        self, mock_verify, user_repo, mock_db_session, sample_user
    ):
        """Test authentication with wrong password."""
        mock_db_session.query.return_value.filter_by.return_value.first.return_value = (
            sample_user
        )
        mock_verify.return_value = False

        login_data = LoginUser(email="john.doe@example.com", password="wrong_password")

        result = user_repo.authenticate_user(login_data)

        assert result is False

    def test_authenticate_user_not_found(self, user_repo, mock_db_session):
        """Test authentication when user doesn't exist."""
        mock_db_session.query.return_value.filter_by.return_value.first.return_value = (
            None
        )

        login_data = LoginUser(email="nonexistent@example.com", password="password")

        result = user_repo.authenticate_user(login_data)

        assert result is False

    def test_get_all_users(self, user_repo, mock_db_session, sample_user):
        """Test getting all users."""
        mock_db_session.query.return_value.all.return_value = [sample_user]

        result = user_repo.get_all_users()

        assert result == [sample_user]
        mock_db_session.query.assert_called_once_with(User)

    def test_get_user_by_id_found(self, user_repo, mock_db_session, sample_user):
        """Test getting user by ID when user exists."""
        mock_db_session.query.return_value.filter.return_value.first.return_value = (
            sample_user
        )

        result = user_repo.get_user_by_id(1)

        assert result == sample_user
        mock_db_session.query.assert_called_once_with(User)

    def test_get_user_by_id_not_found(self, user_repo, mock_db_session):
        """Test getting user by ID when user doesn't exist."""
        mock_db_session.query.return_value.filter.return_value.first.return_value = None

        result = user_repo.get_user_by_id(999)

        assert result is None

    @patch("app.repositories.user_repo.datetime")
    def test_update_user_by_id_success(
        self, mock_datetime, user_repo, mock_db_session, sample_user
    ):
        """Test successful user update."""
        mock_datetime.utcnow.return_value = datetime(2023, 1, 1, 12, 0, 0)
        mock_db_session.query.return_value.filter.return_value.first.return_value = (
            sample_user
        )

        update_data = {"firstname": "Updated Name"}

        result = user_repo.update_user_by_id(1, update_data)

        assert result == sample_user
        assert sample_user.firstname == "Updated Name"
        assert sample_user.updated_at == datetime(2023, 1, 1, 12, 0, 0)
        mock_db_session.commit.assert_called_once()
        mock_db_session.refresh.assert_called_once()

    def test_update_user_by_id_not_found(self, user_repo, mock_db_session):
        """Test updating non-existent user."""
        mock_db_session.query.return_value.filter.return_value.first.return_value = None

        update_data = {"firstname": "Updated Name"}

        result = user_repo.update_user_by_id(999, update_data)

        assert result is None

    def test_delete_user_by_id_success(self, user_repo, mock_db_session, sample_user):
        """Test successful user deletion."""
        mock_db_session.query.return_value.filter.return_value.first.return_value = (
            sample_user
        )

        result = user_repo.delete_user_by_id(1)

        assert result is True
        mock_db_session.delete.assert_called_once_with(sample_user)
        mock_db_session.commit.assert_called_once()

    def test_delete_user_by_id_not_found(self, user_repo, mock_db_session):
        """Test deleting non-existent user."""
        mock_db_session.query.return_value.filter.return_value.first.return_value = None

        result = user_repo.delete_user_by_id(999)

        assert result is False
        mock_db_session.delete.assert_not_called()
