"""Bounded external interpretation checks over fresh Rust library reuse reports.

Python judges this declared finite observation relation, never native identity.
No natural-language inference, program rewrite, or automatic continuation.
"""
import argparse
import copy
import hashlib
import json
import os
from pathlib import Path
import resource
import subprocess
import time

HERE = Path(__file__).resolve().parent


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def file_digest(path):
    if path.stat().st_size > 64 * 1024 * 1024:
        raise ValueError("input exceeds hash boundary")
    result = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(65536), b""):
            result.update(chunk)
    return result.hexdigest()


def meaning(ast, x, depth=1, account=None):
    """Only the stipulated tiny external grammar; not an Adva interpreter."""
    account = [0] if account is None else account
    account[0] += 1
    if depth > 3 or account[0] > 7 or not isinstance(ast, list):
        raise ValueError("outside finite syntax boundary")
    if ast == ["x"]:
        return x
    if len(ast) != 3 or ast[0] not in ("add", "mul"):
        raise ValueError("unknown interpretation constructor")
    left = meaning(ast[1], x, depth + 1, account)
    right = meaning(ast[2], x, depth + 1, account)
    return left + right if ast[0] == "add" else left * right


def bind(mechanism, interpretation, question):
    return {"schema": "adva.interpretation-binding.research.v0",
            "mechanism_sha256": digest(canonical(mechanism)),
            "interpretation_sha256": digest(canonical(interpretation)),
            "question_sha256": digest(canonical(question))}


def judge(contract, mechanism, interpretation, question, binding, rows):
    result = {"status": "RejectedBinding", "binding_passed": False,
              "scope": question.get("inputs"), "comparisons": [], "residual": None}
    if binding != bind(mechanism, interpretation, question):
        return result
    result["binding_passed"] = True
    expected_mechanism = contract["mechanism"]
    if mechanism != expected_mechanism or question.get("relation") != contract["question"]:
        result["status"] = "RejectedScope"
        return result
    scope = question.get("inputs")
    if (not isinstance(scope, list) or not scope or len(scope) > 3
            or any(type(x) is not int or x == 0 or not -8 <= x <= 8 for x in scope)
            or len(set(scope)) != len(scope)):
        result["status"] = "RejectedScope"
        return result
    try:
        predicted = {x: meaning(interpretation["ast"], x) for x in scope}
    except (KeyError, TypeError, ValueError):
        result["status"] = "RejectedSyntax"
        return result
    by_input = {}
    for row in rows:
        x = row.get("input")
        if type(x) is not int or x in by_input or x not in scope:
            result["status"] = "RejectedEvidence"
            return result
        by_input[x] = row
    missing = [x for x in scope if x not in by_input]
    # Deliberately conservative: do not issue a scope-wide acceptance with gaps.
    if missing:
        result.update(status="UnknownCoverage", residual={"missing_inputs": missing})
        return result
    for x in scope:
        row = by_input[x]
        report = row["report"]
        if row["exit_code"] != 0 or report.get("status") != "ReuseChecked":
            result.update(status="UnknownNative", residual={"input": x, "native_status": report.get("status")})
            return result
        request, reuse = report.get("request", {}), report.get("reuse", {})
        if (request.get("input") != x or request.get("epoch") != mechanism["epoch"]
                or request.get("word") != mechanism["word"]
                or report.get("checker_revision") != mechanism["checker_revision"]
                or report.get("snapshot_digest") != mechanism["snapshot_digest"]
                or report.get("expected_digest_matched") is not True
                or reuse.get("input") != x or reuse.get("snapshot_digest") != mechanism["snapshot_digest"]):
            result["status"] = "RejectedEvidence"
            return result
        actual = reuse.get("guarded_values")
        if not isinstance(actual, list) or len(actual) != 2 or any(type(v) is not str for v in actual):
            result["status"] = "RejectedEvidence"
            return result
        expected = [str(predicted[x])] * 2
        result["comparisons"].append({"input": x, "native": actual, "interpretation": expected, "equal": actual == expected})
    mismatches = [r for r in result["comparisons"] if not r["equal"]]
    if mismatches:
        result.update(status="Counterexample", residual={"counterexample": mismatches[0]})
    else:
        result.update(status="MatchedFiniteScope", residual="Unlisted inputs and arbitrary prose remain unchecked")
    return result


def cases(contract, rows):
    mechanism = contract["mechanism"]
    double, square = contract["interpretations"]
    result = []

    def case(name, interpretation, inputs, expected, *, override_rows=None, marker=None):
        question = {"relation": contract["question"], "inputs": inputs}
        selected = [r for r in rows if r["input"] in inputs] if override_rows is None else override_rows
        binding = bind(mechanism, interpretation, question) if marker is None else marker
        outcome = judge(contract, mechanism, interpretation, question, binding, selected)
        assert outcome["status"] == expected, (name, outcome)
        result.append({"name": name, "interpretation": interpretation, "question": question,
                       "binding": binding, "outcome": outcome})

    case("old-square-agrees", square, [2], "MatchedFiniteScope")
    case("target-double-matches", double, [2, 3], "MatchedFiniteScope")
    case("repinned-square-is-false", square, [2, 3], "Counterexample")
    target = {"relation": contract["question"], "inputs": [2, 3]}
    case("changed-without-repin", square, [2, 3], "RejectedBinding", marker=bind(mechanism, double, target))
    case("missing-new-input", square, [2, 3], "UnknownCoverage", override_rows=[rows[0]])
    case("duplicate-input", double, [2], "RejectedEvidence", override_rows=[rows[0], rows[0]])
    case("fresh-double", double, [-3], "MatchedFiniteScope")
    case("fresh-square", square, [-3], "Counterexample")
    case("guard-boundary", double, [0], "RejectedScope")
    case("unknown-syntax-repinned", {"name": "uninterpreted", "ast": ["free"]}, [2], "RejectedSyntax")
    # A control fixture, not a new native invocation or a claim about a forged receipt's authenticity.
    altered = copy.deepcopy(rows[0]); altered["report"]["reuse"]["input"] = 3
    case("wrong-report-coordinate", double, [2], "RejectedEvidence", override_rows=[altered])
    return result


def main(args):
    started = time.monotonic()
    raw = (HERE / "contract.json").read_bytes()
    contract = json.loads(raw)
    output = Path(args.output).resolve()
    output.mkdir(parents=False, exist_ok=False)
    deadline = started + contract["limits"]["wall_seconds"]
    limit = contract["limits"]
    resource.setrlimit(resource.RLIMIT_CPU, (limit["cpu_seconds"], limit["cpu_seconds"]))
    resource.setrlimit(resource.RLIMIT_AS, (limit["address_bytes"], limit["address_bytes"]))
    resource.setrlimit(resource.RLIMIT_FSIZE, (limit["file_bytes"], limit["file_bytes"]))
    report = {"schema": "adva.interpretation-obligation.report.research.v0", "status": "Unknown",
              "contract_sha256": digest(raw), "native_admission": "NotGranted",
              "word": {"name": "interpretation-obligation", "status": "Proposed"},
              "calls": [], "cases": [], "costs": {}, "search_nodes": 0}

    def save(name, value):
        data = value if isinstance(value, bytes) else json.dumps(value, indent=2, allow_nan=False).encode() + b"\n"
        if sum(p.stat().st_size for p in output.iterdir() if p.is_file()) + len(data) > limit["total_output_bytes"]:
            raise TimeoutError("output byte budget")
        with (output / name).open("xb") as stream:
            stream.write(data)

    try:
        save("contract.json", raw)
        save("calibration.py", Path(__file__).read_bytes())
        binary, library = Path(args.adva).resolve(strict=True), Path(args.library).resolve(strict=True)
        before = {p: file_digest(library / p) for p in contract["library_files"]}
        if before != contract["library_files"]:
            raise ValueError("library byte pins differ")
        binary_pin = file_digest(binary)
        report["binary_sha256"] = binary_pin
        report["matches_reference_binary"] = binary_pin == contract["reference_binary_sha256"]
        report["library_files"] = before
        rows = []
        native_started = time.monotonic()
        for i, x in enumerate(contract["native_inputs"]):
            remaining = deadline - time.monotonic()
            if remaining <= 0 or i >= limit["native_calls"]:
                raise TimeoutError("native call budget")
            path = output / f"native-{i}.json"
            command = [str(binary), "library", "reuse", "--path", str(library), "--epoch", "1",
                       "--word", "0", "--input", str(x), "--fuel", str(limit["fuel_each"]),
                       "--expect-digest", contract["mechanism"]["snapshot_digest"], "--output", str(path)]
            t = time.monotonic()
            with (output / f"native-{i}.stdout").open("xb") as stdout, (output / f"native-{i}.stderr").open("xb") as stderr:
                child = subprocess.run(command, stdout=stdout, stderr=stderr, timeout=min(remaining, limit["child_seconds"]))
            native = json.loads(path.read_bytes())
            report["calls"].append({"input": x, "argv": command, "exit_code": child.returncode,
                                    "wall_seconds": time.monotonic() - t, "report_sha256": file_digest(path),
                                    "fuel": native["fuel"]})
            if x == 0:
                assert child.returncode == 2 and native["status"] == "Rejected" and "zero" in native["error"].lower()
            else:
                assert child.returncode == 0 and native["status"] == "ReuseChecked"
                # Independent closed-form fixture oracle for the selected doubling mechanism.
                assert native["reuse"]["guarded_values"] == [str(2 * x)] * 2
            rows.append({"input": x, "exit_code": child.returncode, "report": native})
        report["costs"]["native_construction_and_verification_seconds"] = time.monotonic() - native_started
        report["native_fuel_spent"] = sum(c["fuel"]["spent"] for c in report["calls"])
        assert report["native_fuel_spent"] <= limit["total_native_fuel_limit"]
        t = time.monotonic()
        report["cases"] = cases(contract, rows)
        report["costs"]["binding_and_relation_checks_seconds"] = time.monotonic() - t
        t = time.monotonic()
        encoded = canonical(report["cases"])
        assert json.loads(encoded) == report["cases"]
        assert cases(contract, json.loads(canonical(rows))) == report["cases"]
        report["costs"]["serialization_and_same_checker_replay_seconds"] = time.monotonic() - t
        if before != {p: file_digest(library / p) for p in before} or file_digest(binary) != binary_pin:
            raise ValueError("protected inputs changed during execution")
        if time.monotonic() >= deadline:
            raise TimeoutError("overall budget")
        report["status"] = "CompletedFiniteCalibration"
    except (TimeoutError, subprocess.TimeoutExpired, MemoryError) as error:
        report.update(status="Unknown", error=str(error))
    except (ValueError, KeyError, OSError, AssertionError, RuntimeError) as error:
        report.update(status="Rejected", error=str(error))
    finally:
        report["costs"]["wall_seconds_before_checkpoint"] = time.monotonic() - started
        report["costs"]["self_peak_rss_kib"] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        report["costs"]["largest_child_rss_kib"] = resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss
        report["costs"]["memory_scope"] = "Linux per-process peaks; not aggregate concurrent memory"
        report["files"] = {p.name: {"bytes": p.stat().st_size, "sha256": file_digest(p)} for p in output.iterdir() if p.is_file()}
        save("report.json", report)
        if time.monotonic() >= deadline:
            report.update(status="Unknown", error="checkpoint crossed overall deadline")
            save("checkpoint-limit.json", {"status": "Unknown", "error": report["error"]})
    print(json.dumps({"status": report["status"], "cases": len(report["cases"]), "costs": report["costs"]}))
    return 0 if report["status"] == "CompletedFiniteCalibration" else 2


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--adva", required=True)
    parser.add_argument("--library", required=True)
    parser.add_argument("--output", required=True)
    raise SystemExit(main(parser.parse_args()))
