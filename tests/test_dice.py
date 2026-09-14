"""Dice notation, and the receipt every roll carries."""

import pytest

from tarrasque.domain.dice import (
    BadNotation,
    parse,
    roll,
    with_advantage,
    with_disadvantage,
)
from tarrasque.domain.rng import ScriptedRng, SeededRng


class TestParse:
    @pytest.mark.parametrize(
        "text,expected",
        [
            ("d20", "1d20"),
            ("2d6", "2d6"),
            ("1d8+3", "1d8+3"),
            ("2d6-1", "2d6-1"),
            ("4d6kh3", "4d6kh3"),
            ("2d20kl1", "2d20kl1"),
            (" 2 d 6 ", "2d6"),
        ],
    )
    def test_round_trips(self, text, expected):
        assert str(parse(text)) == expected

    @pytest.mark.parametrize(
        "text", ["", "d", "20", "d1", "0d6", "2d6kh9", "2d6kx1", "d20+", "1d1001"]
    )
    def test_refuses_what_it_cannot_parse(self, text):
        with pytest.raises(BadNotation):
            parse(text)

    def test_names_the_offending_notation(self):
        with pytest.raises(BadNotation, match="banana"):
            parse("banana")


class TestRoll:
    def test_keeps_the_highest(self):
        result = roll(ScriptedRng([1, 6, 3, 5]), "4d6kh3")
        assert result.kept == [6, 3, 5]
        assert result.dropped == [1]
        assert result.total == 14

    def test_keeps_the_lowest(self):
        result = roll(ScriptedRng([18, 4]), "2d20kl1")
        assert result.kept == [4]
        assert result.total == 4

    def test_applies_the_bonus_once_not_per_die(self):
        assert roll(ScriptedRng([2, 2]), "2d6+3").total == 7

    def test_keeps_duplicate_faces_apart(self):
        result = roll(ScriptedRng([5, 5, 5]), "3d6kh2")
        assert sorted(result.kept) == [5, 5]
        assert result.dropped == [5]

    def test_records_where_in_the_stream_it_started(self):
        rng = ScriptedRng([1, 2, 3, 4])
        roll(rng, "2d6")
        assert roll(rng, "2d6").stream_position == 2

    def test_is_natural_only_for_a_single_kept_die(self):
        assert roll(ScriptedRng([20]), "1d20").is_natural(20)
        assert not roll(ScriptedRng([20, 20]), "2d20").is_natural(20)

    def test_a_scripted_stream_refuses_an_impossible_face(self):
        with pytest.raises(ValueError):
            roll(ScriptedRng([21]), "1d20")


class TestReceipt:
    def test_the_wire_form_carries_the_evidence(self):
        payload = roll(SeededRng("fixed"), "2d6+1").to_dict()
        assert set(payload) == {
            "total", "notation", "seed", "stream_position",
            "faces", "kept", "dropped", "bonus",
        }
        assert payload["seed"] == "fixed"
        assert payload["notation"] == "2d6+1"

    def test_the_total_is_derivable_from_the_receipt(self):
        payload = roll(SeededRng("fixed"), "4d6kh3+2").to_dict()
        assert payload["total"] == sum(payload["kept"]) + payload["bonus"]


class TestAdvantage:
    def test_advantage_doubles_the_die_and_keeps_the_highest(self):
        assert with_advantage("1d20+5") == "2d20kh1+5"

    def test_disadvantage_keeps_the_lowest(self):
        assert with_disadvantage("1d20-1") == "2d20kl1-1"

    def test_advantage_needs_a_single_die(self):
        with pytest.raises(BadNotation):
            with_advantage("2d6")
