import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, UniqueConstraint

from app.db.database import Base


class Permission(Base):
    __tablename__ = "permissions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(String)
    module_id = Column(Integer, ForeignKey("modules.id"), nullable=False)
    action_id = Column(Integer, ForeignKey("actions.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    created_by = Column(Integer, ForeignKey("users.id"))

    __table_args__ = (
        UniqueConstraint("module_id", "action_id", name="uq_module_action"),
    )
