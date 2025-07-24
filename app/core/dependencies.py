from typing import Optional

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.db.database import SessionLocal
from app.models import (
    Action,
    Module,
    ObjectPermission,
    Permission,
    Resource,
    RolePermission,
    User,
    UserRole,
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/user/login")


def get_db():
    """Dependency to get the database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user_with_db(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> User:
    """Dependency to get the current user from the token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired token",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_access_token(token)
    if payload is None or "sub" not in payload:
        raise credentials_exception

    user = db.query(User).filter(User.email == payload["sub"]).first()
    if not user:
        raise credentials_exception

    return (
        user,
        db,
    )


def check_permission(
    module_name: str,
    action_name: str,
    resource_id_param: Optional[str] = None,
):
    def checker(
        request: Request,
        user_with_db: tuple = Depends(get_current_user_with_db),
    ):
        user, db = user_with_db

        # --- Resolve Permission ---
        module = db.query(Module).filter_by(name=module_name).first()
        action = db.query(Action).filter_by(name=action_name).first()

        if not module or not action:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid module or action name",
            )

        permission = (
            db.query(Permission)
            .filter_by(module_id=module.id, action_id=action.id)
            .first()
        )

        if not permission:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission not found for {module_name}:{action_name}",
            )

        # --- Check Role-Level Permissions ---
        role_ids = db.query(UserRole.role_id).filter_by(user_id=user.id).all()
        role_ids = [r[0] for r in role_ids]

        has_role_permission = (
            db.query(RolePermission)
            .filter(
                RolePermission.role_id.in_(role_ids),
                RolePermission.permission_id == permission.id,
            )
            .first()
        )

        if has_role_permission:
            return True

        # --- Check Object-Level Permissions (if applicable) ---
        if resource_id_param:
            # Try to extract resource_id from path or query
            resource_value = request.path_params.get(
                resource_id_param
            ) or request.query_params.get(resource_id_param)

            if not resource_value:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Missing `{resource_id_param}` for object-level permission check.",
                )

            # Find resource by module + foreign_id
            resource = (
                db.query(Resource)
                .filter_by(module_id=module.id, foreign_id=resource_value)
                .first()
            )

            if resource:
                object_permission = (
                    db.query(ObjectPermission)
                    .filter_by(
                        user_id=user.id,
                        resource_id=resource.id,
                        permission_id=permission.id,
                    )
                    .first()
                )
                if object_permission:
                    return True

        # --- Final Denial ---
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access denied: missing permission for '{module_name}:{action_name}'",
        )

    return checker
