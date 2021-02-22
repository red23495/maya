from enum import IntEnum


class RequestDataType(IntEnum):
    form = 1
    json = 2
    other = 3


class ResponseDataType(IntEnum):
    json = 1
    other = 2
