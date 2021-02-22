from backend.system import BaseDao
from .model import TestCase
from typing import List


class TestCaseDao(BaseDao):
    model_cls = TestCase

    def get_root_test_cases(self) -> List[TestCase]:
        return self.query(filters={'parent_id': None}).all()
