"""
This module contains the service layer (business logic) for the Tags entity.
It uses the repository layer to interact with the database.
"""

from typing import Optional

from sqlalchemy.orm import Session

from app.api.v1.tag_groups.model import TagGroup
from app.api.v1.tags.model import Tag, TagCreateRequest
from app.api.v1.tags.repository import TagRepository
from app.common.base_entity.model import AdvancedSearchRequest, AdvancedSearchResponse
from app.common.database import get_db
from app.common.utils.logging_utils import get_logger
from fastapi import Depends

logger = get_logger()


class TagService:
    """TagService"""

    def __init__(self, repository: TagRepository):
        self.repository = repository

    def create(self, tag_create: TagCreateRequest) -> Tag:
        # Convert the schema to a model instance
        tag = Tag(**tag_create.model_dump())
        return self.repository.create(tag)

    def get(self, tag_id: int) -> Optional[Tag]:
        return self.repository.get(tag_id)

    def update(self, tag_id: int, tag_update: TagCreateRequest) -> Optional[Tag]:
        tag = self.repository.get(tag_id)
        if tag is None:
            return None
        #  what if I have fields I dont want to update (createdOn vs updatedOn)?
        #  why is there no update in the repository
        for key, value in tag_update.model_dump().items():
            setattr(tag, key, value)

        return self.repository.create(tag)

    def delete(self, tag_id: int) -> int:
        return self.repository.delete_by_id(tag_id)

    def advanced_search(
        self, search_req: AdvancedSearchRequest
    ) -> AdvancedSearchResponse[Tag]:
        return self.repository.advanced_search(search_req)

    def find_by_unique_fields(self, field: str, value: str) -> Optional[Tag]:
        return self.repository.find_by_unique_field(field, value)

    def find_by_name_or_create(self, name: str, tag_group: TagGroup) -> Tag:
        tag = self.find_by_unique_fields("name", name)

        if not tag:
            logger.debug(f"Tag {name} does not exist. Creating new tag")
            tag = self.create(TagCreateRequest(name=name, tag_group_id=tag_group.id))
        elif tag.tag_group_id != tag_group.id:
            raise ValueError(f"Tag {name} already exists in another group")

        return tag

    def delete_tags_with_no_entities(self) -> int:
        return self.repository.delete_tags_with_no_entities()


def get_tag_service(db: Session = Depends(get_db)) -> TagService:
    repository = TagRepository(db)
    return TagService(repository)
