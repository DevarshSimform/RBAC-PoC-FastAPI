from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, UniqueConstraint

from app.db.database import Base


class UserRole(Base):
    __tablename__ = "user_roles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    role_id = Column(String, ForeignKey("roles.id"), nullable=False)
    assigned_by = Column(String, ForeignKey("users.id"))
    assigned_at = Column(DateTime)

    __table_args__ = (UniqueConstraint("user_id", "role_id", name="uq_user_role"),)
