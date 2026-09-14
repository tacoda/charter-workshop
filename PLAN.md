# Wrap It in a Charter — 90-minute workshop plan

**Venue:** AIDevCon (AI Native DevCon) · Context Engineering track
**Format:** Workshop, hands-on, 90 minutes. 3-hour version available.
**Level:** Intermediate → Advanced. Engineers who already run a coding agent daily
and already have a `CLAUDE.md` they do not fully trust.
**Cap:** ~35 per facilitator. Laptops out.

---

## The thesis

**The charter alone moves the band.** Same agent, same model, same machine, same
ticket — and nothing touched but files in the repository. No custom harness, no
orchestrator, no framework, no SDK. By the end of ninety minutes the room has a
five-column matrix showing exactly how far that gets you, on a codebase none of
them wrote.

This is the claim the field keeps asserting and almost nobody measures. We
measure it, in the room, five times.

### Where the line is drawn

Everything that lives in `CLAUDE.md`, `.claude/`, and `.mcp.json` is in scope.
That is the agent's configuration surface, and it is exactly what the charter
owns — including the mechanical parts. A hook is charter content: mechanical,
and the only enforcement the agent could delete. A tool grant is charter
content. A sub-agent's refusal scope is charter content.

The moment enforcement has to move somewhere reconfiguring the agent cannot
reach — a tool that refuses internally, a stage gate, CI, a DAG node — we name
it, write it on the promotion report, and **stop**. That is the next rung up and
it is a different workshop. We give its shape once, in one table, so nobody
leaves thinking the charter is the top of the ladder.

### The counter-thesis, stated honestly in the first five minutes

A charter authored in advance is a list of guesses. That is true, and it is the
strongest objection to the entire exercise. The resolution is that wrapping an
*existing* application is not authoring in advance: **the baseline run is the
incident.** The agent manufactures the evidence on demand, which is why a room
can honestly accrete a charter in ninety minutes when a team normally takes a
year of bad days to do it.

---

## The instrument

One ticket (`TICKET.md`), run five times, against five charter states. After each
run: `make capture RUN=<slug>` freezes the diff and scores it. `make compare`
prints the matrix. That matrix is the deliverable.

Nine checks. Eight are deterministic. One is not, on purpose, and the scorer
prints `n/a — inferential` in that column for the first three rounds. **The hole
in the scorecard is the pedagogy.** It is what the sub-agent in Lever 4 fills,
and it is why the charter cannot be all gates.

| # | check | kind |
|---|---|---|
| C1 | `scope.allowed-paths` — the diff stayed inside the ticket | deterministic |
| C2 | `money.integer-cents` — no float on a money path | deterministic |
| C3 | `rounding.half-even` — no half-up rounding in new code | deterministic |
| C4 | `currency.paired` — no serialized amount without its currency | deterministic |
| C5 | `tenancy.filtered` — no query without a tenant predicate | deterministic |
| C6 | `tests.not-self-approving` — the agent did not edit an assertion that pinned the old behaviour | deterministic |
| C7 | `verify.green` — `make verify` exits 0 | deterministic |
| C8 | `lint.clean` / `types.clean` — the stock toolchain agrees | deterministic |
| C9 | `tenancy.session-derived` — the tenant came from the session, never a caller argument | **inferential** |

Plus two metrics that are not pass/fail and matter anyway: `files_changed` and
`lines_changed`. The baseline's four-hundred-line diff is itself a finding.

---

## The application

`sluice` — usage metering, rating, and invoicing for a multi-tenant API platform.
Python 3.11+. It is a **properly built project**, not a toy, because half the
levers only work if the agent has something real to run:

- `pyproject.toml` — packaged, with `ruff`, `mypy --strict`, and `pytest` configured
- `Makefile` — 14 named targets. The unit of intent, and what the permission
  allowlist points at instead of command strings
- `tests/` — a real suite, sub-second, with the domain layer at full coverage
- `make verify` — lint, types, tests, and the charter gate in under thirty seconds
- **A zero-install floor**: if `ruff`/`mypy`/`pytest` are missing, every target
  degrades to a bundled stdlib fallback. `make gate` is pure standard library and
  always works. Nothing in the critical path depends on a download succeeding on
  conference wifi.

`sluice` is deliberately **three eras deep**, because that is what a real retrofit
meets:

- `sluice/legacy/billing.py` — 2021. Floats, half-up rounding, no currency. Loud,
  large, excluded from the type gate, and the thing the agent will imitate.
- `sluice/api/handlers.py` — 2023. A god file: parse, query, compute, and
  serialize inline in every handler. The dominant pattern by volume.
- `sluice/domain/` — 2026. Pure functions, integer cents, `Money` carries its
  currency, banker's rounding, explicit remainders. Correct, typed, tested, and
  outnumbered.

### Four planted traps, one per lever

1. **A stale `docs/ARCHITECTURE.md`** claiming the service uses `Decimal` end to
   end and a repository pattern it does not have — plus a lying comment in the
   god file pointing at it. A false signal that outranks any rule you write.
   Deleted, not out-argued.
2. **Rounding** — the spec says half-to-even; *every example in the seed is
   half-up*. An **opposed** imitation surface. The rule that proves prose can win.
3. **Currency** — the seed contains no serialization of an amount at all. An
   **absent** imitation surface. The rule that proves prose can reach where there
   is nothing to copy.
4. **Tenancy** — `sluice/repo/queries.py` takes `tenant_id` as a caller-supplied
   first argument in seventeen of twenty functions, and three forget the
   predicate entirely. The agent will write the twenty-first. Its decidable
   shadow is checkable; the rule itself is not.

Traps 2 and 3 come straight from the confound that killed the first version of
the *Layers and Promotion* experiment: **a rule the code already demonstrates
measures nothing.** Both replacement rules are designed so the charter is the
only thing that could have produced the behaviour. Trap 1 is the retrofit
audit. Trap 4 is the inferential column.

### The ticket

`SLU-412` — apply a promotional credit to an open invoice, prorated across its
open line items. One ticket that lands on all four traps: it is money, it rounds,
it serializes, it reads tenant-scoped rows, and it is small enough that a
four-hundred-line diff is self-evidently wrong.

---

## The five levers

Each is charter-layer. Each is a directory you can apply and revert.

| # | lever | what lands | the beat |
|---|---|---|---|
| 0 | — | nothing | the baseline is the incident |
| 1 | **Instruction** | delete the lies, then `CLAUDE.md` | describe the present tense |
| 2 | **Constraint** | `.claude/rules/*.md`, path-scoped, IRON/GOLDEN/PREF | and fix one imitation surface |
| 3 | **Capability** | `.claude/commands/`, `.claude/skills/`, `.claude/agents/`, `.claude/settings.json`, `.mcp.json` | the other half of the charter |
| 4 | **Check** | `.claude/hooks/` (deterministic) + a reviewer sub-agent (inferential) | two verdict sources, one predicate |

**Lever 3 is the half of the charter nobody designs.** Half a charter says what
the agent may not do; the other half says what it can do at all. Four rungs —
command, skill, sub-agent, MCP server — plus plugins as packaging, and the four
attributes every one of them carries: **trigger, rung, grant, return**. Run the
family test backwards to find them: remove it, and if the agent can do *less*,
it was a capability.

In `sluice` that lands as:
- a **command** (`/slu-credit`) — a rehearsed prompt with the ticket and the diff
  stapled to it, `disable-model-invocation: true`, so it costs nothing standing
- a **skill** (`add-endpoint`) — the sequence a rule cannot hold, with the
  deterministic `charter/check.py` bundled beside it as a script, not a server
- a **sub-agent** (`charter-auditor`) — a declared grant that cannot write, and a
  stated return shape
- a **grant** (`.claude/settings.json`) — the allowlist points at `make` targets,
  not at command strings, because a target is a unit of intent somebody decided on
- an **MCP declaration** (`.mcp.json`) — written, then *deleted* in the lab, as the
  worked example of `the server that should have been a script`

**Lever 4 mounts one predicate twice.** `charter/check.py` takes
`{files: [{filename, source}]}` and never opens a file — forty lines of `ast`,
no imports from the repo. That shape is why the same implementation runs as a
`PreToolUse` hook, as a `make gate` target, as a bundled skill script, and later
(not today) anywhere above the charter. One implementation, many mounts.

---

## The run of show

| clock | segment | what happens |
|---|---|---|
| 0:00–0:06 | **Frame** | The thesis, the counter-thesis, the line we stop at. `make doctor`. |
| 0:06–0:18 | **Lab 0 — the baseline** | Run the ticket on a bare repo. `make capture RUN=00-baseline`. Read the scorecard aloud. The first measurement is of the repo, not the agent. |
| 0:18–0:31 | **Lever 1 — instruction** | `make audit` finds the stale signals; delete them. Then author two sections of `CLAUDE.md` by hand and apply the rest. Re-run, capture, compare. |
| 0:31–0:44 | **Lever 2 — constraint** | Write one rule with all four parts — rule, altitude, date-and-link, damage. Apply the tiered rule files. Fix one imitation surface. Re-run, capture, compare. |
| 0:44–0:58 | **Lever 3 — capability** | The family test. The four rungs, the four attributes. Place three capabilities, delete a fourth. Re-run, capture, compare. |
| 0:58–1:10 | **Lever 4 — check** | One predicate, mounted as a hook and as a target. Then the sub-agent for the rule no predicate can hold. Re-run. Column C9 finally has a value. |
| 1:10–1:20 | **The ceiling** | `make promote` — which rules now pass consequential / recurrent / decidable. Then the two rungs above, in one table, and we stop at the line. |
| 1:20–1:30 | **The budget, and Monday** | Forty lines, adding requires removing, deletion day. Fill `HITLIST.md`. Q&A. |

Every lab is the same four beats, which is what makes it a workshop rather than a
demo:

> **author one artifact by hand → `make lever N` lands the rest → re-run the
> ticket → `make compare`**

Nobody types 1,500 words of `CLAUDE.md` in a conference room. They write the two
parts that carry the lesson and read the rest.

---

## What the attendee leaves with

1. A five-column matrix, from their own machine, showing which levers moved which
   checks on a repo they did not write.
2. Working artifacts they keep: an honest `CLAUDE.md`, a tiered rule file, four
   placed capabilities with declared grants, one predicate mounted twice, a
   reviewer sub-agent with a stated return.
3. `HITLIST.md`, filled in during the last segment — their own repo's stale
   signals, their own opposed imitation surface, their own undecidable rule.
4. The promotion report, with the line drawn on it.

---

## Failure modes and fallbacks

- **No agent / broken install** → `runs/reference/` ships five captured runs. Every
  `make compare` works without invoking a model once.
- **Conference wifi** → standard-library Python floor. Nothing downloads. The only
  network call in the room is the agent's own.
- **A run comes out clean on the baseline** → say so, and put it in the matrix. A
  null result is the honest outcome and the instrument was built to report it.
- **Too slow** → Levers 3 and 4 merge; the promotion report runs from
  `runs/reference/` instead of the room's own runs.
- **The room's results disagree with mine** → that is the best outcome available and
  the reason the scorer is in the repo. n is one per attendee; the room is the
  sample, and I will say so from the front.
