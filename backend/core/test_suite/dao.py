from backend.system import BaseDao
from .model import TestSuite


class TestSuiteDao(BaseDao):
    model_cls = TestSuite
