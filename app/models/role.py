import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.db.database import Base


class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(String)
    parent_role_id = Column(
        Integer, ForeignKey("roles.id"), nullable=True, default=None
    )
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    created_by = Column(Integer, ForeignKey("users.id"))

    parent_role = relationship("Role", remote_side=[id], backref="child_roles")
    creator = relationship(
        "User", back_populates="created_roles", foreign_keys=[created_by]
    )
    users = relationship(
        "UserRole", back_populates="role", cascade="all, delete-orphan"
    )
    role_permissions = relationship(
        "RolePermission", back_populates="role", cascade="all, delete-orphan"
    )
