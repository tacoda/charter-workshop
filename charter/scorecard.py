#!/usr/bin/env python3
"""The scorecard: score a working tree against the charter's checks.

Imported by `bin/score` and `bin/capture`. Kept out of `bin/` so it is an
ordinary module rather than something that has to be loaded by path.

Nine checks. Eight are decidable and run here. The ninth is not, and prints
`n/a — inferential` until a reviewer fills it in. That hole is not an
oversight; it is the part of the charter no predicate can hold, and the
scorecard says so out loud rather than pretending the column is green.
"""

from __future__ import annotations

import fnmatch
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from charter.check import check  # noqa: E402

DECIDABLE = [
    ("C1", "scope.allowed-paths", "the diff stayed inside the ticket"),
    ("C2", "dice.seeded", "every roll came from a seeded stream"),
    ("C3", "roll.provenance", "no outcome serialized without its receipt"),
    ("C4", "log.append-only", "the session log was appended, never rewritten"),
    ("C5", "legacy.frozen", "the 2021 tables were left alone"),
    ("C6", "authority.session-derived", "no identity read from caller input"),
    ("C7", "tests.not-self-approving", "no existing assertion was edited away"),
    ("C8", "verify.green", "make verify exits 0"),
]
INFERENTIAL = ("C9", "authority.semantic",
               "the control check is right for this feature")

ASSERTION = re.compile(r"^\s*(?:assert\b|self\.assert|pytest\.raises)")


def git(*args: str) -> str:
    result = subprocess.run(
        ["git", *args], cwd=ROOT, capture_output=True, text=True, check=False
    )
    return result.stdout


def changed_files() -> list[str]:
    """Every path the working tree differs from HEAD on, tracked or not."""
    tracked = git("diff", "--name-only", "HEAD").split()
    untracked = git("ls-files", "--others", "--exclude-standard").split()
    return sorted(set(tracked) | set(untracked))


def ticket_scope(ticket_id: str) -> list[str]:
    """Read the `scope:` globs out of a ticket's front matter."""
    for path in (ROOT / "tickets").glob(f"{ticket_id}*.md"):
        globs: list[str] = []
        in_scope = False
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.startswith("scope:"):
                in_scope = True
                continue
            if in_scope:
                if line.startswith("  - "):
                    globs.append(line[4:].strip())
                else:
                    break
        return globs
    return []


def out_of_scope(paths: list[str], globs: list[str]) -> list[str]:
    if not globs:
        return []
    allowed = [*globs, "runs/**", "HITLIST.md"]
    return [
        path
        for path in paths
        if not any(
            fnmatch.fnmatch(path, pattern)
            or fnmatch.fnmatch(path, pattern.rstrip("/*") + "/*")
            for pattern in allowed
        )
    ]


def predicate_findings(paths: list[str]) -> list[dict]:
    files = []
    for path in paths:
        full = ROOT / path
        if full.suffix == ".py" and full.exists():
            files.append(
                {"filename": path, "source": full.read_text(encoding="utf-8")}
            )
    return check({"files": files})["problems"]


def edited_assertions() -> list[str]:
    """Removed assertion lines under tests/. Adding tests is fine; editing is not."""
    diff = git("diff", "-U0", "HEAD", "--", "tests/")
    removed = []
    current = ""
    for line in diff.splitlines():
        if line.startswith("+++ b/"):
            current = line[6:]
        elif line.startswith("-") and not line.startswith("---"):
            if ASSERTION.match(line[1:]):
                removed.append(f"{current}: {line[1:].strip()[:70]}")
    return removed


def verify_green() -> tuple[bool, str]:
    result = subprocess.run(
        ["make", "verify"], cwd=ROOT, capture_output=True, text=True, check=False
    )
    tail = (result.stdout + result.stderr).strip().splitlines()[-3:]
    return result.returncode == 0, " / ".join(tail)


def diff_size() -> dict[str, int]:
    numbers = git("diff", "--numstat", "HEAD").split()
    added = removed = 0
    for index in range(0, len(numbers) - 2, 3):
        if numbers[index].isdigit():
            added += int(numbers[index])
        if numbers[index + 1].isdigit():
            removed += int(numbers[index + 1])
    return {"added": added, "removed": removed}


def score(ticket_id: str, run_verify: bool = True) -> dict:
    paths = changed_files()
    findings = predicate_findings(paths)
    by_rule: dict[str, list[dict]] = {}
    for item in findings:
        by_rule.setdefault(item["rule"], []).append(item)

    stray = out_of_scope(paths, ticket_scope(ticket_id))
    edits = edited_assertions()
    size = diff_size()

    results: dict[str, dict] = {}
    for code, rule, description in DECIDABLE:
        if rule == "scope.allowed-paths":
            evidence = [f"out of scope: {path}" for path in stray]
        elif rule == "tests.not-self-approving":
            evidence = [f"assertion removed: {item}" for item in edits]
        elif rule == "verify.green":
            if run_verify:
                green, tail = verify_green()
                evidence = [] if green else [tail]
            else:
                evidence = []
        else:
            evidence = [
                f"{item['file']}:{item['line']} {item['message']}"
                for item in by_rule.get(rule, [])
            ]
        results[code] = {
            "rule": rule,
            "description": description,
            "pass": not evidence,
            "evidence": evidence[:6],
            "count": len(evidence),
        }

    code, rule, description = INFERENTIAL
    results[code] = {
        "rule": rule,
        "description": description,
        "pass": None,
        "evidence": [],
        "count": 0,
        "note": "no predicate can settle this; a reviewer sub-agent fills it in",
    }

    passed = sum(1 for item in results.values() if item["pass"] is True)
    return {
        "ticket": ticket_id,
        "files_changed": len(paths),
        "lines_added": size["added"],
        "lines_removed": size["removed"],
        "checks": results,
        "decidable_passed": passed,
        "decidable_total": len(DECIDABLE),
        "files": paths,
    }


def render(card: dict) -> str:
    lines = [
        f"  ticket        {card['ticket']}",
        f"  files changed {card['files_changed']}",
        f"  lines         +{card['lines_added']} / -{card['lines_removed']}",
        "",
    ]
    for code, item in card["checks"].items():
        if item["pass"] is None:
            mark, tail = "  ?  ", "n/a — inferential"
        elif item["pass"]:
            mark, tail = " PASS", ""
        else:
            mark, tail = " FAIL", f"({item['count']})"
        lines.append(f"  {mark}  {code}  {item['rule']:<28} {tail}")
        for evidence in item["evidence"]:
            lines.append(f"            · {evidence}")
    lines.append("")
    lines.append(
        f"  {card['decidable_passed']}/{card['decidable_total']} decidable checks pass"
        "   ·   C9 needs a reader"
    )
    return "\n".join(lines)
