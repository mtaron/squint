import asyncio

import numpy as np
import torch
from PIL import Image
from pydantic import BaseModel, ConfigDict
from squint_core.config import require_env
from squint_core.processes import ProcessWorkers
from transformers import NeoMMEForRetrieval, NeoMMEProcessor

from token_compression import compress_tokens, quantize, warm_up

# FlashAttention 2 from the Hub, pinned in kernels.lock. NeoMME's sliding-window layers need it
# to avoid materializing dense attention masks. The deployment points the kernels library at a
# predownloaded copy through LOCAL_KERNELS.
ATTN_KERNEL = "kernels-community/flash-attn2"


def load_model(
    attn_implementation: str = ATTN_KERNEL,
) -> tuple[NeoMMEProcessor, NeoMMEForRetrieval]:
    if not torch.cuda.is_available():
        raise RuntimeError("the embed worker needs a CUDA device")
    model_path = require_env("MODEL_PATH")
    processor = NeoMMEProcessor.from_pretrained(model_path)
    model = NeoMMEForRetrieval.from_pretrained(
        model_path,
        dtype=torch.bfloat16,
        device_map="cuda",
        attn_implementation=attn_implementation,
    )
    return processor, model


class Encoded(BaseModel):
    """The full-size dense vector, and the quantized late-interaction vectors."""

    model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True)

    dense: np.ndarray
    tokens: np.ndarray


class Encoder:
    def __init__(
        self,
        processor: NeoMMEProcessor,
        model: NeoMMEForRetrieval,
        workers: ProcessWorkers,
    ) -> None:
        self.processor = processor
        self.model = model
        self.workers = workers

    def forward(self, inputs) -> tuple[list[torch.Tensor], np.ndarray]:
        """Each input's token vectors, without padding, and the dense vectors."""
        inputs = inputs.to(self.model.device)
        with torch.inference_mode():
            output = self.model(**inputs)
        tokens = output.embeddings.float().cpu()
        masks = inputs["attention_mask"].bool().cpu()
        dense = output.dense_embeddings.float().cpu().numpy()
        # An idle worker shouldn't keep a batch's memory on a shared GPU
        del inputs, output
        torch.cuda.empty_cache()
        return [row[mask] for row, mask in zip(tokens, masks, strict=True)], dense

    def forward_pages(
        self, images: list[Image.Image]
    ) -> tuple[list[torch.Tensor], np.ndarray]:
        return self.forward(
            self.processor(images=images, padding="longest", return_tensors="pt")
        )

    def forward_queries(
        self, queries: list[str]
    ) -> tuple[list[torch.Tensor], np.ndarray]:
        return self.forward(
            self.processor.apply_chat_template(
                [[{"role": "user", "content": query}] for query in queries],
                task="query",
                tokenize=True,
                return_dict=True,
                return_tensors="pt",
                processor_kwargs={"padding": "longest"},
            )
        )

    async def warm_up(self) -> None:
        """The first pass through the model takes ~11 s whatever its size, which shouldn't land on
        a user's first batch. Also starts the processes that pool pages."""
        await warm_up(self.workers)
        await asyncio.to_thread(self.forward_pages, [Image.new("RGB", (32, 32))])

    async def encode_pages(self, images: list[Image.Image]) -> list[Encoded]:
        """The GPU and the pooling both block, so they stay off the worker's event loop."""
        tokens, dense = await asyncio.to_thread(self.forward_pages, images)
        compressed = await asyncio.gather(
            *(self.workers.run(compress_tokens, page.numpy()) for page in tokens)
        )
        return [
            Encoded(dense=page_dense, tokens=page_tokens)
            for page_dense, page_tokens in zip(dense, compressed, strict=True)
        ]

    def encode_queries(self, queries: list[str]) -> list[Encoded]:
        tokens, dense = self.forward_queries(queries)
        return [
            Encoded(dense=query_dense, tokens=quantize(query_tokens))
            for query_dense, query_tokens in zip(dense, tokens, strict=True)
        ]
