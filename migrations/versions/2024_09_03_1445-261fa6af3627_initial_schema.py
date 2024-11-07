"""initial schema

Revision ID: 261fa6af3627
Revises:
Create Date: 2024-09-03 14:45:42.051907

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from app.common.utils.logging_utils import logger


# revision identifiers, used by Alembic.
revision: str = "261fa6af3627"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    logger.info("Creating initial schema")
    op.create_table(
        "tag_groups",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True, index=True),
        sa.Column("name", sa.String, nullable=False),
        sa.Column("description", sa.String, nullable=True),
        sa.UniqueConstraint("name", name="uq_tag_groups_name"),
    )

    op.create_table(
        "tags",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True, index=True),
        sa.Column("name", sa.String, nullable=False),
        sa.Column(
            "tag_group_id",
            sa.Integer,
            sa.ForeignKey("tag_groups.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.UniqueConstraint("name", name="uq_tags_name"),
    )

    op.create_table(
        "entity_tags",
        sa.Column("entity_id", sa.String, nullable=False),
        sa.Column("entity_type", sa.String, nullable=False),
        sa.Column(
            "tag_id",
            sa.Integer,
            sa.ForeignKey("tags.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("entity_id", "tag_id", name="pk_entity_tags"),
    )


def downgrade() -> None:
    # Drop the entity_tags table
    op.drop_table("entity_tags")

    # Drop the tag_groups table
    op.drop_table("tag_groups")

    # Drop the tags table
    op.drop_table("tags")
