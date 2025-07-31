from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user_with_db, has_permission
from app.models import User
from app.schemas.user_permission_schema import (
    AssignUserPermissionRequest,
    DeAssignUserPermissionRequest,
)
from app.services.user_permission_service import UserPermissionService

router = APIRouter(prefix="/user-permission")


@router.post(
    "/assign",
    response_model=None,
    tags=["User Permission"],
    description="Assign a permission to user.",
)
def assign_permission_to_user(
    user_id: int,
    body: AssignUserPermissionRequest,
    user_with_db: tuple[User, Session] = Depends(get_current_user_with_db),
    _: bool = Depends(has_permission("user_permissions", "create")),
) -> None:
    """Assign a permission to a role."""

    user, db = user_with_db
    service = UserPermissionService(db)
    service.assign_permission_to_user(user_id, body.permission_ids, granted_by=user.id)
    return {"message": "Permissions assigned to user successfully."}


@router.delete(
    "/deassign",
    response_model=None,
    tags=["User Permission"],
    description="Deassign a permission to a user.",
)
def deassign_permission_from_user(
    user_id: int,
    body: DeAssignUserPermissionRequest,
    user_with_db: tuple[User, Session] = Depends(get_current_user_with_db),
    _: bool = Depends(has_permission("role_permissions", "delete")),
) -> None:
    """Deassign a permission from a user."""
    user, db = user_with_db
    service = UserPermissionService(db)
    service.deassign_permission_from_user(user_id, body.permission_ids)
    return {"message": "Permissions deassigned successfully."}
