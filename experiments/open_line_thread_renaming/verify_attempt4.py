"""Independent archive checks for the bounded attempt-4 evidence.

This does not import or execute the experimental receiver.
Original contribution by Codex (OpenAI), under Unknown v0.3.
"""

import hashlib
import json
from pathlib import Path
import resource
import sys
import time


HERE = Path(__file__).resolve().parent
ATTEMPT = HERE / "evidence" / "attempt-4"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path):
    return json.loads(path.read_bytes())


def check(condition, label, counter):
    counter[0] += 1
    if not condition:
        raise AssertionError(label)


def main(output):
    started = time.perf_counter()
    checks = [0]
    contract = load(HERE / "validation-contract.json")
    inherited_contract = load(HERE / "contract.json")
    pinned = {
        "run.py": HERE / "run.py",
        "contract.json": HERE / "contract.json",
        "outcome.json": HERE / "outcome.json",
        "continuation-contract.json": HERE / "continuation-contract.json",
        "continuation-outcome.json": HERE / "continuation-outcome.json",
        "attempt-3-supervision.json": HERE / "evidence" / "attempt-3" / "supervision.json",
    }
    for name, path in pinned.items():
        check(digest(path) == contract["input_sha256"][name], "pin: " + name, checks)

    for record_name in ("outcome.json", "continuation-outcome.json"):
        record = load(HERE / record_name)
        for relative, expected in record["evidence_sha256"].items():
            if relative == "run.py-after-correction":
                check(expected == "3d8f2585c312a681263db2b4fba81b6a721583d5939d0a4d137ec43b9e58dc03",
                      "historical attempt-2 source coordinate", checks)
                continue
            check(digest(HERE / relative) == expected,
                  record_name + " evidence: " + relative, checks)

    cases = load(ATTEMPT / "cases.json")
    execution = load(ATTEMPT / "execution.json")
    supervision = load(ATTEMPT / "supervision.json")
    stdout = json.loads((ATTEMPT / "stdout.txt").read_text())
    check(execution == stdout, "stdout/execution agreement", checks)
    check(execution["status"] == "Passed", "execution status", checks)
    check(execution["assertions"] == 52, "assertion count", checks)
    check(execution["receiving_calls"] == 12, "receiving calls", checks)
    check(execution["positive_pairs"] == 2, "positive count", checks)
    check(execution["refusal_controls"] == 10, "refusal count", checks)
    check(execution["search_nodes"] == 0, "search count", checks)
    check(execution["new_words"] == 0, "word count", checks)
    check(supervision["status"] == "Completed", "supervision status", checks)
    check(supervision["returncode"] == 0, "return code", checks)
    check(supervision["within_1mib"] is True, "evidence budget", checks)
    check(len(cases) == 12, "case count", checks)

    names = [row["case"] for row in cases]
    expected_names = [
        "forward",
        "reversed-reuse",
        *inherited_contract["negative_controls"],
    ]
    check(names == expected_names, "case order", checks)
    check([row["outcome"] for row in cases[:2]] == ["Checked", "Checked"],
          "positive outcomes", checks)
    check(all(row["outcome"] == "Refused" for row in cases[2:]),
          "refusal outcomes", checks)

    first, reversed_case = cases[:2]
    first_result, reverse_result = first["result"], reversed_case["result"]
    check(first_result["status"] == "RenamingCorrespondenceChecked",
          "forward result", checks)
    check(reverse_result["status"] == "RenamingCorrespondenceChecked",
          "reverse result", checks)
    check(first_result["continuation_authorized"] is False and
          reverse_result["continuation_authorized"] is False,
          "no continuation authorization", checks)
    check(first_result["correspondence"] == reverse_result["correspondence"],
          "correspondence reuse", checks)
    check(first_result["mapped_source"] == first["right"],
          "forward mapped source", checks)
    check(reverse_result["mapped_source"] == reversed_case["right"],
          "reverse mapped source", checks)
    check([x["name"] for x in first["left"]["channels"][0]["thread"]] ==
          ["thread-a", "thread-b"], "forward left order", checks)
    check([x["name"] for x in reversed_case["left"]["channels"][0]["thread"]] ==
          ["thread-b", "thread-a"], "reverse left order", checks)
    check([x["name"] for x in first["right"]["channels"][0]["thread"]] ==
          ["reuse-thread-a", "reuse-thread-b"], "forward right order", checks)
    check([x["name"] for x in reversed_case["right"]["channels"][0]["thread"]] ==
          ["reuse-thread-b", "reuse-thread-a"], "reverse right order", checks)

    reasons = {
        "reversed-target-source": "right source differs from complete renamed source",
        "swapped-step-targets": "thread_steps mapping target coverage/order differs",
        "duplicate-step-target": "thread_steps mapping target coverage/order differs",
        "swapped-occurrence-targets": "occurrences mapping target coverage/order differs",
        "swapped-source-targets": "sources mapping target coverage/order differs",
        "swapped-residual-targets": "residuals mapping target coverage/order differs",
        "swapped-hole-targets": "holes mapping target coverage/order differs",
        "reversed-port-map-order": "ports mapping source coverage/order differs",
        "wrong-whole-target": "whole mapping target coverage/order differs",
        "omitted-alternative-map": "alternatives mapping source coverage/order differs",
    }
    for row in cases[2:]:
        check(row["reason"] == reasons[row["case"]],
              "reason: " + row["case"], checks)

    correspondence = first_result["correspondence"]
    by_name = {row["case"]: row for row in cases}
    for label, namespace in (("swapped-occurrence-targets", "occurrences"),
                             ("swapped-source-targets", "sources")):
        mutated = by_name[label]["candidate"][namespace]
        original = correspondence[namespace]
        check(len(mutated) == len(original) == 6, label + " length", checks)
        check(mutated[2:] == original[2:], label + " retained tail", checks)
        check([pair[0] for pair in mutated] == [pair[0] for pair in original],
              label + " source coverage", checks)
        check(sorted(pair[1] for pair in mutated) == sorted(pair[1] for pair in original),
              label + " target coverage", checks)

    report = {
        "status": "ArchiveVerified",
        "checks": checks[0],
        "files": {
            name: digest(ATTEMPT / name) for name in
            ("cases.json", "execution.json", "stderr.txt", "stdout.txt", "supervision.json")
        },
        "verification_seconds": time.perf_counter() - started,
        "peak_rss_kib_linux": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        "search_nodes": 0,
        "new_words": 0,
    }
    payload = json.dumps(report, sort_keys=True, separators=(",", ":")) + "\n"
    output.write_text(payload)
    print(payload, end="")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: python verify_attempt4.py NEW_REPORT_PATH")
    target = Path(sys.argv[1])
    if target.exists():
        raise SystemExit("refuse to overwrite report")
    main(target)
