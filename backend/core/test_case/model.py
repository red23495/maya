from backend.system import BaseModel
from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship
from typing import List


class TestCase(BaseModel):

    __tablename__ = 'test_cases'

    id: int = Column(Integer, primary_key=True, autoincrement=True)
    name: str = Column(String(255), nullable=False)
    suite_id: int = Column(Integer, ForeignKey("test_suites.id"))
    request_id: int = Column(Integer, ForeignKey("requests.id"))
    test_suite: "TestSuite" = relationship("TestSuite", uselist=False)
    request: "Request" = relationship("Request", uselist=False)
    parent_id: int = Column(Integer, ForeignKey("test_cases.id"))
    children: List["TestCase"] = relationship("TestCase")
    parent: "TestCase" = relationship("TestCase", remote_side=[id], uselist=False)


from backend.core.test_suite import TestSuite
from backend.core.request import Request
