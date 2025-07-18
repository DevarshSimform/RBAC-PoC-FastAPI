from app.repositories.resource_repo import ResourceRepository


class ResourceService:

    def __init__(self, db):
        self.resource_repo = ResourceRepository(db)

    def create_resource(self, module_id, forign_id):
        print(f"--------module_id = {module_id}--------")
        print(f"--------forign_id = {forign_id}--------")
        return 1
