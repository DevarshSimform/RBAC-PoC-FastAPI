from sqlalchemy import Column, DateTime, ForeignKey, Integer, String

from app.db.database import Base


class Module(Base):
    __tablename__ = "modules"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime)
    created_by = Column(String, ForeignKey("users.id"))
