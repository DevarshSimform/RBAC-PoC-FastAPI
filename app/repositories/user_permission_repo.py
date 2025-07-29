from sqlalchemy.orm import Session

from app.models import UserPermission


class UserPermissionRepository:
    """Repository for user-permission related database operations."""

    def __init__(self, db: Session):
        self.db = db

    def get_existing_permission_ids(self, user_id: int) -> list[int]:
        """Return which permissions are already assigned to the user."""
        return (
            self.db.query(UserPermission.permission_id)
            .filter(UserPermission.user_id == user_id)
            .all()
        )

    def assign_user_permissions(
        self, user_id: int, permission_ids: list[int], granted_by: int
    ) -> None:
        """Assign permissions to a user."""
        for permission_id in permission_ids:
            new_user_permission = UserPermission(
                user_id=user_id,
                permission_id=permission_id,
                granted_by=granted_by,
            )
            self.db.add(new_user_permission)
        self.db.commit()
        self.db.flush()
        self.db.refresh(new_user_permission)
