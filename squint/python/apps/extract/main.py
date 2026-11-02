import asyncio

from squint_core.hello import HelloWorkflow, say_hello
from squint_core.worker import run_worker

TASK_QUEUE = "extract"
MAX_CONCURRENT_ACTIVITIES = 5


def main():
    asyncio.run(
        run_worker(
            TASK_QUEUE,
            [say_hello],
            workflows=[HelloWorkflow],
            max_concurrent_activities=MAX_CONCURRENT_ACTIVITIES,
        )
    )


if __name__ == "__main__":
    main()
