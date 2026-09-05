#!/usr/bin/env python3
"""Run two existing Rust learn transitions; assert preservation, not truth."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import subprocess

NAMES = ("arithmetic-universality", "hypothesized-arithmetic-truth")
ROOT = Path(__file__).resolve().parents[1]
INPUTS = ROOT / "programs/bootstrap-0"
FIXTURES = INPUTS / "arithmetic-vocabulary"

def read(path):
    return json.loads(path.read_text(encoding="utf-8"))

def require(condition, message):
    if not condition:
        raise RuntimeError(message)

def run(binary, output):
    output.mkdir(parents=True, exist_ok=True)
    original = read(INPUTS / "frontier-2.adva")
    previous = original
    frontier_path = INPUTS / "frontier-2.adva"
    all_new_words = []
    generated = []
    for index, name in enumerate(NAMES, 1):
        resource = FIXTURES / (name + "-resource.adva")
        transition_path = output / (name + "-transition.adva")
        next_path = output / ("frontier-" + str(index) + ".adva")
        completed = subprocess.run(
            [str(binary), "learn", str(frontier_path),
             str(INPUTS / "exploration.adva"), str(resource),
             "--output", str(transition_path), "--frontier-output", str(next_path)],
            cwd=ROOT, capture_output=True, text=True, timeout=20, check=True)
        print(completed.stdout, end="")
        transition = read(transition_path)
        successor = read(next_path)
        out = transition["output"]
        require(transition["input"]["subject"] == previous, "predecessor changed")
        require(transition["input"]["object"] == read(resource), "resource changed")
        require(out["result"]["local_name"] == name, "wrong candidate admitted")
        require(out["result"]["state"] == "proposed", "hypothesis promoted to truth")
        require(out["history"]["introduced_words"] == [name], "unexpected vocabulary")
        require(successor == out["evidence"]["next_frontier"], "frontier mismatch")
        require(successor["obligations"] == original["obligations"], "obligations changed")
        require(successor["source_calibration"] == original["source_calibration"],
                "source calibration changed")
        require(successor["vocabulary"][:-1] == previous["vocabulary"],
                "old vocabulary changed")
        require(successor["lineage"]["sequence"] == original["lineage"]["sequence"] + index,
                "incorrect lineage sequence")
        for key in ("all_obligations_retained", "external_content_not_truth",
                    "candidate_copied_exactly", "interface_preserved"):
            require(out["evidence"][key] == "checked", "missing preservation check: " + key)
        all_new_words.extend(out["history"]["introduced_words"])
        generated.extend([transition_path, next_path])
        frontier_path, previous = next_path, successor
    require(all_new_words == list(NAMES), "exactly two candidate words required")
    # Once admitted outputs are committed, every later run must match all bytes.
    expected_dir = FIXTURES / "witness"
    if expected_dir.exists():
        for path in generated:
            expected = expected_dir / path.name
            require(expected.is_file(), "missing committed witness: " + path.name)
            require(path.read_bytes() == expected.read_bytes(), "replay drift: " + path.name)
    # Text receipts provide a second authorized export route for small artifacts.
    # Hashes concern byte integrity, never semantic identity.
    for path in generated:
        payload = path.read_bytes()
        encoded = base64.b64encode(payload).decode("ascii")
        print("ADVA_FILE_BEGIN", path.name, len(payload), hashlib.sha256(payload).hexdigest())
        for offset in range(0, len(encoded), 4096):
            print("ADVA_FILE_CHUNK", encoded[offset:offset + 4096])
        print("ADVA_FILE_END", path.name)
    summary = {
        "introduced_words": all_new_words,
        "hypothesis_states": ["proposed", "proposed"],
        "initial_sequence": original["lineage"]["sequence"],
        "final_sequence": previous["lineage"]["sequence"],
        "retained_obligations": len(previous["obligations"]),
        "semantic_discharge": False,
        "real_task": "awaiting an actual task and acceptance criterion from Mingli Yuan or Jiamin Zhao",
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--binary", type=Path, default=ROOT / "target/debug/adva")
    parser.add_argument("--output", type=Path, default=ROOT / "target/arithmetic-vocabulary")
    args = parser.parse_args()
    run(args.binary.resolve(), args.output.resolve())

if __name__ == "__main__":
    main()
