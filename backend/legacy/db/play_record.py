from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime
Base = declarative_base()
from .base import _Base


class PlayRecord(Base, _Base):
    __tablename__ = 'play_records'

    id = Column(Integer, primary_key=True, autoincrement=True)
    result = Column(String)
    recorded_at = Column(DateTime)
    filesystem = Column(String)
    package = Column(String)
