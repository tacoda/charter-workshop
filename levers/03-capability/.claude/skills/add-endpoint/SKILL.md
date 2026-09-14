---
name: add-endpoint
description: Add an endpoint to the v2 surface of the tarrasque service. Use when a ticket asks for a new route, a new HTTP verb on an existing route, or a new action a table can take during an encounter. Covers the session, domain, serialization and logging steps this repository requires, in order.
allowed-tools: Read, Edit, Write, Grep, Glob, Bash(make verify:*), Bash(make gate:*), Bash(python3 .claude/skills/add-endpoint/scripts/check_route.py:*)
---

A rule bounds one move. This is a sequence, and the sequence is why endpoints
in this repository keep arriving half-finished: the handler lands, the log
entry does not.

Work in this order. Do not skip a step because the ticket did not mention it.

1. **Read the neighbour.** Open `tarrasque/api/encounters.py` and read the
   closest existing handler end to end. That file is the pattern. Do **not**
   open `tarrasque/api/handlers.py` for an example; it is the `/v1` surface
   and it is the wrong era.

2. **Domain first.** If the endpoint needs a decision made — a comparison, a
   state transition, an allocation — that logic goes in `tarrasque/domain/`
   as a pure function, with its own tests, before the handler exists. The
   handler calls it. The handler does not contain it.

3. **Session, then control.** The handler takes `(connection, session, *path_params)`.
   Call `require_control(connection, session, character_id)` before acting for
   a combatant, or check `session.is_dungeon_master()` for a table-wide
   action. Never read an identity out of the request body.

4. **Roll through a stream.** Any die comes from
   `stream_for(encounter_id, round_number, salt)`. Pick a salt that names the
   occasion, so two different rolls in the same round do not collide.

5. **Serialize the receipt.** Outcomes reach the client through
   `Roll.to_dict()`. A bare total in a response body is a finding.

6. **Append to the log.** Every state change writes an entry, in the same
   request, through `write_entries`. Take sequence numbers from the encounter
   object, which already knows the next one.

7. **Register the route.** Add it to `V2_ROUTES` in `tarrasque/http.py`.
   Then run:

       python3 .claude/skills/add-endpoint/scripts/check_route.py

   It confirms the route resolves, the handler's signature matches what the
   dispatcher will pass it, and the path parameters line up. Do not
   reimplement this check by reading the file yourself.

8. **Test the refusals, not only the success.** At minimum: the unauthenticated
   call, the wrong-table call, the wrong-character call, and the happy path.

9. **`make verify`.** Then read what it says.

## Halt conditions

Stop and ask rather than choosing, when:

- the ticket does not say who may call the endpoint, and more than one answer
  is defensible
- implementing it needs a change to `tarrasque/legacy/`
- an existing test would have to change for your work to pass
