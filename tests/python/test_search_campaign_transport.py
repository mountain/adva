"""Campaign protocol and selection tests without external proof assistants."""

import importlib.util
import json
import sys
import types
from pathlib import Path
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = "campaign_transport_tests"
package = types.ModuleType(PACKAGE)
package.__path__ = [str(ROOT / "python/adva")]
sys.modules[PACKAGE] = package
spec = importlib.util.spec_from_file_location(
    PACKAGE + ".search_campaign", ROOT / "python/adva/search_campaign.py"
)
campaign = importlib.util.module_from_spec(spec)
spec.loader.exec_module(campaign)


def pilot_rows():
    return [
        {
            "depth": depth,
            "seed": seed,
            "expand": direction,
            "policy": policy,
            "status": "Reached",
            "steps": 3,
            "cost": {"work_units": 100},
        }
        for depth in (2, 3, 4)
        for seed in (1, 7, 19)
        for direction in (True, False)
        for policy in campaign.POLICIES
    ]


def test_ranking_prefers_success_then_total_work_then_steps_then_fixed_tie():
    arms = pilot_rows()
    assert campaign.choose_policies(arms)["winners"] == {
        "expansion": "random",
        "contraction": "random",
    }
    for arm in arms:
        if arm["policy"] == "tabu":
            arm["cost"]["work_units"] = 90
    assert set(campaign.choose_policies(arms)["winners"].values()) == {"tabu"}
    for arm in arms:
        if arm["policy"] == "hybrid":
            arm["cost"]["work_units"] = 90
            arm["steps"] = 2
    assert set(campaign.choose_policies(arms)["winners"].values()) == {"hybrid"}
    for arm in arms:
        if arm["policy"] == "hybrid" and arm["expand"] and arm["seed"] == 1:
            arm["status"] = "Unknown"
    assert campaign.choose_policies(arms)["winners"] == {
        "expansion": "tabu",
        "contraction": "hybrid",
    }


def test_ranking_requires_complete_matched_pilot_and_some_success():
    with pytest.raises(ValueError):
        campaign.choose_policies(pilot_rows()[:-1])
    arms = pilot_rows()
    for arm in arms:
        arm["status"] = "Unknown"
    with pytest.raises(ValueError, match="insufficient"):
        campaign.choose_policies(arms)
    arms = pilot_rows()
    arms[0]["seed"] = 1001
    with pytest.raises(ValueError):
        campaign.choose_policies(arms)


def test_schedule_is_exactly_100_new_seed_two_direction_rounds():
    assert campaign.expected_arms("round:1:tabu:hybrid") == [
        (2, True, 1001, "tabu"),
        (2, False, 1001, "hybrid"),
    ]
    assert campaign.expected_arms("round:100:tabu:hybrid") == [
        (2, True, 1100, "tabu"),
        (2, False, 1100, "hybrid"),
    ]
    assert len(campaign.expected_arms("pilot:4")) == 18
    for mode in ("round:0:tabu:hybrid", "round:101:tabu:hybrid", "round:1:unknown:tabu", "pilot:5"):
        with pytest.raises(ValueError):
            campaign.expected_arms(mode)


def test_decode_rejects_duplicates_nonfinite_and_stale_schema():
    with pytest.raises(ValueError):
        campaign._decode('{"x":1,"x":2}')
    with pytest.raises(ValueError):
        campaign._decode('{"x":NaN}')
    with pytest.raises(ValueError):
        campaign.unpack('{"schema":"old"}', "pilot:2")


def test_frozen_external_admission_still_rejects_sorry_and_mm_errors():
    with pytest.raises(ValueError):
        campaign.frozen.checked_lean_log("'adva152e0' depends on axioms: [sorryAx]", ["adva152e0"])
    with pytest.raises(ValueError):
        campaign.frozen.checked_mm_log("adva152e0\n?Error: mismatching proof", ["adva152e0"])
    assert (
        campaign.frozen.digest(ROOT / "python/adva/verifier_search.py") == campaign.OLD_PYTHON_SHA
    )
    assert (
        campaign.frozen.digest(ROOT / "crates/adva-witness/examples/verifier_search.rs")
        == campaign.OLD_RUST_SHA
    )


def test_fresh_output_and_pins_are_enforced(tmp_path):
    supervisor = campaign.Supervisor(tmp_path / "evidence")
    path = supervisor.save("pin", b"original")
    supervisor.pins[str(path)] = campaign.frozen.digest(path)
    supervisor.check_pins()
    with pytest.raises(FileExistsError):
        supervisor.save("pin", b"overwritten")
    with pytest.raises(FileExistsError):
        campaign.Supervisor(tmp_path / "evidence")
    path.write_bytes(b"changed")
    with pytest.raises(ValueError, match="protected file changed"):
        supervisor.check_pins()


def test_deadline_and_child_cap_prevent_launch(tmp_path):
    supervisor = campaign.Supervisor(tmp_path / "evidence")
    supervisor.calls = [{}] * 424
    with pytest.raises(TimeoutError):
        supervisor.call("never", ["/bin/true"])
    assert not (supervisor.output / "never.stdout").exists()
    supervisor.calls = []
    supervisor.deadline = 0
    with pytest.raises(TimeoutError):
        supervisor.call("never", ["/bin/true"])


def test_missing_backend_retains_blocked_report_without_running_rounds(tmp_path):
    args = SimpleNamespace(
        output=tmp_path / "evidence",
        native="no-campaign-native",
        lean="no-campaign-lean",
        metamath="no-campaign-mm",
    )
    result = campaign.run(args)
    assert result["status"] == "Blocked"
    assert result["completed_rounds"] == 0
    assert result["calls"] == []
    assert result["allowed_action"] is None
    assert json.loads((args.output / "report.json").read_text())["status"] == "Blocked"
