import pytest

from cutoff import Drop, cliff

DROP = Drop(of_spread=0.25, of_best=0.05)


@pytest.mark.parametrize(
    "scores, within, expected",
    [
        pytest.param([800, 20, 20, 5], 5, 1, id="one page stands out"),
        pytest.param([0.62, 0.6, 0.31, 0.3, 0.29, 0.28], 5, 2, id="two tiers"),
        pytest.param([0.5, 0.48, 0.46, 0.44, 0.42, 0.4], 5, None, id="steady decline"),
        pytest.param([0.5, 0.5, 0.5], 5, None, id="all equal"),
        pytest.param([0.5, 0.49], 5, None, id="two nearly equal scores"),
        pytest.param([0.9], 5, None, id="a single score"),
        pytest.param([], 5, None, id="no scores"),
        pytest.param(
            [0.6, 0.59, 0.58, 0.57, 0.56, 0.55, 0.2], 3, None, id="drop past the window"
        ),
    ],
)
def test_finds_the_largest_drop_within_the_window(
    scores: list[float], within: int, expected: int | None
):
    assert cliff(scores, DROP, within=within) == expected


def test_a_drop_must_be_large_relative_to_the_spread_of_every_score():
    scores = [1.0, 0.8, 0.7, 0.6, 0.5, 0.0]

    assert cliff(scores, DROP, within=3) is None
    assert cliff(scores, Drop(of_spread=0.1, of_best=0.05), within=3) == 1
