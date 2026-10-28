# Narrative — The Only Variable

Built by running `nail-your-narrative` in reverse against the existing page, then
forward again. This file is the spine. Every cut to `index.html` is judged against it.

---

## Phase 1 · The big idea

**Point of view.** Everybody argues about whether a `CLAUDE.md` helps. Almost nobody
measures it. And the argument is mis-framed anyway: the agent is already governed,
just not by you. The code is the charter it actually obeys.

**What's at stake.** You are merging agent PRs you cannot tell apart from correct
ones, against rules nothing enforces, in a repo that votes against you on every turn.

**Fused, one sentence:**

> Your codebase is already your agent's charter. Today you write a better one, and
> find out whether it won.

**Falsifiable, and it can come out against me.** The instrument ships in the repo so
the room can produce a null result and report it.

---

## Phase 2 · The audience persona

**Dana, four years in, backend, ships a feature most weeks.**

- Uses a coding agent daily, for the boring sixty percent. Trusts it about as far as
  a competent contractor who has never read the codebase.
- Inherited a `CLAUDE.md` from someone who left. Has opened it twice.
- Reviews agent-written PRs and cannot reliably tell a good one from a plausible one.
  That is the thing that actually costs them time.
- Measured on merged PRs and on not breaking production.
- Knows what a hook is in the git sense, not in the agent sense. Has heard of MCP.
  Has never written a sub-agent.

**Why they care.** Their review queue is the bottleneck, and the agent is filling it
faster than they can read it.

**The second persona in the room** is the same person two years later, running the
team. They do not need a different talk. They need the senior decision named out loud
next to each lever: which call was made, what it cost, what the alternative was.

### Three takeaways. Cap at three.

1. **The code outvotes the prose.** Delete the false signal before you write the rule.
2. **Four levers fire at four different moments in a turn.** Match the lever to the
   moment your problem happens: read, read-when-touched, reach-for, refuse.
3. **Every rule names what it cost.** No incident, no rule.

Everything else on the page is support for those three.

---

## Phase 3 · Structure

**Sparkline.** What is, against what could be, oscillating, ending on new bliss.

| beat | section | what is | what could be |
|---|---|---|---|
| open on the gap | §0 | a charter nobody tested | a claim you can falsify today |
| what is | §1–2 | 1 of 8 checks, tests green | |
| what could be | §3–4 | | 8 of 8, from files alone |
| what is (again) | §5 | capabilities installed, never designed | four attributes, one line each |
| what could be | §6 | | two verdict sources, one predicate |
| the honest floor | §7 | nothing earned promotion today | |
| new bliss | §8–9 | | your repo, Monday, a budget and a deletion day |

The oscillation is the argument. A flat "here are four levers" explainer loses it.

---

## Phase 4 · The narrative, spoken with nothing on screen

I can run this without the page:

Your agent already has a charter. It is the code. Eleven hundred lines of a 2023 god
file that rolls unseeded dice and reads identity out of the request body, against one
file from 2026 that does it correctly. Ask an agent for an endpoint and it writes the
eleven-hundred-and-first line, because imitation beats instruction every time the two
disagree.

So we run the ticket bare. One of eight checks passes, and the test suite is green,
which is the ordinary case and the reason the other seven columns exist. That run is
the incident. Every rule we write afterwards points at a diff we watched it produce.

Then four levers, one at a time, and each one plays a different role. The root file
orients: it says which era you are in. The rule files bind: they say which lines are
load-bearing and what each one cost. Capabilities extend: they change what the agent
can reach for at all. Checks refuse: they put something between the model's decision
and the disk.

Levers one and two persuade, and you can talk an agent out of them. Lever four
refuses, and you cannot. Feeling that difference in your own terminal is the point of
the probes.

Re-run. Eight of eight, from files alone. Then the ninth column, the one no predicate
settles, goes red under a reviewer that eight green checks missed. A green scorecard
is not a correct change.

Then we stop, on purpose, at the line where enforcement leaves the repository. Nothing
earned a promotion today, because every rule failed exactly once and once is not
recurrence. Come back in a quarter with your own captured runs.

Monday: a budget, a deletion day, and your own repository.

---

## Phase 5 · Storyboard

Not a deck. The page is the storyboard, and the live artifact is the attendee's own
terminal. Per section the card is: **the role**, **the probe**, **the prediction**,
**the run**, **the takeaway**.

### What changed on the page, and which beat each change serves

| change | beat it serves |
|---|---|
| "The turn, and where you can stand in it" table in §0 | persona onramp: Dana has never seen the four moments named |
| a **role** line on levers 1, 2, 3, 4 | takeaway 2 |
| **probe** blocks: a 30-second behavior check per lever | one-by-one, without paying for a full run |
| **predict** blocks before runs B and C | makes the matrix a test rather than a reveal |
| the persuade-versus-refuse contrast in §6 | takeaway 2, and the senior call nobody names |
| **the call I made** strips | second persona, without a second talk |
| symptom-to-lever rubric in §9 | Monday, for a repo that is not tarrasque |

### What was cut, and why

- Three of four portability blocks. The argument belongs in one closing section, not scattered.
- The restatement paragraph under most figures. The figures carry inline annotation.
- The third sequence diagram's commentary. §7's table already draws that line.
