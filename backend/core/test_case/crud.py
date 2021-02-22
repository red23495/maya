from backend.system import BaseCrud
from .service import TestCaseService
from .schema import TestCaseSchema
from fastapi import Request


class TestCaseCrud(BaseCrud):
    service_cls = TestCaseService

    schema = TestCaseSchema

    default_vocabulary = {
        'model': 'TestCase'
    }

    def tree(self, *, request: Request):
        service: TestCaseService = self.service
        roots = service.get_test_case_tree()
        return {"root": roots}
