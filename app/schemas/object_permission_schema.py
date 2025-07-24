from pydantic import BaseModel


class AssignObjectPermissionRequest(BaseModel):
    user_id: int
    module_id: int
    forign_id: int
    permission_id: int


class DeassignObjectPermissionRequest(BaseModel):
    user_id: int
    module_id: int
    forign_id: int
    permission_id: int
