from backend.system import BaseSchema, DeleteSchema, ListSchema, DeleteResponseSchema
from typing import Optional, List
from backend.core.request.schema import RequestSchema

class BaseTestCaseSchema(BaseSchema):
    name: str
    parent_id: Optional[int]
    suite_id: Optional[int]
    request_id: Optional[int]


class TestCaseSchema(BaseTestCaseSchema):
    id: Optional[int]


class TestCaseCreateSchema(BaseTestCaseSchema):
    ...


class TestCaseUpdateSchema(BaseTestCaseSchema):
    id: int


class TestCaseListSchema(ListSchema):
    data: List[TestCaseSchema]


class TestCaseDeleteSchema(DeleteSchema):
    ...


class TestCaseDeleteResponseSchema(DeleteResponseSchema):
    ...


class TestCaseTreeNodeSchema(TestCaseSchema):
    children: List["TestCaseTreeNodeSchema"] = []
    request: Optional[RequestSchema]


TestCaseTreeNodeSchema.update_forward_refs()


class TestCaseTreeSchema(BaseSchema):
    root: List[TestCaseTreeNodeSchema] = []
