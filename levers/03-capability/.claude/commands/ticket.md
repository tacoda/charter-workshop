---
description: Start a ticket with its text, its scope, and the current diff already in the window
argument-hint: [ticket-id]
allowed-tools: Bash(make ticket:*), Bash(make gate:*), Bash(git diff:*)
disable-model-invocation: true
---

The ticket:

!`make ticket TICKET=$1`

What has changed so far:

!`git diff --stat HEAD`

The charter's verdict on what has changed so far:

!`make gate`

Read `@CLAUDE.md` and the rule files under `@.claude/rules/` that match the
paths in the ticket's scope. Then implement the ticket.

Before you write anything, say in two sentences which of the three eras named
in CLAUDE.md this work belongs to, and which files you will therefore *not*
copy from.

Run `make verify` before you say you are finished.
