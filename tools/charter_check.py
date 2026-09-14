#!/usr/bin/env python3
"""The charter's decidable rules, as one predicate.

    check({"files": [{"filename": "...", "source": "..."}]}) -> {"clean", "problems"}

One implementation, several mount points. It runs as a `PreToolUse` hook, as
the `make gate` target, as a bundled script beside a skill, and as the
deterministic half of the scorer. It would run unchanged at any rung above
the charter, which is the point of the shape.

Two constraints on this file are deliberate and load-bearing:

  * **No imports from `tarrasque`.** The moment this imports the project it can
    only run where the project is installed, and every mount outside the repo
    stops working.
  * **It never opens a file.** Sources arrive as strings, so the same rules run
    over a diff, over a staged tool call, or over a payload from a machine
    with no shared filesystem.

Every refusal names its escape. A guardrail with no sanctioned path produces
creative circumvention; a marked exemption produces a number you can count.
Watch the markers: a spike says the rule is wrong, not that the agent is.
"""

from __future__ import annotations

import ast
import json
import re
import sys
from typing import Any

ESCAPE = re.compile(
    r"#\s*(?P<rule>[a-z-]+)-gate:\s*allow\b(?:\s*[-—]\s*(?P<why>.+))?"
)

#: The one module permitted to reach the standard library's `random`.
RNG_MODULE = "tarrasque/domain/rng.py"

#: Paths the charter does not govern. Frozen legacy, tests, and this file.
OUT_OF_SCOPE = ("tarrasque/legacy/", "tests/", "tools/", "levers/", "bin/")

#: Keys that name an outcome and therefore need provenance beside them.
OUTCOME_KEY = re.compile(r"^(?:total|result|score|roll|outcome)$")

#: Identities a caller must never be allowed to assert for themselves.
ASSERTED_IDENTITY = {
    "character_id", "actor_id", "acting_as", "as_character",
    "user_id", "owner_user_id", "table_id", "combatant_id",
}

#: Names that hold caller-supplied input.
CALLER_INPUT = re.compile(r"^(?:body|payload|params|request|data|json_body)$")

#: Writes the session log is not allowed to take.
LOG_MUTATION = re.compile(
    r"\b(?:UPDATE\s+session_log|DELETE\s+FROM\s+session_log)\b", re.I
)
LOG_MUTATORS = {"update_log_payload", "delete_log_from"}


def _exempt(lines: list[str], node: ast.AST, rule: str) -> bool:
    """True when the node's own line carries `# <rule>-gate: allow`."""
    index = getattr(node, "lineno", 0) - 1
    if not 0 <= index < len(lines):
        return False
    found = ESCAPE.search(lines[index])
    return bool(found and found.group("rule") == rule)


def _through_receipt(value: ast.AST) -> bool:
    """True when a serialized value already went through `.to_dict()`."""
    if isinstance(value, ast.Call) and isinstance(value.func, ast.Attribute):
        return value.func.attr == "to_dict"
    return isinstance(value, (ast.ListComp, ast.List, ast.DictComp))


def _problem(filename: str, node: ast.AST, rule: str, message: str) -> dict[str, Any]:
    return {
        "file": filename,
        "line": getattr(node, "lineno", 0),
        "rule": rule,
        "message": message,
        "escape": f"# {rule.split('.')[0]}-gate: allow - <reason>",
    }


def _string_key(node: ast.AST) -> str | None:
    return node.value if isinstance(node, ast.Constant) and isinstance(node.value, str) else None


def check_source(filename: str, source: str) -> list[dict[str, Any]]:
    """Run every decidable rule over one file's source."""
    if not filename.endswith(".py") or filename.startswith(OUT_OF_SCOPE):
        return []
    try:
        tree = ast.parse(source)
    except SyntaxError as error:
        return [{
            "file": filename, "line": error.lineno or 0, "rule": "syntax",
            "message": f"will not parse: {error.msg}", "escape": "",
        }]

    lines = source.splitlines()
    problems: list[dict[str, Any]] = []
    is_rng_module = filename.endswith(RNG_MODULE)

    for node in ast.walk(tree):

        # -- dice.seeded ------------------------------------------------
        if not is_rng_module:
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name.split(".")[0] == "random" and not _exempt(
                        lines, node, "seeded"
                    ):
                        problems.append(_problem(
                            filename, node, "dice.seeded",
                            "imports `random`; every die comes from an Rng "
                            f"stream opened in {RNG_MODULE}"))
            if isinstance(node, ast.ImportFrom) and (node.module or "").startswith(
                "random"
            ):
                if not _exempt(lines, node, "seeded"):
                    problems.append(_problem(
                        filename, node, "dice.seeded",
                        "imports from `random`; use an injected Rng"))
            if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name):
                if node.value.id == "random" and not _exempt(lines, node, "seeded"):
                    problems.append(_problem(
                        filename, node, "dice.seeded",
                        f"random.{node.attr}(); an unseeded roll cannot be "
                        "replayed from the log"))

        # -- legacy.frozen ----------------------------------------------
        if isinstance(node, ast.ImportFrom):
            module = node.module or ""
            if "tarrasque.legacy" in module and not _exempt(lines, node, "legacy"):
                problems.append(_problem(
                    filename, node, "legacy.frozen",
                    "imports tarrasque.legacy; the 2021 tables are frozen and "
                    "roll unseeded dice"))
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.startswith("tarrasque.legacy") and not _exempt(
                    lines, node, "legacy"
                ):
                    problems.append(_problem(
                        filename, node, "legacy.frozen",
                        "imports tarrasque.legacy; the 2021 tables are frozen"))

        # -- roll.provenance --------------------------------------------
        if isinstance(node, ast.Dict):
            named = {
                key: value
                for key, value in zip(
                    (_string_key(k) for k in node.keys), node.values
                )
                if key is not None
            }
            bare = sorted(
                key for key, value in named.items()
                if OUTCOME_KEY.match(key) and not _through_receipt(value)
            )
            inline = {"notation", "seed"} <= set(named)
            sibling = any(_through_receipt(value) for value in named.values())
            if bare and not (inline or sibling) and not _exempt(
                lines, node, "provenance"
            ):
                problems.append(_problem(
                    filename, node, "roll.provenance",
                    f"serializes {bare} with no notation or seed; a bare number "
                    "settles no argument — use Roll.to_dict()"))

        # -- log.append-only --------------------------------------------
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            if LOG_MUTATION.search(node.value) and not _exempt(lines, node, "log"):
                problems.append(_problem(
                    filename, node, "log.append-only",
                    "mutates session_log; a correction is a new entry, never "
                    "an edit"))
        if isinstance(node, ast.Call):
            called = (
                node.func.id if isinstance(node.func, ast.Name)
                else node.func.attr if isinstance(node.func, ast.Attribute)
                else ""
            )
            if called in LOG_MUTATORS and not _exempt(lines, node, "log"):
                problems.append(_problem(
                    filename, node, "log.append-only",
                    f"{called}() rewrites history; append a correction entry"))

        # -- authority.session-derived (the decidable shadow) -----------
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            if node.func.attr == "get" and isinstance(node.func.value, ast.Name):
                if CALLER_INPUT.match(node.func.value.id) and node.args:
                    key = _string_key(node.args[0])
                    if key in ASSERTED_IDENTITY and not _exempt(
                        lines, node, "authority"
                    ):
                        problems.append(_problem(
                            filename, node, "authority.session-derived",
                            f"reads {key!r} from caller input; authority comes "
                            "from the session, never from the request"))
        if isinstance(node, ast.Subscript) and isinstance(node.value, ast.Name):
            if CALLER_INPUT.match(node.value.id):
                key = _string_key(node.slice)
                if key in ASSERTED_IDENTITY and not _exempt(lines, node, "authority"):
                    problems.append(_problem(
                        filename, node, "authority.session-derived",
                        f"reads {key!r} from caller input; authority comes from "
                        "the session, never from the request"))

    unique: dict[tuple[Any, ...], dict[str, Any]] = {}
    for item in problems:
        unique[(item["file"], item["line"], item["rule"], item["message"])] = item
    return sorted(
        unique.values(), key=lambda item: (item["file"], item["line"], item["rule"])
    )


def check(payload: dict[str, Any]) -> dict[str, Any]:
    """The mountable entry point. Takes files, returns a verdict."""
    problems: list[dict[str, Any]] = []
    for item in payload.get("files", []):
        problems.extend(
            check_source(item.get("filename", "?"), item.get("source", ""))
        )
    return {"clean": not problems, "problems": problems}


def render(problems: list[dict[str, Any]]) -> str:
    """One line per error, location first, rule in brackets. Silent on success."""
    return "\n".join(
        f"{item['file']}:{item['line']}: [{item['rule']}] {item['message']}"
        for item in problems
    )


def main(argv: list[str]) -> int:
    """CLI mount: paths as arguments, or a JSON payload on stdin."""
    if argv:
        files = []
        for path in argv:
            try:
                with open(path, encoding="utf-8") as handle:
                    files.append({"filename": path, "source": handle.read()})
            except OSError as error:
                print(f"{path}: {error}", file=sys.stderr)
                return 2
        payload: dict[str, Any] = {"files": files}
    else:
        payload = json.loads(sys.stdin.read() or '{"files": []}')

    verdict = check(payload)
    if verdict["clean"]:
        return 0
    print(render(verdict["problems"]))
    print(
        f"\n{len(verdict['problems'])} finding(s). Each line names its escape; "
        "see tools/charter_check.py."
    )
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
