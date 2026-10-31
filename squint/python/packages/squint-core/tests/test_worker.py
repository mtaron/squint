from datetime import timedelta

import pytest

from squint_core.worker import shutdown_timeout


def test_reads_the_shutdown_timeout_the_chart_sets(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("WORKER_SHUTDOWN_TIMEOUT_SECONDS", "3595")

    assert shutdown_timeout() == timedelta(seconds=3595)
