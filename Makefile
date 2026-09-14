# tarrasque — the task runner is the unit of intent.
#
# The permission allowlist in .claude/settings.json names targets here, not
# command strings. That is the whole reason this file is the interface: a
# target is a piece of work somebody decided on, and a command string is a
# guess about what that work looks like today.
#
#   make help        what all of this does
#   make verify      lint + types + tests + the charter gate   (< 30s)
#   make ticket      print the ticket you are working
#   make score       score the working tree against the charter
#   make compare     the matrix

PYTHON  ?= python3
TICKET  ?= TAR-412
RUN     ?= scratch
PKG     := tarrasque

# Files the gate looks at: what differs from HEAD, plus anything untracked.
CHANGED := $(shell git diff --name-only HEAD -- '*.py' 2>/dev/null; \
                   git ls-files --others --exclude-standard -- '*.py' 2>/dev/null)

.DEFAULT_GOAL := help
.PHONY: help setup test lint types gate gate-all verify serve seed \
        ticket tickets score capture compare lever levers reset \
        audit grants promote doctor clean

help:  ## what all of this does
	@grep -hE '^[a-z-]+:.*?##' $(MAKEFILE_LIST) \
	 | sed 's/:.*##/@/' | awk -F@ '{printf "  \033[1m%-12s\033[0m %s\n", $$1, $$2}'

# ---------------------------------------------------------------- toolchain

setup:  ## install the dev toolchain into a venv (optional; nothing needs it)
	$(PYTHON) -m venv .venv
	.venv/bin/pip install -q -e '.[dev]'
	@echo "  activate with: source .venv/bin/activate"

test:  ## run the test suite (pytest, or the bundled runner if absent)
	@if command -v pytest >/dev/null 2>&1; then \
	   pytest -q; \
	 else \
	   echo "  pytest not found — bundled runner"; \
	   $(PYTHON) bin/fallback_test.py; \
	 fi

lint:  ## ruff over the package, or a bundled style check if absent
	@if command -v ruff >/dev/null 2>&1; then \
	   ruff check $(PKG) tests tools bin; \
	 else \
	   echo "  ruff not found — compileall only"; \
	   $(PYTHON) -m compileall -q $(PKG) tests tools >/dev/null; \
	 fi

types:  ## mypy --strict over the package (skipped when mypy is absent)
	@if command -v mypy >/dev/null 2>&1; then \
	   mypy; \
	 else \
	   echo "  mypy not found — skipped"; \
	 fi

gate:  ## the charter's decidable rules over what this change added  (< 1s, stdlib)
	@$(PYTHON) bin/gate

gate-all:  ## the same rules over the whole tree — shows the seed's own debt
	@$(PYTHON) bin/gate --all || true

verify:  ## lint + types + tests + gate. The one command CLAUDE.md names.
	@$(MAKE) --no-print-directory lint
	@$(MAKE) --no-print-directory types
	@$(MAKE) --no-print-directory test
	@$(MAKE) --no-print-directory gate
	@echo "  verify: green"

# ------------------------------------------------------------------ the app

serve:  ## run the service on :8099 against seeded in-memory data
	$(PYTHON) -m $(PKG)

seed:  ## print what the seed database contains
	@$(PYTHON) -c "from tarrasque import seed; \
	c=seed.build(); \
	print('tables     ', [r['table_id'] for r in c.execute('SELECT * FROM tables')]); \
	print('characters ', [r['character_id'] for r in c.execute('SELECT * FROM characters')]); \
	print('encounters ', [r['encounter_id'] for r in c.execute('SELECT * FROM encounters')]); \
	print('keys       ', 'tk_live_mira_0001 (dm) · tk_live_jonah_001 · tk_live_pilar_001')"

# -------------------------------------------------------------- the workshop

ticket:  ## print the ticket named by TICKET= (default TAR-412)
	@cat tickets/$(TICKET)*.md

tickets:  ## list every ticket with its size and the rules it touches
	@for f in tickets/*.md; do \
	   printf "  %-12s %-9s %s\n" \
	     "$$(grep -m1 '^id:' $$f | cut -d' ' -f2)" \
	     "$$(grep -m1 '^size:' $$f | cut -d' ' -f2)" \
	     "$$(grep -m1 '^title:' $$f | cut -d' ' -f2-)"; \
	 done

score:  ## score the working tree against the charter
	@$(PYTHON) bin/score --ticket $(TICKET)

capture:  ## freeze a run: make capture RUN=00-baseline
	@$(PYTHON) bin/capture $(RUN) --ticket $(TICKET)

compare:  ## the matrix across every captured run
	@$(PYTHON) bin/compare

reference:  ## the matrix across the runs shipped with the repo
	@$(PYTHON) bin/compare --reference

levers:  ## what is installed, and what is available
	@$(PYTHON) bin/lever status

lever:  ## apply a lever: make lever N=2
	@$(PYTHON) bin/lever apply $(N)

reset:  ## remove the whole charter and start from bare
	@$(PYTHON) bin/lever reset

audit:  ## the retrofit audit — find the signals in this repo that lie
	@$(PYTHON) bin/audit

grants:  ## audit what the permission list actually grants
	@$(PYTHON) bin/grants

promote:  ## which rules have earned the next rung, and where that rung is
	@$(PYTHON) bin/promote

doctor:  ## check this machine can run the workshop
	@$(PYTHON) bin/doctor

clean:  ## remove caches
	@rm -rf .pytest_cache .ruff_cache .mypy_cache
	@find . -name __pycache__ -type d -prune -exec rm -rf {} +
