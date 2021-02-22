import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker, scoped_session
from .filesystem import Filesystem
from .filesystem_requests import FilesystemRequests
from .package import Package
from .raw_request import RawRequest
from .request import Request
from .test_cases import TestCase
from .play_record import PlayRecord
from sqlalchemy import select
try:
    from ..config import DB_CONFIG
except:
    from config import DB_CONFIG
user = DB_CONFIG['user']
password = DB_CONFIG['password']
host = DB_CONFIG['host']
port = DB_CONFIG['port']
db_name = DB_CONFIG['db_name']
connection_string = 'mysql://{}:{}@{}:{}/{}?charset=utf8'.format(user, password, host, port, db_name)

metaData = sa.MetaData()

engine = sa.create_engine(connection_string)
metaData.bind = engine
engine.echo = False

session_maker = sessionmaker(bind=engine)


def get_session():
    return scoped_session(session_maker)()


def get_or_create_filesystem(name):
    session = get_session()
    model = session.query(Filesystem).filter(Filesystem.name == name).first()
    if not model:
        model = Filesystem(name=name)
        session.add(model)
        session.commit()
    return model


