"""
Test data fixtures and factories.
"""

from datetime import datetime
from typing import Any, Dict

import pytest

from app.models.action import Action
from app.models.module import Module
from app.models.permission import Permission
from app.models.role import Role
from app.models.user import User


class UserFactory:
    """Factory for creating test users."""

    @staticmethod
    def create_user_data(
        firstname: str = "Test",
        lastname: str = "User",
        email: str = None,
        password: str = "testpassword123",
        **kwargs,
    ) -> Dict[str, Any]:
        """Create user data dictionary."""
        if email is None:
            email = f"{firstname.lower()}.{lastname.lower()}@test.com"

        return {
            "firstname": firstname,
            "lastname": lastname,
            "email": email,
            "password": password,
            **kwargs,
        }

    @staticmethod
    def create_user_model(
        firstname: str = "Test",
        lastname: str = "User",
        email: str = None,
        password_hash: str = "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj6bm4KyU7fu",
        **kwargs,
    ) -> User:
        """Create user model instance."""
        if email is None:
            email = f"{firstname.lower()}.{lastname.lower()}@test.com"

        return User(
            firstname=firstname,
            lastname=lastname,
            email=email,
            password_hash=password_hash,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            **kwargs,
        )


class RoleFactory:
    """Factory for creating test roles."""

    @staticmethod
    def create_role_data(
        name: str = "test_role", description: str = "Test role for testing", **kwargs
    ) -> Dict[str, Any]:
        """Create role data dictionary."""
        return {"name": name, "description": description, **kwargs}

    @staticmethod
    def create_role_model(
        name: str = "test_role", description: str = "Test role for testing", **kwargs
    ) -> Role:
        """Create role model instance."""
        return Role(name=name, description=description, **kwargs)


class PermissionFactory:
    """Factory for creating test permissions."""

    @staticmethod
    def create_permission_model(
        name: str = "test_permission",
        description: str = "Test permission",
        module_id: int = 1,
        action_id: int = 1,
        **kwargs,
    ) -> Permission:
        """Create permission model instance."""
        return Permission(
            name=name,
            description=description,
            module_id=module_id,
            action_id=action_id,
            **kwargs,
        )


class ModuleFactory:
    """Factory for creating test modules."""

    @staticmethod
    def create_module_model(
        name: str = "test_module", description: str = "Test module", **kwargs
    ) -> Module:
        """Create module model instance."""
        return Module(name=name, description=description, **kwargs)


class ActionFactory:
    """Factory for creating test actions."""

    @staticmethod
    def create_action_model(
        name: str = "test_action", description: str = "Test action", **kwargs
    ) -> Action:
        """Create action model instance."""
        return Action(name=name, description=description, **kwargs)


# Predefined test data sets
TEST_USERS = [
    UserFactory.create_user_data("John", "Doe", "john.doe@test.com"),
    UserFactory.create_user_data("Jane", "Smith", "jane.smith@test.com"),
    UserFactory.create_user_data("Bob", "Johnson", "bob.johnson@test.com"),
    UserFactory.create_user_data("Alice", "Wilson", "alice.wilson@test.com"),
]

TEST_ROLES = [
    RoleFactory.create_role_data("admin", "Administrator role"),
    RoleFactory.create_role_data("user", "Regular user role"),
    RoleFactory.create_role_data("moderator", "Moderator role"),
    RoleFactory.create_role_data("viewer", "Read-only viewer role"),
]

TEST_MODULES = [
    {"name": "users", "description": "User management module"},
    {"name": "roles", "description": "Role management module"},
    {"name": "permissions", "description": "Permission management module"},
    {"name": "reports", "description": "Reporting module"},
]

TEST_ACTIONS = [
    {"name": "create", "description": "Create action"},
    {"name": "read", "description": "Read action"},
    {"name": "update", "description": "Update action"},
    {"name": "delete", "description": "Delete action"},
]


@pytest.fixture
def test_users():
    """Provide test user data."""
    return TEST_USERS.copy()


@pytest.fixture
def test_roles():
    """Provide test role data."""
    return TEST_ROLES.copy()


@pytest.fixture
def user_factory():
    """Provide user factory."""
    return UserFactory


@pytest.fixture
def role_factory():
    """Provide role factory."""
    return RoleFactory


@pytest.fixture
def permission_factory():
    """Provide permission factory."""
    return PermissionFactory


@pytest.fixture
def module_factory():
    """Provide module factory."""
    return ModuleFactory


@pytest.fixture
def action_factory():
    """Provide action factory."""
    return ActionFactory


@pytest.fixture
def populated_db(
    db_session, user_factory, role_factory, module_factory, action_factory
):
    """Provide a database populated with test data."""
    # Create test modules
    modules = [module_factory.create_module_model(**data) for data in TEST_MODULES]
    db_session.add_all(modules)

    # Create test actions
    actions = [action_factory.create_action_model(**data) for data in TEST_ACTIONS]
    db_session.add_all(actions)

    # Create test roles
    roles = [role_factory.create_role_model(**data) for data in TEST_ROLES]
    db_session.add_all(roles)

    # Create test users
    users = [user_factory.create_user_model(**data) for data in TEST_USERS]
    db_session.add_all(users)

    db_session.commit()

    return {"users": users, "roles": roles, "modules": modules, "actions": actions}
