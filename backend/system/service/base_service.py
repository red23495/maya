from backend.system.dao import BaseDao
from backend.system.model import BaseModel
from typing import ClassVar, Tuple, List, Dict, Any
from backend.system.schema import DeleteSchema


class BaseService(object):
    dao_cls: ClassVar = BaseDao

    def __init__(self):
        self._dao = self.dao_cls()

    @property
    def dao(self) -> BaseDao:
        return self._dao

    def get(self, key: int) -> BaseModel:
        return self._dao.get(key)

    def paginate(self, skip: int=0, limit: int=25, filters: Dict[str, str] = None) -> Tuple[List[BaseModel], int]:
        return self.dao.paginate(skip=skip, limit=limit, filters=filters), self.dao.count(filters=filters)

    def before_write(self, data: dict) -> dict:
        return data

    def after_write(self, model: BaseModel) -> BaseModel:
        return model

    def create(self, data: Dict[str, Any], commit: bool=True) -> BaseModel:
        data = self.before_write(data)
        model = self.dao.save(data=data, commit=commit)
        model = self.after_write(model)
        return model

    def update(self, data: Dict[str, Any], commit: bool=True) -> BaseModel:
        data = self.before_write(data)
        model = self.dao.update(data=data, commit=commit)
        model = self.after_write(model)
        return model

    def delete(self, data: DeleteSchema, commit: bool=True):
        self.dao.delete(data=data, commit=commit)
