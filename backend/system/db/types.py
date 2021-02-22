from sqlalchemy.types import TypeDecorator, TEXT, INTEGER
from sqlalchemy.ext.mutable import MutableDict
import json
from enum import IntEnum as IntEnumType


class JSONEncodedDict(TypeDecorator):

    impl = TEXT

    def process_bind_param(self, value, dialect):
        if value is not None:
            value = json.dumps(value)
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            value = json.loads(value)
        return value


JSONDict = MutableDict.as_mutable(JSONEncodedDict)


class IntEnum(TypeDecorator):
    impl = INTEGER

    def __init__(self, enum_cls=IntEnumType, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._enum_cls = enum_cls

    def process_bind_param(self, value, dialect):
        return value.value

    def process_result_value(self, value, dialect):
        return self._enum_cls(value)

