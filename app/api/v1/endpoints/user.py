from typing import Annotated

from fastapi import APIRouter, Body, Depends, Form
from sqlalchemy.orm import Session

from app.core.dependencies import check_permission, get_current_user_with_db
from app.db.database import get_db
from app.schemas.user_schema import (
    LoginUser,
    RegisterUser,
    RegisterUserResponse,
    Token,
    UserRetrieveResponse,
    UserUpdate,
)
from app.services.user_service import UserService

router = APIRouter(prefix="/user")


@router.post(
    "/register",
    response_model=RegisterUserResponse,
    tags=["User"],
    description="Register a new user.",
)
def register_user(
    user: RegisterUser, db: Session = Depends(get_db)
) -> RegisterUserResponse:
    """Register a new user in the system."""

    serivce = UserService(db)
    return serivce.create_user(user)


@router.post(
    "/login",
    response_model=Token,
    deprecated=True,
    tags=["User"],
    description="Login with form data, returns JWT token.",
)
def login_user(
    user: Annotated[LoginUser, Form()], db: Session = Depends(get_db)
) -> Token:
    """Authenticate a user and return a JWT token."""

    service = UserService(db)
    return service.login_user(user)


@router.get(
    "/all",
    response_model=list[RegisterUserResponse],
    tags=["Admin"],
    description="Get all registered users.",
)
def get_all_users(
    user_with_db: tuple[UserRetrieveResponse, Session] = Depends(
        get_current_user_with_db
    ),
    _: bool = Depends(check_permission("user", "view")),
) -> list[RegisterUserResponse]:
    """Fetch all registered users."""

    user, db = user_with_db
    print(f"----------User = {user.email}----------")
    service = UserService(db)
    return service.get_all_users()


@router.get(
    "/{user_id}",
    response_model=UserRetrieveResponse,
    tags=["Admin"],
    description="Admins fetch specific user details.",
)
def get_user(
    user_id: int,
    user_with_db: tuple[UserRetrieveResponse, Session] = Depends(
        get_current_user_with_db
    ),
    _: bool = Depends(check_permission("user", "view")),
) -> UserRetrieveResponse:
    """Fetch details of a specific user by ID."""

    user, db = user_with_db
    service = UserService(db)
    return service.retrieve_user(user_id)


@router.patch(
    "/",
    response_model=UserRetrieveResponse,
    tags=["Admin"],
    description="Update current user profile.",
)
def update_user(
    user_data: Annotated[UserUpdate, Body()],
    user_with_db: tuple[UserRetrieveResponse, Session] = Depends(
        get_current_user_with_db
    ),
    _: bool = Depends(check_permission("user", "update")),
) -> UserRetrieveResponse:
    """Update user details in the database."""

    user, db = user_with_db
    service = UserService(db)
    return service.update_user(user.id, user_data)


@router.delete("/", tags=["Admin"], description="Superadmin deletes a user.")
def delete_user(
    user_id: int,
    user_with_db: tuple[UserRetrieveResponse, Session] = Depends(
        get_current_user_with_db
    ),
    _: bool = Depends(check_permission("user", "delete")),
):
    """Delete a user from the system."""

    user, db = user_with_db
    service = UserService(db)
    service.delete_user(user_id)
    return {"detail": f"User with id {user_id} deleted successfully by {user.email}."}
