from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relation, relationship
Base = declarative_base()
from .package import Package
from .base import _Base


class Filesystem(Base, _Base):
    __tablename__ = 'filesystems'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(1024))
    package_id = Column(Integer)
    package = relationship(
        Package, primaryjoin=package_id == Package.id, foreign_keys=[package_id],
    )

    @property
    def unorganized_requests(self):
        return [model for model in self.filesystem_requests if not model.is_processed]

    def get_package_by_path(self, package_path):
        package_path_list = package_path.strip('/').split('/')
        if not self.package:
            return None
        if package_path_list[0] != 'root':
            return None
        package_path_list = package_path_list[1:]
        package = self.package
        for package_name in package_path_list:
            package = package.find_child_by_name(package_name)
            if not package:
                return None
        return package

    def get_test_case_by_index(self, package_path, test_no):
        package = self.get_package_by_path(package_path)
        if not package:
            raise Exception('Package not found')
        try:
            return package.test_cases[test_no]
        except:
            raise Exception('Test case not found')

    def get_request_by_index(self, package_path, test_no, request_no):
        test_case = self.get_test_case_by_index(package_path, test_no)
        try:
            return test_case.requests[request_no]
        except:
            raise Exception('Request not found')



    @property
    def legacy_format(self):
        return {
            "unorganized_request": [],
            "packages": [self.package.legacy_format],
            "test_index": 0
        }

    def cascade(self):
        return [self.package] + self.filesystem_requests


