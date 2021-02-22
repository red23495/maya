from backend.system import BaseCrud
from .service import RequestService
from .schema import RequestSchema


class RequestCrud(BaseCrud):
    service_cls = RequestService

    schema = RequestSchema

    default_vocabulary = {
        'model': 'Raw Request'
    }
