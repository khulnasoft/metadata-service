"""
An integration test that mimics the typical way RAG uses metadata service
"""

from enum import Enum
from typing import List, Union

from app.api.v1.entity_tags.types import (
    EntityTagDeleteRequest,
    EntityTagResponse,
    ResetEntityTagsByNameRequest,
    ResetEntityTagsByNameResponse,
)
from app.api.v1.tags.model import TagResponse
from app.common.base_entity.model import (
    AdvancedSearchRequest,
    AdvancedSearchResponse,
    BulkResponse,
    DeleteResponse,
    Filter,
    FilterType,
)

# need to import all fixtures for the to be discovered by pytest
# pylint: disable=unused-import
from tests.v1.integration.rag_flow.utils import get_reset_requests_tag_names
from tests.v1.integration.utils.utils import execute_and_validate_endpoint


def assert_reset_entity_tags(
    reset_requests: List[ResetEntityTagsByNameRequest],
) -> List[ResetEntityTagsByNameResponse]:
    entities = execute_and_validate_endpoint(
        "/api/v1/entity_tags/reset", reset_requests, List[ResetEntityTagsByNameResponse]
    )
    assert len(entities) == len(reset_requests), "Mismatch in number of entities"
    # Check that the response matches the request
    for request in reset_requests:
        # Check that entity is in the response
        entity = next(
            (ent for ent in entities if ent.entity_id == request.entity_id), None
        )
        assert (
            entity is not None
        ), f"Entity with ID {request.entity_id} not found in response"

        # Check that it has the correct tags
        request_tags = get_reset_requests_tag_names([request])

        response_tags = {tag.name for tag in entity.tags}
        assert (
            request_tags == response_tags
        ), f"Tags mismatch for entity {request.entity_id}"

        # Ensure there are no errors
        assert entity.errors == [], f"Unexpected errors for entity {request.entity_id}"
    return entities


# TODO: add operator type
def assert_tags_search_results(
    expected_tag_names: list[str],
    advanced_search_request: AdvancedSearchRequest,
) -> List[TagResponse]:
    tags_search_response = execute_and_validate_endpoint(
        "/api/v1/tags/advanced_search",
        advanced_search_request,
        AdvancedSearchResponse[TagResponse],
    )
    found_tags = tags_search_response.results

    assert len(found_tags) == len(expected_tag_names), "Mismatch in number of entities"

    for tag_name in expected_tag_names:
        assert any(
            tag.name == tag_name for tag in found_tags
        ), f"Tag '{tag_name}' not found in search results"

    return found_tags


def assert_tags_advanced_search(
    reset_requests_param: List[ResetEntityTagsByNameRequest],
) -> List[TagResponse]:
    tags_search_response = execute_and_validate_endpoint(
        "/api/v1/tags/advanced_search",
        AdvancedSearchRequest(),
        AdvancedSearchResponse[TagResponse],
    )
    tags = tags_search_response.results

    assert len(tags) == 6, "Mismatch in number of entities"

    expected_tags = get_reset_requests_tag_names(reset_requests_param)
    for tag_name in expected_tags:
        assert any(
            tag.name == tag_name for tag in tags
        ), f"Tag '{tag_name}' not found in search results"

    return tags


class SetOperator(Enum):
    IN = "in"
    NOT_IN = "not_in"
    EQUALS = "equals"


def search_entities_by_tags(
    tags_or_ids: List[Union[TagResponse, int]],
) -> AdvancedSearchResponse[EntityTagResponse]:
    # Determine if the input is a list of TagResponse or a list of tag IDs
    if all(isinstance(tag, TagResponse) for tag in tags_or_ids):
        # Extract tag IDs from TagResponse objects
        tag_ids_str = [str(tag.id) for tag in tags_or_ids]
    elif all(isinstance(tag, int) for tag in tags_or_ids):
        # Use the tag IDs directly
        tag_ids_str = [str(tag) for tag in tags_or_ids]
    else:
        raise ValueError(
            "Input must be a list of TagResponse objects or a list of tag IDs"
        )

    return execute_and_validate_endpoint(
        "/api/v1/entity_tags/advanced_search",
        AdvancedSearchRequest(
            filters=[
                Filter(
                    field="tag_id",
                    field_type="string",
                    filter_type=FilterType.EQUALS,
                    values=tag_ids_str,
                )
            ]
        ),
        AdvancedSearchResponse[EntityTagResponse],
    )


def assert_entity_search_by_tags(
    expected_entities: List[ResetEntityTagsByNameResponse],
    search_by_tags: List[Union[TagResponse, int]],
    operator: SetOperator = SetOperator.IN,
):
    entity_tags_search_response: AdvancedSearchResponse[EntityTagResponse] = (
        search_entities_by_tags(search_by_tags)
    )
    response_entity_ids_set = {
        entity_tag.entity_id for entity_tag in entity_tags_search_response.results
    }
    expected_entity_ids_set = {entity.entity_id for entity in expected_entities}

    if operator == SetOperator.IN:
        assert expected_entity_ids_set.issubset(
            response_entity_ids_set
        ), f"Expected entities not found in search results for tags: '{search_by_tags}'"
    elif operator == SetOperator.EQUALS:
        assert expected_entity_ids_set == response_entity_ids_set
    elif operator == SetOperator.NOT_IN:
        assert expected_entity_ids_set.isdisjoint(
            response_entity_ids_set
        ), f"Expected entities not found in search results for tags: '{search_by_tags}'"
    else:
        raise ValueError(f"Unsupported operator: {operator}")


def assert_delete_tags_wit_no_entities_works() -> DeleteResponse:
    return execute_and_validate_endpoint(
        "/tags/delete_tags_with_no_entities",
        {},
        DeleteResponse,
    )


def assert_entity_tags_bulk_delete(
    entities_to_delete: list[ResetEntityTagsByNameResponse],
) -> BulkResponse[EntityTagDeleteRequest, DeleteResponse]:
    delete_requests = [
        EntityTagDeleteRequest(entity_id=entity.entity_id)
        for entity in entities_to_delete
    ]

    delete_bulk_response = execute_and_validate_endpoint(
        "/api/v1/entity_tags/delete/bulk",
        delete_requests,
        BulkResponse[EntityTagDeleteRequest, DeleteResponse],
    )

    assert (
        len(delete_bulk_response.success) == len(delete_requests)
    ), f"Expected {len(delete_requests)} delete requests, but got {len(delete_bulk_response.success)}"
    assert (
        len(delete_bulk_response.errors) == 0
    ), f"Expected no errors, but got {len(delete_bulk_response.errors)}"

    return delete_bulk_response


def assert_delete_tags_with_no_entities(expected_deleted_count) -> DeleteResponse:
    delete_tags_response = execute_and_validate_endpoint(
        "/api/v1/tags/delete_tags_with_no_entities", {}, DeleteResponse
    )
    assert (
        delete_tags_response.count == expected_deleted_count
    ), f"Expected {expected_deleted_count} tags to be deleted, but got {delete_tags_response.count}"

    return delete_tags_response


def assert_entities_exist_as_expected(
    expected_entities: list[ResetEntityTagsByNameResponse],
):
    for entity in expected_entities:
        # when searching by all the entity tags together, the entity is returned
        assert_entity_search_by_tags([entity], entity.tags, SetOperator.IN)
        # when searching by each tag separately, the entity is returned
        for tag in entity.tags:
            assert_entity_search_by_tags([entity], [tag], SetOperator.IN)
            # when searching by repo_name tag (unique), we expect only one result
            if tag.tag_group.name == "repo_name":
                assert_entity_search_by_tags([entity], [tag], SetOperator.EQUALS)


# Alternative is to keep fixtures in conftest.py, but I prefer to keep them locally
# pylint: disable=redefined-outer-name
def test_flow(rag_flow_reset_requests, capability_tag_group):
    # WA for pytest fixture typing issues
    reset_requests: List[ResetEntityTagsByNameRequest] = rag_flow_reset_requests

    # 1. reset tags
    reset_response_entities = assert_reset_entity_tags(reset_requests)

    # 2. search with no parameters yields all tags
    all_tags = assert_tags_search_results(
        expected_tag_names=list(get_reset_requests_tag_names(reset_requests)),
        advanced_search_request=AdvancedSearchRequest(),
    )

    # 3. search for tags that start with "cap" return the capability tags only
    assert_tags_search_results(
        capability_tag_group.tag_names,
        AdvancedSearchRequest(
            filters=[
                Filter(
                    field="name",
                    field_type="string",
                    filter_type=FilterType.STARTS_WITH,
                    values=["cap"],
                )
            ]
        ),
    )

    # 4. Entities are found correctly when searching by tags
    assert_entities_exist_as_expected(expected_entities=reset_response_entities)

    # 5. when searching by a tag that doesn't exist, no entities are returned
    assert_entity_search_by_tags([], [99999], SetOperator.EQUALS)

    # bulk delete
    assert_entity_tags_bulk_delete(entities_to_delete=reset_response_entities)

    # delete unused tags should delete all tags
    assert_delete_tags_with_no_entities(expected_deleted_count=len(all_tags))

    # search for tags should return no results after deleting all tags
    assert_tags_search_results(
        expected_tag_names=[], advanced_search_request=AdvancedSearchRequest()
    )
