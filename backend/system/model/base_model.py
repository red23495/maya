from backend.system.db import Base
from sqlalchemy import Column, Integer, Boolean
from typing import Dict, Any, Type


class BaseModel(Base):

    __abstract__ = True

    id: int = Column(Integer, primary_key=True, autoincrement=True)
    deleted: bool = Column(Boolean, default=False)

    def update_from_dict(self, data: Dict[str, Any]) -> 'BaseModel':
        for key, value in data.items():
            if self.is_column(key):
                if hasattr(self, key):
                    setattr(self, key, value)
            elif value:
                model_cls = self.get_related_class(key)
                model = model_cls()
                model.update_from_dict(value)
                setattr(self, key, model)
        return self

    @classmethod
    def is_column(cls, key: str) -> bool:
        return hasattr(cls.__table__.c, key)

    @classmethod
    def cast_to_native_type(cls, key: str, val: Any) -> Any:
        column = getattr(cls.__table__.c, key)
        _type = column.type.python_type
        return _type(val)

    @classmethod
    def is_relationship(cls, key: str) -> bool:
        return not cls.is_column(key=key)

    def get_related_class(self, key: str) -> Type["BaseModel"]:
        # @TODO: check if class method
        return self._sa_class_manager[key].comparator.entity.class_
