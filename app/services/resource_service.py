from fastapi import HTTPException, status

from app.models import Resource
from app.repositories.resource_repo import ResourceRepository


class ResourceService:

    def __init__(self, db):
        self.resource_repo = ResourceRepository(db)

    def create_resource(self, module_id: int, foreign_id: int) -> int:
        return self.resource_repo.get_or_create_resource(module_id, foreign_id)

    def get_or_error(self, module_id: int, foreign_id: int) -> Resource:
        resource = self.resource_repo.get_by_module_and_foreign_id(
            module_id, foreign_id
        )
        if not resource:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Resource not found."
            )
        return resource
