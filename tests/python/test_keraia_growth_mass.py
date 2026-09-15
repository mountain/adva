"""Saved, typed divergence certificates and honest same-cut probability gains."""
import hashlib
import json
from fractions import Fraction as F
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
EXPERIMENT = ROOT / "experiments/keraia_growth_mass"
ATTEMPT = EXPERIMENT / "evidence/attempt-1"


def load(name):
    return json.loads((ATTEMPT / name).read_text())


def test_exact_ablation_and_every_terminal_weight():
    for cut in load("primary.json")["cuts"]:
        before, after = cut["cycle_only"], cut["cycle_plus_growth"]
        delta = F(cut["additional_excluded_mass"])
        assert before["accepted"] == after["accepted"]
        assert F(before["unresolved"]) - F(after["unresolved"]) == delta
        assert F(before["upper"]) - F(after["upper"]) == delta
        assert sum(F(after[k]) for k in ("accepted", "certified_nonhalting", "unresolved")) == 1
        sources = [r["source"] for r in cut["growth_certificates"]]
        assert sum((F(1, 2 ** len(c)) for c in sources), F()) == delta
        all_codes = sorted(cut["accepted_codes"] + sources
                           + [r["source"] for r in cut["cycle_certificates"]]
                           + [c for group in cut["unresolved_by_status"].values() for c in group])
        assert all(not b.startswith(a) for a, b in zip(all_codes, all_codes[1:]))
        assert sum((F(1, 2 ** len(c)) for c in all_codes), F()) == 1
    cuts = {row["depth"]: row for row in load("primary.json")["cuts"]}
    assert cuts[15]["additional_excluded_mass"] == "0"
    assert cuts[19]["additional_excluded_mass"] == "19/524288"
    assert cuts[19]["counts"]["additional_growth"] == 13
    assert cuts[19]["cycle_plus_growth"]["unresolved"] == "95519/524288"
    assert "UnknownFuel" not in cuts[19]["unresolved_by_status"]


def test_saved_replay_and_sources_are_still_exact():
    a, b = load("primary.json"), load("fresh-replay.json")
    for result in (a, b):
        assert result["status"] == "Passed" and result["failures"] == []
        for field in ("elapsed_seconds", "peak_rss_kib"):
            result["cost"].pop(field)
        for cut in result["cuts"]:
            cut.pop("timings")
    assert a == b
    for name, digest in a["source_sha256"].items():
        assert hashlib.sha256((ROOT / "experiments" / name).read_bytes()).hexdigest() == digest
        assert hashlib.sha256((ATTEMPT / "sources" / name).read_bytes()).hexdigest() == digest
    execution = load("execution.json")
    assert execution["deterministic_replay_equal"] is True
    assert execution["total_child_work"] <= 162_000_000


def test_receiver_works_with_proposal_kernels_disabled():
    # One bounded receiving-only review, no candidate search or deeper traversal.
    script = r'''
import copy, json, sys
from pathlib import Path
sys.path.insert(0, sys.argv[1])
from common import Budget, M, C
import growth as G
import syntax
p = Path(sys.argv[1])
data = json.loads((p / "evidence/attempt-1/primary.json").read_text())
limits = json.loads((p / "contract.json").read_text())["limits"]
limits.update(max_host_work=2000000, wall_seconds=10)
budget = Budget(limits)
def blocked(*args, **kwargs):
    raise AssertionError("proposal transition used by receiving checker")
M.pure_segment = blocked
syntax.beta = blocked
C.microstep = blocked
G.propose = blocked
receipts = [r for cut in data["cuts"] for r in cut["growth_certificates"]]
receipts += [r["outcome"]["certificate"] for r in data["controls"]["fixtures"].values()
             if r["outcome"]["status"] == "GrowthCandidate"]
for receipt in receipts:
    assert G.check(receipt, receipt["source"], 128, budget)
r = copy.deepcopy(data["controls"]["fixtures"]["growing_stack"]["outcome"]["certificate"])
assert r["pump_entry"] == 0
r["pump_entry"] = False
assert not G.check(r, r["source"], 128, budget)
r = copy.deepcopy(receipts[0]); r["search_fuel"] = 128.0
assert not G.check(r, r["source"], 128, budget)
control = next(r for r in data["controls"]["negative_receipts"] if "certificate" in r)
r = control["certificate"]
assert not G.check(r, r["source"], 128, budget)
print(json.dumps({"received":len(receipts), "work":budget.work, "mutations_refused":3}))
'''
    completed = subprocess.run([sys.executable, "-I", "-S", "-c", script, str(EXPERIMENT)],
                               capture_output=True, text=True, check=True, timeout=15)
    result = json.loads(completed.stdout)
    assert result["received"] == 17 and result["mutations_refused"] == 3


def test_conditional_selector_is_not_global_half_mass():
    selector = load("primary.json")["controls"]["selector_conditional"]
    assert selector["halting"] == selector["certified_growth"] == "1/2"
    assert selector["unresolved"] == "0"
    assert F(selector["global_growth_mass"]) == F(1, 2 ** (selector["program_bits"] + 1))
