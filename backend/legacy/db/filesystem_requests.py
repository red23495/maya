from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from .filesystem import Filesystem
from sqlalchemy.orm import relationship
from .raw_request import RawRequest
Base = declarative_base()
from .base import _Base


class FilesystemRequests(Base, _Base):
    __tablename__ = 'filesystem_requests'

    id = Column(Integer, primary_key=True, autoincrement=True)
    filesystem_id = Column(Integer)
    raw_request_id = Column(Integer)
    is_processed = Column(Boolean)
    filesystem = relationship(
        Filesystem,
        primaryjoin=Filesystem.id == filesystem_id,
        foreign_keys=[filesystem_id], backref='filesystem_requests'
    )
    raw_request = relationship(
        RawRequest, primaryjoin=RawRequest.id == raw_request_id, foreign_keys=[raw_request_id]
    )

    def cascade(self):
        return [self.raw_request]