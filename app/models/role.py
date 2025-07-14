from sqlalchemy import Column, DateTime, ForeignKey, Integer, String

from app.db.database import Base


class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(String)
    parent_role_id = Column(String, ForeignKey("roles.id"), nullable=True)
    created_at = Column(DateTime)
    created_by = Column(String, ForeignKey("users.id"))
