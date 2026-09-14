"""A small WSGI router.

Standard library only. Routes are (method, pattern) pairs; a pattern segment
starting with ':' binds a path parameter. v1 handlers take (connection,
request). v2 handlers take (connection, session, *path_params) and require a
bearer token plus a seat at the table named in the path.
"""

from __future__ import annotations

import json
import sqlite3
from typing import Any, Callable, Iterable
from urllib.parse import parse_qs

from tarrasque.api import encounters, handlers
from tarrasque.api.session import Forbidden, Unauthenticated, session_from_header
from tarrasque.repo import queries

Response = tuple[int, dict[str, str], str]

STATUS_TEXT = {
    200: "200 OK",
    201: "201 Created",
    400: "400 Bad Request",
    401: "401 Unauthorized",
    403: "403 Forbidden",
    404: "404 Not Found",
    405: "405 Method Not Allowed",
    409: "409 Conflict",
    422: "422 Unprocessable Entity",
    500: "500 Internal Server Error",
}


def match(pattern: str, path: str) -> dict[str, str] | None:
    """Match a route pattern against a path, binding ':name' segments."""
    pattern_parts = [part for part in pattern.strip("/").split("/") if part]
    path_parts = [part for part in path.strip("/").split("/") if part]
    if len(pattern_parts) != len(path_parts):
        return None
    bound: dict[str, str] = {}
    for expected, actual in zip(pattern_parts, path_parts):
        if expected.startswith(":"):
            bound[expected[1:]] = actual
        elif expected != actual:
            return None
    return bound


V1_ROUTES: list[tuple[str, str, Callable[..., Response]]] = [
    ("GET", "/healthz", handlers.get_health),
    ("POST", "/v1/roll", handlers.post_roll),
    ("POST", "/v1/attack", handlers.post_attack),
    ("POST", "/v1/save", handlers.post_save),
    ("GET", "/v1/tables/loot", handlers.get_loot),
    ("GET", "/v1/tables/weather", handlers.get_weather),
    ("GET", "/v1/tables/complication", handlers.get_complication),
    ("POST", "/v1/encounters", handlers.post_encounter),
    ("POST", "/v1/damage", handlers.post_damage),
    ("POST", "/v1/encounters/:encounter_id/saving-throws",
     handlers.post_group_save),
    ("POST", "/v1/encounters/:encounter_id/initiative", handlers.post_v1_initiative),
    ("POST", "/v1/encounters/:encounter_id/fix", handlers.post_log_fix),
    ("POST", "/v1/encounters/:encounter_id/rewind", handlers.post_rewind),
]

V2_ROUTES: list[tuple[str, str, Callable[..., Response]]] = [
    ("GET", "/v2/encounters/:encounter_id", encounters.get_encounter),
    ("GET", "/v2/encounters/:encounter_id/log", encounters.get_log),
    ("POST", "/v2/encounters/:encounter_id/initiative", encounters.post_initiative),
    (
        "POST",
        "/v2/encounters/:encounter_id/characters/:character_id/check",
        encounters.post_check,
    ),
]


def _error(status: int, message: str) -> Response:
    return status, {"Content-Type": "application/json"}, json.dumps({"error": message})


def table_of(connection: sqlite3.Connection, encounter_id: str) -> str | None:
    row = queries.get_encounter(connection, encounter_id)
    return None if row is None else str(row["table_id"])


def dispatch(
    connection: sqlite3.Connection,
    method: str,
    path: str,
    query: dict[str, str],
    body: str,
    authorization: str | None,
) -> Response:
    """Route one request. v2 resolves a session against the encounter's table."""
    for route_method, pattern, handler in V2_ROUTES:
        bound = match(pattern, path)
        if bound is None or route_method != method:
            continue
        table_id = table_of(connection, bound["encounter_id"])
        if table_id is None:
            return _error(404, "no such encounter")
        try:
            session = session_from_header(connection, authorization, table_id)
        except Unauthenticated as error:
            return _error(401, str(error))
        except Forbidden as error:
            return _error(403, str(error))
        return handler(connection, session, *bound.values())

    for route_method, pattern, handler in V1_ROUTES:
        bound = match(pattern, path)
        if bound is None or route_method != method:
            continue
        request = {"query": query, "body": body, "path_params": bound}
        return handler(connection, request)

    return _error(404, "no such route")


def application(
    connection: sqlite3.Connection,
) -> Callable[[dict[str, Any], Callable[..., Any]], Iterable[bytes]]:
    """Build a WSGI app bound to one connection."""

    def wsgi(environ: dict[str, Any], start_response: Callable[..., Any]) -> list[bytes]:
        length = int(environ.get("CONTENT_LENGTH") or 0)
        body = environ["wsgi.input"].read(length).decode("utf-8") if length else ""
        query = {
            key: values[0]
            for key, values in parse_qs(environ.get("QUERY_STRING", "")).items()
        }
        status, headers, payload = dispatch(
            connection,
            environ.get("REQUEST_METHOD", "GET"),
            environ.get("PATH_INFO", "/"),
            query,
            body,
            environ.get("HTTP_AUTHORIZATION"),
        )
        start_response(
            STATUS_TEXT.get(status, "500 Internal Server Error"), list(headers.items())
        )
        return [payload.encode("utf-8")]

    return wsgi
