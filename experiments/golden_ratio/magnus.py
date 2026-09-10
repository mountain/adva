#!/usr/bin/env python3
"""Truncated Magnus algebra: the core the extraction rule needs, and nothing more.

The expansion of a word is a sum of non-commuting monomials with exact integer
coefficients, truncated at a declared degree. This run validates that algebra on
classical identities - the degree-one part is the exponent vector, a commutator
has no linear part, a triple commutator has no part below degree three - and does
NOT extract mu-bar(123), which contract-v3 reserves for a later step.

Usage:
  python3 -S experiments/golden_ratio/magnus.py --output target/magnus-fresh.json

Exit codes: 0 Passed, 2 Invalid, 3 Unknown.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

CONTRACT = "experiments/golden_ratio/contract-v3.json"
BUDGET = {"max_seconds": 30.0, "max_checks": 5000, "max_nodes": 200000, "max_degree": 3}


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
        self.checks.append(name)


# --------------------------------------------------------------------------
# Truncated expansions: {monomial tuple -> integer coefficient}, monomial = word.
# --------------------------------------------------------------------------


def multiply(first: dict, second: dict, run: Run) -> dict:
    product: dict = {}
    for left, left_coefficient in first.items():
        for right, right_coefficient in second.items():
            run.tick()
            merged = left + right
            if len(merged) > BUDGET["max_degree"]:
                continue
            product[merged] = product.get(merged, 0) + left_coefficient * right_coefficient
    return {monomial: value for monomial, value in product.items() if value}


def generator(name: int) -> dict:
    """The expansion of x_name is 1 + X_name."""
    return {(): 1, (name,): 1}


def inverse(expansion: dict, run: Run) -> dict:
    """Inverse of 1 + N by the finite geometric series, truncated."""
    result = {(): 1}
    term = {(): 1}
    negation = {monomial: -value for monomial, value in expansion.items() if monomial}
    for _ in range(BUDGET["max_degree"] + 1):
        term = multiply(term, negation, run)
        if not term:
            break
        for monomial, value in term.items():
            result[monomial] = result.get(monomial, 0) + value
    return {monomial: value for monomial, value in result.items() if value}


def reduce_word(*parts: tuple) -> tuple:
    stack: list[int] = []
    for part in parts:
        for letter in part:
            if stack and stack[-1] == -letter:
                stack.pop()
            else:
                stack.append(letter)
    return tuple(stack)


def word_expansion(word: tuple, run: Run) -> dict:
    result = {(): 1}
    for letter in word:
        piece = generator(abs(letter))
        if letter < 0:
            piece = inverse(piece, run)
        result = multiply(result, piece, run)
    return result


def commutator(first: tuple, second: tuple) -> tuple:
    return reduce_word(first, second, tuple(-x for x in reversed(first)), tuple(-x for x in reversed(second)))


def degree_part(expansion: dict, degree: int) -> dict:
    return {monomial: value for monomial, value in expansion.items() if len(monomial) == degree}


def exponent_vector(word: tuple, generators: int) -> tuple:
    return tuple(
        sum(1 if letter == name else (-1 if letter == -name else 0) for letter in word)
        for name in range(1, generators + 1)
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="bounded truncated Magnus algebra")
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
        "schema": "adva.golden-ratio-magnus-core.research",
        "version": 0,
        "status": "Invalid",
        "reason": None,
        "scope": "truncated Magnus algebra only; no link invariant is computed",
        "authority": {
            "authority": "external-exact-algebra-only",
            "native_admission": "not-granted",
            "invariant_computed": False,
        },
        "budget": dict(BUDGET),
        "max_degree": BUDGET["max_degree"],
    }
    try:
        contract_bytes = (root / CONTRACT).read_bytes()
        contract = json.loads(contract_bytes.decode("utf-8"))
        run.check("contract-version-three", contract["version"] == 3)
        report["contract"] = {
            "path": CONTRACT,
            "sha256": __import__("hashlib").sha256(contract_bytes).hexdigest(),
        }

        # 1. the degree-one part is the exponent vector (the abelian projection)
        word = reduce_word((1,), (2,), (-1,), (3,), (2,))
        expansion = word_expansion(word, run)
        linear = degree_part(expansion, 1)
        expected = exponent_vector(word, 3)
        reconstructed = tuple(linear.get((name,), 0) for name in range(1, 4))
        run.check("magnus-linear-part-is-the-exponent-vector", reconstructed == expected)
        run.check("magnus-unit-constant", expansion.get((), 0) == 1)

        # 2. a commutator has no linear part, and its quadratic part is antisymmetric
        bracket = commutator((1,), (2,))
        bracket_expansion = word_expansion(bracket, run)
        run.check("magnus-commutator-has-no-linear-part", not degree_part(bracket_expansion, 1))
        quadratic = degree_part(bracket_expansion, 2)
        run.check(
            "magnus-commutator-quadratic-is-antisymmetric",
            quadratic == {(1, 2): 1, (2, 1): -1} or quadratic == {(1, 2): -1, (2, 1): 1},
        )

        # 3. a triple commutator lives in degree three: nothing below, and non-zero
        triple = commutator((1,), bracket)
        triple_expansion = word_expansion(triple, run)
        run.check(
            "magnus-triple-commutator-has-no-low-part",
            not degree_part(triple_expansion, 1) and not degree_part(triple_expansion, 2),
        )
        run.check("magnus-triple-commutator-degree-three", bool(degree_part(triple_expansion, 3)))

        report["classical_identities"] = {
            "linear_part": list(reconstructed),
            "commutator_quadratic": {str(list(k)): v for k, v in quadratic.items()},
            "triple_commutator_terms_at_degree_three": len(degree_part(triple_expansion, 3)),
        }
        report["not_computed"] = [
            "the relation words of the declared diagram, which need their exact field parameters in process",
            "the extraction rule for mu-bar(123) and its two validation targets",
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
        destination.write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + chr(10), encoding="utf-8"
        )
        print(json.dumps({key: report[key] for key in ("status", "reason", "cost")}, ensure_ascii=False))
    return {"Passed": 0, "Invalid": 2, "Unknown": 3}[report["status"]]


if __name__ == "__main__":
    sys.exit(main())
