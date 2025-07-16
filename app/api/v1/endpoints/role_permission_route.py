from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import check_permission, get_current_user_with_db
from app.models import User
from app.schemas.role_permission_schema import (
    AssignPermissionRequest,
    DeAssignPermissionRequest,
)
from app.services.role_permission_service import RolePermissionService

router = APIRouter(prefix="/role-permission")


@router.post(
    "/assign",
    response_model=None,
    tags=["Role Permission"],
    description="Assign a permission to a role.",
)
def assign_permission_to_role(
    role_id: int,
    body: AssignPermissionRequest,
    user_with_db: tuple[User, Session] = Depends(get_current_user_with_db),
    _: bool = Depends(check_permission("role_permission", "create")),
) -> None:
    """Assign a permission to a role."""

    user, db = user_with_db
    service = RolePermissionService(db)
    service.assign_permission_to_role(role_id, body.permission_ids, granted_by=user.id)
    return {"message": "Permissions assigned successfully."}


@router.delete(
    "/deassign",
    response_model=None,
    tags=["Role Permission"],
    description="Deassign a permission from a role.",
)
def dessign_permission_from_role(
    role_id: int,
    body: DeAssignPermissionRequest,
    user_with_db: tuple[User, Session] = Depends(get_current_user_with_db),
    _: bool = Depends(check_permission("role_permission", "delete")),
) -> None:
    """Deassign a permission from a role."""

    user, db = user_with_db
    service = RolePermissionService(db)
    service.deassign_permission_from_role(role_id, body.permission_ids)
    return {"message": "Permissions deassigned successfully."}
