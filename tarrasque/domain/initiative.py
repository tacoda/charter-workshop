"""Turn order.

Ties break deterministically, which matters more than it sounds: two
creatures with the same initiative must land in the same order on a replay,
or the log stops reproducing. The tie-break ladder is initiative, then
dexterity, then a recorded tie-break roll, then the combatant id.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Sequence

from tarrasque.domain.dice import Roll, roll
from tarrasque.domain.rng import Rng


@dataclass(frozen=True, slots=True)
class Combatant:
    """One creature in an encounter."""

    combatant_id: str
    name: str
    is_player_character: bool
    dexterity_modifier: int
    initiative_modifier: int
    hit_points: int
    max_hit_points: int
    save_modifiers: dict[str, int]

    def is_down(self) -> bool:
        return self.hit_points <= 0

    def to_dict(self) -> dict[str, object]:
        return {
            "combatant_id": self.combatant_id,
            "name": self.name,
            "is_player_character": self.is_player_character,
            "hit_points": self.hit_points,
            "max_hit_points": self.max_hit_points,
        }


@dataclass(frozen=True, slots=True)
class InitiativeEntry:
    """A combatant's place in the order, with the roll that put them there."""

    combatant_id: str
    score: int
    dexterity_modifier: int
    tiebreak: int
    roll: Roll

    def to_dict(self) -> dict[str, object]:
        return {
            "combatant_id": self.combatant_id,
            "score": self.score,
            "roll": self.roll.to_dict(),
        }


def roll_initiative(
    rng: Rng, combatants: Sequence[Combatant]
) -> list[InitiativeEntry]:
    """Roll for every combatant and return them in turn order."""
    entries: list[InitiativeEntry] = []
    for combatant in combatants:
        result = roll(rng, f"1d20{combatant.initiative_modifier:+d}")
        entries.append(
            InitiativeEntry(
                combatant_id=combatant.combatant_id,
                score=result.total,
                dexterity_modifier=combatant.dexterity_modifier,
                tiebreak=rng.roll(20),
                roll=result,
            )
        )
    return order(entries)


def order(entries: Sequence[InitiativeEntry]) -> list[InitiativeEntry]:
    """Sort entries into turn order. Total, and stable across replays."""
    return sorted(
        entries,
        key=lambda entry: (
            -entry.score,
            -entry.dexterity_modifier,
            -entry.tiebreak,
            entry.combatant_id,
        ),
    )


def next_turn(
    entries: Sequence[InitiativeEntry], index: int, round_number: int
) -> tuple[int, int]:
    """Advance the turn pointer, rolling over into the next round."""
    if not entries:
        raise ValueError("an encounter with no combatants has no turns")
    if index + 1 < len(entries):
        return index + 1, round_number
    return 0, round_number + 1


def take_damage(combatant: Combatant, amount: int) -> Combatant:
    """Apply damage, floored at zero. Never raises the hit point total."""
    if amount < 0:
        raise ValueError("damage is not negative; use heal")
    return replace(combatant, hit_points=max(0, combatant.hit_points - amount))


def heal(combatant: Combatant, amount: int) -> Combatant:
    """Heal, capped at the maximum."""
    if amount < 0:
        raise ValueError("healing is not negative; use take_damage")
    return replace(
        combatant,
        hit_points=min(combatant.max_hit_points, combatant.hit_points + amount),
    )
