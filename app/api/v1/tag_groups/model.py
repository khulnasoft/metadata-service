"""
This module contains the ORM model and DTO models related to the TagGroups entity
"""

from typing import Optional

from sqlalchemy import Column, Integer, String, UniqueConstraint
from pydantic import BaseModel
from app.common.database import Base


class TagGroup(Base):
    """Describes the structure of the TagGroup entity in the database"""

    __tablename__ = "tag_groups"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    name = Column(String, nullable=False, unique=True)
    description = Column(String, nullable=True)

    __table_args__ = (UniqueConstraint("name", name="uq_tag_groups_name"),)


class TagGroupCreateRequest(BaseModel):
    name: str
    description: Optional[str] = None


class TagGroupResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None

    @classmethod
    def from_tag_group(cls, tag_group):
        return cls(
            id=tag_group.id, name=tag_group.name, description=tag_group.description
        )
