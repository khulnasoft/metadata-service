"""
This module contains the repository layer (database operations)
for the TagGroups entity.
"""

from sqlalchemy.orm import Session
from app.common.base_entity.repository import BaseRepository
from app.api.v1.tag_groups.model import (
    TagGroup,
)


class TagGroupRepository(BaseRepository[TagGroup]):
    """
    Provides methods to perform CRUD operations
    """

    def __init__(self, db: Session):
        super().__init__(db, TagGroup)

    def delete_by_id(self, tag_group_id: int) -> int:
        deleted_rows = (
            self.db.query(self.model).filter(self.model.id == tag_group_id).delete()
        )
        self.db.commit()
        return deleted_rows
