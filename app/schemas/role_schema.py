from typing import Optional

from pydantic import BaseModel


class CreateRoleRequest(BaseModel):
    name: str
    description: Optional[str] = None


class RoleResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]

    class Config:
        orm_mode = True


class RoleUpdate(BaseModel):
    name: str
    description: str

    class Config:
        orm_mode = True
