from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class LimitOffsetPaginator:
    limit: int = 10
    offset: int = 0
