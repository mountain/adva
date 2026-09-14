"""Fixed integration-review invocations; immutable output directories."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
EXP = HERE.parent
ROOT = HERE.parents[2]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("phase", choices=("before", "after"))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    out = args.output.resolve()
    start = time.monotonic()
    report = {"phase": args.phase, "status": "Running", "invocations": [], "source_sha256": {}}
    for path in [EXP / "check.py", EXP / "compose.py", EXP / "run_composition.py", HERE / "probe.py",
                 ROOT / "experiments/zot_prefix_machine/machine.cjs",
                 ROOT / "experiments/zot_prefix_machine/verify.cjs",
                 ROOT / "experiments/zot_prefix_machine/keraia-boundary.cjs"]:
        report["source_sha256"][str(path.relative_to(ROOT))] = hashlib.sha256(path.read_bytes()).hexdigest()
    py = ["prlimit", "--as=536870912", "--cpu=40", "--fsize=16777216", sys.executable, "-B", "-S"]
    composition = ("composition", py + [str(EXP / "run_composition.py"), "--output-dir", str(out / "composition")], 35)
    commands = [
        ("receiver", py + [str(EXP / "check.py"), "--output", str(out / "receiver.json")], 15),
        composition,
        ("node", ["prlimit", "--cpu=35", "--fsize=16777216", "node", "--max-old-space-size=256", str(ROOT / "experiments/zot_prefix_machine/run.cjs")], 35),
        ("probe", py + [str(HERE / "probe.py")], 15),
    ] if args.phase == "before" else [
        ("regression", py + [str(ROOT / "tests/python/test_mobius_transport_receipt.py")], 15),
        composition,
    ]
    try:
        for name, cmd, seconds in commands:
            begin = time.monotonic()
            stdout, stderr = out / (name + ".stdout"), out / (name + ".stderr")
            with stdout.open("x") as so, stderr.open("x") as se:
                try:
                    completed = subprocess.run(cmd, cwd=ROOT, stdout=so, stderr=se, timeout=seconds, check=False)
                    entry = {"name": name, "returncode": completed.returncode, "seconds": time.monotonic() - begin}
                except subprocess.TimeoutExpired:
                    entry = {"name": name, "status": "UnknownTimeout", "seconds": time.monotonic() - begin}
            report["invocations"].append(entry)
            (out / "execution.json").write_text(json.dumps(report, indent=2) + "\n")
            if entry.get("returncode") != 0:
                raise RuntimeError("command did not complete: " + name)
        report["checks"] = {}
        body = lambda value: {k: v for k, v in value.items() if k != "cost"}
        load = lambda path: json.loads(path.read_text())
        if args.phase == "before":
            report["checks"]["receiver_matches_retained"] = body(load(out / "receiver.json")) == body(load(EXP / "evidence.json"))
            node = load(out / "node.stdout")
            old_zot = load(ROOT / "experiments/zot_prefix_machine/evidence.json")
            report["checks"]["node_campaigns_completed"] = node["zot"]["verdict"] == node["keraia"]["verdict"] == "Completed"
            report["checks"]["node_weighted_ledgers_match"] = all(node["zot"]["modes"][m]["rows"] == old_zot["modes"][m]["rows"] for m in ("direct", "prefix", "state"))
            report["checks"]["node_probability_matches"] = node["zot"]["probability"] == old_zot["probability"]
            old_k = load(ROOT / "experiments/zot_prefix_machine/keraia-evidence.json")
            report["checks"]["node_keraia_counts_match"] = all(node["keraia"][k] == old_k[k] for k in ("syntaxTails", "exhaustive", "readControls", "paperSplit"))
            report["caller_aliases_found"] = sum(r["accepted_record_changed"] for r in load(out / "probe.stdout")["cases"])
        execution = load(out / "composition/execution.json")
        report["checks"]["composition_fresh_replay_matches"] = execution["status"] == "Passed"
        report["checks"]["composition_matches_retained"] = body(load(out / "composition/primary.json")) == body(load(EXP / "composition-evidence/primary.json"))
        report["status"] = "Passed" if all(report["checks"].values()) else "InvalidEvidence"
    except Exception as err:
        report["status"] = "UnknownOrInvalidEvidence"
        report["error"] = str(err)
    report["elapsed_seconds"] = time.monotonic() - start
    (out / "execution.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))
    return 0 if report["status"] == "Passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
