import numpy as np
import pytest
import torch
from squint_core.processes import ProcessWorkers

from token_compression import (
    INT8_SCALE,
    POOL_FACTOR,
    compress_tokens,
    limit_to_one_thread,
    quantize,
    warm_up,
)


def unit_vectors(count: int) -> torch.Tensor:
    vectors = torch.randn(count, 128, generator=torch.Generator().manual_seed(0))
    return vectors / vectors.norm(dim=1, keepdim=True)


def test_inner_products_of_codes_keep_those_of_the_vectors():
    vectors = unit_vectors(200)

    codes = torch.from_numpy(quantize(vectors)).float()

    original = vectors @ vectors.T
    assert torch.allclose(codes @ codes.T / INT8_SCALE**2, original, atol=0.02)


def test_quantizing_saturates_rather_than_overflows():
    codes = quantize(torch.tensor([[1.0, -1.0, 0.0]]))

    assert codes.tolist() == [[127, -127, 0]]
    assert codes.dtype == np.int8


def test_pooling_keeps_about_one_token_in_ten():
    compressed = compress_tokens(unit_vectors(500).numpy())

    assert compressed.dtype == np.int8
    assert compressed.shape == pytest.approx((500 / POOL_FACTOR, 128), abs=1)


async def test_warming_up_loads_every_process():
    with ProcessWorkers(2, limit_to_one_thread) as workers:
        await warm_up(workers)

        assert len(workers.pool._processes) == 2
