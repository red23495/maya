from backend.core.test_case.schema import (
    TestCaseSchema, TestCaseCreateSchema,
    TestCaseUpdateSchema, TestCaseDeleteSchema,
    TestCaseDeleteResponseSchema, TestCaseListSchema, TestCaseTreeSchema
)
from backend.core.test_case.crud import TestCaseCrud
from fastapi import Request, APIRouter

crud = TestCaseCrud()
router = APIRouter()


@router.get('/', tags=['TestCase'], response_model=TestCaseListSchema)
def index(*, request: Request, page: int = 1, limit: int = 25):
    return crud.index_endpoint(request=request, page=page, limit=limit)


@router.post('/', tags=['TestCase'], response_model=TestCaseSchema)
def create(*, request: Request, data: TestCaseCreateSchema):
    return crud.create_endpoint(request=request, data=data)


@router.put('/',tags=['TestCase'], response_model=TestCaseSchema)
def update(*, request: Request, data: TestCaseUpdateSchema):
    return crud.update_endpoint(request=request, data=data)


@router.delete('/',tags=['TestCase'], response_model=TestCaseDeleteResponseSchema)
def delete(*, request: Request, data: TestCaseDeleteSchema):
    return crud.delete_endpoint(request=request, data=data)


@router.get('/tree', tags=['TestCase'], response_model=TestCaseTreeSchema)
def tree(*, request: Request):
    return crud.tree(request=request)


@router.get('/{model_id}', tags=['TestCase'], response_model=TestCaseSchema)
def read(*, request: Request, model_id: int):
    return crud.read_endpoint(request=request, model_id=model_id)
