import asyncio

import torch
from squint_core.config import require_env
from squint_core.hello import HelloWorkflow, say_hello
from squint_core.worker import run_worker
from transformers import NeoMMEForRetrieval, NeoMMEProcessor

TASK_QUEUE = "embed"
# The GPU embeds one batch at a time
MAX_CONCURRENT_ACTIVITIES = 1
# Measured on an RTX 5070 Ti with FlashAttention 2 and torch.compile: throughput plateaus at
# 4 pages (44 letter pages/s, 34 pages/s for 2048x2048 squares; the whole process peaks at
# ~1.9 GiB of GPU memory on squares, which the dev vLLM budget in helmfile.yaml.gotmpl assumes)
BATCH_SIZE = 4
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


def main():
    _processor, model = load_model()
    print(
        f"embed model loaded: {model.name_or_path} on {torch.cuda.get_device_name()}, "
        f"{torch.cuda.memory_allocated() / 2**20:.0f} MiB allocated"
    )
    # ~45% faster than eager; the first batch of each new shape compiles for ~20-30s. Every
    # layer's static layer_idx triggers a recompile, which would exhaust the default limit of 8
    # and silently leave the remaining layers eager (the paper raises it to 256 too).
    torch._dynamo.config.recompile_limit = 256  # ty: ignore[invalid-assignment]
    model = torch.compile(model)
    asyncio.run(
        run_worker(
            TASK_QUEUE,
            [HelloWorkflow],
            [say_hello],
            max_concurrent_activities=MAX_CONCURRENT_ACTIVITIES,
        )
    )


if __name__ == "__main__":
    main()
