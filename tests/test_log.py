"""The session log. Append-only, and a correction is a new entry."""

import pytest

from tarrasque.domain.log import Entry, append, correct, replayable


def entry(sequence: int, kind: str = "check", **payload) -> Entry:
    return Entry(sequence, "enc_1", 1, kind, "usr_mira", payload)


class TestAppend:
    def test_appends_in_sequence(self):
        entries = append(append([], entry(1)), entry(2))
        assert [item.sequence for item in entries] == [1, 2]

    def test_refuses_a_gap(self):
        with pytest.raises(ValueError, match="log is at 1"):
            append(append([], entry(1)), entry(3))

    def test_refuses_a_replay_of_an_existing_sequence(self):
        with pytest.raises(ValueError):
            append(append([], entry(1)), entry(1))

    def test_the_first_entry_must_be_one(self):
        with pytest.raises(ValueError):
            append([], entry(7))


class TestCorrections:
    def test_a_correction_is_appended_not_applied(self):
        entries = append([], entry(1, damage=12))
        corrected = correct(entries, 1, "DM mistyped")
        assert len(corrected) == 2
        assert corrected[0].payload == {"damage": 12}
        assert corrected[1].kind == "correction"
        assert corrected[1].payload["retracts"] == 1

    def test_correcting_an_absent_entry_is_an_error(self):
        with pytest.raises(LookupError):
            correct(append([], entry(1)), 9, "nope")


class TestCanonicalForm:
    def test_is_stable_regardless_of_key_order(self):
        first = Entry(1, "e", 1, "k", "a", {"b": 1, "a": 2})
        second = Entry(1, "e", 1, "k", "a", {"a": 2, "b": 1})
        assert first.canonical() == second.canonical()


class TestReplayable:
    def test_a_log_whose_rolls_carry_seeds_is_replayable(self):
        entries = [entry(1, roll={"total": 14, "seed": "e:1:x", "notation": "1d20"})]
        assert replayable(entries)

    def test_a_bare_total_makes_the_log_unverifiable(self):
        assert not replayable([entry(1, roll={"total": 14})])
