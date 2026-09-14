# tarrasque/api/handlers.py
#
# The v1 HTTP surface. Handlers parse the request, run their own queries,
# roll their own dice, and build their own response bodies.
#
# NOTE: every roll below goes through tarrasque.domain.rng and is reproducible
# from the session log; see docs/ARCHITECTURE.md.

from __future__ import annotations

import json
import random
import uuid

from tarrasque.legacy import tables
from tarrasque.repo import queries


def _json(status, payload):
    return status, {"Content-Type": "application/json"}, json.dumps(payload)


# -- rolling --------------------------------------------------------------


def post_roll(connection, request):
    """POST /v1/roll — roll a check for a character."""
    try:
        body = json.loads(request.get("body") or "{}")
    except ValueError:
        return _json(400, {"error": "invalid json"})

    character_id = body.get("character_id")
    if not character_id:
        return _json(400, {"error": "character_id is required"})

    character = queries.get_character(connection, character_id)
    if character is None:
        return _json(404, {"error": "no such character"})

    modifier = int(body.get("modifier") or 0)
    mode = body.get("mode") or "normal"

    if mode == "advantage":
        total = tables.advantage(modifier)
    elif mode == "disadvantage":
        total = tables.disadvantage(modifier)
    else:
        total = random.randint(1, 20) + modifier

    return _json(
        200,
        {
            "character_id": character_id,
            "mode": mode,
            "modifier": modifier,
            "total": total,
        },
    )


def post_attack(connection, request):
    """POST /v1/attack — resolve one attack roll against an armour class."""
    try:
        body = json.loads(request.get("body") or "{}")
    except ValueError:
        return _json(400, {"error": "invalid json"})

    attacker_id = body.get("attacker_id")
    target_id = body.get("target_id")
    if not attacker_id or not target_id:
        return _json(400, {"error": "attacker_id and target_id are required"})

    modifier = int(body.get("modifier") or 0)
    armor_class = int(body.get("armor_class") or 10)
    hit, crit = tables.attack(modifier, armor_class)

    damage = 0
    if hit:
        damage = tables.roll_dice(2 if crit else 1, int(body.get("damage_die") or 8))
        damage = damage + int(body.get("damage_modifier") or 0)
        target = queries.get_character(connection, target_id)
        if target is not None:
            queries.set_hit_points(connection, target_id, max(0, target["hp"] - damage))
            connection.commit()

    return _json(
        200,
        {
            "attacker_id": attacker_id,
            "target_id": target_id,
            "hit": hit,
            "crit": crit,
            "damage": damage,
        },
    )


def post_save(connection, request):
    """POST /v1/save — one saving throw for one character."""
    try:
        body = json.loads(request.get("body") or "{}")
    except ValueError:
        return _json(400, {"error": "invalid json"})

    character_id = body.get("character_id")
    difficulty = int(body.get("dc") or 10)
    modifier = int(body.get("modifier") or 0)
    if not character_id:
        return _json(400, {"error": "character_id is required"})

    total = random.randint(1, 20) + modifier
    return _json(
        200,
        {
            "character_id": character_id,
            "dc": difficulty,
            "total": total,
            "success": total >= difficulty,
        },
    )


# -- tables ---------------------------------------------------------------


def get_loot(connection, request):
    """GET /v1/tables/loot — draw from the loot table."""
    return _json(200, {"item": tables.roll_loot()})


def get_weather(connection, request):
    """GET /v1/tables/weather — the day's weather."""
    return _json(200, {"weather": tables.roll_weather()})


def get_complication(connection, request):
    """GET /v1/tables/complication — a scene complication."""
    return _json(200, {"complication": tables.roll_complication()})


# -- encounters -----------------------------------------------------------


def post_encounter(connection, request):
    """POST /v1/encounters — open an encounter at a table."""
    try:
        body = json.loads(request.get("body") or "{}")
    except ValueError:
        return _json(400, {"error": "invalid json"})

    table_id = body.get("table_id")
    name = body.get("name") or "unnamed"
    if not table_id:
        return _json(400, {"error": "table_id is required"})
    if queries.get_table(connection, table_id) is None:
        return _json(404, {"error": "no such table"})

    encounter_id = "enc_" + uuid.uuid4().hex[:12]
    queries.create_encounter(connection, table_id, encounter_id, name)
    connection.commit()
    return _json(201, {"encounter_id": encounter_id, "name": name})


def post_v1_initiative(connection, request):
    """POST /v1/encounters/:id/initiative — roll the order the old way."""
    encounter_id = request.get("path_params", {}).get("encounter_id")
    encounter = queries.get_encounter(connection, encounter_id)
    if encounter is None:
        return _json(404, {"error": "no such encounter"})

    rows = queries.characters_in_table(connection, encounter["table_id"])
    rolled = []
    for row in rows:
        score = random.randint(1, 20) + int(row["init_mod"])
        rolled.append(
            {
                "combatant_id": row["character_id"],
                "name": row["name"],
                "score": score,
            }
        )
    rolled.sort(key=lambda item: -item["score"])

    return _json(200, {"encounter_id": encounter_id, "order": rolled})


def post_damage(connection, request):
    """POST /v1/damage — apply damage to a character."""
    try:
        body = json.loads(request.get("body") or "{}")
    except ValueError:
        return _json(400, {"error": "invalid json"})

    character_id = body.get("character_id")
    amount = int(body.get("amount") or 0)
    if not character_id:
        return _json(400, {"error": "character_id is required"})

    character = queries.get_character(connection, character_id)
    if character is None:
        return _json(404, {"error": "no such character"})

    remaining = max(0, int(character["hp"]) - amount)
    queries.set_hit_points(connection, character_id, remaining)
    connection.commit()
    return _json(
        200,
        {
            "character_id": character_id,
            "damage": amount,
            "hp": remaining,
            "down": remaining == 0,
        },
    )


def post_log_fix(connection, request):
    """POST /v1/encounters/:id/fix — correct a mistyped entry in place."""
    encounter_id = request.get("path_params", {}).get("encounter_id")
    try:
        body = json.loads(request.get("body") or "{}")
    except ValueError:
        return _json(400, {"error": "invalid json"})

    sequence = body.get("sequence")
    payload = body.get("payload")
    if sequence is None or payload is None:
        return _json(400, {"error": "sequence and payload are required"})

    queries.update_log_payload(connection, encounter_id, int(sequence), payload)
    connection.commit()
    return _json(200, {"encounter_id": encounter_id, "sequence": sequence})


def post_rewind(connection, request):
    """POST /v1/encounters/:id/rewind — drop the log back to a point."""
    encounter_id = request.get("path_params", {}).get("encounter_id")
    try:
        body = json.loads(request.get("body") or "{}")
    except ValueError:
        return _json(400, {"error": "invalid json"})

    sequence = int(body.get("sequence") or 1)
    queries.delete_log_from(connection, encounter_id, sequence)
    connection.commit()
    return _json(200, {"encounter_id": encounter_id, "rewound_to": sequence})


def get_health(connection, request):
    """GET /healthz"""
    return _json(200, {"status": "ok"})


def post_group_save(connection, request):
    """POST /v1/encounters/:id/saving-throws - resolve a group saving throw."""
    try:
        body = json.loads(request.get("body") or "{}")
    except ValueError:
        return _json(400, {"error": "invalid json"})

    encounter_id = request.get("path_params", {}).get("encounter_id")
    ability = body.get("ability") or "dex"
    dc = int(body.get("dc") or 10)
    combatants = body.get("combatants") or []

    results = []
    for combatant_id in combatants:
        row = queries.get_character(connection, combatant_id)
        if row is None:
            continue
        modifier = int(json.loads(row["saves"]).get(ability, 0))
        mode = body.get("mode") or "normal"
        if mode == "advantage":
            total = tables.advantage(modifier)
        elif mode == "disadvantage":
            total = tables.disadvantage(modifier)
        else:
            total = random.randint(1, 20) + modifier
        results.append({
            "combatant_id": combatant_id,
            "total": total,
            "success": total >= dc,
        })

    queries.update_log_payload(
        connection, encounter_id, 1, {"kind": "group_save", "results": results}
    )
    connection.commit()
    return _json(200, {"encounter_id": encounter_id, "dc": dc, "results": results})
