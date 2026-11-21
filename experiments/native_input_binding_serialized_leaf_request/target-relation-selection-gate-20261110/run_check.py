#!/usr/bin/env python3
"""One bounded invocation for the relation-selection gate."""
import json
import resource
import sys
import time

from evaluate import run_all


MIB = 1024 * 1024


def main():
    resource.setrlimit(resource.RLIMIT_CPU, (10, 10))
    resource.setrlimit(resource.RLIMIT_AS, (256 * MIB, 256 * MIB))
    resource.setrlimit(resource.RLIMIT_FSIZE, (1 * MIB, 1 * MIB))
    started = time.perf_counter_ns()
    results = run_all()
    if len(results) != 8 or not all(row["passed"] for row in results):
        raise SystemExit("finite case mismatch")
    elapsed = time.perf_counter_ns() - started
    usage = resource.getrusage(resource.RUSAGE_SELF)
    payload = {
        "schema": "adva.target-relation-selection-gate.outcome.v0",
        "status": "PassedFiniteRelationSelectionGate",
        "cases": results,
        "cases_run": len(results),
        "cases_passed": sum(row["passed"] for row in results),
        "new_instance_reuse": "same diagram digest with distinct ordered slots, contexts, sources and occurrences",
        "search_candidates": 0,
        "search_nodes": 0,
        "opaque_request_reads": 0,
        "native_diagram_byte_reads": 0,
        "native_executions": 0,
        "correction_replays": 0,
        "process_elapsed_ns_before_serialization": elapsed,
        "process_ru_maxrss_kib": usage.ru_maxrss,
        "memory_scope": "Linux RUSAGE_SELF for this Python process only.",
        "semantic_authority": False,
        "words_formed_or_revised": 0,
        "residual": "The target relation and real request mapping remain unspecified; Rust admission, native controls, certified relation checking and durable receipt implementation are NotRun."
    }
    serialize_started = time.perf_counter_ns()
    json.dumps(payload, indent=2, sort_keys=True)
    payload["serialization_ns"] = time.perf_counter_ns() - serialize_started
    payload["serialized_bytes"] = 0
    while True:
        encoded = json.dumps(payload, indent=2, sort_keys=True) + "\n"
        size = len(encoded.encode("utf-8"))
        if size == payload["serialized_bytes"]:
            break
        payload["serialized_bytes"] = size
    sys.stdout.write(encoded)


if __name__ == "__main__":
    main()
