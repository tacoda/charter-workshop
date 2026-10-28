# The Only Variable

*Change nothing but the charter, and measure what moved.*

A ninety-minute, hands-on workshop. You take an application nobody in the room
wrote, wrap it in an agent charter one lever at a time, and **measure** what
each lever bought — five runs of the same ticket, one scorecard, one matrix.

Nothing outside the repository changes. No custom harness, no orchestrator, no
framework. Only files: `CLAUDE.md`, `.claude/`, `.mcp.json`. The claim under
test is that the charter alone moves the band, and the instrument is in `bin/`
so you can find out rather than take anyone's word for it.

**The workshop page is `workshop/index.html`.** Open it in a browser. It is the
thing to follow along with, and it carries every code sample the instructor
puts on screen.

---

## Setup — about two minutes

    git clone https://github.com/tacoda/charter-workshop.git && cd charter-workshop
    make doctor

Python 3.11 or newer is the only hard requirement. `pytest`, `ruff` and `mypy`
are used when present and every `make` target falls back to a bundled
standard-library equivalent when they are not. Nothing downloads at any point
during the workshop.

Optionally, for the full toolchain:

    make setup && source .venv/bin/activate

Bring a coding agent you already use — Claude Code, Cursor, Codex, Aider. The
charter is plain markdown and the levers are plain files; the workshop names
Claude Code's paths because they need to be *some* tool's paths.

---

## The application

`tarrasque` — a play-session engine for tabletop campaigns. It rolls the dice,
tracks initiative, holds the condition timers, and writes an append-only log a
table can read back afterwards.

It is deliberately three eras deep, because that is what a real retrofit meets:

| where | when | what it looks like |
|---|---|---|
| `tarrasque/domain/` | 2026 | pure functions, injected `Rng`, every roll carries its receipt. Typed, tested, and **outnumbered** |
| `tarrasque/api/handlers.py` | 2023 | the `/v1` god file: parse, query, roll and serialize inline. The dominant pattern by volume |
| `tarrasque/legacy/tables.py` | 2021 | calls `random` directly, keeps state in a module global, returns bare integers. Frozen |

    make serve      # run it on :8099
    make seed       # what is in the seed database
    make test       # 145 tests, well under a second

---

## The tickets

Seven real features, small to medium. Each names its own scope and the rules it
touches, so a run can be scored against the ticket it was actually given.

    make tickets
    make ticket TICKET=TAR-412

| id | size | what |
|---|---|---|
| TAR-412 | medium | group saving throw against an area effect — **the spine ticket** |
| TAR-388 | small | concentration check when a caster takes damage |
| TAR-401 | medium | death saving throws |
| TAR-429 | small | explain the initiative order — **the control ticket**, no dice |
| TAR-455 | small | apply and clear conditions |
| TAR-467 | medium | replay an encounter from its log — **the payoff ticket** |
| TAR-473 | small | draw from the loot table — **the trap ticket** |

---

## The instrument

    make score      TICKET=TAR-412        # score the working tree
    make capture    RUN=00-baseline       # freeze a run and its scorecard
    make compare                          # the matrix
    make reference                        # the runs shipped with the repo

Nine checks. Eight are decidable and run in `tools/charter_check.py`. The ninth is
not, and prints `?` until a reviewer sub-agent fills it in. The hole in the
scorecard is the point.

| | check | kind |
|---|---|---|
| C1 | `scope.allowed-paths` | deterministic |
| C2 | `dice.seeded` | deterministic |
| C3 | `roll.provenance` | deterministic |
| C4 | `log.append-only` | deterministic |
| C5 | `legacy.frozen` | deterministic |
| C6 | `authority.session-derived` | deterministic — *the shadow only* |
| C7 | `tests.not-self-approving` | deterministic |
| C8 | `verify.green` | deterministic |
| C9 | `authority.semantic` | **inferential** |

---

## The levers

    make levers                 # what is installed, what is available
    make lever N=1              # apply one
    make reset                  # remove the whole charter

| | lever | lands |
|---|---|---|
| 1 | **instruction** | `CLAUDE.md` — eight sections, present tense |
| 2 | **constraint** | `.claude/rules/` — path-scoped, IRON / GOLDEN / PREF, every rule dated to an incident |
| 3 | **capability** | `.claude/commands/`, `.claude/skills/`, `.claude/agents/`, `.claude/settings.json`, `.mcp.json` |
| 4 | **check** | `.claude/hooks/` and the repaired grant list |

Everything under those paths is the charter. The moment enforcement has to
move somewhere reconfiguring the agent cannot reach — a tool that refuses
internally, a stage gate, CI — we name it, write it on the promotion report,
and stop. `make promote` draws that line.

---

## The other tools

    make audit      # the retrofit audit: which signals in this repo lie
    make grants     # what the permission list actually grants, versus what you meant
    make promote    # which rules have earned the next rung, and where that rung is
    make gate-all   # the charter's rules over the whole tree — the seed's own debt

---

## Licence

CC BY 4.0 for the workshop material; MIT for the code. Fork it, change every
rule, keep the instrument.

Ian Johnson · [tacoda.dev](https://tacoda.dev)
