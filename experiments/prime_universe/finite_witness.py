#!/usr/bin/env python3
"""Pinned, external finite calibration; not an Adva theorem checker."""
import argparse
import hashlib
import json
import math
import resource
import signal
import time
from pathlib import Path

CONTRACT_SHA = "b1b40b0c89aa46c307e9ff9095f5e411b9ebf8cf25ad279ad7b84f99d043f14b"
MAX_BYTES = 262144


class Limit(Exception):
    pass


class Meter:
    def __init__(self):
        self.units = dict.fromkeys(("construction", "search", "verification", "serialization"), 0)
        self.ns = dict.fromkeys((*self.units, "reuse"), 0)
        self.started = time.perf_counter_ns()

    def charge(self, phase):
        if sum(self.units.values()) >= 1997:
            raise Limit("global budget exhausted; three final writes reserved")
        if time.perf_counter_ns() - self.started >= 5_000_000_000:
            raise Limit("global wall budget exhausted")
        self.units[phase] += 1

    def timed(self, phase, function, *args):
        start = time.perf_counter_ns()
        try:
            return function(*args)
        finally:
            self.ns[phase] += time.perf_counter_ns() - start


def strict_int(value, low, high):
    return type(value) is int and low <= value <= high


def input_shape(primes):
    return (type(primes) is list and len(primes) <= 6
            and all(strict_int(p, 2, 13) for p in primes)
            and primes == sorted(set(primes)))


def integer_list(value, low, high):
    return type(value) is list and all(strict_int(v, low, high) for v in value)


def produce(primes, mode, meter):
    witness = {"primes": primes, "construction_trace": [], "search_trace": [],
               "status": "Candidate", "q": None, "cofactor": None}
    def construct():
        meter.charge("construction")
        if not input_shape(primes):
            raise ValueError("input shape")
        product = 1
        for p in primes:
            meter.charge("construction")
            product *= p
            witness["construction_trace"].append(product)
        meter.charge("construction")
        witness["N"] = product + 1
        if witness["N"] > 65535:
            raise ValueError("integer boundary")
    meter.timed("construction", construct)
    def search():
        n, started = witness["N"], time.perf_counter_ns()
        fuel = 0 if mode == "zero-search-fuel" else 256
        for d in range(2, math.isqrt(n) + 1):
            if len(witness["search_trace"]) >= fuel or time.perf_counter_ns() - started >= 1_000_000_000:
                witness.update(status="Unknown", reason="search budget exhausted")
                break
            meter.charge("search")
            remainder = n % d
            witness["search_trace"].append([d, remainder])
            if remainder == 0:
                witness.update(q=d, cofactor=n // d)
                break
        else:
            witness.update(q=n, cofactor=1)
        witness["search_coverage"] = [2, 2 + len(witness["search_trace"])]
        witness["search_required"] = [2, max(2, math.isqrt(n) + 1)]
    meter.timed("search", search)
    if mode == "forged-q-one":
        witness.update(q=1, cofactor=witness["N"])
    elif mode == "falsely-prime-successor":
        witness.update(q=witness["N"], cofactor=1)
    return witness


def check(primes, witness, meter):
    """Independent arithmetic reconstruction and exhaustive prime checks."""
    evidence = {"input_divisor_checks": [], "q_divisor_checks": [], "trace_checks": []}
    count = 0
    def step():
        nonlocal count
        if count >= 1024:
            raise Limit("verification budget exhausted")
        meter.charge("verification")
        count += 1
    def finish(status, reason):
        return {"status": status, "reason": reason, "verification_units": count,
                "evidence": evidence, "native_universe": "NotImplemented"}
    try:
        step()
        if (type(witness) is not dict or not input_shape(primes)
                or not input_shape(witness.get("primes")) or witness["primes"] != primes
                or witness.get("status") not in ("Candidate", "Unknown")):
            return finish("Blocked", "input shape or binding")
        for p in primes:
            for d in range(2, p):
                step()
                evidence["input_divisor_checks"].append([p, d, p % d])
                if p % d == 0:
                    return finish("Blocked", "composite input")
        product, reconstruction = 1, []
        for p in primes:
            step()
            product = product * p
            reconstruction.append(product)
        step()
        n = witness.get("N")
        if (not strict_int(n, 2, 65535) or n != product + 1
                or not integer_list(witness.get("construction_trace"), 1, 65534)
                or witness["construction_trace"] != reconstruction):
            return finish("Blocked", "product reconstruction")
        q, k = witness.get("q"), witness.get("cofactor")
        if witness.get("status") != "Unknown":
            step()
            if not strict_int(q, 2, 65535) or not strict_int(k, 1, 65535) or q * k != n or q in primes:
                return finish("Blocked", "prime-factor or outside-list relation")
            evidence["q_requested_divisors"] = [2, q]
            for d in range(2, q):
                step()
                remainder = q % d
                evidence["q_divisor_checks"].append([d, remainder])
                if remainder == 0:
                    return finish("Blocked", "claimed prime is composite")
            evidence["q_prime_coverage_complete"] = True
        trace = witness.get("search_trace")
        step()
        if (type(trace) is not list or len(trace) > 256
                or not integer_list(witness.get("search_coverage"), 2, 258)
                or witness["search_coverage"] != [2, len(trace) + 2]
                or not integer_list(witness.get("search_required"), 2, 258)
                or witness["search_required"] != [2, max(2, math.isqrt(n) + 1)]):
            return finish("Blocked", "search coverage encoding")
        for d, entry in enumerate(trace, 2):
            step()
            if (not integer_list(entry, 0, 65535) or len(entry) != 2
                    or entry != [d, n % d] or d * d > n):
                return finish("Blocked", "search trace arithmetic")
            evidence["trace_checks"].append(entry)
            if n % d == 0 and (d != q or d != len(trace) + 1):
                return finish("Blocked", "search continued past a factor")
        if witness.get("status") == "Unknown":
            if q is not None or k is not None or any(entry[1] == 0 for entry in trace):
                return finish("Blocked", "invalid pending search")
            evidence["pending_divisors"] = [2 + len(trace), max(2, math.isqrt(n) + 1)]
            return finish("Unknown", "valid partial search; no extension certified")
        if not ((trace and trace[-1] == [q, 0]) or (q == n and (len(trace) + 2) ** 2 > n)):
            return finish("Blocked", "incomplete successful search")
        return finish("FiniteExtensionVerified", "exact outside-prime certificate")
    except Limit as error:
        return finish("Unknown", str(error))


def encode(value):
    data = (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()
    if len(data) > MAX_BYTES:
        raise ValueError("serialized file bound exceeded")
    return data


def run(contract_path, output):
    resource.setrlimit(resource.RLIMIT_AS, (256 * 1024 ** 2, 256 * 1024 ** 2))
    def alarm(*_):
        raise Limit("five second process deadline")
    signal.signal(signal.SIGALRM, alarm)
    signal.setitimer(signal.ITIMER_REAL, 5)
    meter = Meter()
    with contract_path.open("rb") as stream:
        raw = stream.read(MAX_BYTES + 1)
    if len(raw) > MAX_BYTES or hashlib.sha256(raw).hexdigest() != CONTRACT_SHA:
        raise ValueError("frozen contract bytes do not match")
    contract = json.loads(raw)
    output.mkdir(parents=True, exist_ok=False)
    cases, serialized_main = [], None
    for case in contract["cases"]:
        began = time.perf_counter_ns()
        before = dict(meter.units)
        witness = produce(case["primes"], case["mode"], meter)
        judgment = meter.timed("verification", check, case["primes"], witness, meter)
        record = {"id": case["id"], "input": case, "witness": witness, "judgment": judgment,
                  "expected_met": judgment["status"] == case["expected"]}
        meter.charge("serialization")
        encoded = meter.timed("serialization", encode, record)
        if case["id"] == "main":
            serialized_main = encoded
        if case["id"] == "fresh":
            meter.ns["reuse"] += time.perf_counter_ns() - began
        record["charged_units"] = {k: meter.units[k] - before[k] for k in before}
        cases.append(record)
    began = time.perf_counter_ns()
    meter.charge("serialization")
    loaded = meter.timed("serialization", json.loads, serialized_main)
    recheck = meter.timed("verification", check, loaded["input"]["primes"], loaded["witness"], meter)
    meter.ns["reuse"] += time.perf_counter_ns() - began
    consistent = recheck == cases[0]["judgment"]
    report = {"schema": "adva.prime-universe.finite-report", "version": 0,
              "contract_sha256": CONTRACT_SHA, "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "cases": cases, "serialized_main_recheck": recheck, "serialized_recheck_equal": consistent,
              "all_expected_met": consistent and all(c["expected_met"] for c in cases),
              "native_universe": "NotImplemented", "theorem_status": "ExternalMathematicalArgument",
              "claim_scope": "Eight fixed finite cases; no universal theorem verified by execution",
              "residuals": contract["residuals"]}
    # Count all three final artifact writes before taking the final ledger snapshot.
    meter.units["serialization"] += 3
    if sum(meter.units.values()) > 2000:
        raise Limit("final serialization budget")
    def save_report():
        (output / "contract.json").write_bytes(raw)
        data = encode(report)
        (output / "report.json").write_bytes(data)
        return len(data)
    report_bytes = meter.timed("serialization", save_report)
    costs = {"charged_units": meter.units, "total_units": sum(meter.units.values()),
             "phase_ns": meter.ns, "elapsed_ns_before_costs_write": time.perf_counter_ns() - meter.started,
             "peak_rss_kib_linux": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
             "report_bytes": report_bytes, "global_limit_units": 2000,
             "accounting": "Logical construction/check/divisor steps and serialization events; not CPU instructions",
             "reuse_note": "Overlapping timing for fresh-case construction/check/serialization plus one serialized main recheck",
             "missing_measurements": ["Costs artifact's own encoding/write time and any later peak RSS", "Human research, coding and network time"]}
    (output / "costs.json").write_bytes(encode(costs))
    signal.setitimer(signal.ITIMER_REAL, 0)
    print(json.dumps({"all_expected_met": report["all_expected_met"], "total_units": costs["total_units"], "output": str(output)}))
    return 0 if report["all_expected_met"] else 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    raise SystemExit(run(args.contract, args.output))
