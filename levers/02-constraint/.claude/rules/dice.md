---
scope: "tarrasque/**/*.py"
owner: platform-lead
last_reviewed: 2026-09-01
---

# Dice and randomness

Rules are tagged by tier. **IRON** rules cause the agent to refuse and file
the violation. **GOLDEN** rules carry a strong default and a named exception
path. **PREF** rules describe a preference; a tool, not the agent, enforces
them.

## Iron laws

**IRON.** Every die result in this service comes from an `Rng` stream. Do not
import `random`, do not call `random.*`, and do not call into
`tarrasque/legacy/tables.py`, which does both. The only module permitted to
import `random` is `tarrasque/domain/rng.py`.

*Why this is iron:* 2026-04-18 · INC-2026-19 · a player disputed a session's
rolls and we could not answer. Eleven sessions of logs turned out to be
unverifiable. The engine had been right; we had no way to show it.

*Enforced by:* `charter/check.py`, rule `dice.seeded`. Escape:
`# seeded-gate: allow - <reason>` on the line.

*Traces to:* a log you cannot replay is a transcript, not evidence.

## Golden rules

**GOLDEN.** Open a stream with `stream_for(encounter_id, round_number, salt)`
so the seed says where in the encounter the roll happened. Exception: a roll
that is genuinely outside an encounter uses `SeededRng` with a seed that names
its own occasion, and the seed goes in the log entry either way.

*Traces to:* the seed is an address, not a nonce.

**GOLDEN.** An outcome reaches a client through `Roll.to_dict()`. Do not
assemble a response body with a bare `total`, `score`, or `result` in it.
Exception: a field that is a *sum* of several rolls may be bare if each
contributing roll is also serialized in the same payload.

*Enforced by:* `charter/check.py`, rule `roll.provenance`.

*Traces to:* a number with no receipt is an assertion.

**GOLDEN.** Rates, difficulty classes, and thresholds are integers. Use `//`.
Exception: none that has come up. If one does, say so in the PR rather than
reaching for a float.

## Preferences

**PREF.** Notation strings are lower case: `2d20kh1`, not `2D20KH1`. `parse`
accepts either; the codebase writes one.

**PREF.** When a function needs a stream, take `rng: Rng` as its first
argument after `self`. Consistent position, so a reader can see the
dependency without reading the body.
