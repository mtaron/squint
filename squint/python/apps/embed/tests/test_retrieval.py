"""Runs the real model over checked-in pages, so it needs a GPU and `task download-models`."""

import json
import os
from collections.abc import AsyncGenerator
from itertools import batched
from pathlib import Path

import numpy as np
import pytest
import torch
from PIL import Image
from sentence_transformers.util import mean_maxsim
from squint_core.embedding import EMBED_BATCH_SIZE
from squint_core.processes import ProcessWorkers
from squint_vector.pages import (
    DENSE_DIMENSIONS,
    MAX_TOKENS_PER_PAGE,
    TOKEN_DIMENSIONS,
)
from torch.nn.utils.rnn import pad_sequence

from encoder import Encoded, Encoder, load_model
from token_compression import POOL_FACTOR, limit_to_one_thread

FIXTURES = Path(__file__).parent / "fixtures"
# Landscape and portrait alternate, so every batch has to pad pages of different shapes
PAGES = [
    "adverse-event-reports.jpg",
    "jack-maintenance.jpg",
    "generic-applications.jpg",
    "stock-performance.jpg",
]
# Fits next to the dev cluster on a shared GPU, where a batch of EMBED_BATCH_SIZE might not
TEST_BATCH_SIZE = 2
QUERIES = json.loads((FIXTURES / "queries.json").read_text())

pytestmark = [
    pytest.mark.skipif(
        not torch.cuda.is_available(), reason="needs a CUDA device for the model"
    ),
    pytest.mark.skipif(
        not Path(os.environ["MODEL_PATH"]).exists(),
        reason="needs `task download-models`",
    ),
]


@pytest.fixture(scope="module")
async def encoder() -> AsyncGenerator[Encoder]:
    processor, model = load_model()
    with ProcessWorkers(EMBED_BATCH_SIZE, limit_to_one_thread) as workers:
        yield Encoder(processor, model, workers)


@pytest.fixture(scope="module")
async def pages(encoder: Encoder) -> list[Encoded]:
    images = [Image.open(FIXTURES / page).convert("RGB") for page in PAGES]
    encoded = []
    for batch in batched(images, TEST_BATCH_SIZE):
        encoded += await encoder.encode_pages(list(batch))
    return encoded


@pytest.fixture(scope="module")
def queries(encoder: Encoder) -> list[Encoded]:
    return encoder.encode_queries([entry["query"] for entry in QUERIES])


def late_scores(query: Encoded, pages: list[Encoded]) -> torch.Tensor:
    documents = [torch.from_numpy(page.tokens).float() for page in pages]
    padded = pad_sequence(documents, batch_first=True)
    mask = pad_sequence(
        [torch.ones(len(document)) for document in documents], batch_first=True
    )
    return mean_maxsim(
        torch.from_numpy(query.tokens).float().unsqueeze(0), padded, b_mask=mask
    )[0]


@pytest.mark.parametrize("index", range(len(QUERIES)))
def test_late_interaction_ranks_the_relevant_page_first(
    index: int, pages: list[Encoded], queries: list[Encoded]
):
    scores = late_scores(queries[index], pages)

    assert PAGES[int(scores.argmax())] == QUERIES[index]["page"]


@pytest.mark.parametrize("index", range(len(QUERIES)))
def test_dense_vectors_rank_the_relevant_page_first(
    index: int, pages: list[Encoded], queries: list[Encoded]
):
    scores = np.stack([page.dense for page in pages]) @ queries[index].dense

    assert PAGES[int(scores.argmax())] == QUERIES[index]["page"]


def test_pages_are_pooled_and_quantized_to_fit_the_collection(pages: list[Encoded]):
    for page in pages:
        assert page.tokens.dtype == np.int8
        assert page.tokens.shape[1] == TOKEN_DIMENSIONS
        assert page.tokens.shape[0] <= MAX_TOKENS_PER_PAGE
        # A page has thousands of patches, so pooling leaves hundreds of tokens
        assert page.tokens.shape[0] > MAX_TOKENS_PER_PAGE / POOL_FACTOR
        assert page.tokens.any(axis=1).all()


def test_dense_vectors_are_full_size_and_normalized(pages: list[Encoded]):
    for page in pages:
        assert page.dense.dtype == np.float32
        assert page.dense.shape == (DENSE_DIMENSIONS,)
        # The model normalizes in bfloat16
        assert np.linalg.norm(page.dense) == pytest.approx(1, abs=0.01)


def test_queries_are_quantized_but_not_pooled(queries: list[Encoded]):
    for query in queries:
        assert query.tokens.dtype == np.int8
        assert query.tokens.shape[1] == TOKEN_DIMENSIONS
        assert query.tokens.shape[0] > 10
