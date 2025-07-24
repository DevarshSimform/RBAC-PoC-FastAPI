from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import ObjectPermission


class ObjectPermissionRepository:

    def __init__(self, db: Session):
        self.db = db

    def get_object_permission(
        self, user_id: int, permission_id: int, resource_id: int
    ) -> ObjectPermission | None:
        return (
            self.db.query(ObjectPermission)
            .filter_by(
                user_id=user_id, permission_id=permission_id, resource_id=resource_id
            )
            .first()
        )

    def assign_object_permission_to_user(
        self, user_id, permission_id, resource_id, granted_by
    ):
        obj_perm = ObjectPermission(
            user_id=user_id,
            permission_id=permission_id,
            resource_id=resource_id,
            granted_by=granted_by,
        )
        self.db.add(obj_perm)
        try:
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            raise ValueError(
                "Permission already assigned to this user for this resource."
            )
        return obj_perm

    def delete_object_permission(
        self, user_id: int, permission_id: int, resource_id: int
    ) -> None:
        obj_perm = self.get_object_permission(user_id, permission_id, resource_id)
        if obj_perm:
            self.db.delete(obj_perm)
            self.db.commit()

    def count_by_resource_id(self, resource_id: int) -> int:
        return (
            self.db.query(ObjectPermission).filter_by(resource_id=resource_id).count()
        )
