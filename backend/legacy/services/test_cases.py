from . import BaseService
try:
    from ..db import TestCase
except:
    from db import TestCase


class TestCaseService(BaseService):
    model = TestCase

    def create_test_case(self, name, package_id):
        new_test_case = TestCase(
            name=name,
            package_id=package_id,
            selected=True
        )
        self.session.add(new_test_case)
        self.session.commit()
        new_test_case.execution_order = new_test_case.id
        self.session.commit()
        return new_test_case

    def import_from_legacy_dict(self, data_dict, **kwargs):
        params = data_dict
        params.update(kwargs)
        selected_params = {
            'name': params.get('name'),
            'selected': params.get('selected'),
            'package_id': params.get('package_id'),
        }
        test_case = self.model(**selected_params)
        self.session.add(test_case)
        self.session.commit()
        test_case.execution_order = test_case.id
        self.session.add(test_case)
        self.session.commit()
        return test_case
