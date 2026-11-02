"""Runs the worker in the working directory under debugpy, restarting it when its source changes.

This watches for changes itself because watchfiles.run_process kills a worker 5s after a SIGTERM,
and a worker needs as long as its activities take to drain.
"""
# ruff: noqa: T100

import contextlib
import logging
import os
import runpy
import signal
import socket
import subprocess
import sys
import threading
import time

import debugpy
import watchfiles

SOURCE = "/app"
# How long debugpy's adapter gets to notice that its worker has gone
PORT_RELEASE_TIMEOUT_SECONDS = 10


def run_worker(debug_port: int) -> None:
    debugpy.listen(("0.0.0.0", debug_port))
    runpy.run_path("main.py", run_name="__main__")


def start_worker(debug_port: int) -> subprocess.Popen[bytes]:
    """A plain subprocess, since a multiprocessing child would make its own pools spawn processes
    rather than use the forkserver as they do in production. Its own session lets stop_worker find
    those processes."""
    return subprocess.Popen(
        [
            sys.executable,
            # Frozen stdlib modules can make debugpy miss breakpoints
            "-Xfrozen_modules=off",
            "-c",
            f"from debug_worker import run_worker; run_worker({debug_port})",
        ],
        start_new_session=True,
    )


def wait_for_port_release(debug_port: int) -> None:
    deadline = time.monotonic() + PORT_RELEASE_TIMEOUT_SECONDS
    while time.monotonic() < deadline:
        with socket.socket() as probe:
            if probe.connect_ex(("127.0.0.1", debug_port)) != 0:
                return
        time.sleep(0.1)


def stop_worker(worker: subprocess.Popen[bytes], debug_port: int) -> None:
    """A worker stopped mid-startup hasn't installed its SIGTERM handler, so it leaves its process
    pools behind. They inherit its debugpy connection, which keeps the adapter on the port."""
    worker.terminate()
    worker.wait()
    with contextlib.suppress(ProcessLookupError):
        os.killpg(worker.pid, signal.SIGKILL)
    wait_for_port_release(debug_port)


def main() -> None:
    debug_port = int(sys.argv[1])
    logging.basicConfig(level=logging.INFO, format="%(message)s")

    stopping = threading.Event()
    signal.signal(signal.SIGTERM, lambda *_: stopping.set())

    worker = start_worker(debug_port)
    for _ in watchfiles.watch(
        SOURCE, watch_filter=watchfiles.PythonFilter(), stop_event=stopping
    ):
        stop_worker(worker, debug_port)
        worker = start_worker(debug_port)
    stop_worker(worker, debug_port)


if __name__ == "__main__":
    main()
