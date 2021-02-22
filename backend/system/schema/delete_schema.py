from .base_schema import BaseSchema


class DeleteSchema(BaseSchema):
    id: int
    hard_delete: bool = False
    stop_at_fail: bool = False


class DeleteResponseSchema(BaseSchema):
    id: int
    message: str
