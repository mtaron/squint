import asyncio
from concurrent.futures import ThreadPoolExecutor

from squint_core import postgres, s3
from squint_core.worker import run_worker

from activities import DocumentActivities, PdfActivities
from workflows import IngestDocumentWorkflow

TASK_QUEUE = "ingest"
# PDFium isn't thread safe, so each pod runs one activity at a time on a single thread and the
# autoscaler adds pods instead
MAX_CONCURRENT_ACTIVITIES = 1


async def run() -> None:
    db = await postgres.create_client()
    pdf_activities = PdfActivities(s3.create_sync_client())
    document_activities = DocumentActivities(db, s3.create_client())
    try:
        with ThreadPoolExecutor(max_workers=MAX_CONCURRENT_ACTIVITIES) as executor:
            await run_worker(
                TASK_QUEUE,
                [IngestDocumentWorkflow],
                [
                    pdf_activities.rasterize_pdf,
                    document_activities.record_page_count,
                    document_activities.discard_document,
                ],
                max_concurrent_activities=MAX_CONCURRENT_ACTIVITIES,
                activity_executor=executor,
            )
    finally:
        await db.close()


def main():
    asyncio.run(run())


if __name__ == "__main__":
    main()
