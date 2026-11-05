import asyncio
import logging

from openai import AsyncOpenAI
from squint_core import s3
from squint_core.config import require_env
from squint_core.worker import run_worker
from squint_vector import milvus

from activities import ExtractActivities
from workflows import SearchWorkflow

TASK_QUEUE = "extract"
MAX_CONCURRENT_ACTIVITIES = 5
# Temporal retries a locate that times out, so the client doesn't retry on its own
VLM_TIMEOUT_SECONDS = 90


async def run() -> None:
    # Activities log each search's scores, which is what the cutoffs are calibrated from
    logging.basicConfig()
    logging.getLogger("temporalio.activity").setLevel(logging.INFO)
    vectors = milvus.create_client()
    vlm = AsyncOpenAI(
        base_url=require_env("VLLM_URL"),
        api_key="unused",
        timeout=VLM_TIMEOUT_SECONDS,
        max_retries=0,
    )
    try:
        activities = ExtractActivities(
            s3.create_client(),
            vectors,
            vlm,
            dense_search_min_pages=int(require_env("DENSE_SEARCH_MIN_PAGES")),
        )
        await run_worker(
            TASK_QUEUE,
            # `task temporal-load` starts hello-world workflows here to exercise autoscaling
            [activities.find_pages, activities.locate_text],
            workflows=[SearchWorkflow],
            max_concurrent_activities=MAX_CONCURRENT_ACTIVITIES,
        )
    finally:
        await vlm.close()
        await vectors.close()


def main():
    asyncio.run(run())


if __name__ == "__main__":
    main()
