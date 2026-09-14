# tarrasque — architecture

*Last substantially revised for the 2.0 release.*

`tarrasque` runs a tabletop play session: it rolls the dice, tracks the turn
order, holds the condition timers, and writes everything to a log the table
can read back afterwards.

## Layers

The service is built in three layers with dependencies pointing inward.

    api  →  domain  →  repo

**`tarrasque/api/`** parses requests and renders responses. It contains no
arithmetic and no SQL. Handlers resolve a session, call a domain function,
and serialize what comes back.

**`tarrasque/domain/`** holds the rules of play. Every function here is pure:
it takes its dependencies as arguments and returns values. Nothing in the
domain layer reaches for I/O, the clock, or randomness.

**`tarrasque/repo/`** is the repository layer. Each aggregate — characters,
encounters, the log — has a repository object that owns its queries, so no
SQL string appears anywhere else in the service.

## Randomness

All randomness in this service flows through `tarrasque.domain.rng`. Every
roll is drawn from a stream opened with an explicit seed, and the seed is
recorded alongside the result, which is what lets any session be replayed
from its log. There are no direct calls to the standard library's `random`
anywhere in the codebase.

## The session log

The log is append-only. An entry is written once and never modified. When a
dungeon master needs to correct a mistake, the correction is appended as a new
entry that refers to the old one; the original stays exactly where it was.

## Authority

A request's authority comes from its session. The session is resolved from the
bearer token, and it carries the user, their seat at the table, and the
characters they control. No endpoint accepts a character or table identity
from a request body.

## Versioning

The `/v1` surface is deprecated and scheduled for removal. Every endpoint has
a `/v2` equivalent; new work goes to `/v2`.
