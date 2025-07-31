from typing import List

from pydantic import BaseModel


class AssignUserPermissionRequest(BaseModel):
    permission_ids: List[int]

    class Config:
        from_attributes = True


class DeAssignUserPermissionRequest(BaseModel):
    permission_ids: List[int]

    class Config:
        from_attributes = True
