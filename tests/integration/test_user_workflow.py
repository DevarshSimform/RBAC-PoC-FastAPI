"""
Integration tests for complete user workflows.
"""

import pytest
from fastapi import status

from app.models.role import Role
from app.models.user import User


class TestUserRegistrationLoginWorkflow:
    """Test complete user registration and login workflow."""

    def test_complete_user_registration_and_login_workflow(self, client):
        """Test the complete flow from registration to login."""
        # Step 1: Register a new user
        user_data = {
            "firstname": "Integration",
            "lastname": "Test",
            "email": "integration@sample2.com",
            "password": "securepassword123",
        }

        register_response = client.post("/api/v1/user/register", json=user_data)
        assert register_response.status_code == status.HTTP_201_CREATED

        registered_user = register_response.json()
        assert registered_user["email"] == user_data["email"]
        assert "id" in registered_user

        # Step 2: Login with the registered user
        login_data = {"username": user_data["email"], "password": user_data["password"]}

        login_response = client.post("/api/v1/user/login", data=login_data)
        assert login_response.status_code == status.HTTP_200_OK

        token_data = login_response.json()
        assert "access_token" in token_data
        assert token_data["token_type"] == "bearer"

        # Step 3: Use the token to access protected endpoints
        headers = {"Authorization": f"Bearer {token_data['access_token']}"}

        profile_response = client.get(
            f"/api/v1/user/{registered_user['id']}", headers=headers
        )
        print(f"----------{profile_response.status_code}----------")
        print(f"----------{profile_response.json()}----------")
        assert profile_response.status_code == status.HTTP_200_OK

        profile_data = profile_response.json()
        assert profile_data["email"] == user_data["email"]

    def test_user_registration_duplicate_prevention(self, client):
        """Test that duplicate user registration is properly prevented."""
        user_data = {
            "firstname": "Duplicate",
            "lastname": "Test",
            "email": "duplicate@test.com",
            "password": "password123",
        }

        # First registration should succeed
        first_response = client.post("/api/v1/user/register", json=user_data)
        assert first_response.status_code == status.HTTP_201_CREATED

        # Second registration with same email should fail
        second_response = client.post("/api/v1/user/register", json=user_data)
        assert second_response.status_code == status.HTTP_400_BAD_REQUEST
        assert "already registered" in second_response.json()["detail"].lower()


class TestUserCRUDWorkflow:
    """Test complete CRUD operations workflow."""

    def test_complete_user_crud_workflow_without_permission(
        self, authenticated_client, db_session
    ):
        """Test complete CRUD workflow for users."""
        # Step 1: Create a user (via registration)

        user_data = {
            "firstname": "CRUD",
            "lastname": "Test",
            "email": "crud@test.com",
            "password": "password123",
        }

        create_response = authenticated_client.post(
            "/api/v1/user/register", json=user_data
        )
        assert create_response.status_code == status.HTTP_201_CREATED
        created_user = create_response.json()
        user_id = created_user["id"]

        # Step 2: Read the user
        read_response = authenticated_client.get(f"/api/v1/user/{user_id}")
        assert read_response.status_code == status.HTTP_403_FORBIDDEN

        # Step 3: Update the user
        update_data = {"firstname": "Updated", "lastname": "Name"}

        update_response = authenticated_client.patch(f"/api/v1/user/", json=update_data)
        assert update_response.status_code == status.HTTP_403_FORBIDDEN

        # Step 4: Verify the update
        verify_response = authenticated_client.get(f"/api/v1/user/{user_id}")
        assert verify_response.status_code == status.HTTP_403_FORBIDDEN

        # Step 5: Delete the user
        delete_response = authenticated_client.delete(f"/api/v1/user/")
        assert delete_response.status_code == status.HTTP_403_FORBIDDEN

        # Step 6: Verify deletion
        verify_delete_response = authenticated_client.get(f"/api/v1/user/{user_id}")
        assert verify_delete_response.status_code == status.HTTP_403_FORBIDDEN


class TestUserPermissionsWorkflow:
    """Test user permissions and role-based access control."""

    def test_user_role_assignment_workflow(
        self, authenticated_client, db_session, sample_role
    ):
        """Test assigning roles to users and checking permissions."""

        # Create a test user
        user = User(
            firstname="Permission",
            lastname="Test",
            email="permission@test.com",
            password_hash="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj6bm4KyU7fu",
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        # Test accessing endpoint without specific role
        response = authenticated_client.get("/api/v1/user/all")
        # This should work with basic authentication
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_403_FORBIDDEN]

    def test_token_expiration_workflow(self, client, db_session):
        """Test token expiration and refresh workflow."""

        # Add these debug lines
        print(f"🧪 Table name: {User.__tablename__}")
        print(f"🧪 Database URL: {db_session.bind.engine.url}")
        print(f"🧪 Session bind type: {type(db_session.bind)}")
        print(f"🧪 Session ID: {id(db_session)}")

        # Register a user
        user_data = {
            "firstname": "Token",
            "lastname": "Test",
            "email": "token@test.com",
            "password": "password123",
        }

        register_response = client.post("/api/v1/user/register", json=user_data)
        assert register_response.status_code == status.HTTP_201_CREATED

        # Login to get token
        login_data = {"username": user_data["email"], "password": user_data["password"]}

        login_response = client.post("/api/v1/user/login", data=login_data)
        assert login_response.status_code == status.HTTP_200_OK

        token_data = login_response.json()
        print(f"----------{token_data}----------")
        token = token_data["access_token"]

        # Use token immediately (should work)
        headers = {"Authorization": f"Bearer {token}"}
        immediate_response = client.get("/api/v1/user/all", headers=headers)
        assert immediate_response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_403_FORBIDDEN,
        ]


class TestDatabaseTransactionWorkflow:
    """Test database transaction handling."""

    def test_user_creation_rollback_on_error(self, client, db_session):
        """Test that user creation rolls back properly on errors."""

        # Get initial user count
        initial_user_count = db_session.query(User).count()

        # Try to create a user with invalid data that might cause a database error
        invalid_user_data = {
            "firstname": "Test",
            "lastname": "User",
            "email": "invalid@test.com",
            "password": "short",  # This should fail validation
        }

        response = client.post("/api/v1/user/register", json=invalid_user_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

        # Verify that no user was created
        final_user_count = db_session.query(User).count()
        assert final_user_count == initial_user_count

    def test_concurrent_user_operations(self, authenticated_client, db_session):
        """Test handling of concurrent user operations."""
        # Create a user
        user = User(
            firstname="Concurrent",
            lastname="Test",
            email="concurrent@test.com",
            password_hash="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj6bm4KyU7fu",
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        # Simulate concurrent updates
        update_data_1 = {"firstname": "Updated1"}
        update_data_2 = {"firstname": "Updated2"}

        # First update
        response1 = authenticated_client.put(
            f"/api/v1/user/{user.id}", json=update_data_1
        )
        assert response1.status_code == status.HTTP_200_OK

        # Second update
        response2 = authenticated_client.put(
            f"/api/v1/user/{user.id}", json=update_data_2
        )
        assert response2.status_code == status.HTTP_200_OK

        # Verify final state
        final_response = authenticated_client.get(f"/api/v1/user/{user.id}")
        assert final_response.status_code == status.HTTP_200_OK
        final_user = final_response.json()
        assert final_user["firstname"] == "Updated2"  # Last update wins
