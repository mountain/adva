#!/usr/bin/env python3
"""Original finite receipt producer and supervisor; Unknown v0.3.

ChatGPT (OpenAI), through Mingli Yuan's account proxy; not endorsement.
The receiver is a separate implementation and runs in fresh processes.
"""
import argparse
import copy
from fractions import Fraction as F
import json
from pathlib import Path
import resource
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parent
PROFILE = "adva.research.probability-receipt.v0"


def rat(x):
    x = F(x)
    return [x.numerator, x.denominator]


def put(path, value):
    path.write_text(json.dumps(value, ensure_ascii=True, sort_keys=True, indent=2) + "\n")


def produce(c):
    p, ref, f = [[F(*x) for x in c[key]] for key in ("probability", "reference")] + [
        [F(*x) for x in c["observable"]["values"]]]
    density = [a / b for a, b in zip(p, ref)]
    mean = sum(a * b for a, b in zip(p, f))
    variance = sum(a * (b - mean) ** 2 for a, b in zip(p, f))
    atoms, coarse, residual, tower, within, between = [], F(0), F(0), F(0), F(0), F(0)
    for label in sorted(set(c["observation"])):
        indices = [i for i, q in enumerate(c["observation"]) if q == label]
        m, r = sum(p[i] for i in indices), sum(ref[i] for i in indices)
        d = m / r
        coarse += r * d * d
        residual += sum(ref[i] * (density[i] - d) ** 2 for i in indices)
        if m:
            cond = [p[i] / m if i in indices else F(0) for i in range(len(p))]
            cm = sum(a * b for a, b in zip(cond, f))
            cv = sum(a * (b - cm) ** 2 for a, b in zip(cond, f))
            tower += m * cm
            within += m * cv
            between += m * (cm - mean) ** 2
        else:
            cond = cm = cv = None
        atoms.append({"label": label, "reference_mass": rat(r), "probability_mass": rat(m),
                      "density": rat(d), "conditional": None if cond is None else list(map(rat, cond)),
                      "conditional_mean": None if cm is None else rat(cm),
                      "conditional_variance": None if cv is None else rat(cv)})
    claims = {"density": list(map(rat, density)),
              "density_mean": rat(sum(a * b for a, b in zip(ref, density))),
              "density_energy": rat(sum(a * b * b for a, b in zip(ref, density))),
              "density_variance": rat(sum(a * (b - 1) ** 2 for a, b in zip(ref, density))),
              "atoms": atoms, "observed_energy": rat(coarse), "hidden_residual": rat(residual),
              "expectation": rat(mean), "variance": rat(variance), "tower_expectation": rat(tower),
              "within_variance": rat(within), "between_variance": rat(between)}
    return {"profile": PROFILE, "context": copy.deepcopy(c), "claims": claims}


def contexts():
    old = json.loads((ROOT.parent / "finite_group_probability/evidence/attempt-1/result.json").read_text())
    result = []
    for item in old["instances"]:
        n = len(item["carrier"])
        obs = item["observations"]["conjugacy_class" if n == 6 else "parity"]["map"]
        values = [sum(i == j for i, j in enumerate(g)) for g in item["carrier"]] if n == 6 else list(range(n))
        result.append({"question": item["name"] + "-observable-v0",
                       "carrier": [item["name"] + ":" + str(i) for i in range(n)],
                       "reference": [rat(F(x)) for x in item["reference"]],
                       "probability": [rat(F(x)) for x in item["probability"]],
                       "observation": list(map(str, obs)),
                       "observable": {"name": "fixed-point-count" if n == 6 else "index", "unit": "count", "values": list(map(rat, values))},
                       "history": ["0dbd2d8", "finite-group-probability/" + item["name"]],
                       "scope": "complete-declared-finite-carrier"})
    null = copy.deepcopy(result[-1])
    null.update(question="C4-null-event-v0", probability=[rat(1), rat(0), rat(0), rat(0)])
    null["history"].append("replace-by-identity-point-mass")
    return result + [null]


def mutations(c, good):
    cases = [("valid", good)]
    x = copy.deepcopy(good); x["context"]["question"] += "-other"; cases.append(("changed-question", x))
    for mode in ("reference", "observation", "observable"):
        other = copy.deepcopy(c)
        if mode == "reference":
            n = len(c["carrier"])
            other[mode] = [rat(F(1, 2))] + [rat(F(1, 2 * (n - 1)))] * (n - 1)
        elif mode == "observation":
            other[mode] = ["all"] * len(c["carrier"])
        else:
            other[mode]["values"] = [rat(F(*v) + 1) for v in c[mode]["values"]]
        cases.append(("recomputed-" + mode, produce(other)))
    x = copy.deepcopy(good); x["context"]["history"].append("unrequested"); cases.append(("changed-history", x))
    x = copy.deepcopy(good); x["claims"]["hidden_residual"] = rat(0); cases.append(("erased-residual", x))
    x = copy.deepcopy(good); x["claims"]["variance"] = rat(F(*x["claims"]["variance"]) + 1); cases.append(("wrong-variance", x))
    x = copy.deepcopy(good); x["claims"]["density"].pop(); cases.append(("missing-atom", x))
    x = copy.deepcopy(good); x["claims"]["global_close"] = True; cases.append(("global-close", x))
    x = copy.deepcopy(good); x["claims"]["density"][0][0] = True; cases.append(("boolean-rational", x))
    x = copy.deepcopy(good); x["claims"]["atoms"][-1]["conditional"] = [rat(1)] + [rat(0)] * (len(c["carrier"]) - 1); cases.append(("invented-conditional", x))
    assert len(cases) == 12
    return cases


def limits():
    resource.setrlimit(resource.RLIMIT_AS, (128 * 1024**2,) * 2)
    resource.setrlimit(resource.RLIMIT_CPU, (3, 3))
    resource.setrlimit(resource.RLIMIT_FSIZE, (262144, 262144))


def main(output):
    output.mkdir(parents=True, exist_ok=False)
    (output / "contract.json").write_bytes((ROOT / "contract.json").read_bytes())
    started = time.perf_counter()
    results, calls, metrics = [], 0, []
    report = {"profile": PROFILE, "execution": "ExternalFreshProcessReceiver", "search_candidates": 0}
    try:
        for c in contexts():
            folder = output / c["question"]
            folder.mkdir()
            put(folder / "expected.json", c)
            candidate = produce(c)
            cases = mutations(c, candidate)
            family = {"question": c["question"], "claims": candidate["claims"], "cases": []}
            results.append(family)
            for name, receipt in cases:
                if calls >= 36 or time.perf_counter() - started >= 30:
                    raise RuntimeError("UnknownBudget")
                case = folder / name
                case.mkdir()
                put(case / "candidate.json", receipt)
                calls += 1
                t = time.perf_counter()
                with (case / "stdout.json").open("wb") as out, (case / "stderr.txt").open("wb") as err:
                    run = subprocess.run([sys.executable, "-B", "-S", str(ROOT / "receive.py"),
                                          "--expected", str(folder / "expected.json"), "--candidate", str(case / "candidate.json")],
                                         stdout=out, stderr=err, timeout=min(3, max(0.001, 30 - (time.perf_counter() - started))), preexec_fn=limits)
                metrics.append({"question": c["question"], "case": name, "returncode": run.returncode,
                                "wall_seconds": time.perf_counter() - t,
                                "children_rss_highwater_kib": resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss})
                if run.returncode != 0:
                    raise RuntimeError("ReceiverImplementationFailure")
                received = json.loads((case / "stdout.json").read_text())
                expected = "AcceptedFiniteReceipt" if name == "valid" else "InvalidEvidence"
                assert received["outcome"] == expected, (name, received)
                assert received["expected_context"] == c
                if name != "valid":
                    assert received["semantic_delta"] == []
                family["cases"].append({"name": name, "outcome": received["outcome"], "work_units": received["work_units"]})
        report["outcome"] = "PassedFiniteReceiptCampaign"
    except Exception as error:
        report.update(outcome="Failure", failure={"type": type(error).__name__, "message": str(error)})
    report.update(families=results, calls=calls, metrics=metrics, campaign_wall_seconds=time.perf_counter() - started,
                  peak_children_rss_kib=resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss,
                  cost_scope="Includes constructing, serializing, fresh-process verification and reuse; not separately timed. Excludes final report encoding/writing and research/authoring/publication.")
    put(output / "result.json", report)
    print(json.dumps({k: report[k] for k in ("outcome", "calls", "campaign_wall_seconds", "peak_children_rss_kib")}))
    return 0 if report["outcome"] == "PassedFiniteReceiptCampaign" else 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    raise SystemExit(main(parser.parse_args().output))
