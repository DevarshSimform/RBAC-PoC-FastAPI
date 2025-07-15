from sqlalchemy.orm import Session

from app.models import Role


class RoleRepository:
    """Repository for role-related database operations."""

    def __init__(self, db: Session):
        self.db = db

    def get_role_by_name(self, role_name: str):
        """Fetch a role by its name."""
        return self.db.query(Role).filter(Role.name == role_name).first()

    def create_role(self, role_data, created_by: int) -> Role:
        """Create a new role in the database."""
        new_role = Role(
            name=role_data.name,
            description=getattr(role_data, "description", None),
            parent_role_id=getattr(role_data, "parent_role_id", None),
            created_by=created_by,
        )
        self.db.add(new_role)
        self.db.commit()
        self.db.refresh(new_role)
        return new_role
