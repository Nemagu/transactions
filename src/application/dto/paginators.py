from dataclasses import dataclass


@dataclass
class LimitOffsetPaginator:
    limit: int = 10
    offset: int = 0
