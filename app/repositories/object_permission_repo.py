from sqlalchemy.orm import Session


class ObjectPermissionRepository:

    def __init__(self, db: Session):
        self.db = db
