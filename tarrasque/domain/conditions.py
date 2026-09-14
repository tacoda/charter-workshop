"""Status effects: what they do, how long they last, and how they stack.

Pure data and pure functions. Nothing here rolls a die, reads a clock, or
touches a database; the caller supplies the encounter state and gets a new
one back.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
from typing import Mapping, Sequence


class Stacking(Enum):
    """What happens when a condition is applied to a creature that has it."""

    REFRESH = "refresh"   # take the longer of the two durations
    LEVELS = "levels"     # add a level, up to a cap (exhaustion)
    IGNORE = "ignore"     # already present; the second application does nothing


@dataclass(frozen=True, slots=True)
class ConditionKind:
    """The definition of a condition, not an instance of one."""

    name: str
    stacking: Stacking
    max_level: int = 1
    blocks_actions: bool = False
    grants_advantage_against: bool = False
    imposes_disadvantage_on_self: bool = False
    disadvantage_on_abilities: frozenset[str] = frozenset()
    grants_advantage_on_saves: bool = False
    advantage_on_abilities: frozenset[str] = frozenset()


CATALOG: Mapping[str, ConditionKind] = {
    kind.name: kind
    for kind in (
        ConditionKind("blinded", Stacking.IGNORE,
                      grants_advantage_against=True,
                      imposes_disadvantage_on_self=True),
        ConditionKind("charmed", Stacking.IGNORE),
        ConditionKind("frightened", Stacking.IGNORE,
                      imposes_disadvantage_on_self=True),
        ConditionKind("grappled", Stacking.IGNORE),
        ConditionKind("paralyzed", Stacking.IGNORE,
                      blocks_actions=True,
                      grants_advantage_against=True,
                      disadvantage_on_abilities=frozenset({"str", "dex"})),
        ConditionKind("poisoned", Stacking.IGNORE,
                      imposes_disadvantage_on_self=True),
        ConditionKind("prone", Stacking.IGNORE,
                      imposes_disadvantage_on_self=True),
        ConditionKind("restrained", Stacking.IGNORE,
                      grants_advantage_against=True,
                      disadvantage_on_abilities=frozenset({"dex"})),
        ConditionKind("stunned", Stacking.IGNORE,
                      blocks_actions=True,
                      grants_advantage_against=True,
                      disadvantage_on_abilities=frozenset({"str", "dex"})),
        ConditionKind("blessed", Stacking.REFRESH, grants_advantage_on_saves=True),
        ConditionKind("hasted", Stacking.REFRESH,
                      advantage_on_abilities=frozenset({"dex"})),
        ConditionKind("guided", Stacking.REFRESH, grants_advantage_on_saves=True),
        ConditionKind("exhaustion", Stacking.LEVELS, max_level=6,
                      imposes_disadvantage_on_self=True),
    )
}


class UnknownCondition(KeyError):
    """Raised for a condition name this service has no definition for."""


@dataclass(frozen=True, slots=True)
class Condition:
    """One condition, on one creature, for some number of rounds."""

    name: str
    rounds_remaining: int
    level: int = 1
    source: str = ""

    @property
    def kind(self) -> ConditionKind:
        try:
            return CATALOG[self.name]
        except KeyError as error:
            raise UnknownCondition(self.name) from error

    def to_dict(self) -> dict[str, object]:
        return {
            "name": self.name,
            "rounds_remaining": self.rounds_remaining,
            "level": self.level,
            "source": self.source,
        }


def apply_condition(
    active: Sequence[Condition], incoming: Condition
) -> list[Condition]:
    """Add `incoming` to `active`, honouring the condition's stacking rule."""
    kind = incoming.kind
    existing = next((item for item in active if item.name == incoming.name), None)
    if existing is None:
        return [*active, incoming]

    others = [item for item in active if item.name != incoming.name]
    if kind.stacking is Stacking.IGNORE:
        return [*others, existing]
    if kind.stacking is Stacking.REFRESH:
        longer = max(existing.rounds_remaining, incoming.rounds_remaining)
        return [*others, replace(existing, rounds_remaining=longer)]
    level = min(kind.max_level, existing.level + incoming.level)
    return [*others, replace(existing, level=level,
                             rounds_remaining=max(existing.rounds_remaining,
                                                  incoming.rounds_remaining))]


def tick(active: Sequence[Condition]) -> list[Condition]:
    """Advance one round. Conditions at zero rounds fall off."""
    advanced = [
        replace(item, rounds_remaining=item.rounds_remaining - 1)
        for item in active
        if item.rounds_remaining > 0
    ]
    return [item for item in advanced if item.rounds_remaining > 0]


def can_act(active: Sequence[Condition]) -> bool:
    """False when any active condition blocks taking actions."""
    return not any(item.kind.blocks_actions for item in active)


def saving_throw_advantage(active: Sequence[Condition], ability: str) -> int:
    """Net advantage for a save: +1 advantage, -1 disadvantage, 0 neither.

    Advantage and disadvantage cancel, they do not stack. One source of each
    is the same as ten of each.
    """
    has_advantage = any(
        item.kind.grants_advantage_on_saves
        or ability in item.kind.advantage_on_abilities
        for item in active
    )
    has_disadvantage = any(
        item.kind.imposes_disadvantage_on_self
        or ability in item.kind.disadvantage_on_abilities
        for item in active
    )
    if has_advantage and has_disadvantage:
        return 0
    if has_disadvantage:
        return -1
    return 1 if has_advantage else 0


def auto_fails(active: Sequence[Condition], ability: str) -> bool:
    """True when a condition makes this save fail without a roll."""
    return any(
        item.kind.blocks_actions and ability in item.kind.disadvantage_on_abilities
        for item in active
    )
