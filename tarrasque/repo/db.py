"""SQLite connection and schema.

One connection per process, handed down from the entry point. No ORM: queries
are plain functions over a cursor in `tarrasque.repo.queries`.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS tables (
    table_id    TEXT PRIMARY KEY,
    name        TEXT NOT NULL,
    dm_user_id  TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS memberships (
    table_id    TEXT NOT NULL REFERENCES tables(table_id),
    user_id     TEXT NOT NULL,
    role        TEXT NOT NULL,
    PRIMARY KEY (table_id, user_id)
);

CREATE TABLE IF NOT EXISTS api_keys (
    key_hash    TEXT PRIMARY KEY,
    user_id     TEXT NOT NULL,
    label       TEXT NOT NULL,
    revoked     INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS characters (
    character_id TEXT PRIMARY KEY,
    table_id     TEXT NOT NULL REFERENCES tables(table_id),
    owner_user_id TEXT NOT NULL,
    name         TEXT NOT NULL,
    is_pc        INTEGER NOT NULL DEFAULT 1,
    dex_mod      INTEGER NOT NULL DEFAULT 0,
    init_mod     INTEGER NOT NULL DEFAULT 0,
    hp           INTEGER NOT NULL,
    max_hp       INTEGER NOT NULL,
    saves        TEXT NOT NULL DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS encounters (
    encounter_id TEXT PRIMARY KEY,
    table_id     TEXT NOT NULL REFERENCES tables(table_id),
    name         TEXT NOT NULL,
    status       TEXT NOT NULL,
    round        INTEGER NOT NULL DEFAULT 1,
    turn_index   INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS initiative (
    encounter_id TEXT NOT NULL REFERENCES encounters(encounter_id),
    combatant_id TEXT NOT NULL,
    score        INTEGER NOT NULL,
    dex_mod      INTEGER NOT NULL,
    tiebreak     INTEGER NOT NULL,
    roll_json    TEXT NOT NULL,
    PRIMARY KEY (encounter_id, combatant_id)
);

CREATE TABLE IF NOT EXISTS conditions (
    encounter_id TEXT NOT NULL REFERENCES encounters(encounter_id),
    combatant_id TEXT NOT NULL,
    name         TEXT NOT NULL,
    rounds       INTEGER NOT NULL,
    level        INTEGER NOT NULL DEFAULT 1,
    source       TEXT NOT NULL DEFAULT '',
    PRIMARY KEY (encounter_id, combatant_id, name)
);

CREATE TABLE IF NOT EXISTS session_log (
    encounter_id TEXT NOT NULL REFERENCES encounters(encounter_id),
    sequence     INTEGER NOT NULL,
    round        INTEGER NOT NULL,
    kind         TEXT NOT NULL,
    actor        TEXT NOT NULL,
    payload      TEXT NOT NULL,
    PRIMARY KEY (encounter_id, sequence)
);

CREATE INDEX IF NOT EXISTS idx_characters_table ON characters(table_id);
CREATE INDEX IF NOT EXISTS idx_encounters_table ON encounters(table_id);
"""


def connect(path: str | Path = ":memory:") -> sqlite3.Connection:
    """Open a connection with row access by name and foreign keys enforced."""
    connection = sqlite3.connect(str(path))
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def migrate(connection: sqlite3.Connection) -> None:
    """Create every table and index. Idempotent."""
    connection.executescript(SCHEMA)
    connection.commit()
