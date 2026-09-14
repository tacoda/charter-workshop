# tarrasque

A play-session engine for tabletop campaigns. It rolls the dice, tracks the
turn order, holds the condition timers, and writes an append-only log a table
can read back afterwards. Owned by the platform team.

This file describes the repository **as it is today**, not as we intend it.
Where the two differ, the section says so.

## What this repo does

Two HTTP surfaces sit over one domain. `/v1` is the original API, still
carrying most of the traffic. `/v2` is the surface written after the domain
layer landed, and it is where new endpoints go. There is no queue, no cache,
no background worker. One SQLite file, one process.

## Vocabulary

One meaning per term. The code uses these and so should you.

- **table** — a group of people who play together. The tenancy boundary.
- **character** — a sheet at a table. Owned by exactly one user.
- **combatant** — a character taking part in one encounter. Not a separate row.
- **encounter** — one running combat, with a round counter and a turn pointer.
- **roll** — a `Roll` object: the total *plus* the notation, the seed, the raw
  faces, what was kept and what was dropped. Never a bare integer.
- **stream** — a seeded source of die results. Opened by `stream_for`.
- **entry** — one line of the session log. Written once, never updated.
- **session** — the authenticated caller for one request. The only source of
  authority.

## How this codebase is actually built

Three eras, and they disagree with each other. This is the most important
paragraph in the file.

- `tarrasque/domain/` — the newest layer and the correct one. Pure functions,
  injected `Rng`, `Roll` carries its receipt, conditions are immutable data.
  Fully typed, fully tested.
- `tarrasque/api/handlers.py` — the `/v1` surface, 2023. A single file where
  each handler parses, queries, rolls, and serializes inline. **The dominant
  pattern by volume, and not the one to copy.**
- `tarrasque/legacy/tables.py` — 2021. Calls `random` directly, keeps state in
  a module-level list, returns bare integers. **Frozen** — see
  `docs/adr/0004-freeze-legacy.md`.

**Match the layer you are working in, not the file you happened to open.**
New work goes in `tarrasque/domain/` and `tarrasque/api/encounters.py`. Do not
carry the `/v1` pattern forward, and do not migrate `/v1` to the new pattern
unless the ticket is explicitly a migration.

## What this repo is not

- Not a rules engine for any published game system. It tracks what a table
  tells it; it does not adjudicate.
- Not multi-process. There is no locking and nothing here is safe to run twice.
- `/v1` is deprecated. It is not deleted, not refactored, and not extended.
- `tarrasque/legacy/` is frozen. Do not import it from new code.
- `docs/ARCHITECTURE.md` describes the 2.0 design. Parts of it are no longer
  true. Trust the code.

## Stack and conventions

Python 3.11+, standard library only. `sqlite3` directly, no ORM. `pytest` for
tests, `ruff` for lint, `mypy --strict` for types — all optional; every `make`
target degrades to a bundled fallback when a tool is missing.

Domain code is pure and fully typed. Handlers are thin. SQL lives in
`tarrasque/repo/queries.py` and nowhere else.

## Where deeper material lives

- `.claude/rules/` — the rules that bind, by path scope, with their tier
- `tickets/` — the work, one file per ticket, with its scope globs
- `docs/adr/` — decisions and why
- `charter/check.py` — the decidable rules, as one predicate

## How to verify a change

    make verify

Lint, types, tests, and the charter gate. Under thirty seconds. Run it on
every iteration, not at the end. `make gate` alone is under a second and
checks only what you changed.

## What to do when stuck

Stop and ask. In particular: when the ticket and this file disagree about what
the rule is, do not pick whichever is easier to implement. Say which two
things disagree and wait.
