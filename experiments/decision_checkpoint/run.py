#!/usr/bin/env python3
"""Original finite checkpoint campaign, Unknown v0.3.

ChatGPT (OpenAI), through Mingli Yuan's authorized proxy; not his review.
The producer and supervisor do not import the new receiving implementation.
"""
import argparse
import copy
from fractions import Fraction as F
import hashlib
import importlib.util
import json
from pathlib import Path
import resource
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parent
PROFILE = "adva.research.decision-checkpoint.v0"
spec = importlib.util.spec_from_file_location("checkpoint_composition_producer", ROOT.parent / "decision_scale_composition/run.py")
producer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(producer)
put, rat = producer.put, producer.rat


def produce(expected):
    prefix = producer.produce(expected["prefix_request"])
    endpoint = prefix["summary"]["final_context"]
    checkpoint = {"prefix_receipt": prefix, "endpoint": copy.deepcopy(endpoint),
                  "pending_step": copy.deepcopy(expected["pending_step"]),
                  "allowance": copy.deepcopy(expected["allowance"])}
    allowance_after = copy.deepcopy(expected["allowance"])
    next_receipt = None
    if len(endpoint["history"]) < 4 and allowance_after["remaining"] > 0:
        next_receipt = producer.producer.receipt(dict(source=copy.deepcopy(endpoint), **expected["pending_step"]))
        allowance_after["spent"] += 1
        allowance_after["remaining"] -= 1
    return {"profile": PROFILE, "checkpoint": checkpoint, "next_receipt": next_receipt,
            "allowance_after": allowance_after}


def fixtures():
    f = producer.producer.producer.fixture
    families = [("symmetric", f("checkpoint-symmetric")),
                ("asymmetric-reuse", f("checkpoint-asymmetric", prior=(F(2, 3), F(1, 3)),
                 kernel=((F(3, 4), F(1, 4)), (F(1, 2), F(1, 2))),
                 loss=((0, 2), (3, 0)), cost=F(1, 12)))]
    rows = []
    for name, source in families:
        source["history"] = source["history"][:1]
        expected = {"prefix_request": {"source": source, "steps": [
            {"factor": [2, 1], "target_unit": "middle-unit", "step": name + ":first"},
            {"factor": [1, 2], "target_unit": source["loss_unit"], "step": name + ":second"}]},
            "pending_step": {"factor": [3, 2], "target_unit": "continued-unit", "step": name + ":third"},
            "allowance": {"grant": 3, "spent": 2, "remaining": 1}}
        good = produce(expected)
        rows.append((name + "/continue", expected, good, "AcceptedCheckpointContinuation"))
        saturated = copy.deepcopy(expected)
        saturated["prefix_request"]["source"]["history"].append(name + ":earlier-retained")
        paused = produce(saturated)
        rows.append((name + "/capacity", saturated, paused, "PausedHistoryCapacity"))
        rows.append((name + "/capacity-reload", saturated, copy.deepcopy(paused), "PausedHistoryCapacity"))
        exhausted = copy.deepcopy(expected)
        exhausted["allowance"] = {"grant": 3, "spent": 3, "remaining": 0}
        rows.append((name + "/no-allowance", exhausted, produce(exhausted), "PausedAllowance"))
        x = produce(exhausted); x["next_receipt"] = copy.deepcopy(good["next_receipt"])
        rows.append((name + "/execute-without-allowance", exhausted, x, "InvalidEvidence"))
        x = copy.deepcopy(paused); x["checkpoint"]["endpoint"]["history"].pop(0)
        rows.append((name + "/delete-history", saturated, x, "InvalidEvidence"))
        x = copy.deepcopy(paused); x["checkpoint"]["allowance"] = {"grant": 3, "spent": 0, "remaining": 3}
        rows.append((name + "/reset-allowance", saturated, x, "InvalidEvidence"))
        x = copy.deepcopy(paused); x["checkpoint"]["pending_step"]["factor"] = [1, 1]
        rows.append((name + "/replace-pending", saturated, x, "InvalidEvidence"))
        changed = copy.deepcopy(saturated); changed["prefix_request"]["source"]["history"][0] = "different-origin"
        rows.append((name + "/replace-prefix-history", saturated, produce(changed), "InvalidEvidence"))
        x = copy.deepcopy(paused); x["checkpoint"]["prefix_receipt"]["links"][1]["target_receipt"]["claims"]["net_value"] = [7, 1]
        rows.append((name + "/false-prefix-result", saturated, x, "InvalidEvidence"))
        x = copy.deepcopy(paused); x["next_receipt"] = copy.deepcopy(good["next_receipt"])
        rows.append((name + "/execute-at-capacity", saturated, x, "InvalidEvidence"))
        x = copy.deepcopy(paused); x["allowance_after"] = copy.deepcopy(good["allowance_after"])
        rows.append((name + "/debit-on-pause", saturated, x, "InvalidEvidence"))
        changed = dict(source=copy.deepcopy(good["checkpoint"]["endpoint"]), **expected["pending_step"])
        changed["source"]["loss_unit"] = "substituted-source-unit"
        x = copy.deepcopy(good); x["next_receipt"] = producer.producer.receipt(changed)
        rows.append((name + "/wrong-next-source", expected, x, "InvalidEvidence"))
        x = copy.deepcopy(good); x["next_receipt"]["target_receipt"]["claims"]["net_value"] = [7, 1]
        rows.append((name + "/false-next-result", expected, x, "InvalidEvidence"))
        x = copy.deepcopy(good); x["allowance_after"] = copy.deepcopy(expected["allowance"])
        rows.append((name + "/missing-debit", expected, x, "InvalidEvidence"))
    for name, path, value in [
        ("boolean-allowance", ["allowance", "remaining"], True),
        ("negative-allowance", ["allowance", "remaining"], -1),
        ("unbalanced-allowance", ["allowance", "spent"], 0),
        ("zero-pending-factor", ["pending_step", "factor"], [0, 1]),
        ("boolean-pending-factor", ["pending_step", "factor"], [True, 1]),
        ("oversized-pending-factor", ["pending_step", "factor"], [17, 1]),
    ]:
        bad = copy.deepcopy(saturated); cursor = bad
        for key in path[:-1]: cursor = cursor[key]
        cursor[path[-1]] = value
        rows.append(("context/" + name, bad, paused, "InvalidContext"))
    bad = copy.deepcopy(saturated)
    bad["prefix_request"]["source"]["loss"][0][1] = [8, 1]
    bad["pending_step"]["factor"] = [16, 1]
    rows.append(("context/pending-numeric-overflow", bad, paused, "InvalidContext"))
    assert len(rows) == 37
    return rows


def limits():
    resource.setrlimit(resource.RLIMIT_AS, (128 * 1024**2,) * 2)
    resource.setrlimit(resource.RLIMIT_CPU, (3, 3))
    resource.setrlimit(resource.RLIMIT_FSIZE, (262144, 262144))


def main(output):
    output.mkdir(parents=True, exist_ok=False)
    (output / "contract.json").write_bytes((ROOT / "contract.json").read_bytes())
    started = time.perf_counter(); metrics = []; assertions = 0; units = 0
    phases = dict(construction_seconds=0.0, input_serialization_seconds=0.0, receiving_seconds=0.0)
    report = {"profile": PROFILE, "search_candidates": 0, "new_vocabulary": 0}
    retained = {}
    try:
        t = time.perf_counter(); rows = fixtures(); phases["construction_seconds"] = time.perf_counter() - t
        for name, expected, candidate, wanted in rows:
            remaining = 30 - (time.perf_counter() - started)
            if len(metrics) >= 40 or remaining <= 0: raise RuntimeError("UnknownBudget")
            folder = output / name; folder.mkdir(parents=True)
            t = time.perf_counter()
            if name.endswith("capacity-reload"):
                saved = json.loads((output / name.removesuffix("-reload") / "stdout.json").read_text())
                candidate = {"profile": PROFILE, "checkpoint": saved["checkpoint_retained"],
                             "next_receipt": None, "allowance_after": saved["allowance_after"]}
            put(folder / "expected.json", expected); put(folder / "candidate.json", candidate)
            phases["input_serialization_seconds"] += time.perf_counter() - t
            t = time.perf_counter()
            with (folder / "stdout.json").open("wb") as out, (folder / "stderr.txt").open("wb") as err:
                p = subprocess.run([sys.executable, "-B", "-S", str(ROOT / "receive.py"),
                    "--expected", str(folder / "expected.json"), "--candidate", str(folder / "candidate.json")],
                    stdout=out, stderr=err, timeout=min(3, remaining), preexec_fn=limits)
            elapsed = time.perf_counter() - t; phases["receiving_seconds"] += elapsed
            row = dict(case=name, returncode=p.returncode, wall_seconds=elapsed); metrics.append(row)
            assert p.returncode == 0, row
            r = json.loads((folder / "stdout.json").read_text()); units += r["work_units"]
            row.update(outcome=r["outcome"], reason=r["reason"], work_units=r["work_units"],
                       prefix_checked=r["prefix_checked"], next_checked=r["next_checked"])
            assert r["outcome"] == wanted, (name, r); assertions += 1
            assert r["expected_request"] == expected; assertions += 1
            assert all(r[k] is False for k in ("native_authority", "close_authorized", "free_authorized")); assertions += 1
            if wanted in ("AcceptedCheckpointContinuation", "PausedHistoryCapacity", "PausedAllowance"):
                assert r["checkpoint_retained"] == candidate["checkpoint"]; assertions += 1
                assert r["allowance_after"] == candidate["allowance_after"]; assertions += 1
                assert r["prefix_checked"] is True; assertions += 1
                assert r["next_checked"] is (wanted == "AcceptedCheckpointContinuation"); assertions += 1
                row["checkpoint_sha256"] = hashlib.sha256(json.dumps(r["checkpoint_retained"], sort_keys=True, separators=(",", ":")).encode()).hexdigest()
                retained[name] = r["checkpoint_retained"]
                if name.endswith("capacity-reload"):
                    assert retained[name.removesuffix("-reload")] == r["checkpoint_retained"]; assertions += 1
                if wanted == "AcceptedCheckpointContinuation":
                    c = candidate["checkpoint"]["endpoint"]
                    after = candidate["next_receipt"]["target_receipt"]["context"]
                    assert len(c["history"]) == 3 and after["history"] == c["history"] + [expected["pending_step"]["step"]]; assertions += 1
            else:
                assert r["checkpoint_retained"] is None and r["allowance_after"] is None; assertions += 1
            if wanted != "AcceptedCheckpointContinuation":
                assert r["semantic_delta"] == []; assertions += 1
        report["outcome"] = "PassedDecisionCheckpointCampaign"
    except Exception as error:
        report.update(outcome="Failure", failure={"type": type(error).__name__, "message": str(error)})
    report.update(metrics=metrics, assertions=assertions, work_units=units, phases=phases,
        campaign_wall_seconds=time.perf_counter() - started,
        peak_children_rss_kib=resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss,
        peak_supervisor_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        cost_scope="Construction, input writes, fresh child startup and cumulative nested checks included. Reuse and checkpoint roundtrip included, not separately timed. Final report writing, archive, research and publication excluded.")
    paths = [ROOT / f for f in ("contract.json", "run.py", "receive.py")]
    paths += [ROOT.parent / d / f for d in ("decision_scale_composition", "decision_scale", "finite_decision", "probability_receipt") for f in ("run.py", "receive.py")]
    report["source_sha256"] = {str(p.relative_to(ROOT.parent.parent)): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
    put(output / "result.json", report)
    print(json.dumps({k: report[k] for k in ("outcome", "assertions", "work_units", "campaign_wall_seconds", "peak_children_rss_kib")}))
    return 0 if report["outcome"] == "PassedDecisionCheckpointCampaign" else 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(); parser.add_argument("--output", type=Path, required=True)
    raise SystemExit(main(parser.parse_args().output))
