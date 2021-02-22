from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship, backref
from .package import Package
Base = declarative_base()
from .base import _Base


class TestCase(Base, _Base):
    __tablename__ = 'test_cases'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    selected = Column(Boolean)
    package_id = Column(Integer)
    execution_order = Column(Integer)
    package = relationship(
        Package,
        primaryjoin=package_id == Package.id,
        foreign_keys=[package_id],
        backref=backref("test_cases", order_by=[execution_order])
    )

    def move_request_to_bottom(self, request_id):
        requests = self.requests
        target_index = -1
        for index in xrange(len(requests)):
            rq = requests[index]
            if rq.id == request_id:
                target_index = index
            if target_index != -1 and target_index < index:
                target_rq = requests[target_index]
                rq.execution_order,  target_rq.execution_order = target_rq.execution_order, rq.execution_order


    @property
    def legacy_format(self):
        return {
            "index": self.id,
            "selected": self.selected,
            "name": self.name,
            "requests": [rq.legacy_format for rq in self.requests]
        }

    def cascade(self):
        return self.requests