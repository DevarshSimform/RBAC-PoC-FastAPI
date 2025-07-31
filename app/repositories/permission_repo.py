from sqlalchemy.orm import Session

from app.models import Permission


class PermissionRepository:

    def __init__(self, db: Session):
        self.db = db

    def get_permission_by_id(self, permission_id):
        return self.db.query(Permission).filter(Permission.id == permission_id).first()
