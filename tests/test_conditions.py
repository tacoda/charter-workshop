"""Status effects: stacking, duration, and what they do to a save."""

import pytest

from tarrasque.domain.conditions import (
    Condition,
    UnknownCondition,
    apply_condition,
    auto_fails,
    can_act,
    saving_throw_advantage,
    tick,
)


class TestStacking:
    def test_ignore_keeps_the_first_application(self):
        active = apply_condition([Condition("prone", 3)], Condition("prone", 99))
        assert active[0].rounds_remaining == 3

    def test_refresh_takes_the_longer_duration(self):
        active = apply_condition([Condition("blessed", 2)], Condition("blessed", 9))
        assert active[0].rounds_remaining == 9

    def test_refresh_does_not_shorten(self):
        active = apply_condition([Condition("blessed", 9)], Condition("blessed", 2))
        assert active[0].rounds_remaining == 9

    def test_levels_accumulate_to_a_cap(self):
        active = [Condition("exhaustion", 10, level=5)]
        active = apply_condition(active, Condition("exhaustion", 10, level=3))
        assert active[0].level == 6

    def test_a_new_condition_is_appended(self):
        active = apply_condition([Condition("prone", 1)], Condition("blinded", 2))
        assert {item.name for item in active} == {"prone", "blinded"}

    def test_an_unknown_condition_is_refused(self):
        with pytest.raises(UnknownCondition):
            apply_condition([], Condition("bewildered", 1))


class TestDuration:
    def test_tick_counts_down(self):
        assert tick([Condition("blessed", 3)])[0].rounds_remaining == 2

    def test_a_condition_at_one_round_falls_off(self):
        assert tick([Condition("blessed", 1)]) == []

    def test_ticking_an_empty_list_is_fine(self):
        assert tick([]) == []


class TestEffects:
    def test_stunned_blocks_actions(self):
        assert not can_act([Condition("stunned", 1)])

    def test_prone_does_not_block_actions(self):
        assert can_act([Condition("prone", 1)])

    def test_poisoned_imposes_disadvantage(self):
        assert saving_throw_advantage([Condition("poisoned", 1)], "wis") == -1

    def test_blessed_grants_advantage(self):
        assert saving_throw_advantage([Condition("blessed", 1)], "wis") == 1

    def test_advantage_and_disadvantage_cancel_rather_than_stacking(self):
        active = [Condition("blessed", 1), Condition("poisoned", 1)]
        assert saving_throw_advantage(active, "wis") == 0

    def test_restrained_is_disadvantage_on_dexterity_only(self):
        assert saving_throw_advantage([Condition("restrained", 1)], "dex") == -1
        assert saving_throw_advantage([Condition("restrained", 1)], "wis") == 0

    def test_hasted_is_advantage_on_dexterity_only(self):
        assert saving_throw_advantage([Condition("hasted", 1)], "dex") == 1
        assert saving_throw_advantage([Condition("hasted", 1)], "wis") == 0

    def test_paralysis_fails_strength_and_dexterity_saves_outright(self):
        assert auto_fails([Condition("paralyzed", 1)], "dex")
        assert not auto_fails([Condition("paralyzed", 1)], "wis")
