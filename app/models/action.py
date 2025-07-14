from sqlalchemy import Column, DateTime, ForeignKey, Integer, String

from app.db.database import Base


class Action(Base):
    __tablename__ = "actions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime)
    created_by = Column(String, ForeignKey("users.id"))
