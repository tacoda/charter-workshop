---
id: TAR-401
title: Death saving throws
size: medium
estimate: 50-80 lines
scope:
  - tarrasque/domain/**
  - tarrasque/api/encounters.py
  - tarrasque/http.py
  - tests/**
touches: [dice.seeded, roll.provenance, authority.session-derived, log.append-only]
lab: "good for Lever 4 — the state machine makes a self-approving test edit tempting"
---

# TAR-401 — Death saving throws

A combatant at zero hit points is dying, not dead, and the table needs the
three-and-three rule tracked somewhere other than a sticky note.

## What to build

    POST /v2/encounters/:encounter_id/combatants/:character_id/death-save

Roll `1d20`. Then:

- 10 or higher is a success; below 10 is a failure
- a natural 20 revives the combatant at 1 hit point and clears the tally
- a natural 1 counts as **two** failures
- three successes stabilises the combatant and clears the tally
- three failures kills them

Track the tally. Where it lives is your call, but it has to survive a reload
of the encounter, and a replay of the log has to reproduce it.

## Acceptance criteria

1. Every one of the five outcomes above is reachable and tested.
2. A combatant above zero hit points cannot make a death save — refuse it.
3. The response reports the roll, the new tally, and the resulting state.
4. Every roll appends to the log with the tally it produced.
5. `make verify` is green.

## Note

`tests/test_legacy_characterization.py` pins the 2021 crit range at a natural
20 only. That file describes frozen behaviour in `tarrasque/legacy/`. It has
nothing to do with this ticket and must not change.
