from backend.system.service import BaseService
from backend.system.schema import BaseSchema, DeleteSchema
from backend.system.message_generator import get_message
from backend.system.model import BaseModel
from .crud_messages import CrudMessageKeys
from typing import ClassVar, Dict, Type, Tuple, List, Any, Callable, Optional
from fastapi import Request, APIRouter, HTTPException
from fastapi.exceptions import RequestValidationError
from cached_property import cached_property
from urllib.parse import urlencode
from pydantic import ValidationError
from backend.system.dao.exception import DaoNotFoundException, DaoOperationNotAllowedException


class BaseCrud(object):

    service_cls: ClassVar = BaseService

    schema: Type[BaseSchema] = BaseSchema

    default_vocabulary = {

    }

    def __init__(self):
        self._service: BaseService = self.service_cls()

    @cached_property
    def vocabulary(self) -> Dict[str, str]:
        ret = dict()
        classes = reversed([cls for cls in self.__class__.mro()])
        for cls in classes:
            if hasattr(cls, 'default_vocabulary'):
                ret.update(cls.default_vocabulary)
        return ret

    @cached_property
    def service(self) -> service_cls:
        return self._service

    def read(self, model_id: int) -> BaseModel:
        model = self.service.get(model_id)
        if model is None:
            raise HTTPException(
                status_code=404,
                detail=get_message(CrudMessageKeys.NOT_FOUND, self.vocabulary),
            )
        return model

    def read_endpoint(self, *, request: Request, model_id: int) -> BaseModel:
        response_data = self.read(model_id)
        return response_data

    def index(self, page: int, limit: int, filters: Dict[str, str]) -> Tuple[List, int]:
        skip = page-1
        models, count = self.service.paginate(skip=skip, limit=limit, filters=filters)
        data_set = [self.schema.from_orm(model) for model in models]
        return data_set, count

    def index_endpoint(self, *, request: Request, page: int, limit: int):
        filters: Dict[str,str] = dict(request.query_params)
        filters.pop('page', None)
        filters.pop('limit', None)
        data, total = self.index(page=page, limit=limit, filters=filters)
        url = request.url.components.geturl().split('?')[0]
        next_page = None
        prev_page = None
        if page * limit < total:
            next_page = url + '?' + urlencode({
                'page': page + 1,
                'limit': limit,
                **filters,
            })
        if data and page != 1:
            prev_page = url + '?' + urlencode({
                'page': page - 1,
                'limit': limit,
                **filters,
            })
        response_data = {
            "page": page,
            "limit": limit,
            "total": total,
            "data": data,
            "prev": prev_page,
            "next": next_page,
        }
        return response_data

    def create(self, data: Dict[str, Any]) -> BaseModel:
        model = self.service.create(data=data, commit=True)
        return model

    def create_endpoint(self, *, request: Request, data: BaseSchema):
        try:
            validated_data = data.dict()
            model = self.create(data=validated_data)
        except ValidationError as e:
            raise RequestValidationError(errors=e.raw_errors, body=data)
        return model

    def update(self, data: Dict[str, Any]) -> BaseModel:
        model = self.service.update(data=data, commit=True)
        return model

    def update_endpoint(self, *, request: Request, data: BaseSchema):
        try:
            validated_data = data.dict()
            model = self.update(data=validated_data)
        except ValidationError as e:
            raise RequestValidationError(errors=e.raw_errors, body=data)
        except DaoNotFoundException as e:
            raise HTTPException(
                status_code=404,
                detail=get_message(CrudMessageKeys.NOT_FOUND, self.vocabulary),
            )
        return model

    def delete(self, data: DeleteSchema):
        self.service.delete(data=data, commit=True)

    def delete_endpoint(self, *, request: Request, data: DeleteSchema) -> Dict:
        try:
            self.delete(data)
        except DaoOperationNotAllowedException as e:
            raise HTTPException(
                status_code=403,
                detail=get_message(CrudMessageKeys.OPERATION_NOT_ALLOWED, self.vocabulary),
            )
        except DaoNotFoundException as e:
            raise HTTPException(
                status_code=404,
                detail=get_message(CrudMessageKeys.NOT_FOUND, self.vocabulary),
            )
        return {
            "message": get_message(CrudMessageKeys.DELETE_SUCCESS, self.vocabulary),
            "id": data.id,
        }
