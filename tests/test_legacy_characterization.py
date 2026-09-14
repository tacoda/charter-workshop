"""Characterization tests for the 2021 random tables.

These do not assert what the code *should* do. They pin what it *currently*
does, so that any change to observable behaviour turns them red.

`tarrasque/legacy/tables.py` is frozen. Four campaigns' worth of session
transcripts were produced against exactly this arithmetic, including the crit
range and the module-level draw memory. That is not the behaviour the rest of
the service wants and it is not a thing to fix in passing.

If a ticket genuinely requires changing this behaviour, the ticket says so and
these tests change in the same commit. Otherwise they stay exactly as they are.
"""

import random

import pytest

from tarrasque.legacy import tables


@pytest.fixture(autouse=True)
def fixed_stream():
    """Pin the global stream so the frozen behaviour is observable at all."""
    state = random.getstate()
    random.seed(20210714)
    tables.reset_session()
    yield
    random.setstate(state)


def test_a_crit_is_a_natural_twenty_only():
    assert tables.CRIT_RANGE == 20


def test_the_draw_memory_is_module_level_and_survives_calls():
    first = tables.roll_loot()
    second = tables.roll_loot()
    assert first != second
    assert len(tables._drawn) == 2


def test_the_draw_memory_resets_when_the_table_is_exhausted():
    drawn = [tables.roll_loot() for _ in range(len(tables.LOOT) + 1)]
    assert len(set(drawn)) == len(tables.LOOT)


def test_reset_session_clears_the_memory():
    tables.roll_loot()
    tables.reset_session()
    assert tables._drawn == []


def test_rolls_are_drawn_from_the_global_stream_not_an_injected_one():
    """The whole reason this module is frozen. Two calls, no seed in sight."""
    random.seed(1)
    first = tables.d(20)
    random.seed(1)
    second = tables.d(20)
    assert first == second  # only because the caller reseeded the world

    third = tables.d(20)
    assert tables.d.__code__.co_names == ("random", "randint")
    assert isinstance(third, int)


def test_format_result_returns_a_bare_number():
    assert tables.format_result(17) == 17


def test_advantage_keeps_the_better_of_two_draws():
    random.seed(7)
    expected = max(random.randint(1, 20), random.randint(1, 20)) + 2
    random.seed(7)
    assert tables.advantage(2) == expected
