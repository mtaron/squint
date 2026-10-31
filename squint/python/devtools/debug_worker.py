"""Runs the worker in the working directory under debugpy, restarting it when its source changes.

This watches for changes itself because watchfiles.run_process kills a worker 5s after a SIGTERM,
and a worker needs as long as its activities take to drain.
"""
# ruff: noqa: T100

import logging
import runpy
import signal
import subprocess
import sys
import threading

import debugpy
import watchfiles

SOURCE = "/app"


def run_worker(debug_port: int) -> None:
    debugpy.listen(("0.0.0.0", debug_port))
    runpy.run_path("main.py", run_name="__main__")


def start_worker(debug_port: int) -> subprocess.Popen[bytes]:
    """A plain subprocess, since a multiprocessing child would make its own pools spawn processes
    rather than use the forkserver as they do in production."""
    return subprocess.Popen(
        [
            sys.executable,
            # Frozen stdlib modules can make debugpy miss breakpoints
            "-Xfrozen_modules=off",
            "-c",
            f"from debug_worker import run_worker; run_worker({debug_port})",
        ]
    )


def stop_worker(worker: subprocess.Popen[bytes]) -> None:
    worker.terminate()
    worker.wait()


def main() -> None:
    debug_port = int(sys.argv[1])
    logging.basicConfig(level=logging.INFO, format="%(message)s")

    stopping = threading.Event()
    signal.signal(signal.SIGTERM, lambda *_: stopping.set())

    worker = start_worker(debug_port)
    for _ in watchfiles.watch(
        SOURCE, watch_filter=watchfiles.PythonFilter(), stop_event=stopping
    ):
        stop_worker(worker)
        worker = start_worker(debug_port)
    stop_worker(worker)


if __name__ == "__main__":
    main()
