from . import BaseService
try:
    from ..db import RawRequest
except:
    from db import RawRequest


class RawRequestService(BaseService):
    model = RawRequest

