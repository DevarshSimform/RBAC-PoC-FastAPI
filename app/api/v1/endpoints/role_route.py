from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user_with_db
from app.models.user import User
from app.schemas.role_schema import CreateRoleRequest, RoleResponse
from app.services.role_service import RoleService

router = APIRouter(prefix="/role")


@router.post(
    "/create",
    response_model=RoleResponse,
    tags=["Role"],
    description="Create a new role.",
)
def create_role(
    role_data: CreateRoleRequest,
    user_with_db: tuple[User, Session] = Depends(get_current_user_with_db),
) -> RoleResponse:
    """Create a new role in the system."""

    user, db = user_with_db
    service = RoleService(db)
    return service.create_role(role_data, created_by=user.id)
