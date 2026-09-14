---
id: TAR-467
title: Replay an encounter from its log
size: medium
estimate: 60-90 lines
scope:
  - tarrasque/domain/**
  - tarrasque/api/encounters.py
  - tarrasque/http.py
  - tests/**
touches: [dice.seeded, roll.provenance, log.append-only]
lab: "the payoff ticket — it only works at all if the seeding rule held"
---

# TAR-467 — Replay an encounter from its log

Two sessions ago the Cinderwyrm's breath dropped three characters and one
player has been unhappy about it since. The log has every entry. Nobody can
prove the rolls were real.

## What to build

    GET /v2/encounters/:encounter_id/replay

Walk the log from sequence 1. For every entry carrying a roll, re-open the
stream it names, draw at the position it names, and compare the result
against the recorded total.

Return a verdict: how many rolls were checked, how many reproduced, and a
list of any that did not — with the entry sequence, the recorded total, and
the total the replay produced.

## Acceptance criteria

1. An encounter whose rolls all came through a seeded stream replays with zero
   mismatches.
2. An entry whose payload carries a total but no seed is reported as
   **unverifiable**, counted separately from a mismatch.
3. The replay writes nothing.
4. `make verify` is green.

## Why this one is here

This endpoint is the reason the seeding rule exists. Run it against an
encounter built by an agent that ignored the rule and the answer is
"unverifiable" for every roll it made. That is the most direct demonstration
in the repository of what a charter rule is actually buying.
