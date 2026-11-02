import asyncio

from squint_core import postgres, s3
from squint_core.worker import run_worker

from activities import DocumentActivities, PageWorkers
from workflows import IngestDocumentWorkflow

TASK_QUEUE = "ingest"
# Pages a pod works on at once. It takes as many documents, so when one finishes the next is
# already downloaded and sharing the processes.
PARALLELISM = 8


async def run() -> None:
    db = await postgres.create_client()
    try:
        with PageWorkers(PARALLELISM) as page_workers:
            activities = DocumentActivities(db, s3.create_client(), page_workers)
            await run_worker(
                TASK_QUEUE,
                [
                    activities.rasterize_pdf,
                    activities.record_page_count,
                    activities.discard_document,
                ],
                workflows=[IngestDocumentWorkflow],
                max_concurrent_activities=PARALLELISM,
            )
    finally:
        await db.close()


def main():
    asyncio.run(run())


if __name__ == "__main__":
    main()
