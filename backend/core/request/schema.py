from backend.system import BaseSchema, DeleteSchema, ListSchema, DeleteResponseSchema
from typing import Optional, List, Dict
from .enum import ResponseDataType, RequestDataType


class BaseRequestSchema(BaseSchema):
    request_data_type: RequestDataType
    response_data_type: ResponseDataType
    url: str
    request_method: str
    request_headers: Optional[Dict[str, str]]
    request_body: Optional[str]
    response_headers: Optional[Dict[str, str]]
    response_body: Optional[str]
    response_status: int
    readable_name: Optional[str]
    module: Optional[str]


class RequestSchema(BaseRequestSchema):
    id: Optional[int]


class RequestCreateSchema(BaseRequestSchema):
    ...


class RequestUpdateSchema(BaseRequestSchema):
    id: int


class RequestListSchema(ListSchema):
    data: List[RequestSchema]


class RequestDeleteSchema(DeleteSchema):
    ...


class RequestDeleteResponseSchema(DeleteResponseSchema):
    ...
