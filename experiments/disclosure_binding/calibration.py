"""Research 0158. Synthetic, bounded disclosure-context regression, not a crypto fix."""
from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import json
import resource
import signal
import sys
import time
from pathlib import Path

CONTRACT_SHA = "5ca302509d68bb53ba24166db02ce2ca3f12611be53d2a8a36afc2dd1ff26ddb"


def encoded(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


class Study:
    def __init__(self, root, output, contract):
        self.root, self.output, self.contract = root, output, contract
        self.calls = 0
        self.files = 0
        self.bytes = 0
        self.serialization_ns = 0
        self.write_ns = 0
        self.deadline = time.monotonic() + 4.5
        source = root / contract["source_path"]
        if digest(source.read_bytes()) != contract["source_sha256"]:
            raise ValueError("Pinned source changed; do not relabel this calibration")
        spec = importlib.util.spec_from_file_location("pinned_lineage_0158", source)
        self.lib = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.lib)

    def tick(self):
        if time.monotonic() > self.deadline:
            raise TimeoutError("study deadline")

    def api(self, name, *args, **kwargs):
        self.tick()
        self.calls += 1
        if self.calls > 64:
            raise RuntimeError("repository API call cap")
        return getattr(self.lib, name)(*args, **kwargs)

    def save(self, relative, value):
        self.tick()
        start = time.perf_counter_ns()
        raw = encoded(value)
        self.serialization_ns += time.perf_counter_ns() - start
        if len(raw) > 262144 or self.bytes + len(raw) > 1048576 or self.files >= 64:
            raise RuntimeError("output cap")
        path = self.output / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        start = time.perf_counter_ns()
        with path.open("xb") as handle:
            handle.write(raw)
        self.write_ns += time.perf_counter_ns() - start
        self.files += 1
        self.bytes += len(raw)
        return path

    def slot(self, content, blinding, nonce_pair):
        """Public deterministic fixture nonces. NEVER use these for real secrets."""
        lib = self.lib
        q, r, g, h = lib.PHASE1_Q, lib.PHASE1_R, lib.PHASE1_G, lib.PHASE1_H
        m = int.from_bytes(hashlib.sha256(encoded(content)).digest(), "big") % r
        c = pow(g, m, q) * pow(h, blinding, q) % q
        k1, k2 = nonce_pair
        t = pow(g, k1, q) * pow(h, k2, q) % q
        e = int.from_bytes(hashlib.sha256(encoded([str(v) for v in (q, g, h, c, t)])).digest(), "big") % r
        return {"commitment": {"q": str(q), "g": str(g), "h": str(h), "c": str(c)},
                "proof": {"t": str(t), "s1": str((k1 + e * m) % r),
                          "s2": str((k2 + e * blinding) % r)}}

    def fixtures(self):
        prepared = []
        for item in self.contract["fixtures"]:
            self.tick()
            ident, blinding = item["id"], item["blinding"]
            slot = self.slot(item["content"], blinding, (7, 11))
            replacement = self.slot(item["replacement"], blinding + 1, (13, 17))
            assert slot["commitment"]["c"] != replacement["commitment"]["c"]
            body = {"schema": self.lib.RECORD_SCHEMA, "version": 0,
                    "package": "arithmetic", "seq": 1,
                    "proposition": "synthetic-undisclosed-candidate",
                    "environment": {"note": "public fixture; not a real secret"},
                    "checker": {"id": "research-0158", "version": "0"},
                    "verdict": "Unknown", "residual": None,
                    "cites_same_home": [], "cites_cross": [],
                    "budget_consumed": {"units": 1}, "secret_slot": slot}
            body["digest"] = digest(encoded(body))
            record = self.save(f"{ident}/lineage/arithmetic/records/000001.json", body)
            chain = self.api("compute_chain", "arithmetic", 1,
                             lambda seq: (record.read_bytes(), self.lib.validate_record(body, seq=seq, package="arithmetic")))
            checkpoint = self.api("build_checkpoint", chain)
            anchor = self.api("build_anchor", 0, {"arithmetic": checkpoint}, "")
            anchor_path = self.save(f"{ident}/anchor.json", anchor)
            alternate = self.api("build_anchor", 1, {"arithmetic": checkpoint}, "")
            self.save(f"{ident}/substituted-anchor.json", alternate)
            expected_anchor = digest(anchor_path.read_bytes())
            original = {"schema": self.lib.DISCLOSURE_REQUEST_SCHEMA, "version": 0,
                        **slot, "content": item["content"], "blinding": str(blinding)}
            changed = dict(original, content=item["replacement"])
            replaced = {**original, **replacement, "content": item["replacement"], "blinding": str(blinding + 1)}
            requests = [original, changed, replaced, original, original]
            for index, (control, request) in enumerate(zip(self.contract["controls"], requests)):
                rel = f"{ident}/requests/{control}.json"
                self.save(rel, request)
                supplied_anchor = (f"{ident}/missing-anchor.json" if control == "missing-anchor" else
                                   f"{ident}/substituted-anchor.json" if control == "substituted-anchor" else
                                   f"{ident}/anchor.json")
                prepared.append({"id": ident + "/" + control, "request": rel,
                                 "anchor": supplied_anchor, "root": ident,
                                 "expected_anchor_sha256": expected_anchor,
                                 "expected_raw": self.contract["expected_raw"][index],
                                 "expected_context": self.contract["expected_context"][index]})
        return prepared

    def context_gate(self, case):
        """Fixed one-record, quiescent-root profile; only reference-context binding."""
        self.tick()
        anchor = self.output / case["anchor"]
        if not anchor.is_file():
            return {"status": "Unknown", "reason": "AnchorMissing"}
        if digest(anchor.read_bytes()) != case["expected_anchor_sha256"]:
            return {"status": "Rejected", "reason": "TrustedAnchorMismatch"}
        root = self.output / case["root"]
        report = self.api("tamper_check", root, anchor)
        if report["status"] != "Intact":
            return {"status": "Rejected", "reason": "ChainNotIntact"}
        request_path = self.output / case["request"]
        request = json.loads(request_path.read_bytes())
        record = json.loads((root / "lineage/arithmetic/records/000001.json").read_bytes())
        expected = record["secret_slot"]
        supplied = {"commitment": request["commitment"], "proof": request["proof"]}
        if encoded(supplied) != encoded(expected):
            return {"status": "Rejected", "reason": "AnchoredSlotMismatch"}
        result = self.api("verify", "disclosure", request_path, anchor_path=anchor)
        if result["status"] != "Verified":
            return {"status": result["status"], "reason": "OpeningEquationNotVerified"}
        return {"status": "ContextBoundOpening", "reason": "FixedSlotAndOpeningChecked",
                "original_content_binding": "NotEstablished",
                "native_admission": "NotGranted"}

    def evaluate(self, cases):
        results, raw_ns, gate_ns = [], 0, 0
        for case in cases:
            self.tick()
            t = time.perf_counter_ns()
            raw = self.api("verify", "disclosure", self.output / case["request"],
                           anchor_path=self.output / case["anchor"])
            raw_ns += time.perf_counter_ns() - t
            t = time.perf_counter_ns()
            gated = self.context_gate(case)
            gate_ns += time.perf_counter_ns() - t
            assert raw["status"] == case["expected_raw"], (case, raw)
            assert gated["status"] == case["expected_context"], (case, gated)
            results.append({"id": case["id"], "raw_report": raw, "context_report": gated})
        return results, {"raw_api_ns": raw_ns, "context_gate_ns": gate_ns}


def toy_witnesses(contract):
    group = contract["arithmetic"]["toy"]
    q, r, g, h, a = [group[k] for k in ("modulus", "order", "g", "h", "known_log")]
    assert pow(g, a, q) == h and pow(g, r, q) == 1
    inverse = pow(a, -1, r)
    assert a * inverse % r == 1
    rows = []
    for m, b, different_m in contract["arithmetic"]["toy_cases"]:
        different_b = (b + (m - different_m) * inverse) % r
        assert 1 <= different_b < r and m != different_m
        c = pow(g, m, q) * pow(h, b, q) % q
        other_c = pow(g, different_m, q) * pow(h, different_b, q) % q
        assert c == other_c
        rows.append({"message": m, "blinding": b, "other_message": different_m,
                     "other_blinding": different_b, "commitment": c,
                     "other_commitment": other_c,
                     "exponent_residual_mod_order": (m + a*b - different_m - a*different_b) % r})
    try:
        pow(0, -1, r)
    except ValueError:
        pass
    else:
        raise AssertionError("zero inverse was not rejected")
    return {"group": group, "rows": rows, "zero_inverse": "Rejected",
            "pinned_group_log_recovered": False,
            "scope": "Conditional algebraic illustration only; not pinned-group equivocation"}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    start = time.perf_counter_ns()
    resource.setrlimit(resource.RLIMIT_AS, (268435456, 268435456))
    resource.setrlimit(resource.RLIMIT_CPU, (5, 5))
    resource.setrlimit(resource.RLIMIT_FSIZE, (262144, 262144))
    signal.alarm(5)
    root = Path(__file__).resolve().parents[2]
    raw = (root / "docs/research/0158-disclosure-binding-contract.json").read_bytes()
    if digest(raw) != CONTRACT_SHA:
        raise ValueError("Frozen contract changed")
    contract = json.loads(raw)
    args.output.mkdir(parents=True, exist_ok=False)
    study = Study(root, args.output, contract)
    formation_start = time.perf_counter_ns()
    toy = toy_witnesses(contract)
    cases = study.fixtures()
    formation_ns = time.perf_counter_ns() - formation_start
    initial, initial_cost = study.evaluate(cases)
    snapshot = {"cases": cases, "toy": toy}
    payload_path = study.save("inputs.json", snapshot)
    parse_start = time.perf_counter_ns()
    reloaded = json.loads(payload_path.read_bytes())
    parse_ns = time.perf_counter_ns() - parse_start
    replay_start = time.perf_counter_ns()
    replay, replay_cost = study.evaluate(reloaded["cases"])
    replay_ns = time.perf_counter_ns() - replay_start
    projection = lambda rs: [(r["id"], r["raw_report"]["status"], r["context_report"]) for r in rs]
    assert projection(initial) == projection(replay)
    assert reloaded["toy"] == toy_witnesses(contract)
    report = {"schema": "adva.research.disclosure-binding-result.v0", "status": "CounterexampleRetained",
              "source_sha256": contract["source_sha256"], "contract_sha256": CONTRACT_SHA,
              "toy": toy, "initial": initial, "replay": replay,
              "all_expected_controls": True, "serialized_replay_matches": True,
              "raw_verified_without_expected_context": 6,
              "context_gate_admits_without_expected_context": 0,
              "new_word": {"name": "anchor-bound-disclosure", "status": "Proposed",
                           "guarantee": "Only the frozen one-record context relation; not binding security"},
              "residuals": ["Pinned group known-log setup lacks a binding-security justification",
                            "Numeric pinned-group logarithm was not recovered; toy is not that attack",
                            "No cryptographic security, human acceptance or native free established",
                            "Quiescent synthetic files; not concurrent/adversarial filesystem hardening",
                            "No evidence real records were altered"],
              "cost": {"formation_ns": formation_ns, "initial": initial_cost,
                       "parse_ns": parse_ns, "replay_total_ns": replay_ns, "replay": replay_cost,
                       "repository_api_calls": study.calls, "search_candidates": 0,
                       "native_calls": 0, "signing_key_accesses": 0,
                       "memory_peak_rss_kib_linux": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                       "fresh_reuse": "Fresh fixture uses unchanged gate; timings included in initial/replay totals",
                       "timing_scope": "Nested timings; import/startup and research/network excluded from phase timings"}}
    study.save("report.json", report)
    cost = {"elapsed_ns_through_report_save": time.perf_counter_ns() - start,
            "serialization_ns_through_report": study.serialization_ns,
            "write_ns_through_report": study.write_ns,
            "output_files_before_cost": study.files, "output_bytes_before_cost": study.bytes,
            "repository_api_calls": study.calls,
            "peak_rss_kib_linux": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
            "scope": "Cost-file serialization/write excluded; outer process measurement includes exit. File bytes are not RAM."}
    study.save("cost.json", cost)
    print(json.dumps({"status": report["status"], "controls": 10, "replays": 10,
                      "repository_api_calls": study.calls, "output_files": study.files,
                      "output_bytes": study.bytes}))


if __name__ == "__main__":
    main()
