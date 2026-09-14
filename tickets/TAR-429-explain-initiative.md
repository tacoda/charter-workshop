---
id: TAR-429
title: Explain the initiative order
size: small
estimate: 20-35 lines
scope:
  - tarrasque/api/encounters.py
  - tarrasque/domain/initiative.py
  - tarrasque/http.py
  - tests/**
touches: [roll.provenance, authority.session-derived]
lab: "the control ticket — no dice are rolled, so dice.seeded cannot fire"
---

# TAR-429 — Explain the initiative order

"Why does the Emberling go before Sable? They both rolled 18." Right now the
only answer is to open the database.

## What to build

    GET /v2/encounters/:encounter_id/initiative/explain

Return the order, and for each entry the values that placed it: the
initiative roll, the dexterity modifier, the recorded tie-break, and the
combatant id — in the order the comparison actually applies them.

Where two entries were separated by a tie-break rather than by score, say so
explicitly.

## Acceptance criteria

1. Every entry shows the full roll that produced its score, not just the total.
2. An entry separated from its neighbour by a tie-break is marked.
3. Only a member of the encounter's table may call it.
4. Nothing is written. This endpoint has no side effects and appends no log
   entries.
5. `make verify` is green.

## Why this one is here

No die is rolled, so the seeding rule cannot fire. If the charter moves this
ticket's score at all, it moved it through the other rules. That makes this
the useful control in the set.
