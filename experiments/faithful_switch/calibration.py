#!/usr/bin/env python3
"""Bounded exact representation checks; no native Adva semantic authority."""
import argparse
from collections import Counter, defaultdict
import copy
from functools import lru_cache
import hashlib
import itertools
import json
import math
from pathlib import Path
import resource
import signal
import time

UNITS = 0
LIMIT = 0
DEADLINE = 0.0
IMAGE_CAP = 0


def charge(n=1):
    global UNITS
    UNITS += n
    if UNITS > LIMIT or time.monotonic() > DEADLINE:
        raise TimeoutError("finite work or wall limit")


def canonical(x):
    return json.dumps(x, sort_keys=True, separators=(",", ":"))


def same(x, y):
    charge()
    assert canonical(x) == canonical(y)


def identity(n):
    return [[{0: 1} if i == j else {} for j in range(n)] for i in range(n)]


def multiply(a, b):
    n = len(a)
    out = [[{} for _ in range(n)] for _ in range(n)]
    for i in range(n):
        for j in range(n):
            cell = Counter()
            for k in range(n):
                for e, c in a[i][k].items():
                    for f, d in b[k][j].items():
                        charge()
                        cell[e + f] += c * d
            out[i][j] = {e: c for e, c in cell.items() if c}
    return out


def generator_matrix(n, g):
    out = identity(n)
    i = abs(g) - 1
    if g > 0:
        block = [[{0: 1, 1: -1}, {1: 1}], [{0: 1}, {}]]
    else:
        block = [[{}, {0: 1}], [{-1: 1}, {0: 1, -1: -1}]]
    for a in range(2):
        for b in range(2):
            out[i + a][i + b] = block[a][b]
    return out


def burau(n, word):
    out = identity(n)
    for g in word:
        out = multiply(out, generator_matrix(n, g))
    return out


def pack(matrix):
    return [[[list(x) for x in sorted(p.items())] for p in row] for row in matrix]


def artin(n, word):
    images = [(i,) for i in range(1, n + 1)]
    for g in word:
        i = abs(g)
        substitution = [(j,) for j in range(1, n + 1)]
        if g > 0:
            substitution[i - 1], substitution[i] = (i, i + 1, -i), (i,)
        else:
            substitution[i - 1], substitution[i] = (i + 1,), (-i - 1, i, i + 1)
        following = []
        for image in images:
            stack = []
            for letter in image:
                replacement = substitution[abs(letter) - 1]
                if letter < 0:
                    replacement = tuple(-j for j in reversed(replacement))
                for j in replacement:
                    charge()
                    if stack and stack[-1] == -j:
                        stack.pop()
                    else:
                        stack.append(j)
                    if len(stack) > IMAGE_CAP:
                        raise TimeoutError("free image cap")
            following.append(tuple(stack))
        images = following
    return images


def fox(images):
    """Abelianized Fox Jacobian via signed prefixes; no matrix products."""
    n = len(images)
    matrix = []
    for image in images:
        terms = [Counter() for _ in range(n)]
        height = 0
        for letter in image:
            charge()
            if letter > 0:
                terms[letter - 1][height] += 1
                height += 1
            else:
                height -= 1
                terms[-letter - 1][height] -= 1
        matrix.append([{e: c for e, c in p.items() if c} for p in terms])
    return matrix


def check_row(row, n, word):
    same(row["scope"], {"n": n, "word": list(word), "convention": "right-substitution-v0"})
    images = artin(n, word)
    same(row["free_images"], images)
    same(row["matrix"], pack(fox(images)))


@lru_cache(maxsize=None)
def choose_integer(a, k):
    out = 1
    for j in range(1, k + 1):
        out = out * (a - j + 1) // j
    return out


def jet_poly(p, order):
    charge((order + 1) * len(p) + 1)
    return [sum(c * choose_integer(e, j) for e, c in p.items()) for j in range(order + 1)]


def jet(matrix, order):
    return [[jet_poly(p, order) for p in row] for row in matrix]


def recover(jets, radius):
    """Multiply by t^radius, then change back from h=t-1 to t."""
    degree = 2 * radius
    assert len(jets) >= degree + 1
    b = [sum(math.comb(radius, a) * jets[r - a] for a in range(min(radius, r) + 1)) for r in range(degree + 1)]
    out = {}
    for d in range(degree + 1):
        charge(degree - d + 1)
        c = sum(b[r] * math.comb(r, d) * (-1) ** (r - d) for r in range(d, degree + 1))
        if c:
            out[d - radius] = c
    return out


def words(n, bound):
    alphabet = tuple(range(1, n)) + tuple(range(-1, -n, -1))
    level = [()]
    yield ()
    for _ in range(bound):
        level = [w + (g,) for w in level for g in alphabet if not w or w[-1] != -g]
        yield from level


def swap(matrix, permutation):
    return [[matrix[permutation[i]][permutation[j]] for j in range(len(permutation))] for i in range(len(permutation))]


def reverse_search(case, orders):
    n = case["n"]
    a, b = burau(n, case["left"]), burau(n, case["right"])
    coarse_a, coarse_b = jet(a, 0), jet(b, 0)
    swaps = []
    for pi in itertools.permutations(range(n)):
        charge()
        swaps.append({"basis_order": list(pi), "separated": swap(coarse_a, pi) != swap(coarse_b, pi)})
    attempts, witness = [], None
    for k in orders:
        charge()
        ja, jb = jet(a, k), jet(b, k)
        if ja == jb:
            attempts.append({"order": k, "status": "NotSeparated"})
            continue
        for i in range(n):
            for j in range(n):
                if ja[i][j] != jb[i][j] and witness is None:
                    d = next(r for r in range(k + 1) if ja[i][j][r] != jb[i][j][r])
                    witness = {"row": i, "column": j, "degree": d,
                               "left_coefficient": ja[i][j][d], "right_coefficient": jb[i][j][d],
                               "delta": ja[i][j][d] - jb[i][j][d]}
        attempts.append({"order": k, "status": "Separated"})
        break
    return {"case": case, "swaps": swaps, "attempts": attempts, "witness": witness,
            "status": "Separated" if witness else "SameExactMatrix" if a == b else "Unknown:ObserverFamilyExhausted",
            "raw_words_retained": [case["left"], case["right"]]}


def check_search(receipt, case, orders):
    same(receipt["case"], case)
    # Rebuild the source matrices by the other representation path.
    a, b = fox(artin(case["n"], case["left"])), fox(artin(case["n"], case["right"]))
    n = case["n"]
    same(receipt["raw_words_retained"], [case["left"], case["right"]])
    expected_swaps = []
    for pi in itertools.permutations(range(n)):
        diff = any(sum(a[i][j].values()) != sum(b[i][j].values()) for i in pi for j in pi)
        expected_swaps.append({"basis_order": list(pi), "separated": diff})
    same(receipt["swaps"], expected_swaps)
    attempts, witness = [], None
    for k in orders:
        found = []
        for i in range(n):
            for j in range(n):
                left, right = jet_poly(a[i][j], k), jet_poly(b[i][j], k)
                for degree in range(k + 1):
                    if left[degree] != right[degree]:
                        found.append((i, j, degree, left[degree], right[degree]))
        if not found:
            attempts.append({"order": k, "status": "NotSeparated"})
        else:
            i, j, d, ca, cb = found[0]
            witness = {"row": i, "column": j, "degree": d, "left_coefficient": ca,
                       "right_coefficient": cb, "delta": ca - cb}
            attempts.append({"order": k, "status": "Separated"})
            break
    same(receipt["attempts"], attempts)
    same(receipt["witness"], witness)
    same(receipt["status"], "Separated" if witness else "SameExactMatrix" if a == b else "Unknown:ObserverFamilyExhausted")


def reject(name, fn, controls):
    try:
        fn()
    except AssertionError:
        controls.append({"name": name, "status": "Rejected"})
    else:
        raise AssertionError("negative control accepted: " + name)


def bounded_zero_certificate(p, radius):
    assert all(-radius <= exponent <= radius for exponent in p)
    assert not any(jet_poly(p, 2 * radius))


def run(contract, report):
    records, tables, relations = [], [], []
    report.update(records=records, partition_tables=tables, relation_checks=relations)
    order_max = max(contract["families"]["jet_orders"])
    radius = contract["families"]["max_word_length"]
    coefficients_checked = 0
    for n in contract["families"]["strands"]:
        groups = [defaultdict(set) for _ in range(order_max + 1)]
        actions_by_matrix = defaultdict(set)
        word_count = 0
        for word in words(n, radius):
            charge()
            m, images = burau(n, word), artin(n, word)
            row = {"scope": {"n": n, "word": list(word), "convention": "right-substitution-v0"},
                   "free_images": images, "matrix": pack(m)}
            check_row(row, n, word)
            records.append(row)
            matrix_key, action_key = canonical(pack(m)), canonical(images)
            actions_by_matrix[matrix_key].add(action_key)
            jmax = jet(m, order_max)
            for i in range(n):
                for j in range(n):
                    assert all(-radius <= e <= radius for e in m[i][j])
                    same(pack([[recover(jmax[i][j], radius)]]), pack([[m[i][j]]]))
                    coefficients_checked += 1
            for k in range(order_max + 1):
                jk = [[p[:k + 1] for p in r] for r in jmax]
                groups[k][canonical(jk)].add(matrix_key)
            word_count += 1
        expected = 1 + sum((2 * n - 2) * (2 * n - 3) ** (length - 1) for length in range(1, radius + 1))
        assert word_count == expected
        counts = [len(g) for g in groups]
        assert counts == sorted(counts)
        assert all(len(v) == 1 for v in groups[order_max].values())
        tables.append({"n": n, "words": word_count, "exact_matrix_classes": len(actions_by_matrix),
                       "free_action_classes": len(set().union(*actions_by_matrix.values())),
                       "matrix_classes_with_distinct_free_actions": sum(len(v) > 1 for v in actions_by_matrix.values()),
                       "jet_class_counts": counts,
                       "jet_buckets_merging_exact_matrices": [sum(len(v) > 1 for v in g.values()) for g in groups]})
        pairs = []
        for i in range(1, n):
            pairs.extend([([i, -i], []), ([-i, i], [])])
        pairs.extend(([i, i + 1, i], [i + 1, i, i + 1]) for i in range(1, n - 1))
        pairs.extend(([i, j], [j, i]) for i in range(1, n) for j in range(i + 2, n))
        for left, right in pairs:
            same(pack(burau(n, left)), pack(burau(n, right)))
            same(artin(n, left), artin(n, right))
            relations.append({"n": n, "left": left, "right": right, "both_representations": "Equal", "native_cell": "NotIssued"})
    reverse = []
    for case in contract["families"]["reverse_pairs"]:
        r = reverse_search(case, contract["families"]["jet_orders"])
        check_search(json.loads(canonical(r)), case, contract["families"]["jet_orders"])
        reverse.append(r)
    report["reverse_search"] = reverse
    boundary = {j: math.comb(9, j) * (-1) ** (9 - j) for j in range(10)}
    assert boundary and jet_poly(boundary, 8) == [0] * 9
    report["degree_boundary"] = {"polynomial": sorted(boundary.items()), "jet_order": 8,
                                "jet": jet_poly(boundary, 8), "status": "OutsideDeclaredDegreeWindow"}
    # Explicit witness that a coarse value has multiple exact lifts.
    coarse_left, coarse_right = burau(4, []), burau(4, [1, 1])
    assert jet(coarse_left, 0) == jet(coarse_right, 0) and coarse_left != coarse_right
    report["nonunique_lift"] = {"left_word": [], "right_word": [1, 1], "same_zero_jet": True, "same_exact_matrix": False}
    controls = []
    bad = copy.deepcopy(records[0]); bad["matrix"][0][0][0][1] = 2
    reject("changed_matrix_coefficient", lambda: check_row(bad, 3, ()), controls)
    bad = copy.deepcopy(records[1]); original = tuple(bad["scope"]["word"]); bad["scope"]["word"] = []
    reject("lost_source_word", lambda: check_row(bad, 3, original), controls)
    bad = copy.deepcopy(records[0]); bad["free_images"][0] = (1, 1)
    reject("changed_free_group_image", lambda: check_row(bad, 3, ()), controls)
    bad = copy.deepcopy(records[1]); bad["scope"]["word"][0] = True
    reject("boolean_as_integer", lambda: check_row(bad, 3, (1,)), controls)
    bad = copy.deepcopy(reverse[0]); bad["swaps"][0]["separated"] = True
    reject("forged_swap_witness", lambda: check_search(bad, reverse[0]["case"], list(range(9))), controls)
    bad = copy.deepcopy(reverse[0]); bad["witness"]["delta"] += 1
    reject("wrong_jet_coefficient", lambda: check_search(bad, reverse[0]["case"], list(range(9))), controls)
    bad = copy.deepcopy(reverse[1]); bad["attempts"].pop(0)
    reject("erased_failed_search", lambda: check_search(bad, reverse[1]["case"], list(range(9))), controls)
    reject("false_zero_from_order_eight", lambda: bounded_zero_certificate(boundary, radius), controls)
    reject("coarse_value_claimed_as_unique_lift", lambda: same(pack(coarse_left), pack(coarse_right)), controls)
    same([c["name"] for c in controls], contract["negative_controls"])
    report.update(negative_controls=controls, counts={"words": len(records), "matrix_entries_reconstructed": coefficients_checked,
                  "relation_pairs": len(relations), "reverse_pairs": len(reverse), "negative_controls": len(controls)})


def main():
    global LIMIT, DEADLINE, IMAGE_CAP
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="evidence.json")
    args = parser.parse_args()
    here = Path(__file__).resolve().parent
    raw = (here / "contract.json").read_bytes()
    contract = json.loads(raw); limits = contract["limits"]
    out = Path(args.output)
    if out.exists():
        raise FileExistsError("use a new evidence path")
    start = time.monotonic()
    LIMIT, DEADLINE, IMAGE_CAP = limits["logical_units"], start + limits["wall_seconds"], limits["max_free_image_letters"]
    resource.setrlimit(resource.RLIMIT_CPU, (limits["cpu_seconds"],) * 2)
    resource.setrlimit(resource.RLIMIT_AS, (limits["address_space_mib"] * 2 ** 20,) * 2)
    resource.setrlimit(resource.RLIMIT_FSIZE, (limits["file_bytes"],) * 2)
    signal.signal(signal.SIGALRM, lambda *_: (_ for _ in ()).throw(TimeoutError("wall alarm")))
    signal.alarm(limits["wall_seconds"])
    report = {"schema": "external.faithful-switch.evidence.v0", "status": "Running",
              "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "contract_sha256": hashlib.sha256(raw).hexdigest(), "native_faithfulness": "Open"}
    code = 0
    try:
        run(contract, report)
        report["status"] = "PassedFiniteCalibration"
        data = canonical(report)
        charge(len(data) // 1024 + 1)
        same(json.loads(data), report)
        report["serialized_roundtrip"] = "Passed"
    except TimeoutError as exc:
        report.update(status="Unknown:Resource", failure=str(exc)); code = 2
    except Exception as exc:
        report.update(status="ImplementationFailure", failure=type(exc).__name__ + ": " + str(exc)); code = 1
    report["costs"] = {"logical_units": UNITS, "elapsed_before_checkpoint_seconds": time.monotonic() - start,
                       "peak_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                       "checkpoint": "One exclusive write, at most 8 MiB, OS limits remain active"}
    data = (canonical(report) + "\n").encode()
    if len(data) > limits["file_bytes"]:
        raise RuntimeError("output bound exceeded")
    with out.open("xb") as f:
        f.write(data)
    print(canonical({"status": report["status"], "counts": report.get("counts"), "partition_tables": report["partition_tables"],
                     "costs": report["costs"], "bytes": len(data), "failure": report.get("failure")}))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
