import asyncio

import torch
from squint_core import postgres, s3
from squint_core.embedding import EMBED_BATCH_SIZE, EMBED_TASK_QUEUE
from squint_core.processes import ProcessWorkers
from squint_core.worker import run_worker
from squint_vector import milvus, pages

from activities import EmbedActivities
from encoder import Encoder, load_model
from token_compression import limit_to_one_thread

# The GPU embeds one batch at a time
MAX_CONCURRENT_ACTIVITIES = 1


async def run() -> None:
    processor, model = load_model()
    print(
        f"embed model loaded: {model.name_or_path} on {torch.cuda.get_device_name()}, "
        f"{torch.cuda.memory_allocated() / 2**20:.0f} MiB allocated"
    )
    db = await postgres.create_client()
    vectors = milvus.create_client()
    try:
        await pages.ensure_collection(vectors)
        with ProcessWorkers(EMBED_BATCH_SIZE, limit_to_one_thread) as workers:
            encoder = Encoder(processor, model, workers)
            await encoder.warm_up()
            activities = EmbedActivities(db, s3.create_client(), vectors, encoder)
            await run_worker(
                EMBED_TASK_QUEUE,
                activities=[
                    activities.embed_pages,
                    activities.delete_document_vectors,
                    activities.delete_user_vectors,
                ],
                max_concurrent_activities=MAX_CONCURRENT_ACTIVITIES,
            )
    finally:
        await vectors.close()
        await db.close()


def main():
    asyncio.run(run())


if __name__ == "__main__":
    main()
