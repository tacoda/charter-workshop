"""Encounter state, and the transitions that move it.

An `Encounter` is immutable. Every transition returns a new one alongside the
log entries it produced, so a caller can persist both in one step and a
replay can rebuild the state from the entries alone.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Mapping, Sequence

from tarrasque.domain.conditions import Condition, can_act, tick
from tarrasque.domain.initiative import Combatant, InitiativeEntry, next_turn
from tarrasque.domain.log import Entry


class EncounterEnded(RuntimeError):
    """Raised when a transition is attempted on an encounter that is over."""


@dataclass(frozen=True, slots=True)
class Encounter:
    """One running combat, at one point in time."""

    encounter_id: str
    table_id: str
    status: str
    round_number: int
    turn_index: int
    combatants: Mapping[str, Combatant]
    order: Sequence[InitiativeEntry]
    conditions: Mapping[str, Sequence[Condition]]
    next_sequence: int

    # -- queries ------------------------------------------------------

    def is_running(self) -> bool:
        return self.status == "running"

    def active_combatant_id(self) -> str:
        if not self.order:
            raise ValueError("no initiative order has been rolled")
        return self.order[self.turn_index].combatant_id

    def conditions_on(self, combatant_id: str) -> Sequence[Condition]:
        return self.conditions.get(combatant_id, ())

    def may_act(self, combatant_id: str) -> bool:
        return can_act(self.conditions_on(combatant_id))

    def living(self) -> list[Combatant]:
        return [c for c in self.combatants.values() if not c.is_down()]

    def party(self) -> list[Combatant]:
        return [c for c in self.combatants.values() if c.is_player_character]

    def to_dict(self) -> dict[str, object]:
        return {
            "encounter_id": self.encounter_id,
            "table_id": self.table_id,
            "status": self.status,
            "round": self.round_number,
            "active": self.active_combatant_id() if self.order else None,
            "combatants": [c.to_dict() for c in self.combatants.values()],
            "conditions": {
                combatant_id: [item.to_dict() for item in items]
                for combatant_id, items in self.conditions.items()
                if items
            },
        }

    # -- transitions --------------------------------------------------

    def entry(self, kind: str, actor: str, payload: dict[str, object]) -> Entry:
        """Mint the next log entry for this encounter."""
        return Entry(
            sequence=self.next_sequence,
            encounter_id=self.encounter_id,
            round_number=self.round_number,
            kind=kind,
            actor=actor,
            payload=payload,
        )


def advance_turn(encounter: Encounter) -> tuple[Encounter, list[Entry]]:
    """Move to the next combatant, ticking conditions at the round boundary."""
    if not encounter.is_running():
        raise EncounterEnded(f"{encounter.encounter_id} is {encounter.status}")

    index, round_number = next_turn(
        encounter.order, encounter.turn_index, encounter.round_number
    )
    entries = [encounter.entry("turn_ended", encounter.active_combatant_id(), {})]

    conditions = dict(encounter.conditions)
    if round_number != encounter.round_number:
        conditions = {key: tick(value) for key, value in conditions.items()}
        entries.append(
            replace(
                encounter.entry("round_ended", "system",
                                {"round": encounter.round_number}),
                sequence=encounter.next_sequence + 1,
            )
        )

    return (
        replace(
            encounter,
            turn_index=index,
            round_number=round_number,
            conditions=conditions,
            next_sequence=encounter.next_sequence + len(entries),
        ),
        entries,
    )


def set_conditions(
    encounter: Encounter, combatant_id: str, conditions: Sequence[Condition]
) -> Encounter:
    """Replace the condition list on one combatant."""
    updated = dict(encounter.conditions)
    updated[combatant_id] = list(conditions)
    return replace(encounter, conditions=updated)


def set_combatant(encounter: Encounter, combatant: Combatant) -> Encounter:
    """Replace one combatant's record."""
    updated = dict(encounter.combatants)
    updated[combatant.combatant_id] = combatant
    return replace(encounter, combatants=updated)


def with_entries(encounter: Encounter, count: int) -> Encounter:
    """Advance the sequence counter after writing `count` entries."""
    return replace(encounter, next_sequence=encounter.next_sequence + count)
