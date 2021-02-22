from backend.system import BaseService
from .dao import RequestDao


class RequestService(BaseService):
    dao_cls = RequestDao
