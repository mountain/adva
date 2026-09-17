#!/usr/bin/env python3
"""Original finite decision producer/supervisor, Unknown v0.3.

ChatGPT (OpenAI), through Mingli Yuan's account proxy; not his review.
The producer enumerates four policies; the receiver verifies local minima.
"""
import argparse
import copy
from fractions import Fraction as F
import hashlib
import importlib.util
import itertools
import json
from pathlib import Path
import resource
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parent
PROFILE = "adva.research.finite-decision.v0"
spec = importlib.util.spec_from_file_location("probability_producer", ROOT.parent / "probability_receipt/run.py")
parent = importlib.util.module_from_spec(spec)
spec.loader.exec_module(parent)


def rat(x):
    x = F(x)
    return [x.numerator, x.denominator]


def put(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def fixture(name, prior=(F(1, 2), F(1, 2)), kernel=((F(3, 4), F(1, 4)), (F(1, 4), F(3, 4))), loss=((0, 1), (1, 0)), cost=F(1, 8)):
    return {"question": name, "states": ["s0", "s1"], "observations": ["o0", "o1"],
            "actions": ["a0", "a1"], "prior": list(map(rat, prior)),
            "kernel": [list(map(rat, row)) for row in kernel], "kernel_direction": "observation-given-state",
            "loss": [list(map(rat, row)) for row in loss], "loss_unit": "synthetic-loss-unit",
            "observation_cost": rat(cost), "history": ["finite-decision-20260917", name],
            "scope": "complete-declared-finite-decision"}


def produce(c):
    p = [F(*v) for v in c["prior"]]
    k, loss = [[[F(*v) for v in row] for row in c[field]] for field in ("kernel", "loss")]
    joint = [[p[s] * k[s][o] for o in range(2)] for s in range(2)]
    pc = {"question": c["question"] + "/joint", "carrier": [f"s{s}:o{o}" for s in range(2) for o in range(2)],
          "reference": [rat(F(1, 4)) for _ in range(4)],
          "probability": [rat(joint[s][o]) for s in range(2) for o in range(2)],
          "observation": c["observations"] * 2,
          "observable": {"name": "state-index", "unit": "index", "values": [rat(v) for v in (0, 0, 1, 1)]},
          "history": copy.deepcopy(c["history"]), "scope": "complete-declared-finite-carrier"}
    prior_risks = [sum(p[s] * loss[s][a] for s in range(2)) for a in range(2)]
    baseline = min(prior_risks)
    records = []
    for o in range(2):
        mass = sum(joint[s][o] for s in range(2))
        posterior = [joint[s][o] / mass for s in range(2)] if mass else None
        risks = [sum(posterior[s] * loss[s][a] for s in range(2)) for a in range(2)] if mass else None
        records.append({"label": c["observations"][o], "mass": rat(mass),
                        "posterior": None if posterior is None else list(map(rat, posterior)),
                        "risks": None if risks is None else list(map(rat, risks)),
                        "minimizers": None if risks is None else [c["actions"][a] for a in range(2) if risks[a] == min(risks)]})
    policies = []
    for policy in itertools.product(range(2), repeat=2):
        risk = sum(joint[s][o] * loss[s][policy[o]] for s in range(2) for o in range(2))
        policies.append({"actions": [c["actions"][a] for a in policy], "risk": rat(risk)})
    informed = min(F(*q["risk"]) for q in policies)
    gross = baseline - informed
    net = gross - F(*c["observation_cost"])
    claims = {"observations": records, "prior_risks": list(map(rat, prior_risks)),
              "prior_minimizers": [c["actions"][a] for a in range(2) if prior_risks[a] == baseline],
              "risk_without_observation": rat(baseline), "risk_with_observation": rat(informed),
              "gross_value": rat(gross), "net_value": rat(net),
              "acquisition_minimizers": ["observe"] if net > 0 else ["skip"] if net < 0 else ["skip", "observe"]}
    return {"profile": PROFILE, "context": copy.deepcopy(c), "probability_receipt": parent.produce(pc), "claims": claims}, policies


def cases():
    contexts = [fixture("low-cost"), fixture("high-cost", cost=F(3, 8)),
                fixture("changed-loss", loss=((0, 3), (1, 0)), cost=0),
                fixture("asymmetric-reuse", prior=(F(2, 3), F(1, 3)), kernel=((F(3, 4), F(1, 4)), (F(1, 2), F(1, 2))), loss=((0, 2), (3, 0)), cost=F(1, 12)),
                fixture("zero-event", kernel=((1, 0), (1, 0)), cost=0)]
    results, summaries = [], []
    for c in contexts:
        good, policies = produce(c)
        summaries.append({"context": c, "claims": good["claims"], "policies": policies})
        variants = [("valid", good)]
        changed = copy.deepcopy(c); changed["loss"][0][0] = rat(F(*changed["loss"][0][0]) + 1)
        variants.append(("recomputed-loss", produce(changed)[0]))
        changed = copy.deepcopy(c); changed["actions"].reverse()
        variants.append(("recomputed-action-roles", produce(changed)[0]))
        x = copy.deepcopy(good); x["probability_receipt"]["context"]["question"] += "-other"; variants.append(("wrong-parent", x))
        x = copy.deepcopy(good); x["claims"]["observations"][0]["posterior"] = [rat(1), rat(0)]; variants.append(("wrong-posterior", x))
        x = copy.deepcopy(good); x["claims"]["net_value"] = rat(F(*x["claims"]["net_value"]) + 1); variants.append(("wrong-net-value", x))
        x = copy.deepcopy(good); x["claims"]["native_free"] = True; variants.append(("unsupported-free", x))
        x = copy.deepcopy(good); x["claims"]["prior_risks"][0][0] = True; variants.append(("boolean-rational", x))
        for name, candidate in variants:
            results.append((c["question"] + "/" + name, c, candidate, "AcceptedFiniteDecision" if name == "valid" else "InvalidEvidence"))
    c = contexts[0]; good = produce(c)[0]
    for field, value in (("question", "another-question"), ("loss_unit", "other-unit"), ("kernel_direction", "state-given-observation"), ("history", ["another-history"])):
        x = copy.deepcopy(good); x["context"][field] = value
        results.append(("extra/changed-" + field, c, x, "InvalidEvidence"))
    x = copy.deepcopy(good); x["claims"]["prior_minimizers"] = ["a0"]
    results.append(("extra/missing-tied-action", c, x, "InvalidEvidence"))
    z = contexts[-1]; x = produce(z)[0]; x["claims"]["observations"][1]["posterior"] = [rat(F(1, 2)), rat(F(1, 2))]
    results.append(("extra/invented-null-posterior", z, x, "InvalidEvidence"))
    invalid = copy.deepcopy(c); invalid["kernel"][0][0] = rat(1)
    results.append(("extra/invalid-kernel-mass", invalid, good, "InvalidContext"))
    invalid = fixture("parent-profile-limit", prior=(F(1, 61), F(60, 61)), kernel=((F(1, 59), F(58, 59)), (F(1, 59), F(58, 59))))
    results.append(("extra/unsupported-parent-bound", invalid, good, "InvalidContext"))
    assert len(results) == 48
    return results, summaries


def limits():
    resource.setrlimit(resource.RLIMIT_AS, (128 * 1024**2,) * 2)
    resource.setrlimit(resource.RLIMIT_CPU, (3, 3))
    resource.setrlimit(resource.RLIMIT_FSIZE, (262144, 262144))


def main(output):
    output.mkdir(parents=True, exist_ok=False)
    (output / "contract.json").write_bytes((ROOT / "contract.json").read_bytes())
    started = time.perf_counter()
    results, checks, units = [], 0, 0
    costs = {"construction_seconds": 0.0, "serialization_seconds": 0.0, "receiving_seconds": 0.0}
    report = {"profile": PROFILE, "search_candidates": 0, "deterministic_policies_per_valid_instance": 4,
              "execution": "ExternalFreshProcessDecisionReceiver", "new_vocabulary": 0}
    try:
        t = time.perf_counter(); fixed, summaries = cases(); costs["construction_seconds"] += time.perf_counter() - t
        report["instances"] = summaries
        for name, c, candidate, expected in fixed:
            remaining = 30 - (time.perf_counter() - started)
            if len(results) >= 48 or remaining <= 0:
                raise RuntimeError("UnknownBudget")
            folder = output / name; folder.mkdir(parents=True)
            t = time.perf_counter(); put(folder / "expected.json", c); put(folder / "candidate.json", candidate)
            costs["serialization_seconds"] += time.perf_counter() - t
            t = time.perf_counter()
            with (folder / "stdout.json").open("wb") as out, (folder / "stderr.txt").open("wb") as err:
                process = subprocess.run([sys.executable, "-B", "-S", str(ROOT / "receive.py"), "--expected", str(folder / "expected.json"), "--candidate", str(folder / "candidate.json")], stdout=out, stderr=err, timeout=min(3, remaining), preexec_fn=limits)
            elapsed = time.perf_counter() - t; costs["receiving_seconds"] += elapsed
            row = {"case": name, "returncode": process.returncode, "wall_seconds": elapsed}
            results.append(row)
            assert process.returncode == 0, row
            value = json.loads((folder / "stdout.json").read_text())
            row.update(outcome=value["outcome"], work_units=value["work_units"])
            units += value["work_units"]
            assert value["outcome"] == expected, (name, value); checks += 1
            assert value["expected_context"] == c; checks += 1
            assert all(value[k] is False for k in ("native_authority", "close_authorized", "free_authorized")); checks += 1
            if expected != "AcceptedFiniteDecision":
                assert value["semantic_delta"] == []; checks += 1
        assert units <= 100000
        report["outcome"] = "PassedFiniteDecisionCampaign"
    except Exception as error:
        report.update(outcome="Failure", failure={"type": type(error).__name__, "message": str(error)})
    report.update(results=results, assertions=checks, work_units=units, costs=costs,
                  campaign_wall_seconds=time.perf_counter() - started,
                  peak_children_rss_kib=resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss,
                  peak_supervisor_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                  cost_scope="Construction includes parent receipt construction and mutation candidates. Serialization covers per-case input writes. Receiving includes fresh process startup and parent checking. Reuse is included, not timed separately. Final report encoding/writing, archiving, research and publication excluded.")
    report["source_sha256"] = {str(p.relative_to(ROOT.parent.parent)): hashlib.sha256(p.read_bytes()).hexdigest() for p in (ROOT / "contract.json", ROOT / "run.py", ROOT / "receive.py", ROOT.parent / "probability_receipt/run.py", ROOT.parent / "probability_receipt/receive.py")}
    put(output / "result.json", report)
    print(json.dumps({k: report[k] for k in ("outcome", "assertions", "work_units", "campaign_wall_seconds", "peak_children_rss_kib")}))
    return 0 if report["outcome"] == "PassedFiniteDecisionCampaign" else 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    raise SystemExit(main(parser.parse_args().output))
