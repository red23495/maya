from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Text
from .base import _Base
import json

Base = declarative_base()


class RawRequest(Base, _Base):
    __tablename__ = 'raw_requests'

    json_fields = ['META', 'GET', 'POST', 'REQUEST', 'data', 'COOKIES',]

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(1024))
    META = Column(Text)
    GET = Column(Text)
    POST = Column(Text)
    COOKIES = Column(String(4096))
    REQUEST = Column(Text)
    method = Column(String(10))
    data = Column(Text)
    path = Column(String(1024))
    raw_post_data = Column(String(4096))
    response_content = Column(Text)
    content_type = Column(String(512))
    status_code = Column(Integer)

    @property
    def legacy_format(self):
        return {
            'file': '{}'.format(self.id),
            'index': self.id,
            'content_type': self.content_type,
            'method': self.method,
            'status_code': self.status_code,
            'name': self.name,
            'path': self.path,
            'selected': True,
            'status': 'OK',
            'data': self.REQUEST,
        }

    @property
    def test_format(self):
        data_dict = self.to_dict()
        content = self.response_content
        if self.content_type.startswith('application/json'):
            content = json.loads(content)
        elif not self.content_type.startswith('application/xml'):
            content = ''
        return {
            'index': self.id,
            'expected_response': {
                'content': content,
                'status_code': self.status_code,
                'content_type': self.content_type,
            },
            'request': {
                'COOKIES': data_dict.get('COOKIES', {}),
                'META': data_dict.get('META', {}),
                'GET': data_dict.get('GET', {}),
                'data': data_dict.get('data', {}),
                'POST': data_dict.get('POST', {}),
                'path': data_dict.get('path', {}),
                'REQUEST': data_dict.get('REQUEST', {}),
                'method': data_dict.get('method', {}),
                'raw_post_data': data_dict.get('raw_post_data', {}),
            },
            'name': self.name
        }
