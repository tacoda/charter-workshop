"""Dice notation: parse it, roll it, and keep the receipt.

A roll is not a number. It is a number plus everything needed to defend it:
the notation asked for, the stream it was drawn from, the raw faces, what was
kept, what was dropped, and the modifier applied. `Roll.to_dict()` is the only
sanctioned way an outcome reaches a client, because a bare integer on the wire
is an assertion nobody at the table can check.

Supported notation
------------------
    d20             one twenty-sided die
    2d6             two six-sided dice, summed
    4d6kh3          roll four, keep the highest three
    2d20kl1         roll two, keep the lowest  (disadvantage)
    1d8+3           a flat modifier
    2d6-1
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Sequence

from tarrasque.domain.rng import Rng

NOTATION = re.compile(
    r"""^
    (?P<count>\d*)                 # 2   (empty means one)
    d(?P<faces>\d+)                # d20
    (?P<keep>(?:k[hl]\d+)?)        # kh3 / kl1
    (?P<bonus>[+-]\d+)?            # +3
    $""",
    re.VERBOSE | re.IGNORECASE,
)

MAX_DICE = 100
MAX_FACES = 1000


class BadNotation(ValueError):
    """Raised for notation this service will not parse."""


@dataclass(frozen=True, slots=True)
class Notation:
    """Parsed dice notation. Pure data; rolling it is a separate step."""

    count: int
    faces: int
    keep_highest: int | None
    keep_lowest: int | None
    bonus: int

    def __str__(self) -> str:
        text = f"{self.count}d{self.faces}"
        if self.keep_highest is not None:
            text += f"kh{self.keep_highest}"
        if self.keep_lowest is not None:
            text += f"kl{self.keep_lowest}"
        if self.bonus:
            text += f"{self.bonus:+d}"
        return text


@dataclass(frozen=True, slots=True)
class Roll:
    """One resolved roll, with the evidence attached."""

    notation: str
    seed: str
    stream_position: int
    faces: Sequence[int]
    kept: Sequence[int]
    dropped: Sequence[int]
    bonus: int
    total: int

    def is_natural(self, value: int) -> bool:
        """True when a single kept die showed exactly `value`."""
        return len(self.kept) == 1 and self.kept[0] == value

    def to_dict(self) -> dict[str, object]:
        """The wire form. A result never travels without its provenance."""
        return {
            "total": self.total,
            "notation": self.notation,
            "seed": self.seed,
            "stream_position": self.stream_position,
            "faces": list(self.faces),
            "kept": list(self.kept),
            "dropped": list(self.dropped),
            "bonus": self.bonus,
        }


def parse(notation: str) -> Notation:
    """Parse dice notation, or raise `BadNotation` naming what was wrong."""
    text = notation.strip().replace(" ", "")
    match = NOTATION.match(text)
    if match is None:
        raise BadNotation(f"cannot parse {notation!r}")

    count = int(match.group("count") or 1)
    faces = int(match.group("faces"))
    bonus = int(match.group("bonus") or 0)

    if not 1 <= count <= MAX_DICE:
        raise BadNotation(f"{count} dice is outside 1..{MAX_DICE}")
    if not 2 <= faces <= MAX_FACES:
        raise BadNotation(f"d{faces} is outside d2..d{MAX_FACES}")

    keep_highest: int | None = None
    keep_lowest: int | None = None
    keep = match.group("keep").lower()
    if keep:
        amount = int(keep[2:])
        if not 1 <= amount <= count:
            raise BadNotation(f"cannot keep {amount} of {count} dice")
        if keep.startswith("kh"):
            keep_highest = amount
        else:
            keep_lowest = amount

    return Notation(count, faces, keep_highest, keep_lowest, bonus)


def _select(faces: Sequence[int], notation: Notation) -> tuple[list[int], list[int]]:
    """Split raw results into (kept, dropped) under the keep rule."""
    if notation.keep_highest is None and notation.keep_lowest is None:
        return list(faces), []
    ranked = sorted(range(len(faces)), key=lambda i: (faces[i], i))
    amount = notation.keep_highest or notation.keep_lowest or len(faces)
    chosen = ranked[-amount:] if notation.keep_highest is not None else ranked[:amount]
    keep_at = set(chosen)
    kept = [value for index, value in enumerate(faces) if index in keep_at]
    dropped = [value for index, value in enumerate(faces) if index not in keep_at]
    return kept, dropped


def roll(rng: Rng, notation: str) -> Roll:
    """Roll `notation` against a stream and return the full receipt."""
    parsed = parse(notation)
    opened_at = rng.position
    faces = [rng.roll(parsed.faces) for _ in range(parsed.count)]
    kept, dropped = _select(faces, parsed)
    return Roll(
        notation=str(parsed),
        seed=rng.seed,
        stream_position=opened_at,
        faces=faces,
        kept=kept,
        dropped=dropped,
        bonus=parsed.bonus,
        total=sum(kept) + parsed.bonus,
    )


def with_advantage(notation: str) -> str:
    """Rewrite single-die notation to roll twice and keep the highest."""
    parsed = parse(notation)
    if parsed.count != 1:
        raise BadNotation("advantage applies to a single die")
    return str(Notation(2, parsed.faces, 1, None, parsed.bonus))


def with_disadvantage(notation: str) -> str:
    """Rewrite single-die notation to roll twice and keep the lowest."""
    parsed = parse(notation)
    if parsed.count != 1:
        raise BadNotation("disadvantage applies to a single die")
    return str(Notation(2, parsed.faces, None, 1, parsed.bonus))
