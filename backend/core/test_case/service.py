from backend.system import BaseService
from .dao import TestCaseDao
from typing import List
from .model import TestCase


class TestCaseService(BaseService):
    dao_cls = TestCaseDao

    def get_test_case_tree(self) -> List[TestCase]:
        dao: TestCaseDao = self.dao
        return dao.get_root_test_cases()
