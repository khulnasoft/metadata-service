"""
Fixtures for tag_groups tests.
"""

import pytest
import sqlalchemy

from app.api.v1.entity_tags.types import (
    TagGroupTagsByNameRequest,
)
from app.api.v1.tag_groups.model import TagGroupCreateRequest
from app.common.database import get_db


@pytest.fixture(scope="module")
def teams_tag_group() -> TagGroupTagsByNameRequest:
    request = TagGroupCreateRequest(
        name="Teams group", description="Teams group description"
    )
    yield request
    with next(get_db()) as db:
        db.execute(
            sqlalchemy.text(f"DELETE FROM tag_groups where name = '{request.name}'")
        )
        db.commit()
