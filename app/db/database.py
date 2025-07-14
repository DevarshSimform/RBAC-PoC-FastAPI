from decouple import config
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

# Load DB URL from .env using python-decouple
DATABASE_URL = config("DATABASE_URL")

# Create SQLAlchemy engine
engine = create_engine(DATABASE_URL, pool_pre_ping=True, echo=True)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Base class for ORM models
class Base(DeclarativeBase):
    pass


def get_db():
    """Dependency to get a database session"""
    with SessionLocal() as db:
        yield db
