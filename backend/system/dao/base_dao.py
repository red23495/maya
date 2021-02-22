from backend.system.model import BaseModel
from backend.system.context import GlobalContext
from sqlalchemy.orm import Session, Query
from sqlalchemy import func
from typing import List, Type, Dict, Any, Union
from .exception import DaoNotFoundException, DaoOperationNotAllowedException
from .query_builder import QueryBuilder
from backend.system.schema import DeleteSchema


class BaseDao(object):

    model_cls: Type[BaseModel] = BaseModel
    query_builder_cls: Type[QueryBuilder] = QueryBuilder

    __ALLOW_HARD_DELETE__: bool = False

    def __init__(self):
        self._session: Session = GlobalContext.get_instance().session
        self._query_builder: QueryBuilder = QueryBuilder(self.model_cls)

    @property
    def session(self) -> Session:
        return self._session

    @property
    def query_builder(self) -> QueryBuilder:
        return self._query_builder

    def get(self, pk: int) -> BaseModel:
        return self.query(filters={'id': pk}).first()

    def all(self, filters: Dict[str, Any]) -> List[model_cls]:
        return self.query(filters=filters).all()

    def query(self, select: List=None, filters: Dict[str,Any]=None) -> Query:
        if not select:
            select = [self.model_cls]
        query = self.session.query(*select)
        return self.query_builder.build(query=query, data=filters)

    def paginate(self, skip: int, limit: int, filters: Dict[str, Any]):
        offset = skip * limit
        query = self.query(filters=filters)
        query = query.offset(offset).limit(limit)
        return query.all()

    def count(self, filters: Dict[str, Any]) -> int:
        query = self.query(select=[func.count(self.model_cls.id)], filters=filters)
        return query.scalar()

    def save(self, data: Dict[str, Any], commit: bool=True) -> model_cls:
        model = self.model_cls()
        model.update_from_dict(data=data)
        self._session.add(model)
        self._session.flush()
        if commit:
            self.session.commit()
        return model

    def update(self, data: Dict[str, Any], commit: bool=True):
        model_id = data.get('id')
        model = self.get(model_id)
        if not model:
            raise DaoNotFoundException()
        model.update_from_dict(data)
        self.session.flush()
        if commit:
            self.session.commit()
        return model

    def delete(self, data: DeleteSchema, commit: bool=True):
        model = self.get(data.id)
        if not model:
            raise DaoNotFoundException()
        if data.hard_delete:
            if self.__ALLOW_HARD_DELETE__:
                self._hard_delete(model=model, commit=commit)
            elif not data.stop_at_fail:
                self._soft_delete(model=model, commit=commit)
            else:
                raise DaoOperationNotAllowedException()
        else:
            self._soft_delete(model=model, commit=commit)

    def _hard_delete(self, model: model_cls, commit: bool):
        self.session.delete(model)
        self.session.flush()
        if commit:
            self.session.commit()

    def _soft_delete(self, model: model_cls, commit: bool):
        model.deleted = True
        self.session.flush()
        if commit:
            self.session.commit()





