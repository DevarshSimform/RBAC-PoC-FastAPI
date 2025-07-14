from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, UniqueConstraint

from app.db.database import Base


class Permission(Base):
    __tablename__ = "permissions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(String)
    module_id = Column(String, ForeignKey("modules.id"), nullable=False)
    action_id = Column(String, ForeignKey("actions.id"), nullable=False)
    created_at = Column(DateTime)
    created_by = Column(String, ForeignKey("users.id"))

    __table_args__ = (
        UniqueConstraint("module_id", "action_id", name="uq_module_action"),
    )
