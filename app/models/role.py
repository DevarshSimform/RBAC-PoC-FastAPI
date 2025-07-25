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

    # Relationships
    creator = relationship(
        "User", back_populates="created_roles", foreign_keys=[created_by]
    )
    user_roles = relationship(
        "UserRole", back_populates="role", foreign_keys="[UserRole.role_id]"
    )
    parent_role = relationship("Role", remote_side=[id], backref="child_roles")
