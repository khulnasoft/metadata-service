"""
This module contains DTO models related to the EntityTag entity
"""

from pydantic import BaseModel

from app.api.v1.entity_tags.model import EntityTag
from app.api.v1.tag_groups.service import TagGroupService
from app.api.v1.tags.model import TagResponse
from app.api.v1.tags.service import TagService
from typing import Optional


class EntityTagCreateRequest(BaseModel):
    entity_id: str
    entity_type: str
    tag_id: int


class EntityTagDeleteRequest(BaseModel):
    entity_id: str
    tag_id: Optional[int] = None


class TagGroupTagsByNameRequest(BaseModel):
    tag_group_name: str
    tag_names: list[str]


class ResetEntityTagsByNameRequest(BaseModel):
    entity_id: str
    entity_type: str
    tag_groups: list[TagGroupTagsByNameRequest]


class ResetEntityTagsByNameResponse(BaseModel):
    entity_id: str
    entity_type: str
    tags: list[TagResponse]
    errors: list[str] = []


class EntityTagResponse(BaseModel):
    """Structure of the EntityTag entity to be returned in the API response (DTO)"""

    entity_id: str
    entity_type: str
    tag_id: int
    tag: TagResponse

    @classmethod
    def from_entity_tag(
        cls,
        entity_tag: EntityTag,
        tag_service: TagService,
        tag_group_service: TagGroupService,
    ):
        tag = tag_service.get(entity_tag.tag_id)

        return cls(
            entity_id=entity_tag.entity_id,
            entity_type=entity_tag.entity_type,
            tag_id=entity_tag.tag_id,
            tag=TagResponse.from_tag(tag, tag_group_service),
            # create_date=entity_tag.create_date,
        )
