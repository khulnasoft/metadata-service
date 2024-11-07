"""
This file contains the integration tests for the tag_groups endpoints.
"""

from app.api.v1.tag_groups.model import TagGroupResponse, TagGroupCreateRequest
from app.common.base_entity.model import (
    AdvancedSearchRequest,
    FilterType,
    Filter,
    AdvancedSearchResponse,
    DeleteResponse,
)
from app.common.exceptions import ExceptionResponse
from tests.v1.integration.utils.utils import execute_and_validate_endpoint


def test_tag_groups():
    request = TagGroupCreateRequest(
        name="Teams group", description="Teams group description"
    )

    response = execute_and_validate_endpoint(
        "/api/v1/tag_groups", request, TagGroupResponse
    )
    assert response.description == request.description
    assert response.name == request.name

    search_response = execute_and_validate_endpoint(
        "/api/v1/tag_groups/advanced_search",
        AdvancedSearchRequest(
            filters=[
                Filter(
                    field="id",
                    field_type="string",
                    filter_type=FilterType.EQUALS,
                    values=[f"{response.id}"],
                )
            ]
        ),
        AdvancedSearchResponse[TagGroupResponse],
    )

    assert search_response.count == 1
    assert search_response.results[0].id == response.id

    get_response = execute_and_validate_endpoint(
        f"/api/v1/tag_groups/{response.id}", {}, TagGroupResponse, method="GET"
    )

    assert get_response.id == response.id
    assert get_response.name == response.name
    assert get_response.description == response.description

    # request that throws an error cant be tested successfully (even though it works)
    delete_response = execute_and_validate_endpoint(
        f"/api/v1/tag_groups/{response.id}", {}, DeleteResponse, method="DELETE"
    )
    assert delete_response.count == 1

    get_after_delete_response = execute_and_validate_endpoint(
        f"/api/v1/tag_groups/{response.id}",
        {},
        ExceptionResponse,
        method="GET",
        expected_status_code=404,
    )
    assert get_after_delete_response.error.code == 404
    assert (
        "not found" in get_after_delete_response.error.details.lower()
    ), "Expected 'not found' in the error message"
