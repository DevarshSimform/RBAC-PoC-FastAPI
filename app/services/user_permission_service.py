from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.repositories.user_permission_repo import UserPermissionRepository


class UserPermissionService:
    """Service layer for user-permission related operations."""

    def __init__(self, db: Session):
        self.user_permission_repo = UserPermissionRepository(db)

    def assign_permission_to_user(
        self, user_id: int, permission_ids: list[int], granted_by: int
    ) -> None:
        """Assign permissions to a user."""

        existing_permissions_for_user = (
            self.user_permission_repo.get_existing_permission_ids(user_id)
        )
        if set(permission_ids).issubset(set(existing_permissions_for_user)):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Permissions already assigned to the user",
            )
        self.user_permission_repo.assign_user_permissions(
            user_id, permission_ids, granted_by
        )

    def deassign_permission_from_user(
        self, user_id: int, permission_ids: list[int]
    ) -> None:
        """Deassign permissions from a user."""

        deleted_permissions = self.user_permission_repo.deassign_user_permissions(
            user_id, permission_ids
        )
        if not deleted_permissions:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Permissions not found for the user.",
            )
