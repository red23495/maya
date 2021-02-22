from . import BaseService
from datetime import datetime
try:
    from ..db import PlayRecord
except:
    from db import PlayRecord


class PlayRecordService(BaseService):
    model = PlayRecord

    def save_record(self, record, filesystem, package):
        rec = PlayRecord(
            result=record,
            filesystem=filesystem,
            package=package,
            recorded_at=datetime.now()
        )
        self.save(rec)
        self.refresh(rec)
        return rec

