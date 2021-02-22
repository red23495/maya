from backend.core.request.schema import (
    RequestSchema, RequestCreateSchema,
    RequestUpdateSchema, RequestDeleteSchema,
    RequestDeleteResponseSchema, RequestListSchema
)
from backend.core.request.crud import RequestCrud
from fastapi import Request, APIRouter

crud = RequestCrud()
router = APIRouter()


@router.get('/', tags=['Request'], response_model=RequestListSchema)
def index(*, request: Request, page: int = 1, limit: int = 25):
    return crud.index_endpoint(request=request, page=page, limit=limit)


@router.post('/', tags=['Request'], response_model=RequestSchema)
def create(*, request: Request, data: RequestCreateSchema):
    return crud.create_endpoint(request=request, data=data)


@router.get('/{model_id}', tags=['Request'], response_model=RequestSchema)
def read(*, request: Request, model_id: int):
    return crud.read_endpoint(request=request, model_id=model_id)


@router.put('/',tags=['Request'], response_model=RequestSchema)
def update(*, request: Request, data: RequestUpdateSchema):
    return crud.update_endpoint(request=request, data=data)


@router.delete('/',tags=['Request'], response_model=RequestDeleteResponseSchema)
def delete(*, request: Request, data: RequestDeleteSchema):
    return crud.delete_endpoint(request=request, data=data)
