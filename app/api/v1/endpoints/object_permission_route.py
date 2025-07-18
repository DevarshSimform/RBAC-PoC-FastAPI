from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import check_permission, get_current_user_with_db
from app.models import User
from app.schemas.object_permission_schema import AssignObjectPermissionRequest
from app.services.object_permission_service import ObjectPermissionService
from app.services.resource_service import ResourceService

router = APIRouter(prefix="/object-permission")


@router.post(
    "/assign",
    response_model=None,
    tags=["Object Permission"],
    description="Assign a object permission to a user.",
)
def assign_object_permission_to_user(
    body: AssignObjectPermissionRequest,
    user_with_db: tuple[User, Session] = Depends(get_current_user_with_db),
    _: bool = Depends(check_permission("object_permissions", "create")),
) -> None:
    """Assign a object permission to a user."""

    user, db = user_with_db
    r_service = ResourceService(db)
    obj_service = ObjectPermissionService(db)
    resource_id = r_service.create_resource(body.module_id, body.forign_id)
    obj_service.assign_object_permission_to_user(
        body.user_id, body.permission_id, resource_id, granted_by=user.id
    )
    return {"message": "Object Permission assigned successfully"}
