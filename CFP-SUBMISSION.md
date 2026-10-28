# CFP submission · paste-ready

For **The Only Variable**, the 90-minute workshop in this repo. The session is
`workshop/index.html`, the application under test is `tarrasque`, and the
instrument is `bin/` plus `tools/charter_check.py`. Nothing here describes any
other resource.

AIDevCon · Brooklyn, NY · November 3–4, 2026. One section per form field, in
form order. `CFP.md` stays the working draft; this file is what goes in the
boxes.

---

## Before you open the form

**Blocking.** One required field has no answer yet.

| field | status |
|---|---|
| **Video submission** `*` | **No link exists.** The 60-second script is in `CFP.md` under *Video pitch*. Record it, put it anywhere with a public URL, paste the link. |

**Needs a fact I do not have.** Left blank below, marked `‹fill›`.

- X (Twitter), LinkedIn, Company Website
- Confirmation of the two dropdown values (see *Level* and *Secondary Track*)

**Ready to upload.** Speaker Photo: use `tacoda.github.io/ian3.jpg`. It is
3010 × 2999, the only one of the three that clears the 1000 × 1000 floor, and it
is already square so the crop takes nothing. `ian1.png` (576²) and `ian2.jpg`
(460²) will both be rejected.

**One thing to settle before you paste.** The bio in `CFP.md` calls the book
*Constraint Engineering*. Across tacoda.dev the book is *Harness Engineering*
(151 references), and *Constraint Engineering* is labelled "a design standard"
inside it (19 references). I have written the bio below the second way. If the
book really is titled *Constraint Engineering*, swap it back and fix the 31
bylines on the site instead.

---

## Session

### Session Title `*`

```
The Only Variable: Change Nothing but the Charter, and Measure What Moved
```

### Description `*` · min 400 characters

Full version, **1,735 characters**. Paste this unless the form rejects it.

```
Everyone tells you to write a CLAUDE.md. Nobody shows you what it buys, and the
honest answer is that most teams have no idea, because nobody measures it. This
workshop measures it, on your laptop, three times.

You get a repository you did not write: a tabletop campaign engine, three eras
deep. The correct 2026 domain layer is outnumbered ten to one by a 2023 god file
and a frozen 2021 module that rolls unseeded dice. You get one ticket. You
run it against a bare repo, watch the agent copy the worst thing in the codebase,
then score the result against nine checks and capture it. That run is the
incident every rule you write afterwards points at.

Then you wrap the application one lever at a time, all of them files, and you
probe each lever on its own before you pay for a full run. The root file orients.
The path-scoped rules bind, each one dated to the incident that caused it. The
capabilities extend: commands, skills, sub-agents, MCP, and the permission list
that is a lossy translation of what you meant. The checks refuse. One predicate
mounts twice: as a hook that stops the write inside the turn, and as a reviewer
sub-agent for the rule no predicate can hold. Levers one and two
persuade, and you can talk an agent out of them. Lever four cannot be argued
with. You feel that difference in your own terminal.

The deliverable is a matrix: eight decidable checks and one that is not. The
ninth prints a question mark until the reviewer fills it in, because the hole in
the scorecard is the whole point. A green scorecard is not a correct change. It
is a change with no mechanically detectable problem. We stop at the charter's edge.
When a rule earns the next rung up, we name it, write it down, and leave it
there.
```

<details>
<summary>Short version, 652 characters, if the form has a ceiling</summary>

```
Everyone tells you to write a CLAUDE.md. Nobody shows you what it buys, because
nobody measures it. Here you measure it, on your laptop, three times.

You get a repository you did not write, three eras deep, where the correct code
is outnumbered ten to one. You give your agent one ticket with no charter and
watch it copy the worst thing in the codebase. Then you add four guardrails one
at a time, probe each on its own, and re-run the same ticket after each.

The deliverable is a matrix: eight checks a machine can settle, and one it
cannot, which stays a question mark until a reviewer reads the diff. The hole in
the scorecard is the whole point.
```

</details>

### Session Type `*`

```
Workshop
```

90 minutes, hands-on. A 3-hour version is available; say so in the notes field,
not here.

### Primary Track `*`

```
Context Engineering
```

### Secondary Track

```
The Agent Enablement Platform
```

`‹confirm›` The screenshot shows this dropdown defaulted to *Context
Engineering*, the same as primary. Change it. If that option is not in the list,
leave the field empty rather than duplicating the primary track.

### Level `*`

```
Intermediate
```

`‹confirm›` The form defaults to *Beginner*, which is wrong for this session.
The working plan says "Intermediate → Advanced". The page now defines every
primitive the first time it appears, so an engineer who runs an agent daily but
has never written a sub-agent can follow it. If the dropdown offers
*Intermediate to Advanced* or similar, take that instead.

### Top 3 Takeaways for Attendees `*`

The form renders this as a single-line input, so it wants the compact version.
**477 characters.**

```
1) A measured before-and-after from your own laptop: which charter levers moved which of nine checks, and which measured nothing because the code already agreed. 2) Four artifacts you keep: an honest root file, tiered path-scoped rules, four placed capabilities with declared grants, and one predicate mounted twice. 3) The placement discipline: the family test, the four attributes every capability carries, and the three tests a rule passes before it earns a mechanical rung.
```

### Notes for the CFP Committee

Also a single-line input. **1,203 characters.** Trim from the bottom if it
complains.

```
Hands-on, laptops out, instructor-led with individual implementation throughout. The session page is a self-contained HTML file. It doubles as my teaching surface and their lab guide, so every sample I put on screen stays in front of them as they work. Attendees clone a provided repo ahead of time. Python 3.11+ is the only hard requirement. The app is standard library and the suite runs in under a second. Every make target degrades to a bundled fallback when pytest, ruff and mypy are absent. Nothing downloads during the session. Captured reference runs ship in the repo, so a broken laptop still does the whole workshop, and the cut lines are decided in advance rather than improvised at 1:05. Everything is shown in Claude Code's primitives, because a workshop has to pick one tool's file names. Each is mapped to a provider-agnostic equivalent, so nobody leaves thinking this is Claude-only. I built the instrument so the result can come out against me, and I say so from the front. n is one per attendee. I chose rules designed to make the effect visible. A null result is a real outcome the scorecard reports rather than hides. A 3-hour version is available. Cap roughly 30-40 per facilitator.
```

### Will your session use or integrate with Tessl?

```
No
```

### Video submission `*`

```
‹fill› (nothing recorded yet)
```

**This is the one blocker.** The script is written and timed at roughly 165
words, about 60 seconds to camera with no slides. It is in `CFP.md` under
*Video pitch*, beat by beat: hook, frame, what you'll build, close. Record it,
host it, paste the URL.

### Tags (not exhaustive) `*`

```
workshop, context engineering, CLAUDE.md, agent charter, rules, hooks, skills, sub-agents, MCP, tool permissions, coding agents, measurement, hands-on
```

### In-person confirmation `*`

Tick it. Brooklyn, NY, November 3–4, 2026.

---

## Speaker

### Speaker Name `*`

```
Ian        Johnson
```

### Speaker Tagline `*`

```
Staff engineer at Parento · author of Keystone · founder of Huckleberry
```

### Email

Prefilled as `tacodadev@gmail.com`. Confirm you read that inbox; the organizer
contacts you there.

### Speaker Biography `*` · 300 to 800 characters

**530 characters.** Inside the window with room either way.

```
Ian Johnson is a staff software engineer at Parento and the author of Harness Engineering, a body of work on the machinery and the standards that keep non-deterministic agents inside a band you can ship. He wrote Keystone, an open-source tool for making AI-generated code reliable, and runs Huckleberry, a consultancy helping teams adopt agentic coding without losing the plot. He works on harness and charter engineering: the engine that runs an agent, and the rules it reads before it writes a line. Based outside Austin, Texas.
```

<details>
<summary>Alternate, if the book really is titled <em>Constraint Engineering</em>, 483 characters</summary>

```
Ian Johnson is a staff software engineer at Parento and the author of Constraint Engineering: Building Reliable Systems Around Non-Deterministic Agents. He wrote Keystone, an open-source tool for making AI-generated code reliable, and runs Huckleberry, a consultancy helping teams adopt agentic coding without losing the plot. He works on harness and charter engineering: the engine that runs an agent, and the standards it reads before it writes a line. Based outside Austin, Texas.
```

</details>

### Speaker Photo `*`

```
ian3.jpg   (3010 × 2999)
```

From `tacoda.github.io/ian3.jpg`. The other two on the site are 576² and 460²
and will fail the 1000 × 1000 minimum.

### Links

| field | value |
|---|---|
| X (Twitter) | `‹fill›` |
| LinkedIn | `‹fill›` |
| Blog | `https://tacoda.dev` |
| Company Website | `‹fill›` · parentoleave.com? |

### Company Name `*`

```
Parento
```

### Role `*`

```
Staff Software Engineer
```

### Co-speakers

Leave empty. Single facilitator, cap 30–40.

---

## Character counts, checked

| field | requirement | actual |
|---|---|---|
| Description, full | ≥ 400 | 1,735 ✓ |
| Description, short | ≥ 400 | 652 ✓ |
| Speaker Biography | 300–800 | 530 ✓ |
| Biography, alternate | 300–800 | 483 ✓ |
| Top 3 Takeaways | none stated | 477 |
| Notes for Committee | none stated | 1,203 |
| Tags | none stated | 150 |
