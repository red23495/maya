from backend.system import BaseDao
from .model import Request


class RequestDao(BaseDao):
    model_cls = Request
