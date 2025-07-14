import uvicorn
from fastapi import FastAPI

from app.db.database import Base, engine
from app.models import (  # noqa: F401
    action,
    audit_log,
    module,
    object_permission,
    permission,
    resource,
    role,
    role_permission,
    user,
    user_role,
)

app = FastAPI(title="RBAC PoC FastAPI", version="0.1.0")


@app.get("/")
def read_root():
    return {"message": "Welcome to RBAC PoC FastAPI!"}


@app.on_event("startup")
def startup():
    """Create database tables on startup"""
    Base.metadata.create_all(bind=engine)


def main():
    """Main entry point for the FastAPI application"""
    print("Hello from rbac-poc-fastapi!")
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)  # nosec B104


if __name__ == "__main__":
    main()
