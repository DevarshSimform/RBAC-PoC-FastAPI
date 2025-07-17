from typing import List

from pydantic import BaseModel


class AssignPermissionRequest(BaseModel):
    permission_ids: List[int]

    class Config:
        orm_mode = True


class DeAssignPermissionRequest(BaseModel):
    permission_ids: List[int]

    class Config:
        orm_mode = True


class RolePermissionItem(BaseModel):
    role_id: int
    permissions: List[int]

    class Config:
        orm_mode = True


class RolePermissionResponse(BaseModel):
    user_id: int
    roles: List[RolePermissionItem]

    class Config:
        orm_mode = True
