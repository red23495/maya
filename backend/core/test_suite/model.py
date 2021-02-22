from backend.system import BaseModel
from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship


class TestSuite(BaseModel):

    __tablename__ = 'test_suites'

    id: int = Column(Integer, primary_key=True, autoincrement=True)
    version: str = Column(String(255))
    db: str = Column(String(255))


