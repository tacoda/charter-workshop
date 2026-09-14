---
scope: "tests/**/*.py"
owner: platform-lead
last_reviewed: 2026-09-01
---

# Tests

## Iron laws

**IRON.** Do not edit an existing assertion to make your change pass. Adding
a test is always fine. Changing what an existing test asserts is a claim that
the old behaviour was wrong, and that claim belongs in the ticket, not in the
diff.

*Why this is iron:* 2026-05-30 · near-miss · an agent asked to fix rounding in
the legacy tables also rewrote the characterization test that pinned the old
behaviour. Eleven tests passed, the gate was clean, and the one artifact that
contradicted the change was the one artifact nothing inspected.

*Enforced by:* `bin/score`, check `C7` — it reads the diff for removed
assertion lines. Note that this check lives in the scorer rather than in the
gate, because the gate runs on source and this one needs the diff.

*Traces to:* the enforcing artifact must sit outside the blast radius of what
it enforces against.

## Golden rules

**GOLDEN.** `tests/test_legacy_characterization.py` pins frozen behaviour.
It changes only in a commit whose ticket says the legacy module is changing.
Exception: none that does not require the ticket.

**GOLDEN.** A test for a roll uses `ScriptedRng`, not `SeededRng`, so the
assertion names the faces it expects. Exception: a test *about* reproducibility
uses `SeededRng` twice and compares the two sequences.

*Traces to:* a test that passes for an unstated reason is not a test.

## Preferences

**PREF.** One behaviour per test, named after the behaviour rather than the
function. `test_advantage_and_disadvantage_cancel_rather_than_stacking`, not
`test_saving_throw_advantage_2`.

**PREF.** Group tests by behaviour in a `Test*` class when a module has more
than about eight of them.
