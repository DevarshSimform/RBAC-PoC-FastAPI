import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, UniqueConstraint

from app.db.database import Base


class ObjectPermission(Base):
    __tablename__ = "object_permissions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    resource_id = Column(Integer, ForeignKey("resources.id"), nullable=False)
    permission_id = Column(Integer, ForeignKey("permissions.id"), nullable=False)
    granted_by = Column(Integer, ForeignKey("users.id"))
    granted_at = Column(DateTime, default=datetime.datetime.utcnow)
    expires_at = Column(DateTime)

    __table_args__ = (
        UniqueConstraint("user_id", "resource_id", "permission_id", name="uq_obj_perm"),
    )
