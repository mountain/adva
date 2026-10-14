"""Engineering refusal checks; no new continuation or semantic cases.

Project-original Codex (OpenAI), Unknown v0.3, through Mingli Yuan's
authorized account proxy; not his review or endorsement.
"""

import importlib.util
from pathlib import Path
import subprocess
import sys
from unittest.mock import patch

import pytest

from scripts.crosscheck_ci_observer import observe_run


ROOT = Path(__file__).resolve().parents[2]


def runner():
    spec = importlib.util.spec_from_file_location(
        "crosscheck_timeout_boundary",
        ROOT / "experiments/continuation_resolution_crosscheck/run.py",
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_timeout_reaps_the_child_and_does_not_write_a_receipt(tmp_path):
    module = runner()
    campaign = module.Campaign(tmp_path / "evidence", 0.2)
    original = subprocess.run
    children = []

    def delayed_child(*args, **kwargs):
        # Substitute a finite delayed process only in this engineering control.
        # Capture the actual Popen object to check subprocess.run's cleanup.
        popen = subprocess.Popen

        def capture(*a, **k):
            child = popen(*a, **k)
            children.append(child)
            return child

        with patch.object(subprocess, "Popen", side_effect=capture):
            return original([sys.executable, "-c", "import time; time.sleep(2)"],
                            **kwargs)

    with patch.object(module.subprocess, "run", side_effect=delayed_child) as invoke:
        with pytest.raises(subprocess.TimeoutExpired):
            campaign.invoke("exact-alpha", "completed-alpha", "python", "node")
    assert invoke.call_count == len(children) == 1
    assert children[0].poll() is not None
    assert campaign.records == []
    assert not campaign.output.exists()


def test_nonzero_exit_stops_without_accepting_or_retrying(tmp_path):
    module = runner()
    campaign = module.Campaign(tmp_path / "evidence", 5)
    failed = subprocess.CompletedProcess(["node"], 1, b"", b"failure")
    with patch.object(module.subprocess, "run", return_value=failed) as invoke:
        with pytest.raises(RuntimeError, match="exact-alpha:node-exit"):
            campaign.invoke("exact-alpha", "completed-alpha", "python", "node")
    assert invoke.call_count == 1
    assert invoke.call_args.kwargs["timeout"] == 5
    assert campaign.records == []
    assert not campaign.output.exists()


def test_observer_propagates_timeout_without_changing_arguments():
    records = []
    command = ["node", "--max-old-space-size=32", "receiver.mjs"]
    error = subprocess.TimeoutExpired(command, 5, output=b"partial", stderr=b"")
    with patch("subprocess.run", side_effect=error) as invoke:
        with pytest.raises(subprocess.TimeoutExpired) as raised:
            observe_run(invoke, records, command, timeout=5, capture_output=True,
                        check=False)
    assert raised.value is error
    invoke.assert_called_once_with(command, timeout=5, capture_output=True, check=False)
    assert records[0]["status"] == "TimeoutExpired"
    assert records[0]["stdout_bytes"] == 7
    assert records[0]["timeout_seconds"] == 5
