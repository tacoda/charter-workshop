#!/usr/bin/env python3
"""PreToolUse hook: refuse a write that violates a decidable charter rule.

The rule implementation is not here. It is `tools/charter_check.py`, and this file
is a mount: it takes the content the agent is *about* to write, hands it to
the predicate as `{files: [{filename, source}]}`, and turns the verdict into
an exit code.

That separation is the point of the shape. The same forty lines run as this
hook, as `make gate`, as the scorer's decidable half, and — if this rule ever
earns the crossing — at a rung above the charter, unchanged.

Exit 0 lets the write through. Exit 2 blocks it and returns stderr to the
agent, inside the turn, before it has moved on.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from tools.charter_check import check, render  # noqa: E402


def content_of(tool_input: dict) -> str | None:
    """The text this call is about to put on disk, whichever tool it is."""
    if "content" in tool_input:
        return str(tool_input["content"])
    if "new_string" in tool_input:
        return str(tool_input["new_string"])
    if "edits" in tool_input:
        return "\n".join(str(edit.get("new_string", "")) for edit in tool_input["edits"])
    return None


def main() -> int:
    try:
        event = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return 0

    tool_input = event.get("tool_input", {})
    path = tool_input.get("file_path") or tool_input.get("path") or ""
    source = content_of(tool_input)
    if not path or source is None:
        return 0

    try:
        relative = str(Path(path).resolve().relative_to(ROOT))
    except ValueError:
        relative = path

    verdict = check({"files": [{"filename": relative, "source": source}]})
    if verdict["clean"]:
        return 0

    print(render(verdict["problems"]), file=sys.stderr)
    print(
        "\nThis write was refused by .claude/hooks/charter_gate.py before it "
        "reached disk.\nEach line names the rule and the escape marker that "
        "exempts it. If the\nexemption is right, add the marker with a reason. "
        "If it is not, fix the code.\nThe rules are in .claude/rules/ and the "
        "predicate is tools/charter_check.py.",
        file=sys.stderr,
    )
    return 2


if __name__ == "__main__":
    sys.exit(main())
