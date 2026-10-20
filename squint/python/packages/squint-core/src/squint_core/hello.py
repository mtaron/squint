"""A hello-world workflow every worker registers until it has real work."""

import asyncio
from dataclasses import dataclass
from datetime import timedelta

from temporalio import activity, workflow


@dataclass
class HelloInput:
    name: str
    # Holds an activity slot for this long, to exercise autoscaling
    delay_seconds: float = 0


@activity.defn
async def say_hello(input: HelloInput) -> str:
    await asyncio.sleep(input.delay_seconds)
    return f"Hello, {input.name}!"


@workflow.defn
class HelloWorkflow:
    @workflow.run
    async def run(self, input: HelloInput) -> str:
        return await workflow.execute_activity(
            say_hello,
            input,
            start_to_close_timeout=timedelta(seconds=input.delay_seconds + 10),
        )
