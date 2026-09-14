# Setup — do this before you arrive

Two minutes on a laptop with Python 3.11+ and git. Nothing downloads during the
workshop itself, so please run this on a network you trust rather than the
conference wifi.

## 1 · Clone and check

    git clone <this repo>
    cd charter-workshop
    make doctor

You want every line to say `ok` except possibly `ruff` and `mypy`, which are
optional. `note` is fine. `fail` is not — bring it to a facilitator in the
first five minutes.

## 2 · Bring an agent you already use

Claude Code, Cursor, Codex, Aider — whichever you reach for daily. The workshop
names Claude Code's file paths (`CLAUDE.md`, `.claude/`) because it has to name
*some* tool's. Every idea maps; the facilitator will call out the differences
for Cursor and Codex as they come up.

Make sure it works in this directory before you arrive.

## 3 · If your laptop fails anyway

You will still be able to do the whole workshop. `runs/reference/` ships five
captured runs, and `make reference` prints the matrix from them without
invoking a model. You will read results instead of producing them, which is
worse, but it is not nothing.

## 4 · Optional: the full toolchain

    make setup
    source .venv/bin/activate

This installs `pytest`, `ruff` and `mypy` into a local venv. Everything works
without it — `make test`, `make lint` and `make gate` all fall back to bundled
standard-library equivalents.

## What you do not need

No API keys beyond whatever your agent already uses. No Docker. No database.
No network access during the session.
