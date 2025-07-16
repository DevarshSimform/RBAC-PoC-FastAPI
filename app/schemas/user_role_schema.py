from pydantic import BaseModel, conlist


class AssignRolesRequest(BaseModel):
    role_id: int


class UnassignRolesRequest(BaseModel):
    role_id: int


class UserRoleResponse(BaseModel):
    user_id: int
    role_ids: conlist(int)

    class Config:
        orm_mode = True
