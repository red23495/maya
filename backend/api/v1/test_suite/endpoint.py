from backend.core.test_suite.schema import (
    TestSuiteSchema, TestSuiteCreateSchema,
    TestSuiteUpdateSchema, TestSuiteDeleteSchema,
    TestSuiteDeleteResponseSchema, TestSuiteListSchema
)
from backend.core.test_suite.crud import TestSuiteCrud
from fastapi import Request, APIRouter

crud = TestSuiteCrud()
router = APIRouter()


@router.get('/', tags=['TestSuite'], response_model=TestSuiteListSchema)
def index(*, request: Request, page: int = 1, limit: int = 25):
    return crud.index_endpoint(request=request, page=page, limit=limit)


@router.post('/', tags=['TestSuite'], response_model=TestSuiteSchema)
def create(*, request: Request, data: TestSuiteCreateSchema):
    return crud.create_endpoint(request=request, data=data)


@router.get('/{model_id}', tags=['TestSuite'], response_model=TestSuiteSchema)
def read(*, request: Request, model_id: int):
    return crud.read_endpoint(request=request, model_id=model_id)


@router.put('/',tags=['TestSuite'], response_model=TestSuiteSchema)
def update(*, request: Request, data: TestSuiteUpdateSchema):
    return crud.update_endpoint(request=request, data=data)


@router.delete('/',tags=['TestSuite'], response_model=TestSuiteDeleteResponseSchema)
def delete(*, request: Request, data: TestSuiteDeleteSchema):
    return crud.delete_endpoint(request=request, data=data)
