from backend.system import BaseService
from .dao import TestSuiteDao


class TestSuiteService(BaseService):
    dao_cls = TestSuiteDao
