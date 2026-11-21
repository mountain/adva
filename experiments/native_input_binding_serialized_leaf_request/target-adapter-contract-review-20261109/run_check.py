#!/usr/bin/env python3
"""One bounded structural verification route with process-level measurements."""
import io
import json
from pathlib import Path
import resource
import sys
import time
import unittest

from verify import validate
import test_verify


ROOT = Path(__file__).resolve().parent
MIB = 1024 * 1024


def main():
    resource.setrlimit(resource.RLIMIT_CPU, (20, 20))
    resource.setrlimit(resource.RLIMIT_AS, (256 * MIB, 256 * MIB))
    resource.setrlimit(resource.RLIMIT_FSIZE, (1 * MIB, 1 * MIB))
    started = time.perf_counter_ns()
    load_started = time.perf_counter_ns()
    document = json.loads(
        (ROOT / "adapter-obligation-v0.json").read_text(encoding="utf-8"))
    load_ns = time.perf_counter_ns() - load_started

    verify_started = time.perf_counter_ns()
    direct = validate(document)
    verify_ns = time.perf_counter_ns() - verify_started

    test_started = time.perf_counter_ns()
    stream = io.StringIO()
    suite = unittest.defaultTestLoader.loadTestsFromModule(test_verify)
    result = unittest.TextTestRunner(stream=stream, verbosity=2).run(suite)
    test_ns = time.perf_counter_ns() - test_started
    if not result.wasSuccessful() or result.testsRun != 13:
        raise SystemExit(stream.getvalue())

    elapsed_ns = time.perf_counter_ns() - started
    usage = resource.getrusage(resource.RUSAGE_SELF)
    payload = {
        "schema": "adva.target-adapter-obligation-review.outcome.v0",
        "status": "PassedFiniteStructuralContractReview",
        "direct_verification": direct,
        "tests_run": result.testsRun,
        "canonical_positive_cases": 1,
        "declared_mutation_cases": 12,
        "mutations_rejected": 12,
        "search_candidates": 0,
        "search_nodes": 0,
        "opaque_request_reads": 0,
        "diagram_byte_reads": 0,
        "native_executions": 0,
        "correction_replays": 0,
        "load_ns": load_ns,
        "direct_verification_ns": verify_ns,
        "finite_control_suite_ns": test_ns,
        "process_elapsed_ns_before_serialization": elapsed_ns,
        "process_ru_maxrss_kib": usage.ru_maxrss,
        "memory_scope": "Linux RUSAGE_SELF maximum resident set for this one Python process; not a process-tree or system peak.",
        "limits": {
            "external_wall_seconds": 30,
            "cpu_seconds": 20,
            "address_space_mib": 256,
            "output_bytes": 1048576
        },
        "semantic_authority": False,
        "words_formed_or_revised": 0,
        "residual": "The adapter remains unimplemented and unexecuted; native diagram admission, the exact target request, independent review, Research 0090 coverage and Research 0092 promotion remain open."
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
