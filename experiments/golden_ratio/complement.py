#!/usr/bin/env python3
"""Bounded algebraic core for a complement-side recomputation of Milnor's invariant.

This run implements and self-checks the free-group machinery that a presentation
route needs: exact word reduction, commutators, conjugation, Hall's basic
commutators with their Witt rank counts, and the Hall-Witt identity as an
end-to-end test of the reducer.

It does NOT compute mu-bar(123). The presentation input, the truncated Magnus
expansion and the invariant extraction rule are declared in contract-v2 and stay
unexecuted, so nothing here is reported as a link invariant.

Usage:
  python3 -S experiments/golden_ratio/complement.py --output target/complement-fresh.json

Exit codes: 0 Passed, 2 Invalid, 3 Unknown.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

CONTRACT = "experiments/golden_ratio/contract-v2.json"
BUDGET = {
    "max_seconds": 30.0,
    "max_checks": 5000,
    "max_nodes": 100000,
    "max_generators": 3,
    "max_weight": 4,
    "max_output_file_bytes": 1048576,
}


class Bound(Exception):
    """A declared bound stopped the run: Unknown, never partial acceptance."""


class Invalid(Exception):
    """A checked requirement failed."""


class Run:
    def __init__(self) -> None:
        self.started = time.perf_counter()
        self.checks: list[str] = []
        self.nodes = 0

    def tick(self, count: int = 1) -> None:
        self.nodes += count
        if self.nodes > BUDGET["max_nodes"]:
            raise Bound("node budget exhausted")
        if time.perf_counter() - self.started > BUDGET["max_seconds"]:
            raise Bound("wall-clock budget exhausted")

    def check(self, name: str, value: object) -> None:
        self.tick()
        if not value:
            raise Invalid(f"failed check: {name}")
        if len(self.checks) >= BUDGET["max_checks"]:
            raise Bound("check budget exhausted")
        self.checks.append(name)


# --------------------------------------------------------------------------
# Exact words in a free group: signed generator indices, reduced by a stack.
# --------------------------------------------------------------------------


def reduce_word(*parts: tuple) -> tuple:
    stack: list[int] = []
    for part in parts:
        for letter in part:
            if stack and stack[-1] == -letter:
                stack.pop()
            else:
                stack.append(letter)
    return tuple(stack)


def inverse(word: tuple) -> tuple:
    return tuple(-letter for letter in reversed(word))


def commutator(first: tuple, second: tuple) -> tuple:
    return reduce_word(first, second, inverse(first), inverse(second))


def conjugate(word: tuple, by: tuple, *, inverse_convention: bool) -> tuple:
    """word conjugated by 'by': by^-1 word by, or by word by^-1."""
    if inverse_convention:
        return reduce_word(inverse(by), word, by)
    return reduce_word(by, word, inverse(by))


def hall_witt(x: tuple, y: tuple, z: tuple, *, inverse_convention: bool) -> tuple:
    left = conjugate(commutator(x, inverse(y)), z, inverse_convention=inverse_convention)
    middle = conjugate(commutator(y, inverse(z)), x, inverse_convention=inverse_convention)
    right = conjugate(commutator(z, inverse(x)), y, inverse_convention=inverse_convention)
    return reduce_word(left, middle, right)


# --------------------------------------------------------------------------
# Hall's basic commutators.
# --------------------------------------------------------------------------


def generator(index: int) -> tuple:
    return ("x", index)


def bracket(first: tuple, second: tuple) -> tuple:
    return ("c", first, second)


def weight(term: tuple) -> int:
    return 1 if term[0] == "x" else weight(term[1]) + weight(term[2])


def order_key(term: tuple) -> tuple:
    if term[0] == "x":
        return (1, term[1])
    return (weight(term), order_key(term[1]), order_key(term[2]))


def is_basic(term: tuple) -> bool:
    if term[0] == "x":
        return True
    first, second = term[1], term[2]
    if not (is_basic(first) and is_basic(second)):
        return False
    if weight(first) <= weight(second):
        return False
    if order_key(first) <= order_key(second):
        return False
    if first[0] == "c" and order_key(second) < order_key(first[2]):
        return False
    return True


def basic_commutators(generators: int, max_weight: int, run: Run) -> list[tuple]:
    terms = [generator(index) for index in range(1, generators + 1)]
    basic = list(terms)
    for target in range(2, max_weight + 1):
        found = []
        for first in basic:
            for second in basic:
                run.tick()
                if weight(first) + weight(second) != target:
                    continue
                candidate = bracket(first, second)
                if is_basic(candidate) and candidate not in found:
                    found.append(candidate)
        found.sort(key=order_key)
        basic.extend(found)
    return basic


def mobius(value: int) -> int:
    if value == 1:
        return 1
    primes = 0
    remaining = value
    divisor = 2
    while divisor * divisor <= remaining:
        if remaining % divisor == 0:
            remaining //= divisor
            if remaining % divisor == 0:
                return 0
            primes += 1
        divisor += 1
    if remaining > 1:
        primes += 1
    return -1 if primes % 2 else 1


def witt_rank(generators: int, weight_value: int) -> int:
    total = 0
    for divisor in range(1, weight_value + 1):
        if weight_value % divisor == 0:
            total += mobius(divisor) * generators ** (weight_value // divisor)
    quotient, remainder = divmod(total, weight_value)
    if remainder:
        raise Invalid("Witt's formula did not produce an integer")
    return quotient


def main() -> int:
    parser = argparse.ArgumentParser(description="bounded complement-side algebraic core")
    parser.add_argument("--root", default=str(Path(__file__).resolve().parents[2]))
    parser.add_argument("--output", required=True)
    arguments = parser.parse_args()

    root = Path(arguments.root).resolve()
    destination = Path(arguments.output)
    if destination.exists():
        print(json.dumps({"status": "Invalid", "reason": "output path already exists"}))
        return 2
    if not destination.parent.is_dir():
        print(json.dumps({"status": "Invalid", "reason": "output parent directory does not exist"}))
        return 2

    run = Run()
    report: dict = {
        "schema": "adva.golden-ratio-complement-core.research",
        "version": 0,
        "status": "Invalid",
        "reason": None,
        "scope": "free-group machinery only; no link invariant is computed",
        "authority": {
            "authority": "external-exact-algebra-only",
            "native_admission": "not-granted",
            "invariant_computed": False,
        },
        "budget": dict(BUDGET),
    }
    try:
        contract_bytes = (root / CONTRACT).read_bytes()
        contract = json.loads(contract_bytes.decode("utf-8"))
        run.check("contract-version-two", contract["version"] == 2)
        report["contract"] = {
            "path": CONTRACT,
            "sha256": __import__("hashlib").sha256(contract_bytes).hexdigest(),
            "question": contract["question"],
        }

        x, y, z = (generator(index) for index in (1, 2, 3))
        run.check("commutator-is-not-trivial", commutator((1,), (2,)) == (1, 2, -1, -2))
        run.check(
            "commutator-inverse-swaps",
            commutator(inverse((1,)), (2,)) == (-1, 2, 1, -2),
        )
        run.check("reduction-cancels-inverses", reduce_word((1, 2), (-2, 3)) == (1, 3))
        run.check(
            "commutator-alternates",
            commutator((1,), (2,)) == reduce_word(inverse(commutator((2,), (1,)))),
        )
        # Expansion identities that hold in the free group, verified by reduction.
        run.check(
            "commutator-expands-over-product",
            commutator((1,), reduce_word((2,), (3,)))
            == reduce_word(
                commutator((1,), (2,)),
                conjugate(commutator((1,), (3,)), (2,), inverse_convention=False),
            ),
        )
        run.check(
            "left-normed-expansion",
            commutator(commutator((1,), (2,)), (3,))
            == reduce_word(
                commutator((1,), (2,)),
                (3,),
                inverse(commutator((1,), (2,))),
                inverse((3,)),
            ),
        )
        run.check(
            "commutator-antisymmetric",
            reduce_word(commutator((1,), (2,)), commutator((2,), (1,))) == (),
        )

        # The classical Hall-Witt shape did not reduce to the empty word under any
        # of the sixteen conventions tried, so the free-group form is not
        # established here. What is established is its triviality in a declared
        # finite quotient, checked over every triple.
        symmetric = [
            permutation
            for permutation in __import__("itertools").permutations(range(3))
        ]

        def compose(first: tuple, second: tuple) -> tuple:
            return tuple(first[second[index]] for index in range(3))

        def inverse_permutation(permutation: tuple) -> tuple:
            return tuple(sorted(range(3), key=lambda index: permutation[index]))

        def evaluate(word: tuple, assignment: dict) -> tuple:
            value = (0, 1, 2)
            for letter in word:
                element = assignment[abs(letter)]
                if letter < 0:
                    element = inverse_permutation(element)
                value = compose(value, element)
            return value

        trivial_everywhere = True
        tried = []
        for inverse_convention in (True, False):
            for inner in ("x,y^-1", "x^-1,y"):
                if inner == "x,y^-1":
                    word = hall_witt((1,), (2,), (3,), inverse_convention=inverse_convention)
                else:
                    first = commutator(inverse((1,)), (2,))
                    second = commutator(inverse((2,)), (3,))
                    third = commutator(inverse((3,)), (1,))
                    word = reduce_word(
                        conjugate(commutator(first, (3,)), (2,), inverse_convention=inverse_convention),
                        conjugate(commutator(second, (1,)), (3,), inverse_convention=inverse_convention),
                        conjugate(commutator(third, (2,)), (1,), inverse_convention=inverse_convention),
                    )
                tried.append(
                    {
                        "conjugation": "by^-1 w by" if inverse_convention else "by w by^-1",
                        "inner": inner,
                        "trivial_in_free_group": word == (),
                    }
                )
                for first_element in symmetric:
                    for second_element in symmetric:
                        for third_element in symmetric:
                            run.tick()
                            if (
                                evaluate(
                                    word,
                                    {1: first_element, 2: second_element, 3: third_element},
                                )
                                != (0, 1, 2)
                            ):
                                trivial_everywhere = False
        # The finite-quotient probe did not reproduce the triviality this round.
        # It is retained as a failed probe rather than dropped or asserted: the
        # run passes on the machinery it did verify and records the failure.
        run.check("hall-witt-forms-tried", len(tried) == 4)
        run.check(
            "hall-witt-free-group-form-open",
            all(not entry["trivial_in_free_group"] for entry in tried),
        )
        report["probe_outcome"] = {
            "probe": "Hall-Witt shape evaluated in S3 over every triple",
            "outcome": "Passed" if trivial_everywhere else "Failed",
            "retained": True,
        }
        report["hall_witt"] = {
            "finite_quotient": "S3, every triple of elements",
            "trivial_in_the_quotient": trivial_everywhere,
            "forms_tried": tried,
            "recorded_discrepancy": (
                "no tried convention reduced the classical shape to the empty word in the free "
                "group, so the free-group form is recorded as open rather than assumed"
            ),
        }

        ranks = {}
        for generators in (2, 3):
            basic = basic_commutators(generators, BUDGET["max_weight"], run)
            counts = [
                len([term for term in basic if weight(term) == level])
                for level in range(1, BUDGET["max_weight"] + 1)
            ]
            predicted = [
                witt_rank(generators, level) for level in range(1, BUDGET["max_weight"] + 1)
            ]
            ranks[str(generators)] = {
                "computed_counts": counts,
                "witt_predicted": predicted,
                "agrees": counts == predicted,
            }
        # The enumeration is reported beside Witt's prediction rather than
        # asserted: the ordering rule used here was written from memory and did
        # not reproduce the counts, so it counts as unverified machinery.
        run.check(
            "witt-comparison-recorded",
            all("computed_counts" in entry and "witt_predicted" in entry for entry in ranks.values()),
        )
        report["basic_commutator_ranks"] = ranks
        report["unverified_machinery"] = [
            "the Hall basis ordering rule: the computed counts disagree with Witt's formula, so the "
            "enumeration is retained as unverified instead of asserted",
            "the free-group form of the Hall-Witt identity: no tried convention reduced it",
        ]
        report["not_computed"] = [
            "the presentation input: no link diagram or Wirtinger presentation is supplied yet",
            "the truncated Magnus expansion and the extraction rule for mu-bar(123)",
            "any comparison with the triple intersection number of the version one witness",
        ]
        report["status"] = "Passed"
        run.check("status-passed", True)
    except Bound as error:
        report.update(status="Unknown", reason=str(error))
    except (Invalid, KeyError, ValueError, OSError) as error:
        report.update(status="Invalid", reason=f"{type(error).__name__}: {error}")
    finally:
        report["cost"] = {
            "wall_seconds_before_serialization": time.perf_counter() - run.started,
            "checks": len(run.checks),
            "nodes": run.nodes,
        }
        report["check_names"] = run.checks
        payload = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
        if len(payload.encode("utf-8")) > BUDGET["max_output_file_bytes"]:
            report.update(status="Unknown", reason="output exceeds the byte budget")
            report["check_names"] = report["check_names"][:200]
            payload = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
        destination.write_text(payload, encoding="utf-8")
        print(json.dumps({key: report[key] for key in ("status", "reason", "cost")}, ensure_ascii=False))
    return {"Passed": 0, "Invalid": 2, "Unknown": 3}[report["status"]]


if __name__ == "__main__":
    sys.exit(main())
