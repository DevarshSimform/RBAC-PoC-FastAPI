import datetime

from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.orm import relationship

from app.db.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    firstname = Column(String, nullable=False)
    lastname = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    last_login = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(
        DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow
    )

    roles = relationship(
        "UserRole",
        back_populates="user",
        cascade="all, delete-orphan",
        foreign_keys="[UserRole.user_id]",
    )
    created_roles = relationship(
        "Role", back_populates="creator", foreign_keys="Role.created_by"
    )
    assigned_roles = relationship(
        "UserRole", back_populates="assigner", foreign_keys="[UserRole.assigned_by]"
    )
    user_permissions = relationship(
        "UserPermission",
        back_populates="user",
        cascade="all, delete-orphan",
        foreign_keys="[UserPermission.user_id]",
    )
    granted_permissions = relationship(
        "UserPermission",
        back_populates="grantor",
        foreign_keys="[UserPermission.granted_by]",
    )
