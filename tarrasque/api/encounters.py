"""The v2 encounter surface.

Written after the domain layer landed. These handlers do four things and
nothing else: resolve the session, check what it controls, call into
`tarrasque.domain`, and serialize the result. No dice, no SQL strings, and
no authority taken from the request body.

This is the pattern new endpoints follow. It is also outnumbered by
`tarrasque/api/handlers.py`, which predates it.
"""

from __future__ import annotations

import json
import sqlite3
from typing import Any

from tarrasque.api.session import Forbidden, Session, require_control
from tarrasque.domain import dice, initiative
from tarrasque.domain.conditions import Condition
from tarrasque.domain.encounter import Encounter
from tarrasque.domain.initiative import Combatant
from tarrasque.domain.log import Entry
from tarrasque.domain.rng import stream_for
from tarrasque.repo import queries

Response = tuple[int, dict[str, str], str]


def _json(status: int, payload: dict[str, Any]) -> Response:
    return status, {"Content-Type": "application/json"}, json.dumps(payload)


def _combatant(row: sqlite3.Row) -> Combatant:
    return Combatant(
        combatant_id=row["character_id"],
        name=row["name"],
        is_player_character=bool(row["is_pc"]),
        dexterity_modifier=int(row["dex_mod"]),
        initiative_modifier=int(row["init_mod"]),
        hit_points=int(row["hp"]),
        max_hit_points=int(row["max_hp"]),
        save_modifiers=json.loads(row["saves"]),
    )


def load_encounter(
    connection: sqlite3.Connection, session: Session, encounter_id: str
) -> Encounter | None:
    """Read one encounter, scoped to the session's table, into the domain type."""
    row = queries.get_encounter_in_table(connection, session.table_id, encounter_id)
    if row is None:
        return None

    combatants = {
        character["character_id"]: _combatant(character)
        for character in queries.characters_in_table(connection, session.table_id)
    }

    order: list[initiative.InitiativeEntry] = []
    for entry in queries.initiative_for(connection, encounter_id):
        stored = json.loads(entry["roll_json"])
        order.append(
            initiative.InitiativeEntry(
                combatant_id=entry["combatant_id"],
                score=int(entry["score"]),
                dexterity_modifier=int(entry["dex_mod"]),
                tiebreak=int(entry["tiebreak"]),
                roll=dice.Roll(
                    notation=stored["notation"],
                    seed=stored["seed"],
                    stream_position=stored["stream_position"],
                    faces=stored["faces"],
                    kept=stored["kept"],
                    dropped=stored["dropped"],
                    bonus=stored["bonus"],
                    total=stored["total"],
                ),
            )
        )

    conditions: dict[str, list[Condition]] = {}
    for item in queries.conditions_for(connection, encounter_id):
        conditions.setdefault(item["combatant_id"], []).append(
            Condition(
                name=item["name"],
                rounds_remaining=int(item["rounds"]),
                level=int(item["level"]),
                source=item["source"],
            )
        )

    return Encounter(
        encounter_id=row["encounter_id"],
        table_id=row["table_id"],
        status=row["status"],
        round_number=int(row["round"]),
        turn_index=int(row["turn_index"]),
        combatants=combatants,
        order=initiative.order(order),
        conditions=conditions,
        next_sequence=queries.next_sequence(connection, encounter_id),
    )


def write_entries(
    connection: sqlite3.Connection, entries: list[Entry]
) -> None:
    """Append every entry. The log is never updated and never deleted."""
    for entry in entries:
        queries.append_log(
            connection,
            entry.encounter_id,
            entry.sequence,
            entry.round_number,
            entry.kind,
            entry.actor,
            entry.payload,
        )
    connection.commit()


def get_encounter(
    connection: sqlite3.Connection, session: Session, encounter_id: str
) -> Response:
    """GET /v2/encounters/:id — the encounter's current state."""
    encounter = load_encounter(connection, session, encounter_id)
    if encounter is None:
        return _json(404, {"error": "no such encounter"})
    return _json(200, encounter.to_dict())


def get_log(
    connection: sqlite3.Connection, session: Session, encounter_id: str
) -> Response:
    """GET /v2/encounters/:id/log — the append-only history."""
    if queries.get_encounter_in_table(connection, session.table_id, encounter_id) is None:
        return _json(404, {"error": "no such encounter"})
    rows = queries.log_for(connection, encounter_id)
    return _json(
        200,
        {
            "entries": [
                {
                    "sequence": int(row["sequence"]),
                    "round": int(row["round"]),
                    "kind": row["kind"],
                    "actor": row["actor"],
                    "payload": json.loads(row["payload"]),
                }
                for row in rows
            ]
        },
    )


def post_initiative(
    connection: sqlite3.Connection, session: Session, encounter_id: str
) -> Response:
    """POST /v2/encounters/:id/initiative — roll the order for the encounter."""
    if not session.is_dungeon_master():
        return _json(403, {"error": "only the dungeon master rolls initiative"})

    encounter = load_encounter(connection, session, encounter_id)
    if encounter is None:
        return _json(404, {"error": "no such encounter"})

    rng = stream_for(encounter_id, encounter.round_number, "initiative")
    entries = initiative.roll_initiative(rng, list(encounter.combatants.values()))

    queries.save_initiative(
        connection,
        encounter_id,
        [
            (
                entry.combatant_id,
                entry.score,
                entry.dexterity_modifier,
                entry.tiebreak,
                json.dumps(entry.roll.to_dict()),
            )
            for entry in entries
        ],
    )
    write_entries(
        connection,
        [
            encounter.entry(
                "initiative_rolled",
                session.user_id,
                {"order": [entry.to_dict() for entry in entries]},
            )
        ],
    )
    return _json(200, {"order": [entry.to_dict() for entry in entries]})


def post_check(
    connection: sqlite3.Connection,
    session: Session,
    encounter_id: str,
    character_id: str,
) -> Response:
    """POST /v2/encounters/:id/characters/:cid/check — one ability check."""
    try:
        require_control(connection, session, character_id)
    except Forbidden as error:
        return _json(403, {"error": str(error)})

    encounter = load_encounter(connection, session, encounter_id)
    if encounter is None:
        return _json(404, {"error": "no such encounter"})

    rng = stream_for(encounter_id, encounter.round_number, f"check:{character_id}")
    result = dice.roll(rng, "1d20")
    write_entries(
        connection,
        [
            encounter.entry(
                "check", character_id, {"roll": result.to_dict()}
            )
        ],
    )
    return _json(200, {"character_id": character_id, "roll": result.to_dict()})
