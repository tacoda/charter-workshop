"""The seeded stream. The whole replay story rests on this file."""

import pytest

from tarrasque.domain.rng import ScriptedRng, SeededRng, stream_for


def test_the_same_seed_produces_the_same_sequence():
    first = SeededRng("ashfall:3:breath")
    second = SeededRng("ashfall:3:breath")
    assert [first.roll(20) for _ in range(20)] == [
        second.roll(20) for _ in range(20)
    ]


def test_different_seeds_diverge():
    first = [SeededRng("a").roll(20) for _ in range(10)]
    second = [SeededRng("b").roll(20) for _ in range(10)]
    assert first != second


def test_results_stay_in_range():
    rng = SeededRng("range")
    assert all(1 <= rng.roll(6) <= 6 for _ in range(500))


def test_position_counts_every_draw():
    rng = SeededRng("count")
    for _ in range(7):
        rng.roll(20)
    assert rng.position == 7


def test_a_one_sided_die_is_refused():
    with pytest.raises(ValueError):
        SeededRng("x").roll(1)


def test_the_stream_is_addressed_by_where_the_encounter_is():
    assert stream_for("enc_1", 3, "breath").seed == "enc_1:3:breath"
    assert stream_for("enc_1", 3).seed == "enc_1:3:"


def test_a_scripted_stream_runs_out_loudly():
    rng = ScriptedRng([4])
    rng.roll(6)
    with pytest.raises(IndexError):
        rng.roll(6)
