from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship, backref
from .raw_request import RawRequest
from .test_cases import TestCase
Base = declarative_base()
from .base import _Base


class Request(Base, _Base):
    __tablename__ = 'requests'

    id = Column(Integer, primary_key=True, autoincrement=True)
    raw_request_id = Column(Integer)
    raw_request = relationship(RawRequest, primaryjoin=raw_request_id == RawRequest.id, foreign_keys=[raw_request_id])
    status = Column(String)
    selected = Column(Boolean)
    test_case_id = Column(Integer)
    execution_order = Column(Integer)
    test_case = relationship(
        TestCase,
        primaryjoin=test_case_id == TestCase.id,
        foreign_keys=[test_case_id],
        backref=backref('requests', order_by=[execution_order])
    )

    @property
    def legacy_format(self):
        return {
            "status": self.status,
            "index": self.id,
            "content_type": self.raw_request.content_type,
            "status_code": self.raw_request.status_code,
            "selected": self.selected,
            "file": "{}".format(self.raw_request_id),
            "path": self.raw_request.path,
            "data": self.raw_request.data,
            "method": self.raw_request.method,
            "name": self.raw_request.name
        }

