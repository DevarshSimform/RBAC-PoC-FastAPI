from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import check_permission, get_current_user_with_db
from app.models.user import User
from app.schemas.role_schema import CreateRoleRequest, RoleResponse, RoleUpdate
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
    _: bool = Depends(check_permission("role", "create")),
) -> RoleResponse:
    """Create a new role in the system."""

    user, db = user_with_db
    service = RoleService(db)
    return service.create_role(role_data, created_by=user.id)


@router.get(
    "/all",
    response_model=list[RoleResponse],
    tags=["Role"],
    description="Get all roles.",
)
def get_all_roles(
    user_with_db: tuple[User, Session] = Depends(get_current_user_with_db),
    _: bool = Depends(check_permission("role", "view")),
) -> list[RoleResponse]:
    """Retrieve all roles in the system."""

    _, db = user_with_db
    service = RoleService(db)
    return service.get_all_roles()


@router.get(
    "/{role_id}",
    response_model=RoleResponse,
    tags=["Role"],
    description="Get role details by ID.",
)
def get_role(
    role_id: int,
    user_with_db: tuple[User, Session] = Depends(get_current_user_with_db),
    _: bool = Depends(check_permission("role", "view")),
) -> RoleResponse:
    """Fetch details of a specific role by ID."""

    _, db = user_with_db
    service = RoleService(db)
    return service.retrieve_role(role_id)


@router.patch(
    "/update/{role_id}",
    response_model=RoleResponse,
    tags=["Role"],
    description="Update role details.",
)
def update_role(
    role_id: int,
    role_data: RoleUpdate,
    user_with_db: tuple[User, Session] = Depends(get_current_user_with_db),
    _: bool = Depends(check_permission("role", "update")),
) -> RoleResponse:
    """Update details of a specific role by ID."""

    _, db = user_with_db
    service = RoleService(db)
    return service.update_role(role_id, role_data)


@router.delete(
    "/delete/{role_id}",
    tags=["Role"],
    description="Delete a role by its ID.",
)
def delete_role(
    role_id: int,
    user_with_db: tuple[User, Session] = Depends(get_current_user_with_db),
    _: bool = Depends(check_permission("role", "delete")),
):
    """Delete a role from the system."""

    user, db = user_with_db
    service = RoleService(db)
    service.delete_role(role_id)
    return {
        "detail": f"Role with id {role_id} deleted successfully by user {user.email}."
    }
