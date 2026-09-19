"""Bounded, replayable original calibration; contributed under Unknown v0.3.

Authored by Codex (OpenAI), through Mingli Yuan's authorized account proxy.
No native Adva semantics, search for breakthroughs or third-party data.
"""

import argparse
from dataclasses import asdict, replace
import hashlib
from itertools import combinations, product
import json
from pathlib import Path
import resource
import subprocess
import sys
import time

from model import (P, Work, append, decode, domain_views, encode, evaluate,
                   readback)

ROOT = Path(__file__).resolve().parent


def blob(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def report_write(target, value, maximum):
    encoded = json.dumps(value, ensure_ascii=False, indent=2).encode() + b"\n"
    if len(encoded) > maximum:
        raise RuntimeError("artifact-size budget exhausted")
    target.write_bytes(encoded)


def campaign(output):
    started = time.monotonic()
    contract_bytes = (ROOT / "contract.json").read_bytes()
    contract = json.loads(contract_bytes)
    limits = contract["resources"]
    work = Work(max_decode_calls=limits["maximum_decode_calls"],
                max_candidate_subsets=limits["maximum_candidate_subsets"])
    counts = {}
    digest = hashlib.sha256()
    last = None
    checked = 0
    negatives = {}
    examples = {}

    def check(group, case, success):
        nonlocal checked, last
        last = {"group": group, "case": case}
        if checked >= limits["maximum_cases"]:
            raise RuntimeError("case budget exhausted")
        if time.monotonic() - started > limits["wall_seconds"] - 3:
            raise RuntimeError("worker deadline reserve reached")
        if not success:
            raise AssertionError(last)
        checked += 1
        counts[group] = counts.get(group, 0) + 1
        digest.update(blob(last) + b"\n")

    def decoded(surface, expected, errors=1):
        result = decode(surface, errors=errors, work=work)
        return (result["status"] == "DecodedWithinRadius"
                and result["history"] == tuple(expected))

    try:
        histories = list(product(range(P), repeat=3))
        codebook = {}
        for h in histories:
            original = encode(h)
            # Independent direct monomial oracle versus Horner encoding.
            oracle = tuple(sum(a*pow(x, j, P) for j, a in enumerate(h)) % P
                           for x in original.points)
            check("direct_encoding", h, original.values == oracle)
            codebook[h] = original.values
            check("clean_length_three", h, decoded(original, h))
            for site in range(5):
                for change in range(1, P):
                    values = list(original.values)
                    values[site] = (values[site] + change) % P
                    damaged = replace(original, values=tuple(values))
                    check("one_substitution", [h, site, change], decoded(damaged, h))
            for missing in combinations(range(5), 2):
                values = list(original.values)
                for site in missing:
                    values[site] = None
                check("two_erasures", [h, missing],
                      decoded(replace(original, values=tuple(values)), h, errors=0))
            for token in range(P):
                result = append(original, token, work=work)
                if result["status"] != "Extended":
                    raise AssertionError(result)
                later = result["surface"]
                check("extension", [h, token], decoded(later, h + (token,)))
                check("incremental_sample_update", [h, token],
                      later.values[:5] == tuple((y + token*pow(x, 3, P)) % P
                                                for x, y in zip(original.points,
                                                                original.values)))
                old = readback(later, 3, work=work)
                check("old_history_readback", [h, token],
                      old["status"] == "ReadBack" and old["surface"] == original)

        # Explicitly exhaustive finite distance computation, separate from decoder.
        minimum_distance = min(sum(a != b for a, b in zip(c, d))
                               for c, d in combinations(codebook.values(), 2))
        check("minimum_distance", {"pairs": 58653}, minimum_distance == 3)

        for k in range(6):
            for h in product((0, 1), repeat=k):
                surface = encode(h)
                check("all_binary_lengths", h, decoded(surface, h))
                for j in range(k + 1):
                    first = readback(surface, j, work=work)
                    check("prefix_reconstruction", [h, j],
                          first["surface"] == encode(h[:j]))
                    for i in range(j + 1):
                        twice = readback(first["surface"], i, work=work)
                        direct = readback(surface, i, work=work)
                        check("readback_composition", [h, j, i],
                              twice == direct)

        # Each negative control is a concrete retained witness.
        collision = ((0, 0, 0), (2, 4, 1))
        projections = [tuple(evaluate(h, x) for x in (1, 2)) for h in collision]
        negatives["undersampled_collision"] = {
            "histories": collision, "points": [1, 2], "observations": projections}
        check("negative", "undersampled_collision",
              collision[0] != collision[1] and projections[0] == projections[1])

        order_pair = ((0, 2, 4), (2, 0, 4))
        negatives["lost_global_order"] = {
            "histories": order_pair,
            "domain_views": [domain_views(h) for h in order_pair],
            "surfaces": [asdict(encode(h)) for h in order_pair]}
        check("negative", "lost_global_order",
              domain_views(order_pair[0]) == domain_views(order_pair[1])
              and encode(order_pair[0]).values != encode(order_pair[1]).values)

        negatives["missing_length"] = {
            "histories": [[0], [0, 0]], "same_samples_at_points_1_to_5": [0]*5}
        check("negative", "missing_length",
              all(evaluate((0,), x) == evaluate((0, 0), x) for x in range(1, 6)))

        sample = encode((1, 0, 1))
        repeated = replace(sample, points=(1, 1, 3, 4, 5))
        negatives["repeated_locations"] = decode(repeated, work=work)
        check("negative", "repeated_locations",
              negatives["repeated_locations"].get("reason") == "InvalidSampleLocations")
        negatives["outside_alphabet"] = append(sample, 7, work=work)
        check("negative", "outside_alphabet",
              negatives["outside_alphabet"].get("reason") == "OutsideContinuationScope")

        full = encode((1, 0, 1, 1, 0))
        saved = asdict(full)
        negatives["capacity"] = append(full, 1, work=work)
        check("negative", "capacity",
              negatives["capacity"].get("reason") == "CapacityExceeded"
              and asdict(full) == saved)
        negatives["zero_budget"] = decode(sample, candidate_budget=0, work=work)
        check("negative", "zero_budget",
              negatives["zero_budget"]["status"] == "Unknown"
              and negatives["zero_budget"]["candidates_tried"] == 0)

        erased = replace(sample, values=(None,) + sample.values[1:])
        negatives["mixed_faults_outside_bound"] = decode(erased, errors=1, work=work)
        check("negative", "mixed_faults_outside_bound",
              negatives["mixed_faults_outside_bound"].get("reason")
              == "InsufficientRedundancy")

        zero = encode((0, 0, 0))
        alternative = encode((2, 4, 1))
        values = (0, 0, alternative.values[2], alternative.values[3], 0)
        damaged = replace(zero, values=values)
        result = decode(damaged, work=work)
        negatives["two_error_miscorrection"] = {
            "actual_history": [0, 0, 0], "received": values,
            "substitutions_from_actual": 2, "decoder": result}
        check("negative", "two_error_miscorrection",
              result.get("history") == (2, 4, 1)
              and result["authenticity"] == "NotEstablished")

        clean_words = set(codebook.values())
        distance_ball = set(clean_words)
        for word in clean_words:
            for i in range(5):
                for delta in range(1, P):
                    changed = list(word)
                    changed[i] = (changed[i] + delta) % P
                    distance_ball.add(tuple(changed))
        outside = next(word for word in product(range(P), repeat=5)
                       if word not in distance_ball)
        negatives["outside_every_radius_one_ball"] = {
            "received": outside,
            "decoder": decode(replace(zero, values=outside), work=work)}
        check("negative", "outside_every_radius_one_ball",
              negatives["outside_every_radius_one_ball"]["decoder"]["status"]
              == "NoCodewordWithinRadius")

        narrow, enlarged = (0, 1), (0, 1, 2)
        extensions = [append(sample, a, allowed=enlarged, work=work)["surface"]
                      for a in enlarged]
        examples["declared_scope_extension"] = {
            "old_allowed_symbols": narrow, "new_allowed_symbols": enlarged,
            "successors": [asdict(s) for s in extensions],
            "scope": "Externally declared continuation sets; no endogenous discovery"}
        check("scope_extension", "two_to_three",
              append(sample, 2, allowed=narrow, work=work)["status"] == "Rejected"
              and len(set(extensions)) == 3
              and all(readback(s, 3, work=work)["surface"] == sample for s in extensions))

        clean_new = encode((1, 0, 1, 1))
        noisy_new = replace(clean_new, values=clean_new.values[:2] +
                            ((clean_new.values[2] + 1) % P,) + clean_new.values[3:])
        examples["surface_rewrite"] = {
            "before": asdict(sample), "after": asdict(clean_new),
            "one_fault": asdict(noisy_new), "reconstruction": decode(noisy_new, work=work),
            "old_prefix": asdict(readback(noisy_new, 3, work=work)["surface"])}
        check("rewrite_example", "old_interpretation_after_fault",
              examples["surface_rewrite"]["old_prefix"] == asdict(sample))
        status, failure = "PassedDeclaredFiniteCalibration", None
    except Exception as exc:
        status, failure = "Incomplete", {"type": type(exc).__name__,
                                         "message": str(exc), "last_case": last}

    report = {
        "schema": "adva.history-surface-calibration.report.v0",
        "status": status, "contract_sha256": hashlib.sha256(contract_bytes).hexdigest(),
        "source_sha256": {name: hashlib.sha256((ROOT/name).read_bytes()).hexdigest()
                          for name in ("model.py", "run.py")},
        "author": "Codex (OpenAI), through Mingli Yuan's authorized account proxy",
        "native_semantic_calls": 0, "counts": counts, "checked_cases": checked,
        "case_order_digest_sha256": digest.hexdigest(),
        "work": asdict(work), "elapsed_seconds": time.monotonic()-started,
        "peak_rss_kib_linux": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        "negative_controls": negatives, "examples": examples, "failure": failure,
        "residuals": [
            "No endogenous breakthrough generation or native Adva history import.",
            "Only words over seven declared toy symbols are reconstructed.",
            "Header integrity and the fault bound are assumptions.",
            "No physical surface geometry, locality, holographic duality or infinite fixed memory.",
            "Correction does not authenticate the actual past; two-error control miscorrects.",
        ],
    }
    report_write(output, report, limits["maximum_artifact_bytes"])
    print(json.dumps({"status": status, "checked_cases": checked, "counts": counts,
                      "work": asdict(work), "failure": failure}))
    return 0 if failure is None else 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--worker", action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args()
    if args.worker:
        return campaign(args.output)
    if args.output.exists():
        raise SystemExit("Refusing to overwrite a retained result; select a new output.")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    limits = json.loads((ROOT / "contract.json").read_text())["resources"]

    def restrict():
        resource.setrlimit(resource.RLIMIT_CPU, (limits["cpu_seconds"],)*2)
        resource.setrlimit(resource.RLIMIT_AS, (limits["address_space_bytes"],)*2)
        resource.setrlimit(resource.RLIMIT_FSIZE, (limits["file_size_limit_bytes"],)*2)

    start = time.monotonic()
    try:
        process = subprocess.run(
            [sys.executable, str(Path(__file__).resolve()), "--worker",
             "--output", str(args.output.resolve())],
            timeout=limits["wall_seconds"], preexec_fn=restrict, check=False)
        code = process.returncode
    except subprocess.TimeoutExpired:
        code = 124
    if not args.output.exists():
        report_write(args.output, {
            "status": "Unknown", "reason": "WorkerStoppedWithoutCheckpoint",
            "returncode": code, "elapsed_seconds": time.monotonic()-start,
            "residual": "No completed case ledger recovered; no success claimed.",
        }, limits["maximum_artifact_bytes"])
    return code


if __name__ == "__main__":
    raise SystemExit(main())
