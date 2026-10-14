"""Observe the unchanged frozen CI replay without altering its process budget.

Project-original Codex (OpenAI), Unknown v0.3, through Mingli Yuan's
authorized account proxy; not his review or endorsement.
"""

import hashlib
import json
from pathlib import Path
import platform
import resource
import shutil
import subprocess
import time
from unittest.mock import patch

import pytest


FRESH_TEST = (
    "tests/python/test_continuation_resolution_crosscheck.py::"
    "test_fresh_crosscheck_replays_the_frozen_projection"
)


def observe_run(run, records, *args, **kwargs):
    """Pass the exact arguments through; retain failures and never retry."""
    before = resource.getrusage(resource.RUSAGE_CHILDREN)
    started = time.monotonic()
    record = {"timeout_seconds": kwargs.get("timeout")}
    try:
        completed = run(*args, **kwargs)
        record.update(status="Completed", returncode=completed.returncode,
                      stdout_bytes=len(completed.stdout or b""),
                      stderr_bytes=len(completed.stderr or b""))
        return completed
    except subprocess.TimeoutExpired as error:
        record.update(status="TimeoutExpired", stdout_bytes=len(error.output or b""),
                      stderr_bytes=len(error.stderr or b""))
        raise
    except BaseException as error:
        record.update(status=type(error).__name__)
        raise
    finally:
        after = resource.getrusage(resource.RUSAGE_CHILDREN)
        record.update(wall_seconds=time.monotonic() - started,
                      child_user_seconds=after.ru_utime - before.ru_utime,
                      child_system_seconds=after.ru_stime - before.ru_stime,
                      child_voluntary_switches=after.ru_nvcsw - before.ru_nvcsw,
                      child_involuntary_switches=after.ru_nivcsw - before.ru_nivcsw)
        records.append(record)


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_call(item):
    if item.nodeid != FRESH_TEST:
        yield
        return
    node = shutil.which("node")
    records = []
    metadata = {
        "python": platform.python_version(), "platform": platform.platform(),
        "node_path": node,
        "node_binary_sha256": hashlib.sha256(Path(node).read_bytes()).hexdigest()
        if node else None,
        "process_records": records,
        "classification": "ExecutionTelemetryOnly",
        "no_retry": True,
    }
    original = subprocess.run
    try:
        with patch.object(subprocess, "run", side_effect=lambda *a, **k:
                          observe_run(original, records, *a, **k)):
            yield
    finally:
        # Sizes and timing only: no input bytes, receipt contents or environment
        # variables are disclosed. Exceptions still fail the original test.
        print("CROSSCHECK_CI_TELEMETRY " + json.dumps(metadata, sort_keys=True))
