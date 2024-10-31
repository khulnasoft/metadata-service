"""
This module contains the service layer (business logic) for the EntityTags entity.
It uses the repository layer to interact with the database.
"""

from typing import List
from app.api.v1.entity_tags.types import (
    EntityTag,
    EntityTagCreateRequest,
    EntityTagDeleteRequest,
    ResetEntityTagsByNameRequest,
    ResetEntityTagsByNameResponse,
)
from app.api.v1.entity_tags.repository import EntityTagRepository
from app.api.v1.tag_groups.service import TagGroupService
from app.api.v1.tags.model import Tag, TagResponse
from app.api.v1.tags.service import TagService
from app.common.base_entity.model import (
    AdvancedSearchResponse,
    AdvancedSearchRequest,
)
from app.common.utils.logging_utils import get_logger

logger = get_logger()


class EntityTagService:
    """
    Business logic to Entity Tag operations
    """

    def __init__(self, repository: EntityTagRepository):
        self.repository = repository

    def create(self, create_request: EntityTagCreateRequest) -> EntityTag:
        # Convert the schema to a model instance
        partial_model = EntityTag(**create_request.model_dump())
        return self.repository.create(partial_model)

    def advanced_search(
        self, search_req: AdvancedSearchRequest
    ) -> AdvancedSearchResponse[EntityTag]:
        return self.repository.advanced_search(search_req)

    def delete(self, delete_request: EntityTagDeleteRequest) -> int:
        if not delete_request.tag_id:
            return self.repository.clear_entity_tags(delete_request.entity_id)
        else:
            return self.repository.delete_entity_tag(
                delete_request.entity_id, delete_request.tag_id
            )

    def reset_entity_tags_by_name(
        self,
        request: ResetEntityTagsByNameRequest,
        tag_service: TagService,
        tag_group_service: TagGroupService,
    ) -> ResetEntityTagsByNameResponse:

        tags_created: List[Tag] = []
        errors: List[str] = []

        logger.debug(f"Resetting tags for entity {request.entity_id}")

        logger.debug(f"Deleting existing tags for entity: {request.entity_id}")
        deleted = self.delete(EntityTagDeleteRequest(entity_id=request.entity_id))
        logger.debug(f"Deleted {deleted} tags for entity: {request.entity_id}")

        for tag_group_req in request.tag_groups:
            try:
                logger.debug(f"Looking for tag group: {tag_group_req.tag_group_name}")
                tag_group = tag_group_service.find_by_name_or_create(
                    name=tag_group_req.tag_group_name
                )
                logger.debug(f"Found tag group: {tag_group.name}")
                for tag_name in tag_group_req.tag_names:
                    try:
                        logger.debug(f"Looking for tag: {tag_name}")
                        tag = tag_service.find_by_name_or_create(
                            name=tag_name, tag_group=tag_group
                        )
                        logger.debug(f"Found tag: {tag.name}")
                        logger.debug(
                            f"Creating entity tag for: {request.entity_id} / {tag.name}"
                        )
                        entity_tag = self.create(
                            EntityTagCreateRequest(
                                entity_id=request.entity_id,
                                entity_type=request.entity_type,
                                tag_id=tag.id,
                            )
                        )
                        logger.debug(f"Created entity tag: {entity_tag}")
                        if entity_tag:
                            tags_created.append(tag)
                        logger.debug(f"Tags created: {tags_created}")
                    # pylint: disable=broad-except
                    except Exception as e:
                        err = f"Error creating tag: {tag_name} - {e}"
                        logger.error(err)
                        errors.append(err)
            # pylint: disable=broad-except
            except Exception as e:
                err = f"Error creating tag group: {tag_group_req.tag_group_name} - {e}"
                logger.error(err)
                errors.append(err)

        return ResetEntityTagsByNameResponse(
            entity_id=request.entity_id,
            entity_type=request.entity_type,
            tags=[TagResponse.from_tag(tag, tag_group_service) for tag in tags_created],
            errors=errors,
        )
