from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user_with_db, has_permission
from app.models import User
from app.schemas.user_role_schema import (
    AssignRolesRequest,
    UnassignRolesRequest,
    UserRoleResponse,
)
from app.services.user_role_service import UserRoleService

router = APIRouter(prefix="/user-role")


@router.post(
    "/assign",
    response_model=None,
    tags=["User Role"],
    description="Assign a role to a user.",
)
def assign_role_to_user(
    user_id: int,
    body: AssignRolesRequest,
    user_with_db: tuple[User, Session] = Depends(get_current_user_with_db),
    _: bool = Depends(has_permission("user_roles", "create")),
) -> None:
    """Assign a role to a user."""

    user, db = user_with_db
    service = UserRoleService(db)
    service.assign_role_to_user(user_id, body.role_id, assignor_id=user.id)
    return {"message": "Role assigned successfully."}


@router.get(
    "/assigned-roles",
    response_model=UserRoleResponse,
    tags=["User Role"],
    description="Get all roles assigned to a user.",
)
def get_assigned_roles(
    user_id: int,
    user_with_db: tuple[User, Session] = Depends(get_current_user_with_db),
    _: bool = Depends(has_permission("user_roles", "read")),
) -> UserRoleResponse:
    """Get all roles assigned to a user."""

    _, db = user_with_db
    service = UserRoleService(db)
    return service.get_assigned_roles(user_id)


@router.get(
    "/my-role",
    response_model=UserRoleResponse,
    tags=["User Role"],
    description="Logged in user roles.",
)
def get_my_roles(
    user_with_db: tuple[User, Session] = Depends(get_current_user_with_db),
    _: bool = Depends(has_permission("user_roles", "read")),
) -> UserRoleResponse:
    """Get all roles assigned to a user."""

    user, db = user_with_db
    service = UserRoleService(db)
    return service.get_assigned_roles(user.id)


@router.delete(
    "/deassign",
    response_model=None,
    tags=["User Role"],
    description="Deassign a role to a user.",
)
def deassign_role_to_user(
    user_id: int,
    body: UnassignRolesRequest,
    user_with_db: tuple[User, Session] = Depends(get_current_user_with_db),
    _: bool = Depends(has_permission("user_roles", "delete")),
) -> None:
    """Deassign a role to a user."""

    _, db = user_with_db
    service = UserRoleService(db)
    service.deassign_role_to_user(user_id, body.role_id)
    return {"message": "Role deassigned successfully"}
