"""Transport regressions; no external proof assistant installation required."""

import importlib.util
from pathlib import Path
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location(
    "research_verifier_search", ROOT / "python/adva/verifier_search.py"
)
transport = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(transport)


def test_lean_requires_exact_audit_labels_and_allowlist():
    assert transport.checked_lean_log(
        "'adva152e0' does not depend on any axioms\n", ["adva152e0"]
    ) == {"adva152e0": []}
    assert transport.checked_lean_log(
        "'adva152e0' depends on axioms: [propext, Quot.sound]\n", ["adva152e0"]
    ) == {"adva152e0": ["Quot.sound", "propext"]}
    for raw in (
        "",
        "'adva152e1' does not depend on any axioms\n",
        "'adva152e0' depends on axioms: [sorryAx]\n",
        "'adva152e0' depends on axioms: [trustMe]\n",
        "warning: synthetic\n'adva152e0' does not depend on any axioms\n",
    ):
        with pytest.raises(ValueError):
            transport.checked_lean_log(raw, ["adva152e0"])


def test_metamath_exit_zero_is_not_admission():
    transport.checked_mm_log("adva152e0 adva152e1\nMM> EXIT", ["adva152e0", "adva152e1"])
    for raw in (
        "adva152e0\n?Error: incorrect proof",
        "adva152e0\nWarning: not proved",
        "adva152e0 adva152e1",
        "MM> EXIT",
    ):
        with pytest.raises(ValueError):
            transport.checked_mm_log(raw, ["adva152e0"])
    with pytest.raises(ValueError):
        transport.checked_mm_log("database read, but verification absent")
    transport.checked_mm_log("All proofs in the database were verified in 1.00 s.")


def test_output_is_exclusive_and_child_count_is_bounded(tmp_path):
    supervisor = transport.Supervisor(tmp_path / "evidence")
    supervisor.save("one", "retained")
    with pytest.raises(FileExistsError):
        supervisor.save("one", "overwrite")
    with pytest.raises(FileExistsError):
        transport.Supervisor(tmp_path / "evidence")
    supervisor.calls = [{}] * 24
    with pytest.raises(TimeoutError):
        supervisor.call("never", ["/bin/true"])
    assert (tmp_path / "evidence/one").read_text() == "retained"


def test_shared_deadline_stops_before_child(tmp_path):
    supervisor = transport.Supervisor(tmp_path / "evidence")
    supervisor.deadline = 0
    with pytest.raises(TimeoutError):
        supervisor.call("never", ["/bin/true"])
    assert supervisor.calls == []


def test_missing_backend_preserves_blocked_checkpoint(tmp_path):
    args = SimpleNamespace(
        output=tmp_path / "evidence",
        native="adva-no-such-checker",
        lean="adva-no-such-lean",
        metamath="adva-no-such-metamath",
    )
    result = transport.run(args)
    assert result["status"] == "Blocked"
    assert result["allowed_action"] is None
    assert result["calls"] == []
    assert (args.output / "report.json").is_file()


def test_wrong_export_is_not_a_rust_judgment():
    with pytest.raises(ValueError):
        transport.unpack_export('{"schema":"untrusted"}', "calibrate")


def test_every_metamath_script_disables_pagination_before_reading():
    for pattern in ("*", "adva152*", "adva152bad"):
        commands = transport.mm_commands(Path("/tmp/proofs.mm"), pattern)
        assert commands.splitlines() == [
            "SET SCROLL CONTINUOUS",
            'READ "/tmp/proofs.mm"',
            f"VERIFY PROOF {pattern}",
            "EXIT",
        ]
