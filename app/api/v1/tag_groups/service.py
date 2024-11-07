"""
This module contains the service layer (business logic) for the TagGroups entity.
It uses the repository layer to interact with the database.
"""

from typing import Optional
from app.api.v1.tag_groups.model import (
    TagGroup,
    TagGroupCreateRequest,
)
from app.api.v1.tag_groups.repository import TagGroupRepository
from app.common.base_entity.model import (
    FilterType,
    AdvancedSearchRequest,
    AdvancedSearchResponse,
)
from app.common.utils.logging_utils import get_logger

logger = get_logger()


class TagGroupService:
    """TagGroupService"""

    def __init__(self, repository: TagGroupRepository):
        self.repository = repository

    def create(self, tag_group_create: TagGroupCreateRequest) -> TagGroup:
        # Convert the schema to a model instance
        tag_group = TagGroup(**tag_group_create.model_dump())
        return self.repository.create(tag_group)

    def get(self, tag_group_id: int) -> Optional[TagGroup]:
        return self.repository.get(tag_group_id)

    def advanced_search(
        self, search_req: AdvancedSearchRequest
    ) -> AdvancedSearchResponse[TagGroup]:
        return self.repository.advanced_search(search_req)

    def search(
        self,
        field: str,
        value: str,
        search_type: str = FilterType.CONTAINS,
        is_case_sensitive: bool = False,
    ) -> list[TagGroup]:
        return self.repository.search(field, value, search_type, is_case_sensitive)

    def update(
        self, tag_group_id: int, tag_group_update: TagGroupCreateRequest
    ) -> Optional[TagGroup]:
        tag_group = self.repository.get(tag_group_id)
        if tag_group is None:
            return None

        for key, value in tag_group_update.model_dump().items():
            setattr(tag_group, key, value)

        return self.repository.create(tag_group)

    def delete(self, tag_group_id: int) -> int:
        return self.repository.delete_by_id(tag_group_id)

    def find_by_unique_fields(self, field: str, value: str) -> Optional[TagGroup]:
        return self.repository.find_by_unique_field(field, value)

    def find_by_name_or_create(self, name: str) -> TagGroup:
        tag_group = self.find_by_unique_fields("name", name)

        if not tag_group:
            logger.debug(f"TagGroup {name} does not exist. Creating new tag group")
            tag_group = self.create(
                TagGroupCreateRequest(name=name, description=f"{name} description")
            )
        return tag_group
