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


class RolePermissionResponse(BaseModel):
    role_id: int
    permission_ids: List[int]

    class Config:
        orm_mode = True
