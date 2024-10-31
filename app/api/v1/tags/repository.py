"""
This module contains the repository layer (database operations) for the Tags entity.
"""

from sqlalchemy.orm import Session

from app.api.v1.entity_tags.model import EntityTag
from app.api.v1.tags.model import Tag
from app.common.base_entity.repository import BaseRepository
from app.common.utils.logging_utils import get_logger

logger = get_logger()


class TagRepository(BaseRepository[Tag]):
    """
    Provides methods to perform CRUD operations
    """

    def __init__(self, db: Session):
        super().__init__(db, Tag)

    def delete_tags_with_no_entities(self) -> int:
        ghost_tags = (
            self.db.query(Tag)
            .outerjoin(EntityTag, Tag.id == EntityTag.tag_id)
            # pylint: disable=singleton-comparison
            .filter(EntityTag.entity_id == None)  # noqa: E711
            .all()
        )

        ghost_tag_ids = [tag.id for tag in ghost_tags]
        logger.debug(
            f"Deleting {len(ghost_tags)} tags with no entities: {ghost_tag_ids}"
        )

        count = len(ghost_tags)
        for tag in ghost_tags:
            logger.debug(f"Deleting tag {tag}")
            self.db.delete(tag)
        self.db.commit()
        return count
