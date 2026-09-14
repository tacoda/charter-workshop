#!/usr/bin/env python3
"""Confirm a new v2 route is wired correctly. Deterministic; run, do not read.

Checks, for every route in `V2_ROUTES`:

  * the pattern parses and its parameters have distinct names
  * the handler's signature accepts (connection, session, *path_params)
  * no two routes shadow each other
  * the handler lives in tarrasque/api/encounters.py, not in the v1 god file

Exit 0 and say nothing when everything is wired. One line per problem
otherwise.
"""

from __future__ import annotations

import inspect
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))

from tarrasque.http import V1_ROUTES, V2_ROUTES, match  # noqa: E402

problems: list[str] = []
seen: dict[tuple[str, int], list[str]] = {}

for method, pattern, handler in V2_ROUTES:
    parameters = [
        part[1:] for part in pattern.strip("/").split("/") if part.startswith(":")
    ]
    if len(parameters) != len(set(parameters)):
        problems.append(f"{pattern}: duplicate path parameter name")

    signature = inspect.signature(handler)
    expected = 2 + len(parameters)
    actual = len(signature.parameters)
    if actual != expected:
        problems.append(
            f"{pattern}: {handler.__name__}{signature} takes {actual} argument(s); "
            f"the dispatcher passes {expected} "
            f"(connection, session, {', '.join(parameters) or 'no path params'})"
        )

    module = getattr(handler, "__module__", "")
    if not module.endswith("api.encounters"):
        problems.append(
            f"{pattern}: {handler.__name__} lives in {module}; v2 handlers go in "
            "tarrasque/api/encounters.py"
        )

    shape = (method, len(pattern.strip("/").split("/")))
    for other in seen.get(shape, []):
        sample = "/".join(
            "x" if part.startswith(":") else part
            for part in pattern.strip("/").split("/")
        )
        if match(other, "/" + sample) is not None and other != pattern:
            problems.append(f"{pattern}: shadowed by {other}")
    seen.setdefault(shape, []).append(pattern)

for method, pattern, handler in V1_ROUTES:
    if getattr(handler, "__module__", "").endswith("api.encounters"):
        problems.append(
            f"{pattern}: a v2 handler is registered on the v1 table, so it will "
            "run without a session"
        )

for problem in problems:
    print(f"  {problem}")
print(
    f"  {len(problems)} problem(s) across {len(V2_ROUTES)} v2 route(s)."
    if problems
    else "",
    end="",
)
sys.exit(1 if problems else 0)
