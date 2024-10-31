"""
This module contains the ORM model for EntityTag entity
"""

from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    PrimaryKeyConstraint,
)


from app.common.database import Base


class EntityTag(Base):
    """Describes the structure of the EntityTag entity in the database"""

    __tablename__ = "entity_tags"

    entity_id = Column(String, nullable=False)
    entity_type = Column(String, nullable=False)
    tag_id = Column(Integer, ForeignKey("tags.id", ondelete="RESTRICT"), nullable=False)
    # create_date = Column(DateTime, nullable=False, default=func.now())

    __table_args__ = (
        PrimaryKeyConstraint("entity_id", "tag_id", name="pk_entity_tags"),
    )
