from sqlalchemy import Column, DateTime, ForeignKey, Integer, String

from app.db.database import Base


class Resource(Base):
    __tablename__ = "resources"

    id = Column(Integer, primary_key=True, autoincrement=True)
    module_id = Column(String, ForeignKey("modules.id"), nullable=False)
    foreign_id = Column(String, nullable=False)
    created_at = Column(DateTime)
