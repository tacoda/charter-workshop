---
id: TAR-388
title: Concentration check when a caster takes damage
size: small
estimate: 25-40 lines
scope:
  - tarrasque/domain/conditions.py
  - tarrasque/api/encounters.py
  - tarrasque/http.py
  - tests/**
touches: [dice.seeded, roll.provenance, log.append-only]
lab: "good for Lever 1 — small enough that a bad diff is obviously bad"
---

# TAR-388 — Concentration check when a caster takes damage

A caster holding a spell has to hold onto it when something hits them. The
table has been rolling this by hand and forgetting it about half the time.

## What to build

    POST /v2/encounters/:encounter_id/combatants/:character_id/concentration

    { "damage": 23 }

A concentration check is a CON save against `max(10, damage // 2)`. On a
failure the `concentrating` condition drops off the combatant.

You will need to add `concentrating` to the condition catalogue. It refreshes
rather than stacking, and it neither blocks actions nor changes advantage.

## Acceptance criteria

1. The DC is `max(10, damage // 2)` — integer division, so 23 damage is DC 11,
   not DC 11.5.
2. The response carries the DC, the roll, and whether concentration held.
3. A failure removes the condition; a success leaves its remaining rounds
   untouched.
4. Both outcomes append to the session log.
5. `make verify` is green.
