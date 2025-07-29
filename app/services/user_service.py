from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import create_access_token
from app.models.user import User
from app.repositories.permission_repo import PermissionRepository
from app.repositories.role_permission_repo import RolePermissionRepository
from app.repositories.role_repo import RoleRepository
from app.repositories.user_repo import UserRepository
from app.repositories.user_role_repo import UserRoleRepository
from app.schemas.permission_schema import PermissionResponse
from app.schemas.role_schema import RoleResponse
from app.schemas.user_schema import (
    RegisterUser,
    Token,
    UserRetrieveResponse,
    UserRolesPermissionsResponse,
    UserUpdate,
)


class UserService:
    """Service layer for user-related operations."""

    def __init__(self, db: Session):
        self.user_repo = UserRepository(db)

    def create_user(self, user_data: RegisterUser) -> User:
        """Create a new user in the database."""
        existing_user = self.user_repo.get_user_by_email(user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists.",
            )
        new_user = self.user_repo.create_user(user_data)
        if not new_user:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create user.",
            )
        return new_user

    def login_user(self, user_data: RegisterUser) -> User:
        """Authenticate a user and return a JWT token."""
        user = self.user_repo.authenticate_user(user_data)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        access_token = create_access_token(data={"sub": user.email})  # nosec
        return Token(access_token=access_token, token_type="bearer")  # nosec

    def get_all_users(self) -> list[User]:
        """Fetch all registered users."""
        users = self.user_repo.get_all_users()
        if not users:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="No users found."
            )
        return users

    def retrieve_user(self, user_id: int) -> User:
        """Fetch details of a specific user by ID."""
        user = self.user_repo.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found."
            )
        return user

    def update_user(self, user_id: int, user_update: UserUpdate) -> User:
        """Update user details in the database."""
        if not self.user_repo.get_user_by_id(user_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found."
            )
        user_dict = user_update.model_dump(exclude_unset=True)
        return self.user_repo.update_user_by_id(user_id, user_dict)

    def delete_user(self, user_id: int) -> None:
        """Delete a user by ID."""
        deleted = self.user_repo.delete_user_by_id(user_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found."
            )


class UserRolesPermissions:

    def __init__(self, db):
        self.user_repo = UserRepository(db)
        self.role_repo = RoleRepository(db)
        self.permission_repo = PermissionRepository(db)
        self.user_role_repo = UserRoleRepository(db)
        self.role_permission_repo = RolePermissionRepository(db)

    def get_roles_and_permissions(self, user_id):
        user = self.user_repo.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found."
            )
        user_schema = UserRetrieveResponse.from_orm(user)

        existing_role_ids_for_user = self.user_role_repo.get_existing_role_ids(user_id)
        role_ids = [role_id for (role_id,) in existing_role_ids_for_user]

        roles_schema = []

        for role_id in role_ids:
            role = self.role_repo.get_role_by_id(role_id)
            role_schema = RoleResponse.from_orm(role)
            roles_schema.append(role_schema)

        permission_ids = []
        for role_id in role_ids:
            raw_permissions = self.role_permission_repo.get_existing_permission_ids(
                role_id
            )
            permissions = [perm_id for (perm_id,) in raw_permissions]

            permission_ids.extend(permissions)

        permissions_schema = []

        for permission_id in permission_ids:
            permission = self.permission_repo.get_permission_by_id(permission_id)
            permission_schema = PermissionResponse.from_orm(permission)
            permissions_schema.append(permission_schema)

        return UserRolesPermissionsResponse(
            user_details=user_schema, roles=roles_schema, permissions=permissions_schema
        )
