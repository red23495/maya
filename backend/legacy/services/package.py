from datetime import datetime

from . import BaseService
try:
    from ..db import Package
except:
    from db import Package


class PackageService(BaseService):
    model = Package

    def create_package_with_timestamp(self, parent=None):
        new_package = Package(
            dir=str(datetime.now()).replace(' ', '_').replace(':', '_').replace('.', '_'),
            selected=True,
            parent_package_id=parent
        )
        self.session.add(new_package)
        self.session.commit()
        new_package.execution_order = new_package.id
        self.session.commit()
        return new_package

    def create_package(self, name, parent=None):
        new_package = Package(
            dir=name,
            selected=True,
            parent_package_id=parent
        )
        self.session.add(new_package)
        self.session.commit()
        new_package.execution_order = new_package.id
        self.session.commit()
        return new_package

