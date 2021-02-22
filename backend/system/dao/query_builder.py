from backend.system.model import BaseModel
from typing import Type, Dict, Any
from sqlalchemy.orm import Session, Query
from .query_filter import QueryFilter, NativeFilter


class QueryBuilder(object):

    model_cls: Type[BaseModel] = BaseModel

    default_filters = {
        'deleted': False,
    }

    def __init__(self, model_cls: Type[BaseModel]):
        self._model_cls = model_cls or self.model_cls

    def build(self, query: Query, data: Dict[str, Any]):
        _data = self.default_filters.copy()
        if data:
            _data.update(data)
        _query: Query = query
        state = dict()
        for key, val in _data.items():
            if hasattr(self, key):
                _filter: QueryFilter = getattr(self, key)
            else:
                _filter: QueryFilter = NativeFilter()
            _query: Query = _filter(query=_query, model=self._model_cls, key=key, value=val, state=state)
        return _query
