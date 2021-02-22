from backend.system import BaseModel
from backend.system.db import IntEnum
from sqlalchemy import Column, String, Integer, ForeignKey, Text
from sqlalchemy.orm import relationship
from typing import Dict
from backend.system.db import JSONDict
from .enum import RequestDataType, ResponseDataType


class Request(BaseModel):

    __tablename__ = 'requests'

    id: int = Column(Integer, primary_key=True, autoincrement=True)
    url: str = Column(String(1024))
    request_method: str = Column(String(10))
    request_headers: Dict[str, str] = Column(JSONDict)
    request_body: str = Column(Text)
    request_data_type: RequestDataType = Column(IntEnum(RequestDataType))
    response_headers: Dict[str, str] = Column(JSONDict)
    response_body: str = Column(Text)
    response_data_type: ResponseDataType = Column(IntEnum(ResponseDataType))
    response_status: int = Column(Integer)
    readable_name: str = Column(String(255))
    module: str = Column(String(255))
