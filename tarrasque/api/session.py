"""The authenticated session.

A session is created once per request from the `Authorization` header and
carries the user the caller proved they are, plus what that user controls at
the table. It is the only trustworthy source of authority in the service: a
character id taken from a request body is a character the caller chose.
"""

from __future__ import annotations

import hashlib
import sqlite3
from dataclasses import dataclass

from tarrasque.repo import queries


class Unauthenticated(Exception):
    """Raised when a request carries no usable credential."""


class Forbidden(Exception):
    """Raised when the session may not act for the character it asked for."""


@dataclass(frozen=True, slots=True)
class Session:
    """One authenticated caller, for the duration of one request."""

    user_id: str
    table_id: str
    role: str

    def is_dungeon_master(self) -> bool:
        return self.role == "dm"


def hash_key(raw_key: str) -> str:
    return hashlib.sha256(raw_key.encode("utf-8")).hexdigest()


def session_from_header(
    connection: sqlite3.Connection, authorization: str | None, table_id: str
) -> Session:
    """Resolve `Authorization: Bearer <key>` and a table into a session."""
    if not authorization or not authorization.startswith("Bearer "):
        raise Unauthenticated("missing bearer token")
    user = queries.user_for_key(connection, hash_key(authorization[7:]))
    if user is None:
        raise Unauthenticated("unknown or revoked key")
    seat = queries.membership(connection, table_id, user["user_id"])
    if seat is None:
        raise Forbidden(f"{user['user_id']} is not at {table_id}")
    return Session(
        user_id=user["user_id"], table_id=table_id, role=seat["role"]
    )


def controlled_characters(
    connection: sqlite3.Connection, session: Session
) -> list[str]:
    """Every character this session may act for.

    A dungeon master acts for every character at their own table. A player
    acts for the characters they own, and for nothing else.
    """
    if session.is_dungeon_master():
        rows = queries.characters_in_table(connection, session.table_id)
    else:
        rows = queries.characters_owned_by(
            connection, session.table_id, session.user_id
        )
    return [row["character_id"] for row in rows]


def require_control(
    connection: sqlite3.Connection, session: Session, character_id: str
) -> None:
    """Refuse unless the session controls `character_id`."""
    if character_id not in controlled_characters(connection, session):
        raise Forbidden(f"{session.user_id} does not control {character_id}")
