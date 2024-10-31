"""
This module contains the repository layer (database operations)
for the EntityTags entity.
"""

from sqlalchemy.orm import Session

from app.api.v1.entity_tags.model import EntityTag
from app.common.base_entity.repository import BaseRepository


class EntityTagRepository(BaseRepository[EntityTag]):
    """
    Provides methods to perform CRUD operations
    """

    def __init__(self, db: Session):
        super().__init__(db, EntityTag)

    def clear_entity_tags(self, entity_id: str) -> int:
        rows_deleted = (
            self.db.query(self.model).filter(self.model.entity_id == entity_id).delete()
        )
        self.db.commit()
        return rows_deleted

    def delete_entity_tag(self, entity_id: str, tag_id: int) -> int:
        rows_deleted = (
            self.db.query(self.model)
            .filter(self.model.entity_id == entity_id, self.model.tag_id == tag_id)
            .delete()
        )
        self.db.commit()
        return rows_deleted
