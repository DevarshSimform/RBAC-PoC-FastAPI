from sqlalchemy.orm import Session

from app.models import RolePermission


class RolePermissionRepository:
    """Repository for role-permission related database operations."""

    def __init__(self, db: Session):
        self.db = db

    def get_existing_permission_ids(self, role_id: int) -> list[int]:
        """Return which permissions are already assigned to the role."""
        return (
            self.db.query(RolePermission.permission_id)
            .filter(RolePermission.role_id == role_id)
            .all()
        )

    def assign_permissions(
        self, role_id: int, permission_ids: list[int], granted_by: int
    ) -> None:
        """Assign permissions to a role."""
        for permission_id in permission_ids:
            new_role_permission = RolePermission(
                role_id=role_id,
                permission_id=permission_id,
                granted_by=granted_by,
            )
            self.db.add(new_role_permission)
        self.db.commit()
        self.db.flush()  # Ensure all changes are written to the database
        self.db.refresh(new_role_permission)

    def deassign_permissions(self, role_id: int, permission_ids: list[int]) -> None:
        """Deassign permissions from a role."""
        permissions_to_delete = (
            self.db.query(RolePermission)
            .filter(
                RolePermission.role_id == role_id,
                RolePermission.permission_id.in_(permission_ids),
            )
            .all()
        )
        if not permissions_to_delete:
            return False
        for permission in permissions_to_delete:
            self.db.delete(permission)
        self.db.commit()
        return True
