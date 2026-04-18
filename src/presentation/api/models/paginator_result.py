from typing import Generic, Self, TypeVar
from urllib.parse import urlencode

from fastapi import Request
from pydantic import BaseModel

__all__ = ["LimitOffsetPaginatorResult"]

T = TypeVar("T")


class LimitOffsetPaginatorResult(BaseModel, Generic[T]):
    count: int
    results: list[T]
    next: str | None = None
    previous: str | None = None

    @classmethod
    def create(
        cls,
        request: Request,
        results: list[T],
        total_count: int,
        limit: int,
        offset: int,
    ) -> Self:
        base_url = str(request.url).split("?")[0]
        current_params = dict(request.query_params)

        current_params = {
            k: v for k, v in current_params.items() if k not in ["limit", "offset"]
        }

        next_url = None
        if offset + limit < total_count:
            next_params = {**current_params, "limit": limit, "offset": offset + limit}
            next_url = f"{base_url}?{urlencode(next_params)}"

        previous_url = None
        if offset > 0:
            previous_offset = max(0, offset - limit)
            previous_params = {
                **current_params,
                "limit": limit,
                "offset": previous_offset,
            }
            previous_url = f"{base_url}?{urlencode(previous_params)}"

        return cls(
            count=total_count,
            next=next_url,
            previous=previous_url,
            results=results,
        )
