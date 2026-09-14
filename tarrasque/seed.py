"""Deterministic seed data.

No clock and no randomness: the same call produces the same database, which
is what makes one run comparable to the run before it.
"""

from __future__ import annotations

import json
import sqlite3

from tarrasque.api.session import hash_key
from tarrasque.repo import db, queries

TABLES = [
    ("tbl_ashfall", "The Ashfall Expedition", "usr_mira"),
    ("tbl_saltmarsh", "Saltmarsh Irregulars", "usr_dev"),
]

MEMBERSHIPS = [
    ("tbl_ashfall", "usr_mira", "dm"),
    ("tbl_ashfall", "usr_jonah", "player"),
    ("tbl_ashfall", "usr_pilar", "player"),
    ("tbl_saltmarsh", "usr_dev", "dm"),
    ("tbl_saltmarsh", "usr_jonah", "player"),
]

KEYS = [
    ("tk_live_mira_0001", "usr_mira"),
    ("tk_live_jonah_001", "usr_jonah"),
    ("tk_live_pilar_001", "usr_pilar"),
    ("tk_live_dev_00001", "usr_dev"),
]

CHARACTERS = [
    # id, table, owner, name, is_pc, dex, init, hp, max_hp, saves
    ("chr_brann", "tbl_ashfall", "usr_jonah", "Brann Holt", 1, 1, 1, 34, 34,
     {"str": 5, "dex": 1, "con": 4, "int": -1, "wis": 2, "cha": 0}),
    ("chr_sable", "tbl_ashfall", "usr_pilar", "Sable Vane", 1, 4, 6, 22, 26,
     {"str": -1, "dex": 7, "con": 2, "int": 3, "wis": 1, "cha": 4}),
    ("chr_okra", "tbl_ashfall", "usr_mira", "Okra the Unbothered", 1, 0, 0, 41, 41,
     {"str": 3, "dex": 0, "con": 6, "int": 0, "wis": 5, "cha": 1}),
    ("npc_emberling", "tbl_ashfall", "usr_mira", "Emberling", 0, 3, 3, 18, 18,
     {"str": 1, "dex": 5, "con": 2, "int": -2, "wis": 0, "cha": -1}),
    ("npc_cinderwyrm", "tbl_ashfall", "usr_mira", "Cinderwyrm", 0, 2, 2, 96, 96,
     {"str": 8, "dex": 2, "con": 7, "int": 1, "wis": 4, "cha": 3}),
    ("chr_tull", "tbl_saltmarsh", "usr_jonah", "Tull Mereweather", 1, 2, 2, 28, 28,
     {"str": 2, "dex": 2, "con": 3, "int": 1, "wis": 3, "cha": 2}),
]

ENCOUNTERS = [
    ("enc_ashfall_001", "tbl_ashfall", "The Cinder Gate", "running"),
    ("enc_saltmarsh_01", "tbl_saltmarsh", "Low Tide", "running"),
]


def build(path: str = ":memory:") -> sqlite3.Connection:
    """Create, migrate, and populate a database."""
    connection = db.connect(path)
    db.migrate(connection)

    connection.executemany(
        "INSERT OR REPLACE INTO tables (table_id, name, dm_user_id) VALUES (?, ?, ?)",
        TABLES,
    )
    connection.executemany(
        "INSERT OR REPLACE INTO memberships (table_id, user_id, role) VALUES (?, ?, ?)",
        MEMBERSHIPS,
    )
    connection.executemany(
        "INSERT OR REPLACE INTO api_keys (key_hash, user_id, label) VALUES (?, ?, ?)",
        [(hash_key(raw), user_id, "session") for raw, user_id in KEYS],
    )
    connection.executemany(
        "INSERT OR REPLACE INTO characters "
        "(character_id, table_id, owner_user_id, name, is_pc, dex_mod, init_mod, "
        " hp, max_hp, saves) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        [
            (cid, table, owner, name, is_pc, dex, init, hp, max_hp, json.dumps(saves))
            for cid, table, owner, name, is_pc, dex, init, hp, max_hp, saves
            in CHARACTERS
        ],
    )
    for encounter_id, table_id, name, status in ENCOUNTERS:
        connection.execute(
            "INSERT OR REPLACE INTO encounters "
            "(encounter_id, table_id, name, status) VALUES (?, ?, ?, ?)",
            (encounter_id, table_id, name, status),
        )
        queries.append_log(
            connection, encounter_id, 1, 1, "encounter_opened", "system",
            {"name": name},
        )
    connection.commit()
    return connection
