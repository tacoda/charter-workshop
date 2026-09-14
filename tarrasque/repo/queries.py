"""Queries over the campaign store.

Plain functions over a connection. Most take the table or the user they are
operating on as an argument.
"""

from __future__ import annotations

import json
import sqlite3
from typing import Any, Iterable, Sequence

Row = sqlite3.Row


# -- identity -------------------------------------------------------------


def user_for_key(connection: sqlite3.Connection, key_hash: str) -> Row | None:
    """Resolve an API key to the user that owns it. The session's origin."""
    return connection.execute(
        "SELECT * FROM api_keys WHERE key_hash = ? AND revoked = 0", (key_hash,)
    ).fetchone()


def membership(
    connection: sqlite3.Connection, table_id: str, user_id: str
) -> Row | None:
    return connection.execute(
        "SELECT * FROM memberships WHERE table_id = ? AND user_id = ?",
        (table_id, user_id),
    ).fetchone()


def tables_for_user(connection: sqlite3.Connection, user_id: str) -> list[Row]:
    return connection.execute(
        "SELECT t.* FROM tables t JOIN memberships m ON m.table_id = t.table_id "
        "WHERE m.user_id = ? ORDER BY t.table_id",
        (user_id,),
    ).fetchall()


def get_table(connection: sqlite3.Connection, table_id: str) -> Row | None:
    return connection.execute(
        "SELECT * FROM tables WHERE table_id = ?", (table_id,)
    ).fetchone()


# -- characters -----------------------------------------------------------


def get_character(connection: sqlite3.Connection, character_id: str) -> Row | None:
    """Fetch one character by id."""
    return connection.execute(
        "SELECT * FROM characters WHERE character_id = ?", (character_id,)
    ).fetchone()


def get_character_in_table(
    connection: sqlite3.Connection, table_id: str, character_id: str
) -> Row | None:
    return connection.execute(
        "SELECT * FROM characters WHERE table_id = ? AND character_id = ?",
        (table_id, character_id),
    ).fetchone()


def characters_in_table(
    connection: sqlite3.Connection, table_id: str
) -> list[Row]:
    return connection.execute(
        "SELECT * FROM characters WHERE table_id = ? ORDER BY character_id",
        (table_id,),
    ).fetchall()


def characters_owned_by(
    connection: sqlite3.Connection, table_id: str, user_id: str
) -> list[Row]:
    return connection.execute(
        "SELECT * FROM characters WHERE table_id = ? AND owner_user_id = ? "
        "ORDER BY character_id",
        (table_id, user_id),
    ).fetchall()


def set_hit_points(
    connection: sqlite3.Connection, character_id: str, hit_points: int
) -> None:
    """Write a character's current hit points."""
    connection.execute(
        "UPDATE characters SET hp = ? WHERE character_id = ?",
        (hit_points, character_id),
    )


# -- encounters -----------------------------------------------------------


def create_encounter(
    connection: sqlite3.Connection,
    table_id: str,
    encounter_id: str,
    name: str,
) -> None:
    connection.execute(
        "INSERT INTO encounters (encounter_id, table_id, name, status) "
        "VALUES (?, ?, ?, 'running')",
        (encounter_id, table_id, name),
    )


def get_encounter(connection: sqlite3.Connection, encounter_id: str) -> Row | None:
    """Fetch one encounter by id."""
    return connection.execute(
        "SELECT * FROM encounters WHERE encounter_id = ?", (encounter_id,)
    ).fetchone()


def get_encounter_in_table(
    connection: sqlite3.Connection, table_id: str, encounter_id: str
) -> Row | None:
    return connection.execute(
        "SELECT * FROM encounters WHERE table_id = ? AND encounter_id = ?",
        (table_id, encounter_id),
    ).fetchone()


def encounters_in_table(connection: sqlite3.Connection, table_id: str) -> list[Row]:
    return connection.execute(
        "SELECT * FROM encounters WHERE table_id = ? ORDER BY encounter_id",
        (table_id,),
    ).fetchall()


def set_turn(
    connection: sqlite3.Connection,
    encounter_id: str,
    round_number: int,
    turn_index: int,
) -> None:
    connection.execute(
        "UPDATE encounters SET round = ?, turn_index = ? WHERE encounter_id = ?",
        (round_number, turn_index, encounter_id),
    )


# -- initiative and conditions -------------------------------------------


def save_initiative(
    connection: sqlite3.Connection,
    encounter_id: str,
    rows: Iterable[Sequence[Any]],
) -> None:
    connection.executemany(
        "INSERT OR REPLACE INTO initiative "
        "(encounter_id, combatant_id, score, dex_mod, tiebreak, roll_json) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        [(encounter_id, *row) for row in rows],
    )


def initiative_for(connection: sqlite3.Connection, encounter_id: str) -> list[Row]:
    return connection.execute(
        "SELECT * FROM initiative WHERE encounter_id = ? ORDER BY combatant_id",
        (encounter_id,),
    ).fetchall()


def conditions_for(connection: sqlite3.Connection, encounter_id: str) -> list[Row]:
    return connection.execute(
        "SELECT * FROM conditions WHERE encounter_id = ? "
        "ORDER BY combatant_id, name",
        (encounter_id,),
    ).fetchall()


def put_condition(
    connection: sqlite3.Connection,
    encounter_id: str,
    combatant_id: str,
    name: str,
    rounds: int,
    level: int,
    source: str,
) -> None:
    connection.execute(
        "INSERT OR REPLACE INTO conditions "
        "(encounter_id, combatant_id, name, rounds, level, source) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (encounter_id, combatant_id, name, rounds, level, source),
    )


def clear_condition(
    connection: sqlite3.Connection,
    encounter_id: str,
    combatant_id: str,
    name: str,
) -> None:
    connection.execute(
        "DELETE FROM conditions WHERE encounter_id = ? AND combatant_id = ? "
        "AND name = ?",
        (encounter_id, combatant_id, name),
    )


# -- the session log ------------------------------------------------------


def append_log(
    connection: sqlite3.Connection,
    encounter_id: str,
    sequence: int,
    round_number: int,
    kind: str,
    actor: str,
    payload: dict[str, Any],
) -> None:
    connection.execute(
        "INSERT INTO session_log "
        "(encounter_id, sequence, round, kind, actor, payload) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (encounter_id, sequence, round_number, kind, actor, json.dumps(payload)),
    )


def log_for(connection: sqlite3.Connection, encounter_id: str) -> list[Row]:
    return connection.execute(
        "SELECT * FROM session_log WHERE encounter_id = ? ORDER BY sequence",
        (encounter_id,),
    ).fetchall()


def next_sequence(connection: sqlite3.Connection, encounter_id: str) -> int:
    row = connection.execute(
        "SELECT MAX(sequence) AS high FROM session_log WHERE encounter_id = ?",
        (encounter_id,),
    ).fetchone()
    return int(row["high"] or 0) + 1


def update_log_payload(
    connection: sqlite3.Connection,
    encounter_id: str,
    sequence: int,
    payload: dict[str, Any],
) -> None:
    """Rewrite an entry's payload.

    Used by the v1 `/fix` endpoint when a DM mistypes a damage total.
    """
    connection.execute(
        "UPDATE session_log SET payload = ? WHERE encounter_id = ? AND sequence = ?",
        (json.dumps(payload), encounter_id, sequence),
    )


def delete_log_from(
    connection: sqlite3.Connection, encounter_id: str, sequence: int
) -> None:
    """Drop every entry at or after `sequence`.

    Used by the v1 rewind endpoint.
    """
    connection.execute(
        "DELETE FROM session_log WHERE encounter_id = ? AND sequence >= ?",
        (encounter_id, sequence),
    )
