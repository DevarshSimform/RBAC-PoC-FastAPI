from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models import Role
from app.repositories.role_repo import RoleRepository
from app.schemas.role_schema import CreateRoleRequest, RoleResponse, RoleUpdate


class RoleService:
    """Service layer for role-related operations."""

    def __init__(self, db: Session):
        self.role_repo = RoleRepository(db)

    def get_role_by_name(self, role_name: str) -> Role:
        """Fetch a role by its name."""
        role = self.role_repo.get_role_by_name(role_name)
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Role not found."
            )
        return role

    def create_role(self, role_data: CreateRoleRequest, created_by: int) -> Role:
        """Create a new role in the database."""
        if self.role_repo.get_role_by_name(role_data.name):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Role with this name already exists.",
            )

        # parent_role_id stays None if not provided
        return self.role_repo.create_role(role_data, created_by=created_by)

    def get_all_roles(self) -> list[RoleResponse]:
        """Retrieve all roles from the database."""
        roles = self.role_repo.get_all_roles()
        if not roles:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="No roles found."
            )
        return roles

    def retrieve_role(self, role_id: int) -> Role:
        """Fetch details of a specific role by ID."""
        role = self.role_repo.get_role_by_id(role_id)
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Role not found."
            )
        return role

    def update_role(self, role_id: int, role_date: RoleUpdate) -> Role:
        """Update role details in the database."""
        if not self.role_repo.get_role_by_id(role_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Role not found."
            )
        role_dict = role_date.model_dump(exclude_unset=True)
        return self.role_repo.update_role_by_id(role_id, role_dict)

    def delete_role(self, role_id: int) -> None:
        """Delete a role by its ID."""
        deleted = self.role_repo.delete_role_by_id(role_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Role not found."
            )
