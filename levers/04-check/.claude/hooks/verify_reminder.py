#!/usr/bin/env python3
"""Stop hook: refuse to finish a turn on a tree that does not verify.

A gate that answers after the agent has moved on is a stale signal. This one
answers at the end of the turn, which is the last moment the feedback is still
cheap.

It runs `make verify` over what is actually on disk — never over the agent's
report of what is on disk. Verify from the tree, not from the transcript.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def main() -> int:
    try:
        event = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        event = {}

    if event.get("stop_hook_active"):
        return 0

    changed = subprocess.run(
        ["git", "diff", "--name-only", "HEAD"],
        cwd=ROOT, capture_output=True, text=True, check=False,
    ).stdout.split()
    if not changed:
        return 0

    result = subprocess.run(
        ["make", "verify"], cwd=ROOT, capture_output=True, text=True, check=False
    )
    if result.returncode == 0:
        return 0

    output = (result.stdout + result.stderr).strip().splitlines()
    print("`make verify` is not green on the tree you are leaving behind:",
          file=sys.stderr)
    print("\n".join(output[-25:]), file=sys.stderr)
    print("\nFix it, or say explicitly which failure you are leaving and why.",
          file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
