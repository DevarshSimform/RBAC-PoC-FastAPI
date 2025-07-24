from fastapi import HTTPException, status

from app.repositories.object_permission_repo import ObjectPermissionRepository
from app.repositories.resource_repo import ResourceRepository


class ObjectPermissionService:

    def __init__(self, db):
        self.obj_perm_repo = ObjectPermissionRepository(db)
        self.resource_repo = ResourceRepository(db)

    def assign_object_permission_to_user(
        self, user_id, permission_id, resource_id, granted_by
    ):
        existing = self.obj_perm_repo.get_object_permission(
            user_id, permission_id, resource_id
        )
        if existing:
            raise HTTPException(
                detail="Permission already assigned.",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        return self.obj_perm_repo.assign_object_permission_to_user(
            user_id=user_id,
            permission_id=permission_id,
            resource_id=resource_id,
            granted_by=granted_by,
        )

    def deassign_object_permission_from_user(
        self, user_id: int, permission_id: int, resource_id: int
    ) -> None:
        exists = self.obj_perm_repo.get_object_permission(
            user_id, permission_id, resource_id
        )
        if not exists:
            raise HTTPException(status_code=404, detail="Object permission not found.")

        self.obj_perm_repo.delete_object_permission(user_id, permission_id, resource_id)

        count = self.obj_perm_repo.count_by_resource_id(resource_id)
        if count == 0:
            self.resource_repo.delete_resource(resource_id)
