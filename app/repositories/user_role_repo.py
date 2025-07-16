from datetime import datetime

from sqlalchemy.orm import Session

from app.models import UserRole


class UserRoleRepository:
    """Repository for user-role related database operations."""

    def __init__(self, db: Session):
        self.db = db

    def get_existing_role_ids(self, user_id: int) -> list[int]:
        """Return which roles are already assigned to the user"""
        return self.db.query(UserRole.role_id).filter(UserRole.user_id == user_id).all()

    def assign_roles(self, user_id: int, role_id: int, assigner_id: int):
        """Assign a role to a user."""
        new_user_role = UserRole(
            user_id=user_id,
            role_id=role_id,
            assigned_by=assigner_id,
            assigned_at=datetime.utcnow(),
        )
        self.db.add(new_user_role)
        self.db.commit()
        self.db.refresh(new_user_role)
        return new_user_role

    def delete_user_role(self, user_id, role_id):
        """Delete a user role association."""
        print(
            f"---------Inside delete_user_role REPO: user_id={user_id}, role_id={role_id}---------"
        )
        user_role = (
            self.db.query(UserRole)
            .filter(UserRole.user_id == user_id, UserRole.role_id == role_id)
            .first()
        )
        print(f"---------user_role={user_role}---------")
        if not user_role:
            return False
        self.db.delete(user_role)
        self.db.commit()
        return True
