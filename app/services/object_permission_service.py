from app.repositories.object_permission_repo import ObjectPermissionRepository


class ObjectPermissionService:

    def __init__(self, db):
        self.obj_perm_repo = ObjectPermissionRepository(db)

    def assign_object_permission_to_user(
        self, user_id, permission_id, resource_id, granted_by
    ):
        print(f"--------user = {user_id}--------")
        print(f"--------permission_id = {permission_id}--------")
        print(f"--------resource_id = {resource_id}--------")
        print(f"--------grantor_id = {granted_by}--------")
