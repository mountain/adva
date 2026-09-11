"""Bounded external calibration, not an Adva semantic interpreter.

Authored by ChatGPT (OpenAI), submitted through Mingli Yuan's GitHub
account (mountain) as an authorized proxy. See docs/AI_ATTRIBUTION.md.
"""
import argparse
from collections import Counter, defaultdict
import hashlib
from itertools import combinations, permutations
import json
from pathlib import Path
import resource
import time


class Exhausted(Exception):
    pass


class Fuel:
    def __init__(self, cap, deadline):
        self.cap, self.deadline, self.used = cap, deadline, 0

    def tick(self):
        if self.used >= self.cap or time.monotonic() >= self.deadline:
            raise Exhausted()
        self.used += 1


def even(p):
    return sum(p[i] > p[j] for i in range(len(p))
               for j in range(i + 1, len(p))) % 2 == 0


def cycle_even(p):
    seen, cycles = set(), 0
    for i in range(len(p)):
        if i not in seen:
            cycles += 1
            while i not in seen:
                seen.add(i)
                i = p[i] - 1
    return (len(p) - cycles) % 2 == 0


def compose(p, q):
    return tuple(p[i - 1] for i in q)


def partition(domain, points, fuel):
    groups = defaultdict(list)
    for p in domain:
        fuel.tick()
        groups[tuple(p[i - 1] for i in points)].append(p)
    collision = next((ps[:2] for ps in groups.values() if len(ps) > 1), None)
    return {"points": list(points), "objects": len(domain),
            "observations": len(groups),
            "fibre_histogram": dict(sorted(Counter(map(len, groups.values())).items())),
            "status": "Ambiguous" if collision else "Separated",
            "collision": collision}


def coverage_judgment(submitted, universe, points, fuel):
    # universe is the internally enumerated reference, never a sender's count.
    if len(set(submitted)) != len(submitted) or not set(submitted) <= set(universe):
        return "InvalidDomain"
    if set(submitted) != set(universe):
        return "UnknownCoverage"
    try:
        return partition(submitted, points, fuel)["status"]
    except Exhausted:
        return "UnknownResource"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    start = time.perf_counter_ns()
    contract_path = Path(__file__).with_name("contract.json")
    contract_bytes = contract_path.read_bytes()
    contract = json.loads(contract_bytes)
    budget = contract["budgets"]
    resource.setrlimit(resource.RLIMIT_AS, (budget["address_space_bytes"], budget["address_space_bytes"]))
    resource.setrlimit(resource.RLIMIT_CPU, (10, 10))
    fuel = Fuel(budget["work_units"], time.monotonic() + budget["wall_seconds"])
    checks = []

    def check(name, condition):
        fuel.tick()
        if not condition:
            raise AssertionError(name)
        checks.append(name)

    report = {"schema": contract["schema"], "native_authority": "NotGranted",
              "contract_sha256": hashlib.sha256(contract_bytes).hexdigest(),
              "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    try:
        construction_start = time.perf_counter_ns()
        domains, candidates = {}, 0
        for n in (5, 6):
            domains[n] = []
            for p in permutations(range(1, n + 1)):
                fuel.tick()
                candidates += 1
                if even(p) != cycle_even(p):
                    raise AssertionError("parity oracles disagree")
                if even(p):
                    domains[n].append(p)
        construction_ns = time.perf_counter_ns() - construction_start
        a5, a6 = domains[5], domains[6]
        check("domain sizes 60 and 360", (len(a5), len(a6)) == (60, 360))
        embedded = [p + (6,) for p in a5]
        check("injective inclusion into A6", len(set(embedded)) == 60 and set(embedded) <= set(a6))
        verification_start = time.perf_counter_ns()
        for p in a5:
            for q in a5:
                fuel.tick()
                pq = compose(p, q)
                if compose(p + (6,), q + (6,)) != pq + (6,) or pq not in a5:
                    raise AssertionError("inclusion homomorphism")
        check("all 3600 inclusion products preserved", True)
        initial = {"A5_Q3": partition(a5, (1, 2, 3), fuel),
                   "embedded_A5_Q3": partition(embedded, (1, 2, 3), fuel),
                   "A6_Q3": partition(a6, (1, 2, 3), fuel),
                   "A6_Q4": partition(a6, (1, 2, 3, 4), fuel)}
        check("old scope remains separated", initial["A5_Q3"]["status"] == initial["embedded_A5_Q3"]["status"] == "Separated")
        check("expanded Q3 has 120 fibres of size 3", initial["A6_Q3"]["fibre_histogram"] == {3: 120})
        check("Q4 separates all A6", initial["A6_Q4"]["observations"] == 360)
        identity, cycle = (1, 2, 3, 4, 5, 6), (1, 2, 3, 5, 6, 4)
        check("explicit (456) collision and repair", identity != cycle and cycle in a6 and identity[:3] == cycle[:3] and identity[:4] != cycle[:4])
        verification_ns = time.perf_counter_ns() - verification_start
        search_start = time.perf_counter_ns()
        subsets, minima = {}, {}
        for n, domain in domains.items():
            rows = []
            for k in range(n + 1):
                for points in combinations(range(1, n + 1), k):
                    fuel.tick()
                    row = partition(domain, points, fuel)
                    rows.append(row)
            subsets[str(n)] = rows
            minima[str(n)] = min(len(r["points"]) for r in rows if r["status"] == "Separated")
        check("minimum cardinalities in coordinate observer grammar", minima == {"5": 3, "6": 4})
        search_ns = time.perf_counter_ns() - search_start
        reuse_start = time.perf_counter_ns()
        reuse = [partition(a5, (2, 4, 5), fuel), partition(a6, (2, 4, 5), fuel),
                 partition(a6, (2, 4, 5, 1), fuel)]
        check("nonprefix reuse", [r["status"] for r in reuse] == ["Separated", "Ambiguous", "Separated"])
        reuse_ns = time.perf_counter_ns() - reuse_start
        controls = {
            "missing": coverage_judgment(a6[:-1], a6, (1, 2, 3, 4), fuel),
            "duplicate_same_count": coverage_judgment(a6[:-1] + [a6[0]], a6, (1, 2, 3, 4), fuel),
            "odd": coverage_judgment(a6 + [(2, 1, 3, 4, 5, 6)], a6, (1, 2, 3, 4), fuel),
            "zero_fuel": coverage_judgment(a6, a6, (1, 2, 3, 4), Fuel(0, time.monotonic() + 1))}
        check("coverage and fuel refusals", controls == {"missing": "UnknownCoverage", "duplicate_same_count": "InvalidDomain", "odd": "InvalidDomain", "zero_fuel": "UnknownResource"})
        payload = {"domains": {str(n): ps for n, ps in domains.items()}, "initial": initial,
                   "coordinate_subsets": subsets, "minimum_coordinates": minima,
                   "reuse": reuse, "controls": controls, "checks": checks,
                   "explicit_counterexample": [identity, cycle]}
        serialization_start = time.perf_counter_ns()
        serialized = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        # JSON tuple/list and integer/string key normalization is explicit.
        decoded = json.loads(serialized)
        assert json.dumps(decoded, sort_keys=True, separators=(",", ":")) == serialized
        restored = [tuple(p) for p in decoded["domains"]["6"]]
        check("serialized domain replay", coverage_judgment(restored, a6, (1, 2, 3, 4), fuel) == "Separated")
        serialization_replay_ns = time.perf_counter_ns() - serialization_start
        report.update(status="Passed", evidence=json.loads(json.dumps(payload)),
                      candidate_permutations=candidates, coordinate_subsets=96,
                      inclusion_pairs=3600,
                      costs_ns={"construction": construction_ns, "verification": verification_ns,
                                "subset_search": search_ns, "reuse": reuse_ns,
                                "serialization_and_replay": serialization_replay_ns})
    except Exhausted:
        report.update(status="UnknownResource", passed_checks=checks)
    report.update(work_units=fuel.used, elapsed_before_final_write_ns=time.perf_counter_ns() - start,
                  peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                  limits_installed={"address_space_bytes": budget["address_space_bytes"], "cpu_seconds": 10},
                  platform="Linux; ru_maxrss in KiB", correction_replays=0)
    output = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if len(output.encode()) > budget["output_bytes"]:
        raise Exhausted("output limit")
    with open(args.output, "x", encoding="utf-8") as handle:
        handle.write(output)
    print(json.dumps({k: v for k, v in report.items() if k != "evidence"}, sort_keys=True))


if __name__ == "__main__":
    main()
