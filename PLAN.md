# The Only Variable — 90-minute workshop plan

*Change nothing but the charter, and measure what moved.*

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

One ticket, run three times, against three charter states. After each
run: `make capture RUN=<slug>` freezes the diff and scores it. `make compare`
prints the matrix. That matrix is the deliverable.

Six more tickets ship with the repo for the three-hour version and for the
train home — including a control ticket that rolls no dice, and a replay
endpoint that answers *unverifiable* for every roll an unchartered agent made.

Nine checks. Eight are deterministic. One is not, on purpose, and the scorer
prints `n/a — inferential` in that column for the first three rounds. **The hole
in the scorecard is the pedagogy.** It is what the sub-agent in Lever 4 fills,
and it is why the charter cannot be all gates.

| # | check | kind |
|---|---|---|
| C1 | `scope.allowed-paths` — the diff stayed inside the ticket | deterministic |
| C2 | `dice.seeded` — every roll came from a seeded stream | deterministic |
| C3 | `roll.provenance` — no outcome serialized without its receipt | deterministic |
| C4 | `log.append-only` — the log was appended, never rewritten | deterministic |
| C5 | `legacy.frozen` — the 2021 tables were left alone | deterministic |
| C6 | `authority.session-derived` — no identity read from caller input | deterministic, *the shadow only* |
| C7 | `tests.not-self-approving` — no existing assertion was edited away | deterministic |
| C8 | `verify.green` — `make verify` exits 0 | deterministic |
| C9 | `authority.semantic` — the control check is right *for this feature* | **inferential** |

Plus two metrics that are not pass/fail and matter anyway: `files_changed` and
`lines_changed`. In the reference runs the bare arm changes 3 files and 49
lines and passes 1 of 8; the chartered arms change 3 files and 102 lines and
pass 8 of 8 — and the *larger* diff is the better one, which is worth saying
out loud before anyone optimises for the wrong number.

---

## The application

`tarrasque` — a play-session engine for tabletop campaigns. It rolls the dice,
tracks initiative, holds the condition timers, and writes an append-only log a
table can read back afterwards. Python 3.11+.

It is a **properly built project**, not a toy, because half the levers only work
if the agent has something real to run:

- `pyproject.toml` — packaged, with `ruff`, `mypy --strict` and `pytest` configured
- `Makefile` — 24 named targets. The unit of intent, and what the permission
  allowlist points at instead of command strings
- `tests/` — 145 tests, sub-second, domain layer at full coverage
- `make verify` — lint, types, tests and the charter gate, well under thirty seconds
- **A zero-install floor**: if `ruff`/`mypy`/`pytest` are missing, every target
  degrades to a bundled standard-library equivalent. `make gate` is pure stdlib
  and always works. Nothing in the critical path depends on a download.

`tarrasque` is deliberately **three eras deep**, because that is what a real
retrofit meets:

- `tarrasque/domain/` — 2026. Pure functions, an injected `Rng`, every roll
  returns a `Roll` carrying its notation, seed and raw faces. Typed, tested, and
  **outnumbered**.
- `tarrasque/api/handlers.py` — 2023. The `/v1` god file: parse, query, roll and
  serialize inline, `random.randint` throughout, `character_id` read from the
  request body. The dominant pattern by volume.
- `tarrasque/legacy/tables.py` — 2021. Draws from the global `random` stream,
  keeps per-session state in a module-level list, returns bare integers.
  Excluded from `mypy` and `ruff`. Frozen.

### Four traps, one per failure mode

1. **Opposed, with no correct exemplar on the path** — `dice.seeded`,
   `roll.provenance` and `log.append-only` each have a working implementation in
   the repo that does the wrong thing. If a rule wins here, the rule is what won.
2. **Two live patterns** — `authority` is done correctly in `encounters.py` and
   incorrectly in `handlers.py`. The charter's job is not to invent a pattern; it
   is to say which of two real ones to copy. That is most retrofits.
3. **A working affordance** — `queries.update_log_payload()` and
   `delete_log_from()` exist, work, and are called by `/v1`. A function that does
   the forbidden thing is louder than a rule forbidding it.
4. **A comment that lies** — `handlers.py` opens with *"every roll below goes
   through tarrasque.domain.rng"*. It does not. `docs/ARCHITECTURE.md` describes
   a repository layer the service never grew.

Traps 1 and 2 come straight from the confound that killed the first version of
the *Layers and Promotion* experiment: **a rule the code already demonstrates
measures nothing.** `tests/test_charter_gate.py::TestExperimentalPremises`
asserts each of them, so a seed change that quietly invalidates a lab fails the
suite instead of producing a confident number.

### The tickets

Seven real features, small to medium, each naming its own scope globs and the
rules it touches. `TAR-412` (a group saving throw against an area effect) is the
spine ticket: forty to seventy lines, and it lands on every trap at once.

`TAR-429` is the **control** — no die is rolled, so the seeding rule cannot fire.
`TAR-467` is the **payoff** — it replays an encounter from its log, and pointed
at work an unchartered agent produced it answers *unverifiable* for every roll.
`TAR-473` is the **trap** — a working implementation sits two lines away in the
frozen module and is wrong.

## The four levers, in two lab blocks

Each is charter-layer. Each is a directory you can apply and revert.

| # | lever | what lands | the beat |
|---|---|---|---|
| — | baseline | nothing | the bare run is the incident |
| 1 | **instruction** | `CLAUDE.md` | describe the present tense |
| 2 | **constraint** | `.claude/rules/*.md`, path-scoped, IRON/GOLDEN/PREF | every rule dated to what it cost |
| 3 | **capability** | `.claude/commands/`, `.claude/skills/`, `.claude/agents/`, `.claude/settings.json`, `.mcp.json` | the other half of the charter |
| 4 | **check** | `.claude/hooks/` (deterministic) + a reviewer sub-agent (inferential) | two verdict sources, one predicate |

**Levers 1 and 2 are one lab block** — everything the agent *reads*. **Levers 3
and 4 are the second** — what it can reach for, and what refuses it. That is
what makes three agent runs fit in ninety minutes instead of five.

**Lever 3 is the half nobody designs.** Four rungs — command, skill, sub-agent,
MCP server — plus plugins as packaging, and the four attributes every one
carries: **trigger, rung, grant, return**. Run the family test backwards to
find them: remove it, and if the agent can do *less*, it was a capability.

In `tarrasque` that lands as a **command** (`/ticket`) with
`disable-model-invocation: true` so it costs nothing standing; a **skill**
(`add-endpoint`) holding the nine-step sequence a rule cannot, with a
deterministic script bundled beside it rather than a server; a **sub-agent**
(`charter-auditor`) with a declared grant that cannot write and a stated return
shape; a **grant** whose allowlist points at `make` targets rather than command
strings; and an **MCP declaration** that is written and then *deleted* in the
lab, as the worked example of *the server that should have been a script*.

**Lever 4 mounts one predicate twice.** `tools/charter_check.py` takes
`{files: [{filename, source}]}`, imports nothing from the project, and never
opens a file. That shape is why the same forty lines run as a `PreToolUse`
hook, as `make gate`, as a bundled skill script, and — later, not today —
anywhere above the charter.

---

## The run of show · three agent runs, 90 minutes

| clock | segment | what happens |
|---|---|---|
| 0:00–0:06 | **0 · the claim** | The thesis, the counter-thesis, the line we stop at. `make doctor`. |
| 0:06–0:12 | **1 · the repository** | Three eras, four traps. I talk, they read. No typing. |
| 0:12–0:26 | **2 · run A, bare** | The ticket, unaided. Capture. Read the scorecard aloud. `make audit`, then delete the lying comment. |
| 0:26–0:38 | **3 · what it reads** | Author one rule with all four parts by hand, then `make lever N=1 N=2`. |
| 0:38–0:46 | **4 · run B** | Same ticket, fresh session. Capture, compare. Collect the disagreements from the room. |
| 0:46–0:58 | **5 · what it can do** | The family test, four rungs, four attributes. `make lever N=3`, then `make grants` and fix one accidental grant by hand. Delete `.mcp.json`. |
| 0:58–1:10 | **6 · what refuses it** | `make lever N=4`. Feel the hook refuse. Run C, plus the reviewer sub-agent to fill C9. Compare. |
| 1:10–1:18 | **7 · the ceiling** | `make promote`. The two rungs above in one table, and we stop at the line. |
| 1:18–1:26 | **8 · what we built** | Three sequence diagrams: one turn with the charter, one without, one with the rungs above. The portability map. |
| 1:26–1:30 | **9 · Monday** | `HITLIST.md`, the budget, deletion day, questions. |

Every lab is the same four beats, which is what makes it a workshop rather than
a demo:

> **author one artifact by hand → `make lever N=<n>` lands the rest → re-run
> the ticket → `make compare`**

Nobody types 1,500 words of `CLAUDE.md` in a conference room. They write the two
parts that carry the lesson and read the rest.

### The cut lines, decided in advance

Pacing fails in one direction: labs run long. So the cuts are chosen now rather
than improvised at 1:05.

- **Behind at 0:46** — skip the `make grants` exercise and show the findings
  from the front. Costs five minutes and nothing structural.
- **Behind at 0:58** — do not run C. Apply lever 4, demonstrate the hook
  refusing live from the front, and fill the third column from
  `runs/reference/02-checks`. Costs eight minutes.
- **Behind at 1:10** — §7 and §8 merge into one six-minute close using the
  sequence diagrams alone. The promotion report goes home as reading.
- **Never cut** — §2 (the baseline is the whole argument), the C9 beat in §6
  (it is the one idea nobody else teaches), and §9 (they came for Monday).

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

- **No agent / broken install** → `runs/reference/` ships three captured runs,
  produced by the real scorer rather than typed. `make reference` prints the
  matrix without invoking a model once.
- **Conference wifi** → standard-library Python floor. Nothing downloads. The only
  network call in the room is the agent's own.
- **A run comes out clean on the baseline** → say so, and put it in the matrix. A
  null result is the honest outcome and the instrument was built to report it.
- **Too slow** → the cut lines above, decided in advance rather than improvised.
- **The room's results disagree with mine** → that is the best outcome available and
  the reason the scorer is in the repo. n is one per attendee; the room is the
  sample, and I will say so from the front.
