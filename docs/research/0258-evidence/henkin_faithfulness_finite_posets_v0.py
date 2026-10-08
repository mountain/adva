#!/usr/bin/env python3
"""External finite-poset calibration, v0.

For a finite poset E and signed constraints (P, N):
  an order ideal I with P <= I and I disjoint N exists
  iff downward_closure(P) is disjoint N.

Also check that event-membership probes separate every two distinct ideals.
This is an abstract model, not an extraction of Adva execution evidence.
Only n = 1, 2, 3, 4 is checked. No third-party packages are required.

Usage:
  python henkin_faithfulness_finite_posets_v0.py
  python henkin_faithfulness_finite_posets_v0.py --output report.json

The optional output must not already exist.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from itertools import product
from pathlib import Path
from typing import Iterator


def require(condition: bool, message: str) -> None:
    # Deliberately not "assert": checks also run under python -O.
    if not condition:
        raise RuntimeError(message)


def finite_posets(n: int) -> Iterator[tuple[int, ...]]:
    """Enumerate all labeled posets on {0, ..., n-1}, using predecessor masks."""
    if n not in range(1, 5):
        raise ValueError("Frozen scope: 1 <= n <= 4")
    pairs = [(i, j) for i in range(n) for j in range(i + 1, n)]
    for choices in product((0, 1, -1), repeat=len(pairs)):
        lower = [1 << j for j in range(n)]
        for (i, j), direction in zip(pairs, choices):
            if direction == 1:
                lower[j] |= 1 << i
            elif direction == -1:
                lower[i] |= 1 << j
        # Antisymmetry is ensured by construction; now test transitivity.
        if all(not (lower[i] & ~lower[j])
               for j in range(n) for i in range(n)
               if lower[j] & (1 << i)):
            yield tuple(lower)


def calibrate() -> dict:
    rows = []
    for n in range(1, 5):
        poset_count = constraint_count = pair_count = 0
        for lower in finite_posets(n):
            poset_count += 1
            ideals = [
                I for I in range(1 << n)
                if all(not (lower[e] & ~I)
                       for e in range(n) if I & (1 << e))
            ]
            for P in range(1 << n):
                down_P = 0
                for e in range(n):
                    if P & (1 << e):
                        down_P |= lower[e]
                for N in range(1 << n):
                    witnesses = [
                        I for I in ideals if not (P & ~I) and not (N & I)
                    ]
                    closure_passes = not (down_P & N)
                    require(bool(witnesses) == closure_passes,
                            f"Existence mismatch: n={n}, order={lower}, P={P}, N={N}")
                    if closure_passes:
                        require(down_P in witnesses, "Canonical model is not a witness")
                        require(all(not (down_P & ~I) for I in witnesses),
                                "Canonical model is not least")
                    constraint_count += 1
            for a, I in enumerate(ideals):
                for J in ideals[a + 1:]:
                    delta = I ^ J
                    e = (delta & -delta).bit_length() - 1
                    require(bool(I & (1 << e)) != bool(J & (1 << e)),
                            "Event probe failed to separate distinct ideals")
                    pair_count += 1
        rows.append({
            "n": n, "labeled_posets": poset_count,
            "signed_constraint_cases": constraint_count,
            "separated_ideal_pairs": pair_count
        })

    expected_poset_counts = [1, 3, 19, 219]
    require([row["labeled_posets"] for row in rows] == expected_poset_counts,
            "Poset enumeration count mismatch")

    # Concrete example: e0 precedes eL and eR; eL and eR are incomparable.
    root, left, right = 1, 2, 4
    I, J = root | left, root | right
    require(I.bit_count() == J.bit_count(), "Count-only negative control broken")
    require(bool(I & left) != bool(J & left), "Source-position probe control broken")
    P, N, down_P = left, root, root | left
    require(not (P & N) and bool(down_P & N),
            "Ignoring prerequisites should miss the explicit contradiction")

    return {
        "schema": "external.henkin-faithfulness.finite-posets.v0",
        "status": "PassedFiniteCalibration",
        "scope": "All labeled posets of sizes 1 through 4; abstract order ideals only",
        "not_claimed": [
            "Adva native execution correctness",
            "Adva event-trace reconstruction or observer implementability",
            "Faithfulness on proof cells or coherence cells",
            "General search termination or proof-assistant verification"
        ],
        "by_size": rows,
        "totals": {
            "labeled_posets": sum(row["labeled_posets"] for row in rows),
            "signed_constraint_cases": sum(row["signed_constraint_cases"] for row in rows),
            "separated_ideal_pairs": sum(row["separated_ideal_pairs"] for row in rows)
        },
        "example": {
            "order": [["e0", "eL"], ["e0", "eR"]],
            "ideals": [[], ["e0"], ["e0", "eL"], ["e0", "eR"], ["e0", "eL", "eR"]],
            "count_only_collision": [["e0", "eL"], ["e0", "eR"]],
            "separating_probe": "membership of eL",
            "inconsistent_constraints": {"positive": ["eL"], "negative": ["e0"]}
        }
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="Write a new JSON file; never overwrite.")
    args = parser.parse_args()
    report = calibrate()
    report["source_sha256"] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    text = json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if args.output is None:
        print(text, end="")
    else:
        with args.output.open("x", encoding="utf-8") as stream:
            stream.write(text)


if __name__ == "__main__":
    main()
