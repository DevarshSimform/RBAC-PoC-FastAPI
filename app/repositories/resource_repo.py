from sqlalchemy.orm import Session


class ResourceRepository:

    def __init__(self, db: Session):
        self.db = db
