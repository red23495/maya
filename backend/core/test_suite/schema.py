from backend.system import BaseSchema, DeleteSchema, ListSchema, DeleteResponseSchema
from typing import Optional, List


class BaseTestSuiteSchema(BaseSchema):
    version: str
    db: str


class TestSuiteSchema(BaseTestSuiteSchema):
    id: Optional[int]


class TestSuiteCreateSchema(BaseTestSuiteSchema):
    ...


class TestSuiteUpdateSchema(BaseTestSuiteSchema):
    id: int


class TestSuiteListSchema(ListSchema):
    data: List[TestSuiteSchema]


class TestSuiteDeleteSchema(DeleteSchema):
    ...


class TestSuiteDeleteResponseSchema(DeleteResponseSchema):
    ...
