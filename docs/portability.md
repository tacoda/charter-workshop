# Staying portable — the four levers, and what they are called elsewhere

The workshop shows everything in Claude Code's primitives, because it has to
pick one tool's file names. **Nothing in the design is Claude-only.** The lever
is the concept; the filename is whichever host you happen to be on.

## The substitutions

| lever | the concept | Claude Code | Cursor | anywhere else |
|---|---|---|---|---|
| 1 · instruction | read on every turn | `CLAUDE.md` | `.cursorrules` | `AGENTS.md` |
| 2 · constraint | read when a path matches | `.claude/rules/*.md` | `.cursor/rules/<id>.mdc` with `globs:` | a doc the root file points at, by path |
| 3 · capability | what it can reach for | `.claude/commands/`, `.claude/skills/`, `.claude/agents/`, `.mcp.json`, `settings.json` | saved prompts, MCP, host permissions | a named doc, a second session, MCP |
| 4 · check | what refuses, and what judges | `PreToolUse` / `Stop` hooks, a reviewer sub-agent | pre-commit, a second session | pre-commit, a second session |

## The one lossy substitution

A host with no tool-call hook **cannot refuse a write inside the turn.** You
fall back to a pre-commit gate, which answers after the agent has moved on.

Same rule, later feedback, and the loop converges less often. That is the
difference §6 of the workshop makes you feel, and it is the single biggest
reason to check whether your host has a hook before you plan around one.

## Where the standards are

Some of this is genuinely converging. `AGENTS.md` is becoming the common place
for the always-on instruction, and agent skills are settling into a recognisable
shape across hosts. Neither is universal yet: coverage is partial, providers
implement different subsets, and **nothing standard reaches the check layer at
all.** Levers 1 and 3 are getting easier to write once. Levers 2 and 4 are not.

So until that finishes, you have two options and both are fine.

## Option one: maintain the copies by hand

The substitutions above are mechanical. For two hosts and a handful of rules,
a hand-maintained copy per host is honest and cheap, and the whole cost is
remembering to update both.

## Option two: compile them from one source

Author once, in one canonical file, and generate each host's dialect from it.
The tool I use for this is Keystone, which compiles typed primitives under
`.charter/` down to `.claude/`, `.cursor/rules/*.mdc`, or a pointer block in
`AGENTS.md`. It is one tool among several and none of the workshop depends on
it; a shell script that copies and rewrites frontmatter does the same job.

## The rule that matters either way

**Pick one canonical file, and treat every projection as build output.**

Editing the projected copy means editing a compiled artifact, and the next
projection overwrites it. This is what stops a charter drifting into four
slightly different copies across four agent surfaces, which is what happens to
every team that adopts a second agent and does nothing about it.

Four implementations of one rule disagree within a month, and then the agent
learns that some edits are free at one mount and blocked at the next.

## Why the predicate in this repo is shaped the way it is

`tools/charter_check.py` takes `{files: [{filename, source}]}`, imports nothing
from `tarrasque`, and never opens a file. That shape is what lets the same forty
lines run as a `PreToolUse` hook, as `make gate`, as a bundled script beside a
skill, and, if the rule ever earns the crossing, at any rung above the charter,
in any host, on a machine with no shared filesystem.

Write it once.
