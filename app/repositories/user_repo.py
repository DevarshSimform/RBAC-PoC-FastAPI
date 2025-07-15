from datetime import datetime

from sqlalchemy.orm import Session

from app.core.security import get_password_hash, verify_password
from app.models.user import User
from app.schemas.user_schema import LoginUser


class UserRepository:
    """Repository for user-related database operations."""

    def __init__(self, db: Session):
        self.db = db

    def get_user_by_email(self, email: str) -> User:
        """Fetch a user by their email address."""
        return self.db.query(User).filter(User.email == email).first()

    def create_user(self, user_data: User) -> User:
        """Create a new user in the database."""
        new_user = User(
            firstname=user_data.firstname,
            lastname=user_data.lastname,
            email=user_data.email,
            password_hash=get_password_hash(user_data.password),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        self.db.add(new_user)
        self.db.commit()
        self.db.refresh(new_user)
        return new_user

    def authenticate_user(self, user_login: LoginUser):
        """Authenticate a user by email and password."""
        user = self.db.query(User).filter_by(email=user_login.email).first()
        if not user or not verify_password(user_login.password, user.password_hash):
            return False
        user.last_login = datetime.now()
        self.db.commit()
        return user

    def get_all_users(self) -> list[User]:
        """Fetch all users from the database."""
        return self.db.query(User).all()

    def get_user_by_id(self, user_id: int) -> User:
        """Fetch a user by their ID."""
        return self.db.query(User).filter(User.id == user_id).first()

    def update_user_by_id(self, user_id: int, user_data: dict) -> User:
        """Update user details in the database."""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return None
        for key, value in user_data.items():
            if hasattr(user, key):
                setattr(user, key, value)
        user.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(user)
        return user

    def delete_user_by_id(self, user_id: int) -> bool:
        """Delete a user by their ID."""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return False
        self.db.delete(user)
        self.db.commit()
        return True
