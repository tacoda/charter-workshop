# AIDevCon — CFP submission

Slots into the existing slate as the **Context Engineering** workshop. Pairs
with the talk *Why "Add a Rule" Is Usually Wrong*, and stands alone.

---

## Speaker fields

**Speaker Name:** Ian Johnson

**Speaker Tagline:** Staff engineer at Parento · author of Keystone · founder of Huckleberry

**Speaker Biography:**
> Ian Johnson is a staff software engineer at Parento and the author of Keystone, an open-source
> tool for making AI-generated code reliable. He runs Huckleberry, a consultancy helping teams
> adopt agentic coding without losing the plot. He wrote *Constraint Engineering: Building
> Reliable Systems Around Non-Deterministic Agents* and built open-refinery, the MIT-licensed
> dark-factory control plane his workshops draw from. He works on harness and charter engineering
> — the machinery and the standards that keep non-deterministic agents inside a band you can
> ship. Based outside Austin, Texas.

---

## Session

**Session Title:**
> Wrap It in a Charter: Ninety Minutes from Bare Repo to Governed Agent

**Session Type:** Workshop (hands-on) — 90 minutes. A 3-hour version is available.

**Primary Track:** Context Engineering

**Secondary Track:** The Agent Enablement Platform

**Level:** Intermediate → Advanced

**Description:**
> Everyone tells you to write a `CLAUDE.md`. Nobody shows you what it buys, and the honest answer
> is that most teams have no idea — because nobody measures it. This workshop measures it, on your
> laptop, three times.
>
> You get a repository you did not write: a tabletop campaign engine, three eras deep, where the
> correct 2026 domain layer is outnumbered ten to one by a 2023 god file and a frozen 2021 module
> that rolls unseeded dice. You get one ticket. You run it against a bare repo and watch the agent
> copy the worst thing in the codebase, then score the result against nine checks and capture it.
>
> Then you wrap the application one lever at a time, all of them files: the instruction layer, the
> path-scoped rules with the incident that caused each one, the capability half nobody designs
> — commands, skills, sub-agents, MCP, and the permission list that is a lossy translation of what
> you meant — and finally the checks, one predicate mounted as a hook that refuses inside the turn
> and a reviewer sub-agent for the rule no predicate can hold. You re-run the same ticket after
> each block and compare.
>
> The deliverable is a matrix. Eight decidable checks and one that is not, which prints a question
> mark until the reviewer fills it in — because the hole in the scorecard is the whole point. We
> stop at the charter's edge: when a rule earns the next rung up, we name it, write it down, and
> leave it there.

**Top 3 Takeaways:**
> 1. A measured before-and-after from your own machine: which charter levers moved which checks on
>    a codebase you did not write, and which measured nothing because the code already agreed.
> 2. Four working artifacts you keep — an honest root file, tiered path-scoped rules, four placed
>    capabilities with declared grants, and one predicate mounted as both a hook and a target.
> 3. The placement discipline: the family test, the four attributes every capability carries, the
>    three tests a rule passes before it earns a mechanical rung, and where to stop.

**Notes for the CFP Committee:**
> Hands-on, laptops out, instructor-led with individual implementation throughout. The session page
> is a self-contained HTML file that doubles as my teaching surface and their lab guide, so every
> code sample I put on screen stays in front of them while they work.
>
> Attendees clone a provided repo ahead of time. Python 3.11+ is the only hard requirement: the
> app is standard library, the test suite runs in under a second, and every `make` target degrades
> to a bundled fallback when `pytest`/`ruff`/`mypy` are absent. Nothing downloads during the
> session. Five captured reference runs ship in the repo, so a broken laptop still does the whole
> workshop.
>
> Everything is shown in Claude Code's primitives because a workshop has to pick one tool's file
> names, and each one is mapped to its provider-agnostic Keystone equivalent so nobody leaves
> thinking this is Claude-only. Bring Cursor or Codex if that is what you use; the differences are
> called out as they come up.
>
> The instrument is deliberately built so the result can come out against me, and I say so from
> the front: n is one per attendee, I chose rules designed to make the effect visible, and a null
> result is a real outcome the scorecard reports rather than hides. Drawn from my book,
> *Constraint Engineering*. Cap roughly 30–40 per facilitator.

**Will your session use or integrate with Tessl?** No

**Tags:** workshop, context engineering, CLAUDE.md, agent charter, rules, hooks, skills, sub-agents,
MCP, tool permissions, coding agents, measurement, hands-on

---

## Video pitch (≈60s, to camera, no slides)

**(0:00–0:15) — Hook**
> Everybody tells you to write a CLAUDE.md. Nobody tells you what it actually buys you — and if I
> asked you right now which of your rules is doing any work at all, you probably could not answer.
> In this workshop you find out, on your own laptop, in ninety minutes.

**(0:15–0:25) — Frame**
> I'm Ian Johnson. It's hands-on. Bring the coding agent you already use.

**(0:25–0:52) — What you'll build**
> You get a repo you didn't write, three eras deep, where the correct code is outnumbered ten to
> one. You give your agent one ticket, with no charter, and watch it copy the worst thing in the
> codebase. Then you wrap it — the root file, the rules, the capabilities and the grants, and one
> predicate mounted as a hook that refuses before the bytes hit disk. Same ticket, three times,
> scored against nine checks. Eight of them a machine can settle. The ninth is the one that
> matters, and it stays a question mark until a reviewer reads the diff.

**(0:52–1:00) — Close**
> You leave with the matrix, the artifacts, and a hit list for your own repo. And I built the
> instrument so it can come out against me. See you in Brooklyn.

_~165 words._
