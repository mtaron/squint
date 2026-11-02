"""Shrinks a page's late-interaction vectors for storage, from about 1.5 MB to 39 kB per page."""

import asyncio

import numpy as np
import torch
from sentence_transformers.multi_vector_encoder.modules import HierarchicalTokenPooling
from squint_core.processes import ProcessWorkers
from squint_vector.pages import TOKEN_DIMENSIONS

# Keeps 99.16% of NeoMME's nDCG@10 with int8 vectors, the last point above 99% in the paper's
# compression study. Factor 19 drops to 98.1%.
POOL_FACTOR = 10
# Coordinates of unit vectors this wide rarely pass 0.37, so codes keep most of int8's range while
# 1 in 100,000 clips. The paper's per-token scales have nowhere to go in Milvus, and without them
# inner products would be skewed, so every token and query shares this one. Scores on sampled
# ViDoRe v3 pages correlate 0.99999 with float32.
INT8_SCALE = 340


pooler = HierarchicalTokenPooling(pool_factor=POOL_FACTOR)


def limit_to_one_thread() -> None:
    """Each process pools one page, so PyTorch's own threads would only compete with each other."""
    torch.set_num_threads(1)


async def warm_up(workers: ProcessWorkers) -> None:
    """Starting a process imports PyTorch and pooling imports SciPy, which would stall the first
    batch for ~20 s."""
    tokens = np.eye(2, TOKEN_DIMENSIONS, dtype=np.float32)
    await asyncio.gather(
        *(workers.run(compress_tokens, tokens) for _ in range(workers.size))
    )


def quantize(tokens: torch.Tensor) -> np.ndarray:
    codes = (tokens * INT8_SCALE).round().clamp(-127, 127)
    return codes.to(torch.int8).numpy()


def compress_tokens(tokens: np.ndarray) -> np.ndarray:
    """Clustering a page takes ~190 ms in SciPy, which holds the GIL, so this runs in a process."""
    return quantize(pooler.pool([torch.from_numpy(tokens)])[0])
