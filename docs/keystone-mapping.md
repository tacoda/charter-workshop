# Staying portable — every primitive we install, and what it is elsewhere

The workshop shows everything in Claude Code's primitives, because it has to
pick one tool's file names. Nothing in the design is Claude-only. This is the
map.

## The mapping

| lever | Claude Code | fires when | Keystone kind |
|---|---|---|---|
| 1 · instruction | `CLAUDE.md` | every turn | `guide`, unscoped |
| 2 · constraint | `.claude/rules/*.md` | the glob matches the files touched | `guide` with `globs:` |
| 3 · capability | `.claude/commands/*.md` | a human types it | `command` |
| | `.claude/skills/*/SKILL.md` | the model matches the description | `skill` (or a `playbook` wrapping it) |
| | `.claude/agents/*.md` | the parent turn spawns it | `agent` |
| | `.mcp.json` | the model matches a schema | `tool`, `transport: mcp` |
| | `.claude/settings.json` · permissions | every tool call | `posture` |
| 4 · check | `.claude/hooks/*.py` + the `hooks` block | `PreToolUse`, `Stop` | `sensor` with `run:` |
| | the `charter-auditor` sub-agent | asked, or on a signal | `sensor` with `returns:` |
| — | a plugin | whatever it ships fires | a vendored `policy`, pinned by hash |

## The three ideas worth taking even if you never install anything

**One canonical layer, many projections.** You author once, under
`.charter/`, in typed primitives with `kind`, `id` and `description` in
frontmatter. `keystone project` compiles that down to whatever host you point
it at: rule shims under `.claude/rules/`, `.cursor/rules/<id>.mdc` with the
globs mirrored verbatim, a pointer block in `AGENTS.md` for everything else.

**The projected layer is build output.** Editing `.claude/` in a repo like
that is editing a compiled artifact, and the next projection overwrites it.
This is the rule that stops a charter drifting into four slightly different
copies across four agent surfaces — which is what happens to every team that
adopts a second agent.

**There is no `hook` kind.** What was a hook is a *sensor* that self-subscribes
to a moment via `on:`. A computational sensor declares `run:` and its exit
status is the verdict; an inferential sensor declares `returns:` and is
dispatched as an agent review. Same subscription model, two verdict sources —
and because the subscription lives in the canonical file, you cannot quietly
unhook a gate without the change showing up in the same diff as the rule it
enforces.

## Why the predicate in this repo is shaped the way it is

`tools/charter_check.py` takes `{files: [{filename, source}]}`, imports nothing
from `tarrasque`, and never opens a file. That shape is what lets the same
forty lines run as a `PreToolUse` hook, as `make gate`, as a bundled script
beside a skill, and — if the rule ever earns the crossing — at any rung above
the charter, in any host, on a machine with no shared filesystem.

Four implementations of one rule disagree within a month, and then the agent
learns that some edits are free at one mount and blocked at the next. Write it
once.

## The other direction

If you are on Cursor or Codex today and want to try this workshop's material
without Keystone, the substitutions are mechanical:

- `CLAUDE.md` → `.cursorrules` / `AGENTS.md`
- `.claude/rules/x.md` with a scope → `.cursor/rules/x.mdc` with `globs:`
- `.claude/commands/` → whatever your host calls a saved prompt
- `.claude/skills/` → a document your rules point at, invoked by name
- `.claude/agents/` → a second session with a narrower tool list
- `.claude/hooks/` → your host's tool-call hook, or `make gate` in a
  pre-commit hook if it has none

The last substitution is the lossy one, and it is worth naming: a host without
a tool-call hook cannot refuse a write *inside the turn*. You fall back to a
pre-commit gate, which answers after the agent has moved on. Same rule, later
feedback, and the loop converges less often.
