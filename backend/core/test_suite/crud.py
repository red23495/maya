from backend.system import BaseCrud
from .service import TestSuiteService
from .schema import TestSuiteSchema


class TestSuiteCrud(BaseCrud):
    service_cls = TestSuiteService

    schema = TestSuiteSchema

    default_vocabulary = {
        'model': 'TestSuite'
    }
