"""
API tests for user routes.
"""

from unittest.mock import patch

import pytest
from fastapi import status

from app.models.user import User


class TestUserRegistration:
    """Test user registration endpoint."""

    def test_register_user_success(self, client, sample_user_data):
        """Test successful user registration."""
        response = client.post("/api/v1/user/register", json=sample_user_data)

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["email"] == sample_user_data["email"]
        assert data["firstname"] == sample_user_data["firstname"]
        assert data["lastname"] == sample_user_data["lastname"]
        assert "id" in data
        assert "password" not in data  # Password should not be returned

    def test_register_user_duplicate_email(self, client, sample_user_data, db_session):
        """Test registration with duplicate email."""
        # First registration
        client.post("/api/v1/user/register", json=sample_user_data)

        # Second registration with same email
        response = client.post("/api/v1/user/register", json=sample_user_data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "User with this email already registered" in response.json()["detail"]

    def test_register_user_invalid_email(self, client):
        """Test registration with invalid email format."""
        invalid_data = {
            "firstname": "John",
            "lastname": "Doe",
            "email": "invalid-email",
            "password": "password123",
        }

        response = client.post("/api/v1/user/register", json=invalid_data)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_register_user_short_password(self, client):
        """Test registration with password too short."""
        invalid_data = {
            "firstname": "John",
            "lastname": "Doe",
            "email": "john@example.com",
            "password": "123",  # Too short
        }

        response = client.post("/api/v1/user/register", json=invalid_data)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_register_user_missing_fields(self, client):
        """Test registration with missing required fields."""
        incomplete_data = {
            "firstname": "John",
            "email": "john@example.com",
            # Missing lastname and password
        }

        response = client.post("/api/v1/user/register", json=incomplete_data)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestUserLogin:
    """Test user login endpoint."""

    def test_login_user_success(self, client, sample_user_data, db_session):
        """Test successful user login."""
        # First register a user
        client.post("/api/v1/user/register", json=sample_user_data)

        # Then login
        login_data = {
            "username": sample_user_data["email"],
            "password": sample_user_data["password"],
        }

        response = client.post("/api/v1/user/login", data=login_data)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_user_wrong_password(self, client, sample_user_data, db_session):
        """Test login with wrong password."""
        # First register a user
        client.post("/api/v1/user/register", json=sample_user_data)

        # Then login with wrong password
        login_data = {
            "username": sample_user_data["email"],
            "password": "wrongpassword",
        }

        response = client.post("/api/v1/user/login", data=login_data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Invalid email or password" in response.json()["detail"]

    def test_login_user_nonexistent(self, client):
        """Test login with non-existent user."""
        login_data = {"username": "nonexistent@example.com", "password": "password123"}

        response = client.post("/api/v1/user/login", data=login_data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Invalid email or password" in response.json()["detail"]

    def test_login_user_invalid_format(self, client):
        """Test login with invalid data format."""
        response = client.post("/api/v1/user/login", json={"invalid": "format"})

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestUserManagement:
    """Test user management endpoints."""

    def test_get_all_users_authenticated(self, authenticated_client, db_session):
        """Test getting all users with authentication."""
        # Add some test users
        user1 = User(firstname="User1", lastname="Test", email="user1@test.com")
        user2 = User(firstname="User2", lastname="Test", email="user2@test.com")
        db_session.add_all([user1, user2])
        db_session.commit()

        response = authenticated_client.get("/api/v1/user/all")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 2  # At least the test users plus authenticated user

    def test_get_all_users_unauthenticated(self, client):
        """Test getting all users without authentication."""
        response = client.get("/api/v1/user/all")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_user_by_id_success(self, authenticated_client, mock_user, db_session):
        """Test getting user by ID successfully."""
        response = authenticated_client.get(f"/api/v1/user/{mock_user.id}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == mock_user.id
        assert data["email"] == mock_user.email

    def test_get_user_by_id_not_found(self, authenticated_client):
        """Test getting non-existent user by ID."""
        response = authenticated_client.get("/api/v1/user/999")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "User not found" in response.json()["detail"]

    def test_update_user_success(self, authenticated_client, mock_user):
        """Test successful user update."""
        update_data = {"firstname": "Updated", "lastname": "Name"}

        response = authenticated_client.put(
            f"/api/v1/user/{mock_user.id}", json=update_data
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["firstname"] == "Updated"
        assert data["lastname"] == "Name"

    def test_update_user_not_found(self, authenticated_client):
        """Test updating non-existent user."""
        update_data = {"firstname": "Updated", "lastname": "Name"}

        response = authenticated_client.put("/api/v1/user/999", json=update_data)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_user_success(self, authenticated_client, db_session):
        """Test successful user deletion."""
        # Create a user to delete
        user = User(firstname="Delete", lastname="Me", email="delete@test.com")
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        response = authenticated_client.delete(f"/api/v1/user/{user.id}")

        assert response.status_code == status.HTTP_200_OK
        assert "deleted successfully" in response.json()["message"]

    def test_delete_user_not_found(self, authenticated_client):
        """Test deleting non-existent user."""
        response = authenticated_client.delete("/api/v1/users/999")

        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestUserPermissions:
    """Test user permission-related endpoints."""

    def test_access_protected_endpoint_with_permission(self, authenticated_client):
        """Test accessing protected endpoint with proper permissions."""
        with patch("app.core.dependencies.check_permissions") as mock_check:
            mock_check.return_value = lambda user: user  # Allow access

            response = authenticated_client.get("/api/v1/user/all")

            assert response.status_code == status.HTTP_200_OK

    def test_access_protected_endpoint_without_permission(self, authenticated_client):
        """Test accessing protected endpoint without proper permissions."""
        with patch("app.core.dependencies.check_permissions") as mock_check:

            def raise_forbidden(user):
                from fastapi import HTTPException

                raise HTTPException(status_code=403, detail="Insufficient permissions")

            mock_check.return_value = raise_forbidden

            response = authenticated_client.get("/api/v1/user/all")

            assert response.status_code == status.HTTP_403_FORBIDDEN


class TestInputValidation:
    """Test input validation for user endpoints."""

    def test_register_user_email_validation(self, client):
        """Test email validation during registration."""
        test_cases = [
            {"email": "", "should_fail": True},
            {"email": "invalid", "should_fail": True},
            {"email": "@example.com", "should_fail": True},
            {"email": "user@", "should_fail": True},
            {"email": "valid@example.com", "should_fail": False},
        ]

        for case in test_cases:
            user_data = {
                "firstname": "Test",
                "lastname": "User",
                "email": case["email"],
                "password": "password123",
            }

            response = client.post("/api/v1/user/register", json=user_data)

            if case["should_fail"]:
                assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
            else:
                assert response.status_code in [
                    status.HTTP_201_CREATED,
                    status.HTTP_400_BAD_REQUEST,
                ]

    def test_register_user_name_validation(self, client):
        """Test name validation during registration."""
        test_cases = [
            {"firstname": "", "should_fail": True},
            {"firstname": "A", "should_fail": True},  # Too short
            {"firstname": "AB", "should_fail": False},  # Minimum length
            {"lastname": "", "should_fail": True},
            {"lastname": "A", "should_fail": True},  # Too short
            {"lastname": "AB", "should_fail": False},  # Minimum length
        ]

        for case in test_cases:
            user_data = {
                "firstname": case.get("firstname", "Valid"),
                "lastname": case.get("lastname", "Valid"),
                "email": f"test{hash(str(case))}@example.com",  # Unique email
                "password": "password123",
            }

            response = client.post("/api/v1/user/register", json=user_data)

            if case["should_fail"]:
                assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
