from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship, relation, backref
Base = declarative_base()
from .base import _Base


class Package(Base, _Base):
    __tablename__ = 'packages'

    id = Column(Integer, primary_key=True, autoincrement=True)
    parent_package_id = Column(Integer, ForeignKey('packages.id'))
    selected = Column(Boolean)
    dir = Column(String(1024))
    execution_order = Column(Integer)
    parent = relationship(
        'Package',
        remote_side=[id],
        backref=backref("children", order_by=[execution_order])
    )

    def is_root(self):
        return self.parent_package_id is None

    def has_child(self, target_package):
        target_id = target_package.id
        for pkg in self.children:
            if pkg.id == target_id:
                return True
            if pkg.has_child(target_package):
                return True
        return False

    def has_child_by_name(self, name):
        for child in self.children:
            if child.dir == name:
                return True
        return False

    def find_child_by_name(self, name):
        for child in self.children:
            if child.dir == name:
                return child
        return None

    def rename(self, name):
        if name == 'root':
            raise Exception('Naming package as root is not allowed')
        if self.dir == 'root':
            raise Exception('Can\'t rename root packages')
        parent = self.parent
        if not parent:
            self.dir = name
            return
        if parent.find_child_by_name(name):
            raise Exception('Child with same name already exists')
        self.dir = name

    def move_test_case_to_bottom(self, test_case_id):
        test_cases = self.test_cases
        target_index = -1
        for index in xrange(len(test_cases)):
            tc = test_cases[index]
            if tc.id == test_case_id:
                target_index = index
            if target_index != -1 and target_index < index:
                target_tc = test_cases[target_index]
                tc.execution_order,  target_tc.execution_order = target_tc.execution_order, tc.execution_order

    def move_package_to_bottom(self, package_id):
        packages = self.children
        target_index = -1
        for index in xrange(len(packages)):
            pkg = packages[index]
            if pkg.id == package_id:
                target_index = index
            if target_index != -1 and target_index < index:
                target_pkg = packages[target_index]
                pkg.execution_order,  target_pkg.execution_order = target_pkg.execution_order, pkg.execution_order


    @property
    def legacy_format(self):
        return {
            "packages": [pkg.legacy_format for pkg in self.children],
            "selected": self.selected,
            "dir": self.dir,
            "test_cases": [tc.legacy_format for tc in self.test_cases]
        }

    def cascade(self):
        return self.children + self.test_cases
