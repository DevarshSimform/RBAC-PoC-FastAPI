from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.repositories.user_role_repo import UserRoleRepository


class UserRoleService:
    """Service layer for user-role related operations."""

    def __init__(self, db: Session):
        self.user_role_repo = UserRoleRepository(db)

    def assign_role_to_user(self, user_id: int, role_id: int, assignor_id: int) -> None:
        """Assign a role to a user."""
        existing_role_ids_for_user = self.user_role_repo.get_existing_role_ids(user_id)
        if role_id in existing_role_ids_for_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Role already assigned"
            )
        return self.user_role_repo.assign_roles(user_id, role_id, assignor_id)

    def get_assigned_roles(self, user_id: int) -> list[int]:
        """Get all roles assigned to a user."""
        existing_role_ids_for_user = self.user_role_repo.get_existing_role_ids(user_id)
        if not existing_role_ids_for_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No roles assigned to the user",
            )
        response = {
            "user_id": user_id,
            "role_ids": [role_id for role_id, in existing_role_ids_for_user],
        }
        return response

    def deassign_role_to_user(self, user_id: int, role_id: int) -> None:
        """Deassign a role to a user."""
        print(
            f"---------Inside deassign_role_to_user SERVICE: user_id={user_id}, role_id={role_id}---------"
        )
        deleted = self.user_role_repo.delete_user_role(user_id, role_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Role not found for the user",
            )
