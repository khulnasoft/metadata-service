"""
This module contains the controller (endpoints) for the EntityTags entity.
It handles all API/HTTP related issues.
It uses the service layer to perform the business logic.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session


from app.api.v1.entity_tags.repository import EntityTagRepository
from app.api.v1.entity_tags.service import EntityTagService
from app.api.v1.tag_groups.controller import get_tag_group_service
from app.api.v1.tag_groups.service import TagGroupService
from app.api.v1.tags.controller import get_tag_service
from app.api.v1.tags.service import TagService
from app.common.base_entity.model import (
    AdvancedSearchRequest,
    AdvancedSearchResponse,
    DeleteResponse,
    BulkResponse,
    ErrorItem,
    SuccessItem,
)
from app.common.database import get_db
from app.api.v1.entity_tags.types import (
    EntityTagResponse,
    EntityTagCreateRequest,
    EntityTag,
    EntityTagDeleteRequest,
    ResetEntityTagsByNameResponse,
    ResetEntityTagsByNameRequest,
)

from app.common.utils.logging_utils import get_logger

logger = get_logger()

router = APIRouter()


def get_entity_tag_service(db: Session = Depends(get_db)) -> EntityTagService:
    repository = EntityTagRepository(db)
    return EntityTagService(repository)


def convert_advanced_search_response(
    response: AdvancedSearchResponse[EntityTag],
    tag_service=Depends(get_tag_service),
    tag_group_service=Depends(get_tag_group_service),
) -> AdvancedSearchResponse[EntityTagResponse]:
    entity_tag_responses = [
        EntityTagResponse.from_entity_tag(entity_tag, tag_service, tag_group_service)
        for entity_tag in response.results
    ]
    return AdvancedSearchResponse[EntityTagResponse](
        results=entity_tag_responses,
        count=response.count,
        offset=response.offset,
        count_total=response.count_total,
    )


@router.post("/entity_tags", response_model=EntityTagResponse)
def create_entity_tag(
    create_request: EntityTagCreateRequest,
    tag_service: TagService = Depends(get_tag_service),
    tag_group_service: TagGroupService = Depends(get_tag_group_service),
    entity_tag_service: EntityTagService = Depends(get_entity_tag_service),
):
    try:
        created: EntityTag = entity_tag_service.create(create_request)
        return EntityTagResponse.from_entity_tag(
            created, tag_service, tag_group_service
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    # todo: remove error handling when global error is working


@router.post(
    "/entity_tags/advanced_search",
    response_model=AdvancedSearchResponse[EntityTagResponse],
)
def advanced_search(
    search_request: AdvancedSearchRequest,
    tag_service: TagService = Depends(get_tag_service),
    tag_group_service: TagGroupService = Depends(get_tag_group_service),
    entity_tag_service: EntityTagService = Depends(get_entity_tag_service),
):
    try:
        advanced_search_response = entity_tag_service.advanced_search(search_request)
        converted = convert_advanced_search_response(
            advanced_search_response, tag_service, tag_group_service
        )
        return converted
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.post("/entity_tags/delete", response_model=DeleteResponse)
def delete(
    delete_request: EntityTagDeleteRequest,
    entity_tag_service: EntityTagService = Depends(get_entity_tag_service),
):
    try:
        deleted_count = entity_tag_service.delete(delete_request)

        if deleted_count == 0:
            raise HTTPException(status_code=404, detail="No Tags found for entity")

        return DeleteResponse(count=deleted_count)

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.post(
    "/entity_tags/delete/bulk",
    response_model=BulkResponse[EntityTagDeleteRequest, DeleteResponse],
)
def delete_bulk(
    delete_requests: List[EntityTagDeleteRequest],
    response: Response,
    entity_tag_service: EntityTagService = Depends(get_entity_tag_service),
):
    bulk_response = BulkResponse(
        success=[],
        errors=[],
    )

    for delete_request in delete_requests:
        try:
            deleted_count = entity_tag_service.delete(delete_request)

            if deleted_count == 0:
                bulk_response.errors.append(
                    ErrorItem(req=delete_request, errors=["No Tags found for entity"])
                )
            else:
                bulk_response.success.append(
                    SuccessItem(
                        req=delete_request, res=DeleteResponse(count=deleted_count)
                    )
                )
        # pylint: disable=broad-except
        except Exception as e:
            bulk_response.errors.append(ErrorItem(req=delete_request, errors=[str(e)]))

    if bulk_response.success and not bulk_response.errors:
        response.status_code = status.HTTP_200_OK
    if bulk_response.success and bulk_response.errors:
        response.status_code = status.HTTP_207_MULTI_STATUS
    elif not bulk_response.success and bulk_response.errors:
        response.status_code = status.HTTP_400_BAD_REQUEST

    return bulk_response


@router.post("/entity_tags/reset", response_model=List[ResetEntityTagsByNameResponse])
def reset(
    reset_requests: list[ResetEntityTagsByNameRequest],
    entity_tag_service: EntityTagService = Depends(get_entity_tag_service),
    tag_service: TagService = Depends(get_tag_service),
    tag_group_service: TagGroupService = Depends(get_tag_group_service),
):
    results = []
    for reset_request in reset_requests:
        try:

            reset_entity_response = entity_tag_service.reset_entity_tags_by_name(
                reset_request, tag_service, tag_group_service
            )

            results.append(reset_entity_response)
        # pylint: disable=broad-except
        except Exception as e:
            logger.debug(
                f"Error resetting tags by name for entity {reset_request.entity_id} \
                - {e}"
            )

    return results
