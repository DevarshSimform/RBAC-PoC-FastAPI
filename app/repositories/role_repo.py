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
            created_by=created_by,
        )
        self.db.add(new_role)
        self.db.commit()
        self.db.refresh(new_role)
        return new_role

    def get_all_roles(self) -> list[Role]:
        """Retrieve all roles from the database."""
        return self.db.query(Role).all()

    def get_role_by_id(self, role_id: int) -> Role:
        """Fetch a role by its ID."""
        return self.db.query(Role).filter(Role.id == role_id).first()

    def update_role_by_id(self, role_id: int, role_data: dict) -> Role:
        """Update role details in the database."""
        role = self.db.query(Role).filter(Role.id == role_id).first()
        if not role:
            return None
        for key, value in role_data.items():
            if hasattr(role, key):
                setattr(role, key, value)
        self.db.commit()
        self.db.refresh(role)
        return role

    def delete_role_by_id(self, role_id: int) -> None:
        """Delete a role by its ID."""
        role = self.db.query(Role).filter(Role.id == role_id).first()
        if not role:
            return False
        self.db.delete(role)
        self.db.commit()
        return True
