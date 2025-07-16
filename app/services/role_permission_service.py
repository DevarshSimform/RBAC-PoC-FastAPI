from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.repositories.role_permission_repo import RolePermissionRepository


class RolePermissionService:
    """Service layer for role-permission related operations."""

    def __init__(self, db: Session):
        self.role_permission_repo = RolePermissionRepository(db)

    def assign_permission_to_role(
        self, role_id: int, permission_ids: list[int], granted_by: int
    ) -> None:
        """Assign permissions to a role."""
        existing_permissions_for_role = (
            self.role_permission_repo.get_existing_permission_ids(role_id)
        )
        if set(permission_ids).issubset(set(existing_permissions_for_role)):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Permissions already assigned to the role",
            )
        self.role_permission_repo.assign_permissions(
            role_id, permission_ids, granted_by
        )
        print(f"Role ID: {role_id}, Permission IDs: {permission_ids}")

    def deassign_permission_from_role(
        self, role_id: int, permission_ids: list[int]
    ) -> None:
        """Deassign permissions from a role."""
        deleted_permissions = self.role_permission_repo.deassign_permissions(
            role_id, permission_ids
        )
        if not deleted_permissions:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Permissions not found for the role",
            )
