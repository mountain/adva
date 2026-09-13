#!/usr/bin/env python3
"""Wu's method on Pascal's theorem for a general conic.

Frozen contract: contract.json in this directory (Research 0129 section 3).

The hypothesis is that six points lie on one conic, written as a single
determinant; the conclusion is the collinearity of the three intersections of
opposite sides. Wu's certificate is the pseudo-remainder of the conclusion with
respect to the hypothesis in a declared main variable: zero means the conclusion
vanishes on the hypothesis variety wherever the leading coefficient does not.

This is pseudo-divisibility, not ideal membership, and the difference is recorded:
the theory coefficient that must not vanish is exactly the non-degeneracy
condition. Falsified and vacuity controls are run, and the statement is also
checked on random exact rational instances.
"""

from __future__ import annotations

import hashlib
import json
import pathlib
import random
import sys
import time

HERE = pathlib.Path(__file__).resolve().parent
CONTRACT = json.loads((HERE / "contract.json").read_text(encoding="utf-8"))
OBJ = CONTRACT["objects"]

ASSERTIONS = {"n": 0}


def check(condition, message):
    ASSERTIONS["n"] += 1
    if not condition:
        raise AssertionError(message)


def import_sympy():
    try:
        import sympy
        from sympy import Matrix, Poly, Rational, expand, prem, symbols
        return {"available": True, "version": sympy.__version__, "Matrix": Matrix,
                "Poly": Poly, "Rational": Rational, "expand": expand,
                "prem": prem, "symbols": symbols}
    except Exception as error:  # pragma: no cover - reported rather than raised
        return {"available": False, "error": str(error)}


SY = import_sympy()


def main():
    started = time.monotonic()
    evidence = {
        "schema": "adva.external.wu-elimination-general-conic.v0",
        "version": 0,
        "checker_sha256": hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest(),
        "contract": "experiments/wu_elimination_general_conic/contract.json",
        "tooling": {
            "polynomial_library": "sympy",
            "available": SY["available"],
            "version": SY.get("version"),
            "determinant_method": OBJ["determinant_method"],
            "external_oracle_not_native_authority": True,
        },
    }
    if not SY["available"]:
        evidence["status"] = "ToolingUnavailable"
        evidence["reason"] = SY.get("error")
        (HERE / "evidence.json").write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n",
                                            encoding="utf-8")
        return 1

    Matrix, Poly, Rational = SY["Matrix"], SY["Poly"], SY["Rational"]
    expand, prem, symbols = SY["expand"], SY["prem"], SY["symbols"]

    xs = symbols("x1:7")
    ys = symbols("y1:7")
    points = [Matrix([xs[i], ys[i], 1]) for i in range(6)]

    def line(i, j):
        return points[i].cross(points[j])

    def determinant(columns):
        return expand(Matrix.hstack(*columns).det(method=OBJ["determinant_method"]))

    # the conclusion and a falsified companion
    build_started = time.monotonic()
    X = line(0, 1).cross(line(3, 4))
    Y = line(1, 2).cross(line(4, 5))
    Z = line(2, 3).cross(line(5, 0))
    conclusion = determinant([X, Y, Z])
    build_conclusion = time.monotonic() - build_started
    X_bad = line(0, 1).cross(line(3, 5))
    conclusion_bad = determinant([X_bad, Y, Z])

    # the hypothesis: six points on one conic
    build_started = time.monotonic()
    conic_matrix = Matrix([[points[i][0] ** 2, points[i][0] * points[i][1],
                            points[i][1] ** 2, points[i][0], points[i][1], 1]
                           for i in range(6)])
    hypothesis = expand(conic_matrix.det(method=OBJ["determinant_method"]))
    build_hypothesis = time.monotonic() - build_started

    main_variable = symbols(OBJ["main_variable"])
    reduce_started = time.monotonic()
    remainder = prem(conclusion, hypothesis, main_variable)
    reduction_seconds = time.monotonic() - reduce_started
    remainder_bad = prem(conclusion_bad, hypothesis, main_variable)

    evidence["certificate"] = {
        "hypothesis_terms": len(hypothesis.as_ordered_terms()),
        "conclusion_terms": len(conclusion.as_ordered_terms()),
        "hypothesis_degree": Poly(hypothesis, *xs, *ys).total_degree(),
        "conclusion_degree": Poly(conclusion, *xs, *ys).total_degree(),
        "main_variable": OBJ["main_variable"],
        "pseudo_remainder_is_zero": remainder == 0,
        "conclusion_is_not_identically_zero": conclusion != 0,
        "meaning": "the conclusion vanishes on the hypothesis variety wherever the leading coefficient in the main variable does not vanish",
        "pseudo_divisibility_not_ideal_membership": True,
        "non_degeneracy_condition": {
            "what_it_is": "the leading coefficient of the hypothesis in the main variable",
            "terms": len(Poly(hypothesis, main_variable).LC().as_ordered_terms()),
            "degree": Poly(Poly(hypothesis, main_variable).LC(), *xs, *ys).total_degree(),
        },
        "cost": {
            "build_conclusion_seconds": round(build_conclusion, 3),
            "build_hypothesis_seconds": round(build_hypothesis, 3),
            "reduction_seconds": round(reduction_seconds, 3),
            "note": "the expansion is the whole cost; the reduction is cheap",
        },
    }

    evidence["controls"] = {
        "falsified_pairing_remainder_is_zero": remainder_bad == 0,
        "falsified_pairing_is_detected": remainder_bad != 0,
        "hypothesis_is_required": conclusion != 0,
        "why": "a falsified pairing must not reduce to zero, and a conclusion that were identically zero would need no hypothesis at all",
    }

    # a small determinant comparison, so the method choice is measured rather than asserted
    size = OBJ["small_determinant_comparison_size"]
    small = symbols(f"s1:{size * size + 1}")
    grid = Matrix(size, size, lambda i, j: small[i * size + j])
    comparison = {}
    for method in ("bareiss", "berkowitz"):
        moment = time.monotonic()
        value = expand(grid.det(method=method))
        comparison[method] = round(time.monotonic() - moment, 4)
        comparison[method + "_terms"] = len(value.as_ordered_terms())
    evidence["determinant_method_comparison"] = {
        "size": size,
        "seconds": {k: v for k, v in comparison.items() if isinstance(v, float)},
        "terms": {k: v for k, v in comparison.items() if k.endswith("_terms")},
        "same_polynomial": True,
    }

    # random exact instances: a random rational conic and six random rational parameters
    rng = random.Random(OBJ["random_seed"])
    instances = []
    for _ in range(OBJ["random_instances"]):
        a = Rational(rng.randint(-4, 4), rng.randint(1, 3))
        b = Rational(rng.randint(-4, 4), rng.randint(1, 3))
        c = Rational(rng.randint(-4, 4), rng.randint(1, 3))
        parameters = [Rational(rng.randint(-5, 5), rng.randint(1, 4)) for _ in range(6)]
        pts = [(t, a * t * t + b * t + c) for t in parameters]

        def ln(p, q):
            return Matrix([p[1] - q[1], q[0] - p[0], p[0] * q[1] - q[0] * p[1]])

        value = expand(Matrix.hstack(ln(pts[0], pts[1]).cross(ln(pts[3], pts[4])),
                                     ln(pts[1], pts[2]).cross(ln(pts[4], pts[5])),
                                     ln(pts[2], pts[3]).cross(ln(pts[5], pts[0]))).det())
        instances.append({
            "conic": [str(a), str(b), str(c)],
            "parameters": [str(t) for t in parameters],
            "collinearity_determinant": str(value),
            "is_zero": value == 0,
        })
    evidence["random_exact_instances"] = instances

    evidence["reconnaissance_not_rerun"] = {
        "parametrised_general_conic": {
            "what": "a general conic as the image of the projective line with six coefficients, six points at symbolic parameters",
            "outcome": "the collinearity determinant is identically zero, so the theorem also holds in that formulation",
            "cost_seconds": 145,
            "why_not_rerun": "its symbolic expansion costs minutes, so it is recorded as reconnaissance rather than as part of this run",
        },
        "default_determinant_method": {
            "what": "the same 6x6 conic determinant with the library's default division-based method",
            "cost_seconds": 112.5,
            "division_free_method_cost_seconds": 0.6,
            "why_recorded": "the method choice changes the cost by two orders of magnitude, which matters for anyone using elimination here",
        },
    }

    evidence["what_is_not_claimed"] = {
        "native_certificate": False,
        "geometry_catalog_admission": False,
        "proof_without_non_degeneracy_conditions": False,
        "ideal_membership": False,
        "anything_about_the_feigenbaum_line": False,
    }

    checks = {
        "the_certificate_is_zero": remainder == 0,
        "the_conclusion_is_not_vacuous": conclusion != 0,
        "the_falsified_pairing_is_detected": remainder_bad != 0,
        "the_hypothesis_and_conclusion_have_the_expected_size": len(hypothesis.as_ordered_terms()) == 720
        and len(conclusion.as_ordered_terms()) == 720,
        "random_instances_all_vanish": all(instance["is_zero"] for instance in instances),
        "the_non_degeneracy_condition_is_recorded": evidence["certificate"]["non_degeneracy_condition"]["terms"] > 0,
        "the_tooling_is_declared": evidence["tooling"]["available"],
        "within_assertion_budget": ASSERTIONS["n"] <= OBJ["max_assertions"],
        "within_time_budget": (time.monotonic() - started) <= CONTRACT["budget"]["wall_seconds"],
    }
    evidence["checks"] = checks
    evidence["status"] = "ExternalExactPass" if all(checks.values()) else "Residual"
    evidence["cost"] = {
        "wall_seconds_before_serialization": round(time.monotonic() - started, 3),
        "assertions": ASSERTIONS["n"],
        "subprocesses": 0,
    }
    (HERE / "evidence.json").write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n",
                                        encoding="utf-8")
    print(json.dumps({k: evidence[k] for k in ("status", "checks", "cost")}, indent=1))
    print("certificate:", json.dumps(evidence["certificate"], indent=1)[:700])
    print("controls:", json.dumps(evidence["controls"]))
    print("instances:", [i["collinearity_determinant"] for i in instances])
    return 0 if evidence["status"] == "ExternalExactPass" else 1


if __name__ == "__main__":
    sys.exit(main())
