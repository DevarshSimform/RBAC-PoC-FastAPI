from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, UniqueConstraint

from app.db.database import Base


class ObjectPermission(Base):
    __tablename__ = "object_permissions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    resource_id = Column(String, ForeignKey("resources.id"), nullable=False)
    permission_id = Column(String, ForeignKey("permissions.id"), nullable=False)
    granted_by = Column(String, ForeignKey("users.id"))
    granted_at = Column(DateTime)
    expires_at = Column(DateTime)

    __table_args__ = (
        UniqueConstraint("user_id", "resource_id", "permission_id", name="uq_obj_perm"),
    )
