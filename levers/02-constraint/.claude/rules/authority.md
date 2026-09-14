---
scope: "tarrasque/api/**/*.py"
owner: platform-lead
last_reviewed: 2026-09-01
---

# Authority

## Iron laws

**IRON.** Authority comes from the session. Never read `character_id`,
`user_id`, `table_id`, `combatant_id`, `acting_as`, or any other identity out
of a request body or query string and act on it. Path parameters name *what*
is being addressed; the session decides *whether* this caller may address it.

*Why this is iron:* 2026-02-11 · INC-2026-08 · `/v1/roll` takes
`character_id` from the body. A player rolled a death save for another
player's character, on purpose, to end an argument. Nothing refused it and
nothing in the log distinguished it from a legitimate roll.

*Enforced by:* `tools/charter_check.py`, rule `authority.session-derived` — which
catches the *shape* of the mistake, not the mistake. See below.

## Golden rules

**GOLDEN.** A v2 handler calls `require_control(connection, session, character_id)`
before acting for a combatant. Exception: an endpoint that acts for the whole
table at once checks `session.is_dungeon_master()` instead, and says which it
chose in a comment.

*Traces to:* the check is cheap; finding out you skipped it is not.

## The rule no gate holds

**Whether the control check is the *right* check is not decidable.**

The predicate can see that you read an identity from the body. It cannot see
that a dungeon master should be able to roll for an unconscious player's
character, that a charmed character is controlled by whoever charmed them for
the duration, or that a player rolling their *own* death save is fine while a
player rolling someone else's is the incident above.

Those are judgements. When a ticket touches authority and the right answer is
not obvious from this file, say so in the PR and name the two readings. Do not
pick the one that is easier to implement.

*Altitude:* `none`. This is the most valuable rule on this page and nothing
mechanical enforces it.
