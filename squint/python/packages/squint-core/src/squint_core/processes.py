import asyncio
from collections.abc import Callable
from concurrent.futures import ProcessPoolExecutor
from concurrent.futures.process import BrokenProcessPool
from typing import Self


class ProcessWorkers:
    """Processes for CPU work that can't run in parallel on threads."""

    def __init__(
        self, size: int, initializer: Callable[[], None] | None = None
    ) -> None:
        self.size = size
        self.initializer = initializer
        self.pool = self.create_pool()

    def create_pool(self) -> ProcessPoolExecutor:
        return ProcessPoolExecutor(self.size, initializer=self.initializer)

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *_exception: object) -> None:
        self.pool.shutdown()

    async def run[T](self, function: Callable[..., T], *args: object) -> T:
        pool = self.pool
        try:
            return await asyncio.get_running_loop().run_in_executor(
                pool, function, *args
            )
        except BrokenProcessPool:
            # One process dying breaks the pool for good, and retries on it would use up the
            # attempts of every document on this pod
            if pool is self.pool:
                self.pool = self.create_pool()
            raise
