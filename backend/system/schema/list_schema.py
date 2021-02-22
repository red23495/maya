from .base_schema import BaseSchema
from typing import List, Optional


class ListSchema(BaseSchema):
    page: int
    limit: int
    total: int
    data: List
    prev: Optional[str]
    next: Optional[str]

