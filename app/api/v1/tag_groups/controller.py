"""
This module contains the controller for the TagGroup entity.
It handles all http requests related to the TagGroup entity.
It uses the TagGroupService to perform the business logic.
"""

from readyapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.v1.tag_groups.model import (
    TagGroupResponse,
    TagGroupCreateRequest,
    TagGroup,
)
from app.api.v1.tag_groups.repository import TagGroupRepository
from app.api.v1.tag_groups.service import TagGroupService
from app.common.database import get_db
from app.common.base_entity.model import (
    AdvancedSearchRequest,
    AdvancedSearchResponse,
    DeleteResponse,
)

router = APIRouter()


# Dependency function to provide TagGroupService
def get_tag_group_service(db: Session = Depends(get_db)) -> TagGroupService:
    repository = TagGroupRepository(db)
    return TagGroupService(repository)


def convert_advanced_search_response(
    response: AdvancedSearchResponse[TagGroup],
) -> AdvancedSearchResponse[TagGroupResponse]:
    tag_group_responses = [
        TagGroupResponse.from_tag_group(tag_group) for tag_group in response.results
    ]
    return AdvancedSearchResponse[TagGroupResponse](
        results=tag_group_responses,
        count=response.count,
        offset=response.offset,
        count_total=response.count_total,
    )


@router.post("/tag_groups", response_model=TagGroupResponse)
def create_tag_group(
    create_request: TagGroupCreateRequest,
    service: TagGroupService = Depends(get_tag_group_service),
):
    try:
        created: TagGroup = service.create(create_request)
        return TagGroupResponse.from_tag_group(created)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.get("/tag_groups/{tag_group_id}", response_model=TagGroupResponse)
def get_tag_group(
    tag_group_id: int, service: TagGroupService = Depends(get_tag_group_service)
):
    tag_group = service.get(tag_group_id)
    if tag_group is None:
        raise HTTPException(status_code=404, detail="Tag group not found")
    return TagGroupResponse.from_tag_group(tag_group)


@router.put("/tag_groups/{tag_group_id}", response_model=TagGroupResponse)
def update_tag_group(
    tag_group_id: int,
    tag_group: TagGroupCreateRequest,
    service: TagGroupService = Depends(get_tag_group_service),
):
    try:
        updated: TagGroup = service.update(tag_group_id, tag_group)
        return TagGroupResponse.from_tag_group(updated)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.post(
    "/tag_groups/advanced_search",
    response_model=AdvancedSearchResponse[TagGroupResponse],
)
def advanced_search(
    search_req: AdvancedSearchRequest,
    service: TagGroupService = Depends(get_tag_group_service),
) -> AdvancedSearchResponse[TagGroupResponse]:
    try:
        advanced_search_response = service.advanced_search(search_req)
        return convert_advanced_search_response(advanced_search_response)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.delete("/tag_groups/{tag_group_id}")
def delete_tag_group(
    tag_group_id: int, service: TagGroupService = Depends(get_tag_group_service)
):
    deleted_count = service.delete(tag_group_id)

    if deleted_count == 0:
        raise HTTPException(status_code=404, detail="Tag group not found")

    return DeleteResponse(count=deleted_count)
