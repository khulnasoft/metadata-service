"""
fixtures for rag_flow tests
"""

import pytest
import sqlalchemy

from app.api.v1.entity_tags.types import (
    TagGroupTagsByNameRequest,
    ResetEntityTagsByNameRequest,
)
from app.common.database import get_db

from tests.v1.integration.rag_flow.utils import get_reset_requests_tag_names


@pytest.fixture(scope="module")
def capability_tag_group() -> TagGroupTagsByNameRequest:
    return TagGroupTagsByNameRequest(
        tag_group_name="capability", tag_names=["cap1", "cap2"]
    )


@pytest.fixture(scope="module")
def language_tag_group() -> TagGroupTagsByNameRequest:
    return TagGroupTagsByNameRequest(
        tag_group_name="language", tag_names=["java", "python"]
    )


@pytest.fixture(scope="module")
def bu_tag_group() -> TagGroupTagsByNameRequest:
    return TagGroupTagsByNameRequest(tag_group_name="bu", tag_names=["bu-1", "bu-2"])


@pytest.fixture(scope="module")
def repo_name_tag_group() -> callable:
    def _repo_name_tag_group(name):
        return TagGroupTagsByNameRequest(tag_group_name="repo_name", tag_names=[name])

    return _repo_name_tag_group


@pytest.fixture(scope="module")
def rag_flow_reset_requests(
    # pylint: disable=redefined-outer-name
    language_tag_group,
    bu_tag_group,
    capability_tag_group,
    repo_name_tag_group,
) -> list[ResetEntityTagsByNameRequest]:
    repo_1 = ResetEntityTagsByNameRequest(
        entity_id="/khulnasoft/repo1",
        entity_type="repo",
        tag_groups=[
            language_tag_group,
            bu_tag_group,
            repo_name_tag_group("/khulnasoft/repo1"),
        ],
    )

    repo_2 = ResetEntityTagsByNameRequest(
        entity_id="/khulnasoft/repo2",
        entity_type="repo",
        tag_groups=[
            bu_tag_group,
            capability_tag_group,
            repo_name_tag_group("/khulnasoft/repo2"),
        ],
    )
    yield [repo_1, repo_2]
    # teardown code
    with next(get_db()) as db:
        db.execute(
            sqlalchemy.text(
                "DELETE FROM entity_tags WHERE entity_id IN ('/khulnasoft/repo1', '/khulnasoft/repo2')"
            )
        )

        tag_names = get_reset_requests_tag_names([repo_1, repo_2])

        db.execute(
            sqlalchemy.text("DELETE FROM tags WHERE name IN :tag_names").bindparams(
                tag_names=tuple(list(tag_names))
            )
        )
        db.commit()

        db.execute(
            sqlalchemy.text(
                "DELETE FROM tag_groups WHERE name IN ('language', 'business_unit', 'capability')"
            )
        )
        db.commit()
