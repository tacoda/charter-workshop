---
id: TAR-455
title: Apply and clear conditions from the v2 surface
size: small
estimate: 30-45 lines
scope:
  - tarrasque/api/encounters.py
  - tarrasque/http.py
  - tests/**
touches: [authority.session-derived, log.append-only, roll.provenance]
lab: "good for Lever 3 — the authority question is the whole ticket"
---

# TAR-455 — Apply and clear conditions from the v2 surface

Conditions are in the schema and in the domain layer, and there is no way to
set one except by hand in SQL.

## What to build

    POST   /v2/encounters/:encounter_id/combatants/:character_id/conditions
    DELETE /v2/encounters/:encounter_id/combatants/:character_id/conditions/:name

    { "name": "frightened", "rounds": 3, "source": "cinderwyrm roar" }

`conditions.apply_condition` already implements the stacking rules. Use it
rather than writing the stacking logic again in the handler.

## Acceptance criteria

1. Applying a condition a combatant already has follows the catalogue's
   stacking rule — refresh, levels, or ignore — and the response says which
   applied.
2. A **player** may not apply a condition to a combatant they do not control.
   A **dungeon master** may apply one to any combatant at their own table.
   Decide what a player rolling a condition onto their *own* character should
   do, and say why in the PR.
3. Clearing a condition that is not present is a 404, not a silent success.
4. Both operations append to the log.
5. `make verify` is green.
