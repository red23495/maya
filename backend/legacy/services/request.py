from . import BaseService
try:
    from ..db import Request
except:
    from db import Request


class RequestService(BaseService):
    model = Request

    def import_from_legacy_dict(self, data_dict, test_case_id):
        params = {
            'raw_request_id': data_dict['index'],
            'status': data_dict['status'],
            'selected': data_dict['selected'],
            'test_case_id': test_case_id,
        }
        rq = self.model(**params)
        self.session.add(rq)
        self.session.commit()
        rq.execution_order = rq.id
        self.session.add(rq)
        self.session.commit()
        return rq
