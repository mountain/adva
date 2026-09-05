"""Finite vocabulary search and reusable relation checks; no native authority.

The frozen universe is all partial orders on four labelled model states.
Words are monotone Boolean predicates, not native Adva operations or identities.
"""

from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import dataclass
import hashlib
from itertools import combinations, product
import json
from pathlib import Path
import platform
from statistics import median
import sys
from time import perf_counter
import tracemalloc


N = 4
PAIRS = tuple(product(range(N), repeat=2))
FULL = (1 << (N * N)) - 1
SCHEMA = "adva.research.finite-vocabulary-gradient.v1"
CACHE_LIMIT = 65536
ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / "examples/verified_witness/knowledge-gradient-four-states.json"


def encoded(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def digest(value: object) -> str:
    return hashlib.sha256(encoded(value)).hexdigest()


def relates(relation: int, i: int, j: int) -> bool:
    return bool(relation & (1 << (N * i + j)))


def is_order(relation: int) -> bool:
    return (
        type(relation) is int and 0 <= relation <= FULL
        and all(relates(relation, i, i) for i in range(N))
        and all(i == j or not (relates(relation, i, j) and relates(relation, j, i))
                for i, j in PAIRS)
        and all(not (relates(relation, i, j) and relates(relation, j, k))
                or relates(relation, i, k) for i, j, k in product(range(N), repeat=3))
    )


def monotone(relation: int, word: int) -> bool:
    return all(not relates(relation, i, j) or (word >> i & 1) <= (word >> j & 1)
               for i, j in PAIRS)


@dataclass(frozen=True)
class Task:
    relation: int
    coarse: tuple[int, ...] = ()

    def __post_init__(self) -> None:
        if not is_order(self.relation):
            raise ValueError("expected a partial order on exactly four labelled states")
        if type(self.coarse) is not tuple or len(set(self.coarse)) != len(self.coarse):
            raise ValueError("coarse coordinates must be a tuple without duplicates")
        if any(type(m) is not int or not 0 <= m < 16 or not monotone(self.relation, m)
               for m in self.coarse):
            raise ValueError("coarse coordinates must preserve the declared order")

    @property
    def words(self) -> tuple[int, ...]:
        return tuple(m for m in range(1, 15)
                     if m not in self.coarse and monotone(self.relation, m))

    @property
    def forbidden(self) -> int:
        return FULL ^ self.relation


def all_tasks() -> tuple[Task, ...]:
    """Enumerate all 3^6 antisymmetric off-diagonal assignments, then filter."""
    diagonal = sum(1 << (N * i + i) for i in range(N))
    tasks = []
    for directions in product(range(3), repeat=6):
        relation = diagonal
        for (i, j), direction in zip(combinations(range(N), 2), directions):
            if direction:
                left, right = (i, j) if direction == 1 else (j, i)
                relation |= 1 << (N * left + right)
        if is_order(relation):
            tasks.append(Task(relation))
    return tuple(sorted(tasks, key=lambda t: t.relation))


def scalar_energy(task: Task, family: tuple[int, ...]) -> int:
    """Independent coordinatewise specification, including lost true relations."""
    coordinates = [[bool(m & (1 << i)) for m in task.coarse + family] for i in range(N)]
    return sum(
        all(left <= right for left, right in zip(coordinates[i], coordinates[j]))
        != relates(task.relation, i, j)
        for i, j in PAIRS
    )


def exclusion_mask(word: int) -> int:
    return sum(1 << (N * i + j) for i, j in PAIRS
               if (word >> i & 1) and not (word >> j & 1))


def union(masks) -> int:
    result = 0
    for mask in masks:
        result |= mask
    return result


def make_table(task: Task) -> bytes:
    return encoded({"schema": SCHEMA, "relation": task.relation,
                    "coarse": list(task.coarse),
                    "rows": [[word, exclusion_mask(word)] for word in task.words]})


def check_table(task: Task, blob: bytes) -> dict[int, int]:
    """Check a bounded external coverage table against the requested task.

    No producer coverage function is called. Each row is checked through Boolean
    value lists and the coordinate-comparison specification over all 16 pairs.
    The table is task-bound by exact data, not authenticated by its digest.
    """
    if len(blob) > CACHE_LIMIT:
        raise ValueError("table exceeds byte limit")
    data = json.loads(blob)
    if type(data) is not dict or set(data) != {"schema", "relation", "coarse", "rows"}:
        raise ValueError("invalid table fields")
    if (data["schema"] != SCHEMA or type(data["relation"]) is not int
            or data["relation"] != task.relation or type(data["coarse"]) is not list
            or any(type(m) is not int for m in data["coarse"])
            or data["coarse"] != list(task.coarse)):
        raise ValueError("table belongs to a different task or schema")
    expected = []
    for word in range(1, 15):
        values = [bool(word & (1 << i)) for i in range(N)]
        if word not in task.coarse and all(
            not relates(task.relation, i, j) or values[i] <= values[j] for i, j in PAIRS
        ):
            expected.append(word)
    rows = data["rows"]
    if type(rows) is not list or len(rows) != len(expected):
        raise ValueError("missing or additional coverage rows")
    checked = {}
    for row, word in zip(rows, expected):
        if (type(row) is not list or len(row) != 2
                or any(type(v) is not int for v in row) or row[0] != word):
            raise ValueError("invalid or reordered row")
        values = [bool(word & (1 << i)) for i in range(N)]
        expected_bits = 0
        for index, (i, j) in enumerate(PAIRS):
            if not (values[i] <= values[j]):
                expected_bits += 2 ** index
        if row[1] != expected_bits:
            raise ValueError("incorrect coverage row")
        checked[word] = row[1]
    return checked


def object_bytes(value: object) -> int:
    """Conservative recursive size: shared child objects may be counted twice."""
    if isinstance(value, dict):
        return sys.getsizeof(value) + sum(object_bytes(k) + object_bytes(v) for k, v in value.items())
    if isinstance(value, (list, tuple)):
        return sys.getsizeof(value) + sum(object_bytes(v) for v in value)
    return sys.getsizeof(value)


class Evaluator:
    def __init__(self, task: Task, mode: str = "checked", cache_limit: int = CACHE_LIMIT):
        if mode not in ("scalar", "cached", "checked"):
            raise ValueError("unknown evaluation mode")
        if type(cache_limit) is not int or cache_limit < 0:
            raise ValueError("invalid cache limit")
        self.task, self.mode = task, mode
        self.words = task.words
        self.base = union(exclusion_mask(m) for m in task.coarse)
        self.blob = make_table(task) if mode == "checked" else b""
        self.table = (check_table(task, self.blob) if mode == "checked" else
                      {m: exclusion_mask(m) for m in self.words} if mode == "cached" else {})
        self.storage_bytes = object_bytes((self.words, self.base, self.table, self.blob))
        if self.storage_bytes > cache_limit:
            raise ValueError("retained evaluator payload exceeds cache limit")

    def energy(self, family: tuple[int, ...]) -> int:
        if any(type(m) is not int or m not in self.words for m in family):
            raise ValueError("family contains an unadmitted word")
        if self.mode == "scalar":
            return scalar_energy(self.task, family)
        covered = self.base | union(self.table[m] for m in family)
        return (self.task.forbidden & ~covered).bit_count()


def search(task: Task, policy: str, max_words: int = 3,
           fuel: int = 100, width: int = 4) -> dict:
    """A deterministic bounded search; fuel charges candidate-energy queries.

    Predicate admission and table checking are separate, bounded setup work.
    Ties use ascending word-mask tuples. No timing estimate chooses a word.
    """
    if policy not in ("terminal", "greedy", "beam"):
        raise ValueError("unknown search policy")
    if (any(type(v) is not int or v < 0 for v in (max_words, fuel))
            or type(width) is not int or width < 1):
        raise ValueError("invalid search limits")
    evaluator = Evaluator(task)
    trace: list[tuple[tuple[int, ...], int]] = []
    energies: dict[tuple[int, ...], int] = {}
    frontier = [()]
    best = ()
    reason = "word_budget"
    if fuel:
        trace.append(((), evaluator.energy(())))
        energies[()] = trace[0][1]
        if energies[()] == 0:
            reason = "witness"
    else:
        reason = "evaluation_budget"
    for _ in range(min(max_words, len(evaluator.words))) if fuel and reason != "witness" else ():
        children = sorted({tuple(sorted(family + (m,))) for family in frontier
                           for m in evaluator.words if m not in family})
        scored = []
        for child in children:
            if len(trace) == fuel:
                reason = "evaluation_budget"
                break
            energy = evaluator.energy(child)
            trace.append((child, energy))
            energies[child] = energy
            if (energy, len(child), child) < (energies[best], len(best), best):
                best = child
            scored.append((energy, child))
            if energy == 0:
                best, reason = child, "witness"
                break
        if reason in ("evaluation_budget", "witness"):
            break
        if not scored:
            reason = "candidate_family_exhausted"
            break
        scored.sort()
        if policy != "beam":
            old_energy = energies[frontier[0]]
            score = (lambda e: int(e != 0)) if policy == "terminal" else (lambda e: e)
            if score(scored[0][0]) >= score(old_energy):
                reason = "no_strict_descent"
                best = frontier[0]
                break
            frontier = [scored[0][1]]
            best = frontier[0]
        else:
            frontier = [family for _, family in scored[:width]]
    final_energy = energies.get(best)
    if final_energy is None:
        # No fuel means no candidate evaluation, including the initial state.
        final_energy = None
    status = "Found" if final_energy == 0 and trace else "Unknown"
    # Publication checks the complete selected interface by the scalar spec.
    if final_energy is not None and final_energy != scalar_energy(task, best):
        raise AssertionError("search result failed independent coordinate check")
    return {"status": status, "reason": reason, "selected": list(best),
            "energy": final_energy, "evaluations": len(trace),
            "query_trace_sha256": digest(trace),
            "frontier": [list(f) for f in frontier],
            "budget": {"max_words": max_words, "queries": fuel, "beam_width": width}}


def exact_minimum(task: Task) -> dict:
    """Complete cardinality-ordered finite oracle, checked by scalar semantics."""
    checked = 0
    for count in range(len(task.words) + 1):
        for family in combinations(task.words, count):
            checked += 1
            if scalar_energy(task, family) == 0:
                return {"selected": list(family), "minimum_words": count,
                        "families_checked": checked}
    raise AssertionError("complete monotone family did not separate this order")


def fixture_report() -> dict:
    rows = []
    histogram: Counter = Counter()
    solved: Counter = Counter()
    query_counts: Counter = Counter()
    for task in all_tasks():
        exact = exact_minimum(task)
        unlimited = search(task, "greedy", max_words=14)
        policies = {p: search(task, p) for p in ("terminal", "greedy", "beam")}
        for policy, result in policies.items():
            solved[policy] += result["status"] == "Found"
            query_counts[policy] += result["evaluations"]
        histogram[(len(unlimited["selected"]), exact["minimum_words"])] += 1
        if unlimited["status"] != "Found":
            raise AssertionError("unrestricted greedy calibration did not terminate")
        rows.append({"relation": task.relation, "coverage_table": json.loads(make_table(task)),
                     "exact": exact, "greedy_unrestricted": unlimited, "bounded": policies})
    return {"schema": SCHEMA, "scope": "all four-state labelled partial orders; empty coarse interface",
            "configuration": {"states": N, "assignments_enumerated": 3 ** 6,
                              "word_cost": 1, "bounded_words": 3, "query_fuel": 100,
                              "beam_width": 4, "cache_payload_limit_bytes": CACHE_LIMIT},
            "summary": {"tasks": len(rows), "bounded_solved": dict(solved),
                        "bounded_queries": dict(query_counts),
                        "exact_feasible_at_three": sum(r["exact"]["minimum_words"] <= 3 for r in rows),
                        "greedy_vs_exact": [{"greedy": g, "exact": e, "tasks": count}
                                            for (g, e), count in sorted(histogram.items())]},
            "tasks": rows,
            "open_obligations": ["Native Adva identity and transport certificates",
                                 "Measured advantage over ordinary caching",
                                 "Generalization beyond the frozen finite family",
                                 "A real user task and acceptance criterion",
                                 "Physical interpretation and vocabulary-spectrum correspondence"]}


def frozen_workload() -> tuple[tuple, float]:
    """Shared task/query generation and independent scalar answers are charged."""
    start = perf_counter()
    workload = []
    for task in all_tasks():
        families = tuple(f for size in range(4) for f in combinations(task.words, size))
        reference = tuple(scalar_energy(task, f) for f in families)
        workload.append((task, families, reference))
    return tuple(workload), perf_counter() - start


def evaluate_workload(workload: tuple, mode: str) -> dict:
    """Time setup, admission, table construction/checking, queries and recording.

    One task table is resident at a time. Result serialization and comparison
    with the shared independently generated reference are inside the timer.
    """
    start = perf_counter()
    hasher = hashlib.sha256()
    peak_storage = queries = record_bytes = 0
    for task, families, reference in workload:
        evaluator = Evaluator(task, mode)
        answers = tuple(evaluator.energy(f) for f in families)
        if answers != reference:
            raise AssertionError("evaluation disagrees with scalar specification")
        payload = encoded([task.relation, answers])
        hasher.update(payload)
        queries += len(answers)
        record_bytes += len(payload)
        peak_storage = max(peak_storage, evaluator.storage_bytes)
        del evaluator, answers, payload
    return {"seconds": perf_counter() - start, "queries": queries,
            "answer_sha256": hasher.hexdigest(), "serialized_answer_bytes": record_bytes,
            "max_retained_evaluator_bytes": peak_storage}


def benchmark(repetitions: int = 5) -> dict:
    if type(repetitions) is not int or not 1 <= repetitions <= 20:
        raise ValueError("repetitions must be between one and twenty")
    workload, common_seconds = frozen_workload()
    modes = ("scalar", "cached", "checked")
    samples = {mode: [] for mode in modes}
    for repeat in range(repetitions):
        for mode in modes[repeat % 3:] + modes[:repeat % 3]:
            samples[mode].append(evaluate_workload(workload, mode))
    memory = {}
    # Separate instrumentation runs do not contaminate latency observations.
    for mode in modes:
        tracemalloc.start()
        evaluate_workload(workload, mode)
        _, memory[mode] = tracemalloc.get_traced_memory()
        tracemalloc.stop()
    medians = {m: median(s["seconds"] for s in samples[m]) for m in modes}
    return {"schema": SCHEMA, "python": sys.version, "platform": platform.platform(),
            "repetitions": repetitions, "cold_tables_each_run": True,
            "common_preparation_and_scalar_reference_seconds": common_seconds,
            "median_variant_seconds": medians,
            "median_total_including_common_seconds": {m: common_seconds + s for m, s in medians.items()},
            "peak_traced_allocations_bytes_excluding_shared_workload": memory,
            "samples": samples,
            "measurement_scope": "post-import in-process; includes table setup/checks, queries, reference comparison, result serialization and hashing; shared preparation separately charged; excludes interpreter startup and final file write",
            "workload_sha256": digest([[t.relation, fs] for t, fs, _ in workload])}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--check", type=Path)
    parser.add_argument("--benchmark", type=Path)
    args = parser.parse_args()
    if args.benchmark:
        report = benchmark()
        args.benchmark.write_bytes(encoded(report))
        print(json.dumps({k: v for k, v in report.items() if k != "samples"}, indent=2))
    else:
        payload = encoded(fixture_report())
        if args.check and args.check.read_bytes() != payload:
            parser.exit(1, "fixture differs from the complete finite replay\n")
        if args.output:
            args.output.write_bytes(payload)
        print(json.dumps(json.loads(payload)["summary"], indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
