from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, UniqueConstraint

from app.db.database import Base


class RolePermission(Base):
    __tablename__ = "role_permissions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    role_id = Column(String, ForeignKey("roles.id"), nullable=False)
    permission_id = Column(String, ForeignKey("permissions.id"), nullable=False)
    granted_by = Column(String, ForeignKey("users.id"))
    granted_at = Column(DateTime)

    __table_args__ = (
        UniqueConstraint("role_id", "permission_id", name="uq_role_permission"),
    )
