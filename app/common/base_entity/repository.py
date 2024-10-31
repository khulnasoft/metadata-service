""" BaseRepository """

from sqlalchemy import asc, desc, and_, or_, inspect
from sqlalchemy.exc import MultipleResultsFound, NoResultFound
from sqlalchemy.orm import Session
from typing import Type, TypeVar, Generic, List

from app.common.base_entity.model import (
    FilterType,
    SortType,
    AdvancedSearchResponse,
    AdvancedSearchRequest,
    LogicOperator,
)

T = TypeVar("T")


class BaseRepository(Generic[T]):
    """Provides methods to perform CRUD operations"""

    def __init__(self, db: Session, model: Type[T]):
        self.db = db
        self.model = model

    def create(self, entity: T) -> T:
        self.db.add(entity)
        self.db.commit()
        self.db.refresh(entity)
        return entity

    def get(self, entity_id: int) -> T:
        return self.db.query(self.model).filter(self.model.id == entity_id).first()

    # what if id is not integer?
    def search(
        self,
        field: str,
        value: str,
        filter_type: str = FilterType.CONTAINS,
        is_case_sensitive: bool = False,
    ) -> List[T]:

        if value is not None and not is_case_sensitive:
            value = value.lower()

        if field is None:
            return self.db.query(self.model).all()

        if not hasattr(self.model, field):
            raise ValueError(f"Invalid field: {field}")

        column = getattr(self.model, field)

        if filter_type == FilterType.EQUALS:
            return self.db.query(self.model).filter(column == value).all()
        elif filter_type == FilterType.STARTS_WITH:
            return self.db.query(self.model).filter(column.ilike(f"{value}%")).all()
        elif filter_type == FilterType.CONTAINS:
            return self.db.query(self.model).filter(column.ilike(f"%{value}%")).all()
        else:
            raise ValueError(
                "Invalid search_type. Use 'exact', 'starts-with', or 'contains'."
            )

    def delete(self, entity: T) -> T:
        self.db.delete(entity)
        self.db.commit()
        return entity

    def delete_by_id(self, row_id: int) -> int:
        deleted_rows = (
            self.db.query(self.model).filter(self.model.id == row_id).delete()
        )
        self.db.commit()
        return deleted_rows

    def find_by_unique_field(self, field: str, value: str) -> T:
        if not self._is_unique_field(field):
            raise ValueError(f"The field '{field}' is not unique.")

        try:
            return (
                self.db.query(self.model)
                .filter(getattr(self.model, field) == value)
                .one_or_none()
            )
        except MultipleResultsFound as e:
            raise ValueError(
                f"Multiple records found for field '{field}' with value '{value}'"
            ) from e
        except NoResultFound:
            return None

    def _is_unique_field(self, field: str) -> bool:
        """Check if a field has a unique constraint."""
        mapper = inspect(self.model)
        for column in mapper.columns:
            if column.name == field and column.unique:
                return True
        return False

    def advanced_search(
        self, search_req: AdvancedSearchRequest
    ) -> AdvancedSearchResponse[T]:
        query = self.db.query(self.model)

        # todo: add going over all the values, and adding them with or condition
        filter_clauses = []
        for f in search_req.filters:
            column = getattr(self.model, f.field)
            value_clauses = []
            for value in f.values:
                if f.filter_type == FilterType.EQUALS:
                    value_clauses.append(column == value.lower())
                elif f.filter_type == FilterType.STARTS_WITH:
                    value_clauses.append(column.ilike(f"{value.lower()}%"))
                elif f.filter_type == FilterType.CONTAINS:
                    value_clauses.append(column.ilike(f"%{value.lower()}%"))

            if value_clauses:
                filter_clauses.append(or_(*value_clauses))

        if search_req.filters_operator == LogicOperator.AND:
            query = query.filter(and_(*filter_clauses))
        else:
            query = query.filter(or_(*filter_clauses))

        for sort in search_req.sorts:
            column = getattr(self.model, sort.field)
            if sort.sort_type == SortType.ASC:
                query = query.order_by(asc(column))
            else:
                query = query.order_by(desc(column))

        total_count = query.count()
        results = query.offset(search_req.offset).limit(search_req.limit).all()

        return AdvancedSearchResponse[T](
            results=results,
            count=len(results),
            offset=search_req.offset,
            count_total=total_count,
        )
