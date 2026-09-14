---
scope: "tarrasque/**/*.py"
owner: platform-lead
last_reviewed: 2026-09-01
---

# The session log

## Iron laws

**IRON.** The session log is append-only. Never `UPDATE session_log`, never
`DELETE FROM session_log`, and never call `queries.update_log_payload` or
`queries.delete_log_from`. A correction is a new entry that retracts an old
one — `log.correct()` writes it.

*Why this is iron:* 2025-11-02 · INC-2025-44 · a DM used the `/v1/fix`
endpoint to correct a damage total, then the party disputed the outcome and
the log showed only the corrected number. There was no way to tell what had
been changed or by whom.

*Enforced by:* `tools/charter_check.py`, rule `log.append-only`. Escape:
`# log-gate: allow - <reason>`.

*Traces to:* history that can be edited is not history.

## Golden rules

**GOLDEN.** Every state change appends an entry in the same operation that
makes it. Exception: a read-only endpoint appends nothing at all, and that is
the point of a read-only endpoint — say so in the ticket.

**GOLDEN.** Sequence numbers are contiguous per encounter. Take the next one
from `queries.next_sequence`, and write every entry a single request produces
before returning. Exception: none.

*Traces to:* a gap in the sequence is indistinguishable from a deletion.

## Note on the two functions that break this rule

`queries.update_log_payload` and `queries.delete_log_from` exist, work, and
are called by `/v1`. They are the reason this rule is written down rather than
assumed. They are not an invitation.
