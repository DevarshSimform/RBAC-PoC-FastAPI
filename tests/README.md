# Test Suite Documentation

This directory contains comprehensive test cases for the FastAPI application with role-based access control (RBAC).

## Test Structure

```
tests/
├── __init__.py
├── conftest.py              # Test configuration and fixtures
├── pytest.ini              # Pytest configuration
├── requirements.txt         # Test dependencies
├── README.md               # This documentation
├── unit/                   # Unit tests
│   ├── __init__.py
│   ├── test_security.py    # Security functions tests
│   ├── test_user_repository.py  # User repository tests
│   ├── test_user_service.py     # User service tests
│   └── test_dependencies.py     # Dependencies tests
├── integration/            # Integration tests
│   ├── __init__.py
│   ├── test_user_workflow.py   # Complete user workflows
│   └── test_database.py        # Database integration tests
├── api/                    # API endpoint tests
│   ├── __init__.py
│   └── test_user_routes.py     # User API endpoint tests
└── fixtures/               # Test data and factories
    ├── __init__.py
    └── test_data.py            # Test data factories
```

## Test Categories

### Unit Tests
- **Security Tests**: Password hashing, JWT token creation/validation
- **Repository Tests**: Database operations with mocked sessions
- **Service Tests**: Business logic with mocked dependencies
- **Dependencies Tests**: Authentication and permission checking

### Integration Tests
- **User Workflows**: Complete registration, login, and CRUD operations
- **Database Tests**: Constraints, relationships, and transactions
- **Permission Workflows**: Role-based access control testing

### API Tests
- **User Routes**: All user management endpoints
- **Authentication**: Login and token-based authentication
- **Authorization**: Permission-based access control
- **Input Validation**: Request validation and error handling

## Running Tests

### Prerequisites
```bash
# Install test dependencies
pip install -r tests/requirements.txt
```

### Run All Tests
```bash
pytest
```

### Run Specific Test Categories
```bash
# Unit tests only
pytest tests/unit/ -m unit

# Integration tests only
pytest tests/integration/ -m integration

# API tests only
pytest tests/api/ -m api
```

### Run with Coverage
```bash
pytest --cov=app --cov-report=html
```

### Run Specific Test Files
```bash
# Security tests
pytest tests/unit/test_security.py

# User workflow tests
pytest tests/integration/test_user_workflow.py

# API tests
pytest tests/api/test_user_routes.py
```

### Run Tests with Markers
```bash
# Authentication related tests
pytest -m auth

# Permission related tests
pytest -m permissions

# Slow tests
pytest -m slow
```

## Test Configuration

### Environment Variables
- `TESTING=true` - Automatically set during test execution
- Database uses SQLite in-memory for testing

### Test Database
- Each test gets a fresh database session
- Database is created and destroyed for each test session
- Transactions are rolled back after each test

### Fixtures Available

#### Database Fixtures
- `db_engine` - Test database engine
- `db_session` - Fresh database session per test
- `populated_db` - Database with test data

#### Client Fixtures
- `client` - Test client for API calls
- `authenticated_client` - Pre-authenticated test client

#### Data Fixtures
- `mock_user` - Sample user object
- `sample_user_data` - User registration data
- `sample_role` - Sample role object
- `jwt_token` - Sample JWT token

#### Factory Fixtures
- `user_factory` - User object factory
- `role_factory` - Role object factory
- `permission_factory` - Permission object factory

## Test Best Practices

### Writing Tests
1. Use descriptive test names that explain what is being tested
2. Follow the Arrange-Act-Assert pattern
3. Test both success and failure scenarios
4. Use appropriate fixtures to minimize setup code
5. Mock external dependencies in unit tests

### Test Organization
1. Group related tests in classes
2. Use appropriate markers for test categorization
3. Keep test files focused on specific components
4. Use factories for creating test data

### Performance
1. Use `pytest-xdist` for parallel test execution
2. Mock heavy operations in unit tests
3. Use appropriate database fixtures to avoid unnecessary setup

## Coverage Goals

- **Overall Coverage**: 80%+ (enforced by pytest configuration)
- **Critical Components**: 90%+ (security, authentication, core business logic)
- **API Endpoints**: 100% (all endpoints should have tests)

## Continuous Integration

The test suite is designed to run in CI/CD pipelines:

```yaml
# Example GitHub Actions workflow
- name: Run tests
  run: |
    pytest --cov=app --cov-report=xml
    
- name: Upload coverage
  uses: codecov/codecov-action@v1
```

## Test Data Management

### Factories
Use factories in `fixtures/test_data.py` for creating test objects:

```python
user = user_factory.create_user_model(
    firstname="Custom",
    lastname="User",
    email="custom@test.com"
)
```

### Predefined Data
Common test data sets are available as constants:
- `TEST_USERS` - Sample user data
- `TEST_ROLES` - Sample role data
- `TEST_MODULES` - Sample module data
- `TEST_ACTIONS` - Sample action data

## Troubleshooting

### Common Issues

1. **Database Connection Errors**
   - Ensure test database is properly configured
   - Check that migrations are applied

2. **Authentication Errors**
   - Verify JWT secret key configuration
   - Check token format and expiration

3. **Permission Errors**
   - Ensure test user has appropriate roles
   - Verify permission checking logic

### Debugging Tests
```bash
# Run with verbose output
pytest -v

# Run with print statements
pytest -s

# Run single test with debugging
pytest tests/unit/test_security.py::TestPasswordHashing::test_get_password_hash_returns_string -v -s
```

## Contributing

When adding new features:
1. Write tests first (TDD approach)
2. Ensure all tests pass
3. Maintain coverage above 80%
4. Update documentation as needed

## Test Coverage Report

The test suite covers:

### Unit Tests (tests/unit/)
- ✅ Security module (password hashing, JWT tokens)
- ✅ User repository (all CRUD operations)
- ✅ User service (business logic)
- ✅ Dependencies (authentication, authorization)

### Integration Tests (tests/integration/)
- ✅ Complete user workflows (registration → login → CRUD)
- ✅ Database constraints and relationships
- ✅ Transaction handling and rollback
- ✅ Performance testing

### API Tests (tests/api/)
- ✅ User registration endpoint
- ✅ User login endpoint
- ✅ User management endpoints (CRUD)
- ✅ Authentication and authorization
- ✅ Input validation and error handling

### Test Infrastructure
- ✅ Comprehensive fixtures and factories
- ✅ Database session management
- ✅ Test data generation
- ✅ Mock and stub utilities