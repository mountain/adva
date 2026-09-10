"""External static inspection only. This does not implement the Rust loader."""
import hashlib
import json
import resource
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def require(condition, message):
    if not condition:
        raise ValueError(message)


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, "duplicate JSON key: " + key)
        result[key] = value
    return result


def inspect():
    start = time.perf_counter_ns()
    names = ["presentation.json", "contract.json", "obligations.json", "symbol-surface.adva"]
    raw = {}
    for name in names:
        with (ROOT / name).open("rb") as stream:
            raw[name] = stream.read(32769)
        require(len(raw[name]) <= 32768, "file budget exceeded")
    p, c, o, d = [json.loads(raw[name], object_pairs_hook=unique_object) for name in names]
    require(d["schema"] == "adva.neutral-carrier-graph.research" and d["version"] == 0, "envelope tag")
    require(len(d["carriers"]) == 3 and len(d["frames"]) == 1, "fixed envelope size")
    for index, name in enumerate(names[:3]):
        carrier = d["carriers"][index]
        require(carrier["id"] == index, "carrier order")
        require(carrier["carrier"]["structure"] == "sha256:" + hashlib.sha256(raw[name]).hexdigest(), "payload reference")
    items = o["items"]
    ids = [item["id"] for item in items]
    require(len(ids) == 9 and len(set(ids)) == 9 and ids == p["obligation_ids"], "obligation references")
    require(all(item["status"] == "Open" for item in items), "obligations must remain open")
    sites = [item["document_frontier_coordinate"] for item in items]
    require(sites == [{"role": "construction", "hole": i, "occurrence": 0} for i in range(9)], "annotation coordinates")
    require(d["carriers"][0]["carrier"]["frontier"]["sites"] == sites, "subject frontier")
    require(all(not carrier["carrier"]["frontier"]["sites"] for carrier in d["carriers"][1:]), "other frontiers")
    frame = d["frames"][0]
    require(frame["id"] == 0 and frame["input"] == {"subject": 0, "method": 1, "object": 2}, "frame references")
    require(frame["mechanism"] == {"kind": "verify", "declared_subject": {"sites": sites}, "discharges": []}, "ready verification frame")
    require(frame["output"] == {"history": None, "result": None, "evidence": None}, "no native result")
    require(d["entrypoints"] == [{"name": "inspect", "frame": 0}], "entrypoint")
    symbols = p["symbols"]
    codes = [symbol["address_code"] for symbol in symbols]
    require(len(symbols) == 3 and len({symbol["id"] for symbol in symbols}) == 3, "symbol identity")
    require(all(code and set(code) <= {"0", "2"} for code in codes), "address alphabet")
    require(all(not b.startswith(a) for i, a in enumerate(codes) for j, b in enumerate(codes) if i != j), "prefix-free codes")
    holes = []
    def walk(node):
        if set(node) == {"hole"}:
            holes.append(node["hole"])
        else:
            require(set(node) == {"op", "args"} and node["op"] in {"sub", "mul"}, "AST constructor")
            require(len(node["args"]) == 2, "AST arity")
            for arg in node["args"]:
                walk(arg)
    walk(p["template"]["body"])
    require(holes == p["template"]["holes"] == ["a", "b", "c"], "hole occurrences")
    occurrences = p["occurrences"]
    require(len(occurrences) == 3 and len({x["id"] for x in occurrences}) == 3, "distinct occurrence identities")
    require(p["fill"] == {"a": "a-zero", "b": "b-one", "c": "c-one"}, "fill references")
    require({x["id"] for x in occurrences} == set(p["fill"].values()), "occurrence coverage")
    require(all(x["type"] == "Complex" for x in occurrences), "declared occurrence types")
    require(p["coercion_boundary"]["target"] == "Complex", "comparison type boundary")
    address = p["cantor_presentation"]["finite_address"]
    word = "".join(address["digits"])
    require(address["length"] == len(word) and address["terminated"] is True, "finite address boundary")
    remaining, decoded = word, []
    while remaining:
        matches = [s for s in symbols if remaining.startswith(s["address_code"])]
        require(len(matches) == 1, "incomplete or ambiguous symbol address")
        decoded.append(matches[0]["id"])
        remaining = remaining[len(matches[0]["address_code"]):]
    require(all(t["application_status"] == "Open" for t in p["theorem_interfaces"]), "open theorem interfaces")
    require(p["pi_record"]["branch_index"] == c["log_branch"]["index"] == 0, "branch annotation")
    require(p["result_claim"]["status"] == p["pi_record"]["status"] == "DeclaredNotExecuted", "unevaluated claims")
    require(all(p["game"][key] == "NotRun" for key in ["evaluation", "search", "proof_replay"]), "representation scope")
    require(c["native_load_status"] == c["proof_status"] == "NotRun", "native status")
    return {"status": "ExternalRepresentationConsistent", "open_obligations": len(ids),
            "files_sha256": {name: hashlib.sha256(value).hexdigest() for name, value in raw.items()},
            "decoded_address": {"word": word, "symbol_ids": decoded},
            "native_load": "NotRun: Rust compiler unavailable; no read-only document-load CLI used",
            "arithmetic_evaluations": 0, "game_moves": 0, "search_nodes": 0,
            "static_inspection_ms": (time.perf_counter_ns() - start) / 1e6,
            "process_peak_rss_kib_linux": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
            "unmeasured": ["file construction cost", "research time", "network time", "serialization time"],
            "scope": "Fixed-record integrity and selected structure checks, not a general validator, proof, native execution or learning claim"}


if __name__ == "__main__":
    result = inspect()
    (ROOT / "inspection.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
