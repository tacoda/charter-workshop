"""Turn order, and the tie-breaks that keep a replay stable."""

import pytest

from tarrasque.domain.dice import roll
from tarrasque.domain.initiative import (
    Combatant,
    InitiativeEntry,
    heal,
    next_turn,
    order,
    roll_initiative,
    take_damage,
)
from tarrasque.domain.rng import ScriptedRng, SeededRng


def combatant(cid: str, dex: int = 0, hp: int = 20) -> Combatant:
    return Combatant(cid, cid.title(), True, dex, dex, hp, 20, {"dex": dex})


def entry(cid: str, score: int, dex: int = 0, tiebreak: int = 0) -> InitiativeEntry:
    return InitiativeEntry(cid, score, dex, tiebreak, roll(ScriptedRng([1]), "1d20"))


class TestOrder:
    def test_highest_score_goes_first(self):
        result = order([entry("a", 8), entry("b", 19), entry("c", 12)])
        assert [item.combatant_id for item in result] == ["b", "c", "a"]

    def test_dexterity_breaks_a_tied_score(self):
        result = order([entry("a", 15, dex=1), entry("b", 15, dex=4)])
        assert [item.combatant_id for item in result] == ["b", "a"]

    def test_the_recorded_tiebreak_breaks_a_tied_dexterity(self):
        result = order([entry("a", 15, 2, tiebreak=3), entry("b", 15, 2, tiebreak=17)])
        assert [item.combatant_id for item in result] == ["b", "a"]

    def test_the_combatant_id_is_the_last_resort(self):
        result = order([entry("zeta", 10, 0, 5), entry("alpha", 10, 0, 5)])
        assert [item.combatant_id for item in result] == ["alpha", "zeta"]

    def test_the_order_is_total_so_a_replay_reproduces_it(self):
        entries = [entry("a", 10, 0, 5), entry("b", 10, 0, 5), entry("c", 10, 0, 5)]
        assert order(entries) == order(list(reversed(entries)))


class TestRollInitiative:
    def test_rolls_once_per_combatant_plus_a_tiebreak(self):
        rng = SeededRng("enc:1:initiative")
        result = roll_initiative(rng, [combatant("a"), combatant("b")])
        assert len(result) == 2
        assert rng.position == 4  # two d20s, two tie-breaks

    def test_is_reproducible_from_the_seed(self):
        crew = [combatant("a", 2), combatant("b", 3)]
        first = roll_initiative(SeededRng("enc:1:initiative"), crew)
        second = roll_initiative(SeededRng("enc:1:initiative"), crew)
        assert [item.score for item in first] == [item.score for item in second]

    def test_every_entry_carries_the_roll_that_made_it(self):
        result = roll_initiative(SeededRng("s"), [combatant("a", 3)])
        assert result[0].roll.notation == "1d20+3"
        assert result[0].roll.total == result[0].score


class TestTurns:
    def test_advances_within_a_round(self):
        assert next_turn([entry("a", 1), entry("b", 1)], 0, 3) == (1, 3)

    def test_rolls_over_into_the_next_round(self):
        assert next_turn([entry("a", 1), entry("b", 1)], 1, 3) == (0, 4)

    def test_an_empty_order_has_no_turns(self):
        with pytest.raises(ValueError):
            next_turn([], 0, 1)


class TestHitPoints:
    def test_damage_floors_at_zero(self):
        assert take_damage(combatant("a", hp=5), 99).hit_points == 0

    def test_healing_caps_at_the_maximum(self):
        assert heal(combatant("a", hp=5), 99).hit_points == 20

    def test_negative_damage_is_refused(self):
        with pytest.raises(ValueError):
            take_damage(combatant("a"), -1)

    def test_negative_healing_is_refused(self):
        with pytest.raises(ValueError):
            heal(combatant("a"), -1)
