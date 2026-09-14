# ADR 0004 — Freeze `tarrasque/legacy/tables.py`

**Status:** accepted · 2024-02-19

## Context

The 2021 random tables predate the domain layer. They draw from the standard
library's global `random` stream, keep the per-session draw memory in a module
level list, and return bare integers.

Four campaigns' worth of published session transcripts were generated against
exactly this code, including its crit range and its draw-without-repeat
behaviour. Several of those transcripts are cited in the community wiki.

## Decision

The module is frozen. It is excluded from `mypy` and from the `ruff` rule set,
and `charter/check.py` does not govern it.

New code does not import it. New behaviour goes in `tarrasque/domain/`.

Rewriting it is a migration ticket with its own review, not something that
rides along with a feature.

## Consequences

The service has two ways of rolling dice and only one of them is replayable.
That is a known cost and it is the reason `/v1` is deprecated.

Anyone reading `tarrasque/legacy/tables.py` for an example of how this service
works will learn the wrong thing. The exclusion is written down here and in
`pyproject.toml` so that at least the boundary is discoverable.
