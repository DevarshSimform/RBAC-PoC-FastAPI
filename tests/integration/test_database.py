"""
Integration tests for database operations.
"""

import pytest
from sqlalchemy.exc import IntegrityError

from app.models.action import Action
from app.models.module import Module
from app.models.permission import Permission
from app.models.role import Role
from app.models.user import User


class TestDatabaseConstraints:
    """Test database constraints and relationships."""

    def test_user_email_uniqueness_constraint(self, db_session):
        """Test that user email uniqueness is enforced at database level."""

        # Add these debug lines
        print(f"🧪 Table name: {User.__tablename__}")
        print(f"🧪 Database URL: {db_session.bind.engine.url}")
        print(f"🧪 Session bind type: {type(db_session.bind)}")
        print(f"🧪 Session ID: {id(db_session)}")

        # Create first user
        user1 = User(
            firstname="First",
            lastname="User",
            email="unique@test.com",
            password_hash="hash1",
        )
        db_session.add(user1)
        db_session.commit()

        # Try to create second user with same email
        user2 = User(
            firstname="Second",
            lastname="User",
            email="unique@test.com",  # Same email
            password_hash="hash2",
        )
        db_session.add(user2)

        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_role_name_uniqueness_constraint(self, db_session):
        """Test that role name uniqueness is enforced."""
        # Create first role
        role1 = Role(name="unique_role", description="First role")
        db_session.add(role1)
        db_session.commit()

        # Try to create second role with same name
        role2 = Role(name="unique_role", description="Second role")
        db_session.add(role2)

        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_permission_module_action_uniqueness(self, db_session):
        """Test that permission module-action combination is unique."""
        # Create module and action
        module = Module(name="test_module")
        action = Action(name="test_action")
        db_session.add_all([module, action])
        db_session.commit()

        # Create first permission
        permission1 = Permission(
            name="first_permission",
            description="First permission",
            module_id=module.id,
            action_id=action.id,
        )
        db_session.add(permission1)
        db_session.commit()

        # Try to create second permission with same module-action combination
        permission2 = Permission(
            name="second_permission",
            description="Second permission",
            module_id=module.id,
            action_id=action.id,
        )
        db_session.add(permission2)

        with pytest.raises(IntegrityError):
            db_session.commit()


class TestDatabaseRelationships:
    """Test database relationships and foreign key constraints."""

    def test_user_role_relationship(self, db_session):
        """Test user-role many-to-many relationship."""
        # Create user and role
        user = User(
            firstname="Test",
            lastname="User",
            email="relationship@test.com",
            password_hash="hash",
        )
        role = Role(name="test_role", description="Test role")

        db_session.add_all([user, role])
        db_session.commit()

        # Test that relationships can be accessed
        assert len(user.assigned_roles) == 0
        assert len(role.user_roles) == 0

    def test_permission_foreign_keys(self, db_session):
        """Test permission foreign key relationships."""
        # Create module and action
        module = Module(name="fk_module")
        action = Action(name="fk_action")
        user = User(
            firstname="Creator",
            lastname="User",
            email="creator@test.com",
            password_hash="hash",
        )

        db_session.add_all([module, action, user])
        db_session.commit()

        # Create permission with foreign keys
        permission = Permission(
            name="fk_permission",
            description="FK test permission",
            module_id=module.id,
            action_id=action.id,
            created_by=user.id,
        )
        db_session.add(permission)
        db_session.commit()

        # Verify relationships
        assert permission.module_id == module.id
        assert permission.action_id == action.id
        assert permission.created_by == user.id

    def test_cascade_deletion_behavior(self, db_session):
        """Test cascade deletion behavior."""
        # Create user
        user = User(
            firstname="Delete",
            lastname="Test",
            email="delete@test.com",
            password_hash="hash",
        )
        db_session.add(user)
        db_session.commit()
        user_id = user.id

        # Delete user
        db_session.delete(user)
        db_session.commit()

        # Verify user is deleted
        deleted_user = db_session.query(User).filter(User.id == user_id).first()
        assert deleted_user is None


class TestDatabaseTransactions:
    """Test database transaction handling."""

    def test_transaction_rollback_on_error(self, db_session):
        """Test that transactions rollback properly on errors."""
        initial_count = db_session.query(User).count()

        try:
            # Start a transaction
            user1 = User(
                firstname="Valid",
                lastname="User",
                email="valid@test.com",
                password_hash="hash",
            )
            db_session.add(user1)

            # This should cause an error (duplicate email if we add the same user again)
            user2 = User(
                firstname="Invalid",
                lastname="User",
                email="valid@test.com",  # Same email - will cause constraint violation
                password_hash="hash",
            )
            db_session.add(user2)
            db_session.commit()
        except IntegrityError:
            db_session.rollback()

        # Verify that no users were added due to rollback
        final_count = db_session.query(User).count()
        assert final_count == initial_count

    def test_bulk_operations(self, db_session):
        """Test bulk database operations."""
        # Create multiple users in bulk
        users = [
            User(
                firstname=f"Bulk{i}",
                lastname="User",
                email=f"bulk{i}@test.com",
                password_hash="hash",
            )
            for i in range(5)
        ]

        db_session.add_all(users)
        db_session.commit()

        # Verify all users were created
        bulk_users = (
            db_session.query(User).filter(User.firstname.startswith("Bulk")).all()
        )
        assert len(bulk_users) == 5

        # Clean up
        for user in bulk_users:
            db_session.delete(user)
        db_session.commit()


class TestDatabasePerformance:
    """Test database performance and optimization."""

    def test_query_performance_with_indexes(self, db_session):
        """Test that queries perform well with proper indexing."""
        # Create multiple users
        users = [
            User(
                firstname=f"Perf{i}",
                lastname="User",
                email=f"perf{i}@test.com",
                password_hash="hash",
            )
            for i in range(100)
        ]

        db_session.add_all(users)
        db_session.commit()

        # Test email lookup (should be fast due to unique constraint/index)
        import time

        start_time = time.time()

        found_user = (
            db_session.query(User).filter(User.email == "perf50@test.com").first()
        )

        end_time = time.time()
        query_time = end_time - start_time

        assert found_user is not None
        assert found_user.email == "perf50@test.com"
        # Query should be reasonably fast (less than 1 second for this small dataset)
        assert query_time < 1.0

        # Clean up
        for user in users:
            db_session.delete(user)
        db_session.commit()
