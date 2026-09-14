"""The session log.

Append-only, and that is the whole design. An entry is written once, carries
the sequence number it was written at, and is never updated or deleted. A
correction is a new entry that refers to the old one.

The rule that protects this is `log.append-only`.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Sequence


@dataclass(frozen=True, slots=True)
class Entry:
    """One event in an encounter's history."""

    sequence: int
    encounter_id: str
    round_number: int
    kind: str
    actor: str
    payload: dict[str, Any]

    def to_dict(self) -> dict[str, object]:
        return {
            "sequence": self.sequence,
            "encounter_id": self.encounter_id,
            "round": self.round_number,
            "kind": self.kind,
            "actor": self.actor,
            "payload": self.payload,
        }

    def canonical(self) -> str:
        """A stable string form, so entries can be hashed or diffed."""
        return json.dumps(self.to_dict(), sort_keys=True, separators=(",", ":"))


def append(entries: Sequence[Entry], entry: Entry) -> list[Entry]:
    """Add an entry, refusing anything that is not the next sequence number."""
    expected = (entries[-1].sequence + 1) if entries else 1
    if entry.sequence != expected:
        raise ValueError(f"log is at {expected - 1}; got sequence {entry.sequence}")
    return [*entries, entry]


def correct(entries: Sequence[Entry], sequence: int, reason: str) -> list[Entry]:
    """Retract an earlier entry by appending, never by editing."""
    target = next((item for item in entries if item.sequence == sequence), None)
    if target is None:
        raise LookupError(f"no entry at sequence {sequence}")
    return append(
        entries,
        Entry(
            sequence=entries[-1].sequence + 1,
            encounter_id=target.encounter_id,
            round_number=target.round_number,
            kind="correction",
            actor="system",
            payload={"retracts": sequence, "reason": reason},
        ),
    )


def replayable(entries: Sequence[Entry]) -> bool:
    """True when every roll in the log carries the seed that produced it."""
    for entry in entries:
        for value in entry.payload.values():
            if isinstance(value, dict) and "total" in value and "seed" not in value:
                return False
    return True
