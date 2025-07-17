from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.repositories.role_permission_repo import RolePermissionRepository
from app.repositories.user_role_repo import UserRoleRepository
from app.schemas.role_permission_schema import (
    RolePermissionItem,
    RolePermissionResponse,
)


class RolePermissionService:
    """Service layer for role-permission related operations."""

    def __init__(self, db: Session):
        self.role_permission_repo = RolePermissionRepository(db)
        self.user_role_repo = UserRoleRepository(db)

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

    def get_assigned_permissions(self, user_id: int) -> RolePermissionResponse:
        """Get all permissions assigned to each role of a user."""

        # Step 1: Get all role IDs assigned to the user and flatten them
        raw_role_ids = self.user_role_repo.get_existing_role_ids(user_id)
        role_ids = [role_id for (role_id,) in raw_role_ids]
        if not role_ids:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No roles assigned to the user",
            )
        # Step 2: For each role, get permissions and flatten them too
        roles_with_permissions = []
        for role_id in role_ids:
            raw_permissions = self.role_permission_repo.get_existing_permission_ids(
                role_id
            )
            permissions = [perm_id for (perm_id,) in raw_permissions]
            if not permissions:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"No permissions assigned to role {role_id}",
                )
            roles_with_permissions.append(
                RolePermissionItem(role_id=role_id, permissions=permissions)
            )
        # Step 3: Return structured response
        return RolePermissionResponse(user_id=user_id, roles=roles_with_permissions)

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
