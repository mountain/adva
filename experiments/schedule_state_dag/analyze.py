"""Artifact-level state-DAG fold over already native-verified prefix receipts."""
import copy
import hashlib
import json
from pathlib import Path
import resource
import sys
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def form(prefix):
    started = time.perf_counter_ns()
    states = {}
    record_visits = edge_visits = 0
    for record in prefix["records"]:
        record_visits += 1
        cut = tuple(record["cut"])
        edges = record["edges"]
        edge_visits += len(edges)
        normalized = [{"event": edge["event"],
                       "next_cut": edge["step"]["result"]["after"]["completed"],
                       "step": edge["step"]} for edge in edges]
        old = states.get(cut)
        if old is not None and canonical(old) != canonical(normalized):
            raise ValueError(f"inconsistent transition facts at {cut}")
        states[cut] = normalized
    return ({"schema": "history-preserving-state-dag.artifact-v0",
             "diagram_hash": prefix["diagram_hash"],
             "states": [{"cut": list(cut), "edges": edges} for cut, edges in sorted(states.items())]},
            {"prefix_records_read": record_visits, "prefix_edges_read": edge_visits,
             "counted_units": record_visits + edge_visits,
             "formation_ns": time.perf_counter_ns() - started})


def receive(prefix, dag):
    started = time.perf_counter_ns()
    cost = {"reference_records": 0, "reference_edges": 0, "dag_states": 0,
            "dag_edges": 0, "path_prefixes": 0}
    def finish(outcome, residual):
        cost["counted_units"] = sum(cost.values())
        cost["receiving_ns"] = time.perf_counter_ns() - started
        return outcome, residual, cost
    if dag.get("schema") != "history-preserving-state-dag.artifact-v0" or dag.get("diagram_hash") != prefix.get("diagram_hash"):
        return finish("InvalidContext", None)
    expected, _ = form(prefix)
    expected_map = {tuple(s["cut"]): s["edges"] for s in expected["states"]}
    cost["reference_records"] = len(prefix["records"])
    cost["reference_edges"] = sum(len(r["edges"]) for r in prefix["records"])
    supplied = {}
    for state in dag.get("states", []):
        cost["dag_states"] += 1
        cut = tuple(state.get("cut", []))
        if cut in supplied or list(cut) != sorted(cut):
            return finish("InvalidEvidence", None)
        supplied[cut] = state.get("edges", [])
        cost["dag_edges"] += len(supplied[cut])
    missing = sorted(set(expected_map) - set(supplied))
    if missing:
        return finish("UnknownCoverage", {"missing_state": list(missing[0])})
    extra = sorted(set(supplied) - set(expected_map))
    if extra:
        return finish("InvalidEvidence", {"unreachable_state": list(extra[0])})
    for cut, edges in expected_map.items():
        if len(supplied[cut]) < len(edges):
            return finish("UnknownCoverage", {"incomplete_edges_at": list(cut)})
        if canonical(supplied[cut]) != canonical(edges):
            return finish("InvalidEvidence", {"wrong_edges_at": list(cut)})
    node_count = max(len(s["cut"]) for s in expected["states"])
    words = []
    queue = [((), [])]
    while queue:
        cut, word = queue.pop(0)
        cost["path_prefixes"] += 1
        if len(word) == node_count:
            words.append(word)
            continue
        for edge in supplied[cut]:
            queue.append((tuple(edge["next_cut"]), word + [edge["event"]]))
    return finish("Verified", sorted(words))


def main():
    out = Path(sys.argv[1]).resolve()
    out.mkdir(parents=True, exist_ok=False)
    started = time.perf_counter()
    prior_dir = ROOT / "experiments/schedule_prefix/evidence/attempt-1"
    prior_results = json.loads((prior_dir / "results.json").read_text())
    known = {x["name"]: x for x in prior_results if "producer_cost" in x}
    results = []
    status = "ImplementationFailure"
    try:
        for name in ("diamond", "three", "delayed", "two-chains"):
            prefix = json.loads((prior_dir / f"{name}.tree.json").read_text())
            dag, formation = form(prefix)
            outcome, words, receiving = receive(prefix, dag)
            assert outcome == "Verified"
            assert words == known[name]["result"]["legal_words"]
            (out / f"{name}.dag.json").write_text(canonical(dag) + "\n")
            results.append({"name": name, "outcome": outcome, "legal_words": words,
                            "prefix_records": len(prefix["records"]), "dag_states": len(dag["states"]),
                            "formation_cost": formation, "receiving_cost": receiving})
        prefix = json.loads((prior_dir / "diamond.tree.json").read_text())
        dag, _ = form(prefix)
        controls = []
        def check(name, change, expected):
            candidate = copy.deepcopy(dag)
            change(candidate)
            outcome, residual, cost = receive(prefix, candidate)
            assert outcome == expected, (name, outcome, residual)
            controls.append({"name": name, "expected": expected, "outcome": outcome,
                             "residual": residual, "cost": cost})
        check("missing-edge", lambda d: d["states"][0]["edges"].pop(), "UnknownCoverage")
        check("missing-state", lambda d: d["states"].pop(), "UnknownCoverage")
        check("wrong-next", lambda d: d["states"][0]["edges"][0].update(next_cut=[]), "InvalidEvidence")
        check("duplicate-state", lambda d: d["states"].append(copy.deepcopy(d["states"][0])), "InvalidEvidence")
        check("wrong-binding", lambda d: d.update(diagram_hash="wrong"), "InvalidContext")
        check("unreachable-state", lambda d: d["states"].append({"cut": [999], "edges": []}), "InvalidEvidence")
        results.extend(controls)
        status = "PassedArtifactLevel"
    finally:
        execution = {"status": status, "wall_seconds": time.perf_counter() - started,
                     "supervisor_peak_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                     "native_receiver_executed": False,
                     "native_receiver_residual": "Rust/Cargo absent from this execution environment"}
        (out / "results.json").write_text(json.dumps(results, indent=2, sort_keys=True) + "\n")
        (out / "execution.json").write_text(json.dumps(execution, indent=2, sort_keys=True) + "\n")
        sources = {name: hashlib.sha256((HERE / name).read_bytes()).hexdigest()
                   for name in ("contract.json", "analyze.py", "Cargo.toml", "Cargo.lock", "src/main.rs", "run.py")}
        (out / "sources.json").write_text(json.dumps(sources, indent=2, sort_keys=True) + "\n")
        manifest = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(out.iterdir())}
        (out / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
