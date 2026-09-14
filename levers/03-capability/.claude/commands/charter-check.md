---
description: Check the current diff against the charter and report violations without fixing them
argument-hint: [base-ref]
allowed-tools: Bash(git diff:*), Bash(make gate:*), Bash(make score:*)
disable-model-invocation: true
---

The diff under review, against ${1:-HEAD}:

!`git diff ${1:-HEAD} --unified=0`

The decidable verdict:

!`make gate`

Read `@.claude/rules/`. Check the diff against the rules the gate cannot
settle — the `none`-altitude rule in `authority.md` above all.

Report one line per finding: `path:line · rule · what it violates`. Then one
summary line. Do not fix anything and do not write files.
