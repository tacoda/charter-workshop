"""The only module in this service that may import `random`.

Every die rolled anywhere in `tarrasque` comes through here, from a stream
opened with an explicit seed. That is what makes a session log replayable: a
log you cannot replay is a transcript, and a transcript settles no argument.

The rule that protects this is `dice.seeded`, and the one escape hatch is
`# seeded-gate: allow - <reason>` on the offending line.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Protocol


class Rng(Protocol):
    """A stream of die results. Implementations must be deterministic."""

    def roll(self, faces: int) -> int:
        """Return a result in 1..faces and advance the stream."""

    @property
    def seed(self) -> str:
        """The seed this stream was opened with."""

    @property
    def position(self) -> int:
        """How many results have been drawn. Part of a roll's provenance."""


@dataclass(slots=True)
class SeededRng:
    """A reproducible stream. Same seed, same sequence, every time, forever."""

    _seed: str
    _position: int = 0
    _source: random.Random = field(init=False, repr=False)

    def __post_init__(self) -> None:
        self._source = random.Random(self._seed)

    def roll(self, faces: int) -> int:
        if faces < 2:
            raise ValueError(f"a die needs at least two faces, got {faces}")
        self._position += 1
        return self._source.randrange(1, faces + 1)

    @property
    def seed(self) -> str:
        return self._seed

    @property
    def position(self) -> int:
        return self._position


@dataclass(slots=True)
class ScriptedRng:
    """A fixed sequence of results, for tests and for replaying a log."""

    results: list[int]
    _position: int = 0

    def roll(self, faces: int) -> int:
        if self._position >= len(self.results):
            raise IndexError("scripted stream exhausted")
        value = self.results[self._position]
        self._position += 1
        if not 1 <= value <= faces:
            raise ValueError(f"scripted {value} is not a valid d{faces} result")
        return value

    @property
    def seed(self) -> str:
        return "scripted"

    @property
    def position(self) -> int:
        return self._position


def stream_for(encounter_id: str, round_number: int, salt: str = "") -> SeededRng:
    """Open the canonical stream for a point in an encounter.

    The seed is derived from where the encounter *is*, so replaying the log
    from the top reproduces every roll in it.
    """
    return SeededRng(f"{encounter_id}:{round_number}:{salt}")
