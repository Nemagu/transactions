from __future__ import annotations

from urllib.parse import parse_qs, urlparse

from starlette.requests import Request

from presentation.api.models.paginator_result import LimitOffsetPaginatorResult


def _build_request(path: str, query: str) -> Request:
    scope = {
        "type": "http",
        "http_version": "1.1",
        "method": "GET",
        "scheme": "http",
        "path": path,
        "raw_path": path.encode("utf-8"),
        "query_string": query.encode("utf-8"),
        "headers": [],
        "client": ("127.0.0.1", 12345),
        "server": ("testserver", 80),
    }
    return Request(scope)


def test_limit_offset_paginator_result_create_builds_next_and_previous_urls() -> None:
    request = _build_request("/items", "limit=2&offset=2&state=active")

    result = LimitOffsetPaginatorResult[int].create(
        request=request,
        results=[10, 11],
        total_count=10,
        limit=2,
        offset=2,
    )

    assert result.count == 10
    assert result.results == [10, 11]
    assert result.next is not None
    assert result.previous is not None

    next_query = parse_qs(urlparse(result.next).query)
    prev_query = parse_qs(urlparse(result.previous).query)
    assert next_query["state"] == ["active"]
    assert next_query["limit"] == ["2"]
    assert next_query["offset"] == ["4"]
    assert prev_query["state"] == ["active"]
    assert prev_query["limit"] == ["2"]
    assert prev_query["offset"] == ["0"]


def test_limit_offset_paginator_result_create_omits_prev_and_next_on_edges() -> None:
    request = _build_request("/items", "limit=3&offset=0")

    result = LimitOffsetPaginatorResult[int].create(
        request=request,
        results=[1, 2],
        total_count=2,
        limit=3,
        offset=0,
    )

    assert result.previous is None
    assert result.next is None
