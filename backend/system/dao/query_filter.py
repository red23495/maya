from sqlalchemy.orm import Query
from backend.system.model.base_model import BaseModel
from typing import Any, Tuple, Type, Dict
import abc
from enum import Enum


class QueryOperator(Enum):
    eq = 'eq'
    ne = 'ne'
    le = 'le'
    ge = 'ge'
    lt = 'lt'
    gt = 'gt'
    like = 'like'
    likep = 'likep'


class QueryFilter(object):

    @abc.abstractmethod
    def __call__(self, query: Query, model: BaseModel, key: str, value: Any, state: Dict[str, Any]) -> Query:
        ...


class NativeFilter(QueryFilter):

    default_operator: QueryOperator = QueryOperator.eq

    def __call__(self, query: Query, model: Type[BaseModel], key: str, value: Any, state: Dict[str, Any]) -> Query:
        name, operator = self._split_key(key)
        if not model.is_column(name):
            return query
        val = model.cast_to_native_type(name, value) if value is not None else None
        col = getattr(model, name)
        _query: Query = query
        if operator == QueryOperator.eq:
            _query = query.filter(col == val)
        elif operator == QueryOperator.ne:
            _query = query.filter(col != val)
        elif operator == QueryOperator.gt:
            _query = query.filter(col > val)
        elif operator == QueryOperator.lt:
            _query = query.filter(col < val)
        elif operator == QueryOperator.ge:
            _query = query.filter(col >= val)
        elif operator == QueryOperator.le:
            _query = query.filter(col <= val)
        elif operator == QueryOperator.like:
            _query = query.filter(col.like('{}%'.format(val)))
        elif operator == QueryOperator.likep:
            _query = query.filter(col.like(val))
        return _query

    def _split_key(self, key: str) -> Tuple[str, QueryOperator]:
        key_tokens = key.split('.')
        _name = key_tokens[0]
        if len(key_tokens) > 1:
            operator = QueryOperator(key_tokens[1])
        else:
            operator = self.default_operator
        return _name, operator
