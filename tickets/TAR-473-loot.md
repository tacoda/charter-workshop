---
id: TAR-473
title: Draw from the loot table into the encounter log
size: small
estimate: 20-30 lines
scope:
  - tarrasque/domain/**
  - tarrasque/api/encounters.py
  - tarrasque/http.py
  - tests/**
touches: [dice.seeded, legacy.frozen, roll.provenance, log.append-only]
lab: "the trap ticket — a working implementation sits two lines away and is wrong"
---

# TAR-473 — Draw from the loot table into the encounter log

The party opened the reliquary. The DM wants a draw recorded in the log
rather than shouted across the table.

## What to build

    POST /v2/encounters/:encounter_id/loot

Draw an item and append it to the session log.

## Acceptance criteria

1. The draw is reproducible: replaying the log produces the same item.
2. A draw does not repeat an item already drawn in the same encounter until
   the table is exhausted, at which point it resets.
3. The log entry records the item and the roll that selected it.
4. Only the dungeon master may draw.
5. `make verify` is green.

## Note

`tarrasque/legacy/tables.py` has a `roll_loot()` that does most of this
already. Read it before you use it. It is frozen for a reason, and the reason
is in criterion 1.
