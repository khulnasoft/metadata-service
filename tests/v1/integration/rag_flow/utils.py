"""
Utility functions for the RAG flow integration tests.
"""

from app.api.v1.entity_tags.types import ResetEntityTagsByNameRequest

# Define a generic type variable for the response model


def get_reset_requests_tag_names(
    reset_requests: list[ResetEntityTagsByNameRequest],
) -> set[str]:
    tag_names = []
    for reset_request in reset_requests:
        for tag_group in reset_request.tag_groups:
            tag_names.extend(tag_group.tag_names)
    # Remove duplicates by converting to a set and back to a list
    return set(tag_names)
