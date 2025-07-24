from typing import Optional

from sqlalchemy.orm import Session

from app.models import Resource


class ResourceRepository:

    def __init__(self, db: Session):
        self.db = db

    def get_or_create_resource(self, module_id: int, foreign_id: int) -> int:
        resource = (
            self.db.query(Resource)
            .filter_by(module_id=module_id, foreign_id=foreign_id)
            .first()
        )
        if resource:
            return resource.id

        new_resource = Resource(module_id=module_id, foreign_id=foreign_id)
        self.db.add(new_resource)
        self.db.commit()
        self.db.refresh(new_resource)
        return new_resource.id

    def get_by_module_and_foreign_id(
        self, module_id: int, foreign_id: int
    ) -> Optional[Resource]:
        return (
            self.db.query(Resource)
            .filter_by(module_id=module_id, foreign_id=foreign_id)
            .first()
        )

    def delete_resource(self, resource_id: int) -> None:
        resource = self.db.query(Resource).get(resource_id)
        if resource:
            self.db.delete(resource)
            self.db.commit()
