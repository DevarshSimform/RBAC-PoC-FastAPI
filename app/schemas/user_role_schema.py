from typing import List

from pydantic import BaseModel


class AssignRolesRequest(BaseModel):
    role_id: int


class UnassignRolesRequest(BaseModel):
    role_id: int


class UserRoleResponse(BaseModel):
    user_id: int
    role_ids: List[int]

    class Config:
        from_attributes = True
