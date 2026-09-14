#!/usr/bin/env python3
"""A zero-dependency test runner, for when pytest is not installed.

Discovers `test_*` functions and `Test*` classes under `tests/`, runs them,
and understands just enough of `pytest.raises`, `pytest.fixture`, and
`pytest.mark.parametrize` to run this repository's suite.

It exists so that nothing in the critical path of a ninety-minute workshop
depends on a download succeeding.
"""

from __future__ import annotations

import importlib.util
import inspect
import sys
import traceback
import types
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


class _Raises:
    def __init__(self, expected, match=None):
        self.expected, self.match = expected, match

    def __enter__(self):
        return self

    def __exit__(self, kind, value, tb):
        if kind is None:
            raise AssertionError(f"did not raise {self.expected}")
        if not issubclass(kind, self.expected):
            return False
        if self.match and self.match not in str(value):
            raise AssertionError(f"{value!r} does not match {self.match!r}")
        return True


def _stub_pytest() -> types.ModuleType:
    module = types.ModuleType("pytest")
    module.raises = _Raises

    def fixture(*args, **kwargs):
        def wrap(function):
            function.__is_fixture__ = True
            return function
        return wrap(args[0]) if args and callable(args[0]) else wrap

    def parametrize(names, values):
        def wrap(function):
            function.__params__ = (names, values)
            return function
        return wrap

    module.fixture = fixture
    module.mark = types.SimpleNamespace(parametrize=parametrize)
    module.skip = lambda *a, **k: None
    return module


def _load(path: Path) -> types.ModuleType:
    spec = importlib.util.spec_from_file_location(path.stem, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _fixtures(module: types.ModuleType) -> dict:
    return {
        name: value
        for name, value in vars(module).items()
        if callable(value) and getattr(value, "__is_fixture__", False)
    }


def _call(function, fixtures, instance=None) -> None:
    signature = inspect.signature(function)
    names = [n for n in signature.parameters if n != "self"]
    cases = [({},)]
    params = getattr(function, "__params__", None)
    if params:
        keys = [k.strip() for k in params[0].split(",")]
        cases = [
            (dict(zip(keys, row if isinstance(row, tuple) else (row,))),)
            for row in params[1]
        ]
    for (bound,) in cases:
        kwargs = dict(bound)
        for name in names:
            if name in kwargs:
                continue
            if name in fixtures:
                generated = fixtures[name]()
                kwargs[name] = (
                    next(generated) if inspect.isgenerator(generated) else generated
                )
        if instance is None:
            function(**kwargs)
        else:
            function(instance, **kwargs)


def main() -> int:
    sys.modules["pytest"] = _stub_pytest()
    sys.path.insert(0, str(ROOT))

    passed, failures = 0, []
    for path in sorted((ROOT / "tests").glob("test_*.py")):
        try:
            module = _load(path)
        except Exception:
            failures.append((path.name, traceback.format_exc()))
            continue
        fixtures = _fixtures(module)
        for name, value in sorted(vars(module).items()):
            targets = []
            if name.startswith("test_") and callable(value):
                targets = [(value, None)]
            elif name.startswith("Test") and inspect.isclass(value):
                targets = [
                    (method, value())
                    for method_name, method in sorted(vars(value).items())
                    if method_name.startswith("test_") and callable(method)
                ]
            for function, instance in targets:
                try:
                    _call(function, fixtures, instance)
                    passed += 1
                    print(".", end="", flush=True)
                except Exception:
                    failures.append(
                        (f"{path.name}::{name}", traceback.format_exc())
                    )
                    print("F", end="", flush=True)

    print()
    for where, trace in failures:
        print(f"\nFAILED {where}\n{trace}")
    print(f"{passed} passed, {len(failures)} failed  (bundled runner, no pytest)")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
