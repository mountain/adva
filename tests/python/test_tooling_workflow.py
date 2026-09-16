"""Receive the tooling workflow helpers; they run no research campaign.

`docs/TOOLING_WORKFLOW.md` section 6 lists three first deliverables: read-only
navigation, a problem worksheet, and a small bounded execution adapter. These tests
check the properties that document states, not just that the commands return zero:
labels that keep recorded facts apart from observed ones, missing fields that stay
missing, refusals that are not folded into a success, and a `NotRun` that keeps its
reason.
"""

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts"


def load(name: str):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


NAVIGATE = load("navigate")
CARD = load("problem_card")
BOUNDED = load("run_bounded")


def run(script: str, *arguments: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(SCRIPTS / script), *arguments],
                          capture_output=True, text=True, cwd=ROOT, check=False)


def test_navigation_keeps_recorded_facts_apart_from_observed_ones():
    done = run("navigate.py", "futamura")
    assert done.returncode == 0
    assert "no conclusion is inferred from titles" in done.stdout
    assert "RECORDED" in done.stdout and "OBSERVED HERE" in done.stdout
    rows = json.loads(run("navigate.py", "futamura", "--json").stdout)
    assert len(rows) == 2
    for row in rows:
        assert row["state"] in {"historical", "runnable-here", "not-yet-executed"}
        assert row["recorded_status"] == "bounded-experiment"
        assert row["evidence_present"], row
        assert row["state_reason"]


def test_navigation_reports_absence_without_claiming_absence_of_work():
    done = run("navigate.py", "no-such-question-anywhere")
    assert done.returncode == 1
    assert "not evidence that no such work exists" in done.stderr


def test_navigation_exposes_the_follow_up_correction_index():
    rows = json.loads(run("navigate.py", "--corrections", "--json").stdout)
    assert rows, "the record contains corrections and they must be reachable"
    for row in rows:
        assert row["note"].startswith("docs/")
        assert row["corrects"] and all(name.endswith(".md") for name in row["corrects"])
        assert row["markers"]


def test_the_problem_card_template_states_all_ten_fields():
    done = run("problem_card.py", "template")
    assert done.returncode == 0
    for key, label, _ in CARD.FIELDS:
        assert key in done.stdout and label in done.stdout
    assert "predecessor" in done.stdout and "change_reason" in done.stdout
    assert "receiver_confirms_same_question" in done.stdout


def complete_card():
    """A card that satisfies every declared rule; the ten text fields are filled first."""
    card = {key: "filled" for key, _, _ in CARD.TEXT_FIELDS}
    card.update({
        "question_id": "tooling-selftest",
        "round": 1,
        "predecessor": None,
        "change_reason": "",
        "budget": {"wall_seconds": 60, "launches": 8},
        "stop_conditions": ["stop at the first mismatch"],
        "attempts": [{"command": "python3 -c pass", "output_dir": "/tmp/x",
                      "stop_condition": "one run", "outcome": "completed",
                      "budget": {"wall_seconds": 30, "launches": 1}}],
        "handoff": {"question": "q", "candidates": "c", "checks": "k",
                    "evidence": "e", "residuals": "r",
                    "receiver_confirms_same_question": True},
    })
    return card


def test_a_complete_card_passes_and_missing_fields_stay_missing(tmp_path):
    card = complete_card()
    assert CARD.check_card(card, tmp_path / "card.json") == []

    del card["raw_question"]
    card["next_step"] = "   "
    problems = CARD.check_card(card, tmp_path / "card.json")
    assert any("raw_question" in problem for problem in problems)
    assert any("next_step" in problem for problem in problems)
    assert len(problems) == 2

    written = tmp_path / "card.json"
    written.write_text(json.dumps(card))
    done = run("problem_card.py", "check", str(written))
    assert done.returncode == 1
    assert "none filled in for you" in done.stdout


def test_a_failure_must_be_retained_and_a_notrun_must_keep_its_reason(tmp_path):
    card = complete_card()
    card["attempts"][0]["outcome"] = "failed"
    problems = CARD.check_card(card, tmp_path / "card.json")
    assert any("first_failure" in problem for problem in problems)

    card["attempts"][0]["outcome"] = "refused"
    card["attempts"][0]["first_failure"] = "the checker refused the input"
    assert CARD.check_card(card, tmp_path / "card.json") == []

    card["attempts"][0] = {"command": "x", "output_dir": "y", "stop_condition": "z",
                           "outcome": "not-run",
                           "budget": {"wall_seconds": 30, "launches": 1}}
    problems = CARD.check_card(card, tmp_path / "card.json")
    assert any("reason" in problem for problem in problems)


def test_an_unconfirmed_handoff_and_a_changed_question_stay_open(tmp_path):
    card = complete_card()
    card["handoff"]["receiver_confirms_same_question"] = False
    assert any("same question" in problem
               for problem in CARD.check_card(card, tmp_path / "card.json"))

    card = complete_card()
    card["handoff"]["receiver_confirms_same_question"] = True
    card["budget"] = {"wall_seconds": 30, "launches": 4}
    predecessor = complete_card()
    (tmp_path / "previous.json").write_text(json.dumps(predecessor))
    card["predecessor"] = "previous.json"
    problems = CARD.check_card(card, tmp_path / "card.json")
    assert any("change_reason" in problem for problem in problems)

    card["change_reason"] = "a smaller budget was declared for the successor round"
    assert CARD.check_card(card, tmp_path / "card.json") == []


def test_every_bounded_plan_declares_scope_budget_and_residual():
    assert set(BOUNDED.PLANS) == {"exchange-chain", "data-machine-sample"}
    for name, plan in BOUNDED.PLANS.items():
        assert plan["scope"] and plan["unknown"] and plan["remediation"]
        assert plan["requirements"]
        assert plan["budget"]["wall_seconds"] > 0 and plan["budget"]["cpu_seconds"] > 0
        assert plan["budget"]["output_bytes"] > 0


def test_the_exchange_plan_separates_its_facts_and_never_folds_them(tmp_path):
    done = run("run_bounded.py", "--plan", "exchange-chain", "--output-dir", str(tmp_path))
    assert done.returncode == 0
    assert "green success by itself" in done.stdout
    assert "DisclosedByteChainChecked" in done.stdout
    assert "Withheld" in done.stdout
    assert "Unverified" in done.stdout
    assert "RLIMIT_AS" in done.stdout
    record = json.loads((tmp_path / "bounded-run-exchange-chain.json").read_text())
    assert record["execution"] == "completed"
    assert record["checker verdict"]["top level"]["status"] == ["DisclosedByteChainChecked"]
    assert record["checker verdict"]["repeated per row"]["semantic_acceptance"] == ["Withheld"]
    assert {entry["state"] for entry in record["limits"]} <= {"applied", "refused-by-host"}


def test_a_plan_that_cannot_run_here_reports_notrun_with_its_reason(tmp_path):
    BOUNDED.PLANS["selftest-missing"] = {
        "command": [sys.executable, "-c", "print('never')"],
        "scope": "no scope; this plan exists to exercise the not-run path",
        "requirements": [("file", "does-not-exist/at-all.py")],
        "remediation": "create does-not-exist/at-all.py",
        "verdict_keys": ["status"], "separate_keys": [],
        "budget": {"wall_seconds": 5, "cpu_seconds": 5, "output_bytes": 1024},
        "unknown": "everything, because nothing ran",
    }
    try:
        exit_code = BOUNDED.run_plan("selftest-missing", BOUNDED.PLANS["selftest-missing"],
                                     tmp_path, as_json=True)
    finally:
        del BOUNDED.PLANS["selftest-missing"]
    assert exit_code == 3
    record = json.loads((tmp_path / "bounded-run-selftest-missing.json").read_text())
    assert record["execution"].startswith("not-started")
    assert record["remediation"] == "create does-not-exist/at-all.py"
    assert record["material accepted"] == "no"
