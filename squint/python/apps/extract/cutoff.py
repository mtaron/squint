"""Where a ranked list of search scores drops off: the knee that separates the pages a query is
about from the rest."""

from collections.abc import Sequence
from dataclasses import dataclass
from itertools import pairwise


@dataclass(frozen=True)
class Drop:
    """How large a gap between neighboring scores must be to count: as a share of the spread of
    every score, so a list that declines steadily has no drop, and relative to the best score, so
    two nearly equal scores don't make one."""

    of_spread: float
    of_best: float


def cliff(scores: Sequence[float], drop: Drop, *, within: int) -> int | None:
    """How many of the best scores come before the largest gap among the first `within` + 1, or
    None when that gap isn't a `drop`. `scores` are best first."""
    if len(scores) < 2:
        return None
    spread = scores[0] - scores[-1]
    gaps = [higher - lower for higher, lower in pairwise(scores[: within + 1])]
    largest = max(range(len(gaps)), key=gaps.__getitem__)
    gap = gaps[largest]
    if gap <= 0 or gap < drop.of_spread * spread or gap < drop.of_best * abs(scores[0]):
        return None
    return largest + 1
