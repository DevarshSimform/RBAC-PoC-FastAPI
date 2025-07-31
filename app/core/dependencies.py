import time
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
    Role,
    RolePermission,
    User,
    UserPermission,
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


def has_role(required_role: str):
    """
    Dependency to check if the current user has a specific role.
    Usage: _: bool = Depends(has_role("admin"))
    """

    def checker(user_with_db: tuple[User, Session] = Depends(get_current_user_with_db)):
        user, db = user_with_db

        # Fetch all roles assigned to this user
        role_names = (
            db.query(Role.name)
            .join(UserRole, Role.id == UserRole.role_id)
            .filter(UserRole.user_id == user.id)
            .all()
        )
        role_names = {r[0] for r in role_names}  # convert to set of names

        if required_role not in role_names:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied: User does not have the '{required_role}' role",
            )

        return True

    return checker


def has_permission(
    module_name: str,
    action_name: str,
    resource_id_param: Optional[str] = None,
):
    """
    Dependency to check if the current user has a specific permission.
    """

    def checker(
        request: Request,
        user_with_db: tuple = Depends(get_current_user_with_db),
    ):
        start_time = time.perf_counter()  # ⏱ start timing
        try:
            user, db = user_with_db

            # --- Resolve Module, Action & Permission ---
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

            # 1) Get all permissions directly assigned to the user
            user_permission_ids = {
                p.permission_id
                for p in db.query(UserPermission.permission_id)
                .filter_by(user_id=user.id)
                .all()
            }

            # 2) Get all permissions from roles
            role_ids = [
                r[0]
                for r in db.query(UserRole.role_id).filter_by(user_id=user.id).all()
            ]
            role_permission_ids = {
                rp.permission_id
                for rp in db.query(RolePermission.permission_id)
                .filter(RolePermission.role_id.in_(role_ids))
                .all()
            }

            # 3) Union of both sets (user-level + role-level)
            all_permission_ids = user_permission_ids.union(role_permission_ids)

            # 4) Check if the required permission exists in the union
            if permission.id in all_permission_ids:
                return True

            # 5) If not found yet, check object-level permissions (if applicable)
            if resource_id_param:
                resource_value = request.path_params.get(
                    resource_id_param
                ) or request.query_params.get(resource_id_param)

                if not resource_value:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Missing `{resource_id_param}` for object-level permission check.",
                    )

                resource = (
                    db.query(Resource)
                    .filter_by(module_id=module.id, foreign_id=resource_value)
                    .first()
                )

                if resource:
                    obj_perm = (
                        db.query(ObjectPermission)
                        .filter_by(
                            user_id=user.id,
                            resource_id=resource.id,
                            permission_id=permission.id,
                        )
                        .first()
                    )
                    if obj_perm:
                        return True

            # If no permission is found
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied: missing permission for '{module_name}:{action_name}'",
            )

        finally:
            end_time = time.perf_counter()
            duration_ms = (end_time - start_time) * 1000
            print(
                f"-------------------------⏳ Permission check for '{module_name}:{action_name}' took {duration_ms:.2f} ms -------------------------"
            )

    return checker


# module_cache = {}
# action_cache = {}

# def has_permission(module_name: str, action_name: str, resource_id_param: Optional[str] = None):
#     def checker(request: Request, user_with_db: tuple = Depends(get_current_user_with_db)):
#         start_time = time.perf_counter()
#         try:
#             user, db = user_with_db

#             # 1) Cache Modules/Actions (in-memory or Redis)
#             module = module_cache.get(module_name) or db.query(Module).filter_by(name=module_name).first()
#             action = action_cache.get(action_name) or db.query(Action).filter_by(name=action_name).first()

#             if not module or not action:
#                 raise HTTPException(status_code=400, detail="Invalid module or action")

#             # 2) Fetch Permission ID (also cacheable)
#             permission = db.query(Permission).filter_by(module_id=module.id, action_id=action.id).first()
#             if not permission:
#                 raise HTTPException(status_code=403, detail=f"Permission not found for {module_name}:{action_name}")

#             # 3) Check cached permissions in request
#             if hasattr(request.state, "perm_cache"):
#                 all_permission_ids = request.state.perm_cache
#             else:
#                 # Batch fetch user + role permissions in one query
#                 rows = (
#                     db.query(Permission.id)
#                     .outerjoin(RolePermission, RolePermission.permission_id == Permission.id)
#                     .outerjoin(UserRole, UserRole.role_id == RolePermission.role_id)
#                     .outerjoin(UserPermission, UserPermission.permission_id == Permission.id)
#                     .filter((UserRole.user_id == user.id) | (UserPermission.user_id == user.id))
#                     .distinct()
#                     .all()
#                 )
#                 all_permission_ids = {r[0] for r in rows}
#                 request.state.perm_cache = all_permission_ids

#             # 4) Check if permission is granted
#             if permission.id in all_permission_ids:
#                 return True

#             # 5) Object-Level Permission (only if needed)
#             if resource_id_param:
#                 resource_value = request.path_params.get(resource_id_param) or request.query_params.get(resource_id_param)
#                 if not resource_value:
#                     raise HTTPException(status_code=400, detail=f"Missing `{resource_id_param}`")

#                 obj_perm_exists = (
#                     db.query(ObjectPermission.id)
#                     .join(Resource, Resource.id == ObjectPermission.resource_id)
#                     .filter(
#                         ObjectPermission.user_id == user.id,
#                         Resource.module_id == module.id,
#                         Resource.foreign_id == resource_value,
#                         ObjectPermission.permission_id == permission.id,
#                     )
#                     .first()
#                 )
#                 if obj_perm_exists:
#                     return True

#             raise HTTPException(status_code=403, detail=f"Access denied for '{module_name}:{action_name}'")
#         finally:
#             end_time = time.perf_counter()
#             duration_ms = (end_time - start_time) * 1000
#             print(
#                 f"-------------------------⏳ Permission check for '{module_name}:{action_name}' took {duration_ms:.2f} ms -------------------------"
#             )

#     return checker
