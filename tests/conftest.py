"""
Test configuration and fixtures for the FastAPI application.
"""

import os
import tempfile
from unittest.mock import Mock

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.dependencies import get_current_user_with_db, get_db
from app.db.database import Base
from app.main import app
from app.models.action import Action
from app.models.module import Module
from app.models.permission import Permission
from app.models.role import Role
from app.models.user import User

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session")
def db_engine():
    """Create test database engine."""
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db_session(db_engine):
    """Create a fresh database session for each test."""
    connection = db_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    try:
        yield session
    finally:
        session.rollback()  # Roll back any changes
        session.close()
        transaction.close()
        connection.close()


@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with dependency overrides."""

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def mock_user():
    """Create a mock user for testing."""
    return User(
        id=1,
        firstname="John",
        lastname="Doe",
        email="john.doe@example.com",
        password_hash="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj6bm4KyU7fu",  # "password123"
    )


@pytest.fixture
def authenticated_client(client, mock_user, db_session):
    """Create an authenticated test client."""
    # Add the mock user to the database
    db_session.add(mock_user)
    db_session.commit()

    def override_get_current_user_with_db():
        return mock_user

    app.dependency_overrides[get_current_user_with_db] = (
        override_get_current_user_with_db
    )

    yield client

    app.dependency_overrides.clear()


@pytest.fixture
def sample_user_data():
    """Sample user data for testing."""
    return {
        "firstname": "Jane",
        "lastname": "Smith",
        "email": "jane.smith@example.com",
        "password": "securepassword123",
    }


@pytest.fixture
def sample_role(db_session):
    """Create a sample role for testing."""
    role = Role(name="test_role", description="Test role for unit testing")
    db_session.add(role)
    db_session.commit()
    db_session.refresh(role)
    return role


@pytest.fixture
def sample_module(db_session):
    """Create a sample module for testing."""
    module = Module(name="test_module", description="Test module for unit testing")
    db_session.add(module)
    db_session.commit()
    db_session.refresh(module)
    return module


@pytest.fixture
def sample_action(db_session):
    """Create a sample action for testing."""
    action = Action(name="test_action", description="Test action for unit testing")
    db_session.add(action)
    db_session.commit()
    db_session.refresh(action)
    return action


@pytest.fixture
def sample_permission(db_session, sample_module, sample_action):
    """Create a sample permission for testing."""
    permission = Permission(
        name="test_permission",
        description="Test permission for unit testing",
        module_id=sample_module.id,
        action_id=sample_action.id,
    )
    db_session.add(permission)
    db_session.commit()
    db_session.refresh(permission)
    return permission


@pytest.fixture
def jwt_token():
    """Sample JWT token for testing."""
    return "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"


@pytest.fixture(autouse=True)
def setup_test_env():
    """Setup test environment variables."""
    os.environ["TESTING"] = "true"
    yield
    if "TESTING" in os.environ:
        del os.environ["TESTING"]
