"""
This module contains models that are used across multiple entities.
"""

from enum import Enum
from typing import Optional, TypeVar, Generic, List
from pydantic import BaseModel

from app.common.constants import MAX_SEARCH_RESULTS


class FilterType(str, Enum):
    CONTAINS = "contains"
    EQUALS = "equals"
    STARTS_WITH = "starts_with"


class SortType(str, Enum):
    ASC = "asc"
    DESC = "desc"


# not needed?
class Sort(BaseModel):
    field: str
    sort_type: SortType = SortType.ASC


class FieldType(str, Enum):
    STRING = "string"
    NUMBER = "number"
    DATE = "date"
    BOOLEAN = "boolean"


class Filter(BaseModel):
    field: str
    field_type: FieldType
    filter_type: FilterType
    values: list[str]
    # values operator is "or"


class LogicOperator(str, Enum):
    AND = "and"
    OR = "or"


# multiple filters with and / or condition between them, multiple sorts, set filter


class AdvancedSearchRequest(BaseModel):
    filters: Optional[list[Filter]] = []
    filters_operator: Optional[LogicOperator] = LogicOperator.AND
    sorts: Optional[list[Sort]] = []
    limit: Optional[int] = MAX_SEARCH_RESULTS
    offset: Optional[int] = 0


# Define a generic type variable
T = TypeVar("T")


class AdvancedSearchResponse(BaseModel, Generic[T]):
    results: List[T]
    count: int
    offset: int
    count_total: int

    class Config:
        arbitrary_types_allowed = True


class DeleteResponse(BaseModel):
    count: int


# Define TypeVars to parameterize request and response types
REQUEST = TypeVar("REQUEST")
RESPONSE = TypeVar("RESPONSE")


# Generic Pydantic models for Success and Error entries
class SuccessItem(BaseModel, Generic[REQUEST, RESPONSE]):
    req: REQUEST
    res: RESPONSE


class ErrorItem(BaseModel, Generic[T]):
    req: REQUEST
    errors: List[str]


# Generic BulkResponse model that combines success and error lists
class BulkResponse(BaseModel, Generic[REQUEST, RESPONSE]):
    success: List[SuccessItem[REQUEST, RESPONSE]]
    errors: List[ErrorItem[REQUEST]]
