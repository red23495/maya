from . import BaseService
try:
    from ..db import FilesystemRequests
except:
    from db import FilesystemRequests
from sqlalchemy import update


class FilesystemRequestService(BaseService):
    model = FilesystemRequests

    def set_all_requests_as_processed(self, requests):
        for request in requests:
            table = request.__table__
            stmt = update(table).where(table.c.id == request.id).values(is_processed=1)
            self.session.execute(stmt)
            self.session.commit()
