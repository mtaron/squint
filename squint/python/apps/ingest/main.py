import asyncio

from activities import rasterize_pdf, record_result
from document import IngestDocumentWorkflow
from library import LibraryWorkflow
from squint_core.worker import run_worker

TASK_QUEUE = "ingest"
MAX_CONCURRENT_ACTIVITIES = 5


def main():
    asyncio.run(
        run_worker(
            TASK_QUEUE,
            [IngestDocumentWorkflow, LibraryWorkflow],
            [rasterize_pdf, record_result],
            max_concurrent_activities=MAX_CONCURRENT_ACTIVITIES,
        )
    )


if __name__ == "__main__":
    main()
