from sqlalchemy import Column, DateTime, ForeignKey, Integer, String

from app.db.database import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    action = Column(String)
    target_type = Column(String)
    target_id = Column(String)
    timestamp = Column(DateTime)
    details = Column(String)
