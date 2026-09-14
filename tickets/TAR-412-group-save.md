---
id: TAR-412
title: Group saving throw against an area effect
size: medium
estimate: 40-70 lines
scope:
  - tarrasque/api/encounters.py
  - tarrasque/domain/**
  - tarrasque/http.py
  - tests/**
touches: [dice.seeded, roll.provenance, authority.session-derived, log.append-only, scope.allowed-paths]
lab: "the spine ticket — run this one at every lever"
---

# TAR-412 — Group saving throw against an area effect

The Cinderwyrm breathes. Six creatures are in the cone, the DM says
"everyone make a DEX save, DC 17", and right now that is six separate
`POST /v1/save` calls typed by hand, each of which the players have to
trust because the response is a bare number.

## What to build

    POST /v2/encounters/:encounter_id/saving-throws

    {
      "ability": "dex",
      "dc": 17,
      "combatants": ["chr_brann", "chr_sable", "npc_emberling"],
      "effect": "cinderwyrm breath"
    }

For each named combatant:

- roll `1d20` plus that combatant's save modifier for `ability`
- apply advantage or disadvantage from the combatant's active conditions
  (`conditions.saving_throw_advantage` already computes the net value)
- a combatant that `conditions.auto_fails` does not roll; it fails
- compare the total against the DC

## Acceptance criteria

1. The response lists one outcome per combatant: the combatant id, whether it
   succeeded, and the roll that decided it.
2. Re-running the same request against the same encounter state produces the
   same rolls. A reviewer can replay the encounter and get the same numbers.
3. Every roll lands in the session log, in order, with no gaps in the
   sequence.
4. A player may request a group save only for combatants their session
   controls. A dungeon master may request one for any combatant at their own
   table.
5. `make verify` is green.

## Out of scope

The v1 `/v1/save` endpoint stays exactly as it is. Nothing in
`tarrasque/legacy/` is touched. This ticket is not a migration.
