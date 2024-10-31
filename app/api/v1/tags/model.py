"""
This module contains the ORM model and DTO models related to the Tags entity
"""

from typing import Optional
from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint
from pydantic import BaseModel
from app.api.v1.tag_groups.model import TagGroupResponse
from app.api.v1.tag_groups.service import TagGroupService
from app.common.database import Base


class Tag(Base):
    """Describes the structure of the Tag entity in the database"""

    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    name = Column(String, nullable=False, unique=True)
    tag_group_id = Column(
        Integer, ForeignKey("tag_groups.id", ondelete="RESTRICT"), nullable=False
    )

    __table_args__ = (UniqueConstraint("name", name="uq_tags_name"),)

    class Config:
        arbitrary_types_allowed = True

    # don't understand why it stopped being able to generate the schema
    # def __get_pydantic_core_schema__(self):
    #     class TagSchema(BaseModel):
    #         id: Optional[int] = Field(
    #             None, description="The unique identifier of the tag"
    #         )
    #         name: str = Field(..., description="The name of the tag")
    #         tag_group_id: int = Field(..., description="The ID of the tag group")
    #
    #         class Config:
    #             from_attributes = True
    #
    #     return TagSchema.model_json_schema()


# make fields optional so you can update one at a time?
class TagCreateRequest(BaseModel):
    name: str
    tag_group_id: int


class TagUpdateRequest(BaseModel):
    id: int
    name: Optional[str]
    tag_group_id: Optional[int]


class TagResponse(BaseModel):
    """Structure of the Tag entity to be returned in the API response (DTO)"""

    id: int
    name: str
    tag_group_id: int
    tag_group: TagGroupResponse

    # should I include the group data, or just id?
    @classmethod
    def from_tag(cls, tag: Tag, tag_group_service: TagGroupService):
        tag_group = tag_group_service.get(tag.tag_group_id)

        return cls(
            id=tag.id,
            name=tag.name,
            tag_group_id=tag.tag_group_id,
            tag_group=TagGroupResponse.from_tag_group(tag_group),
        )
