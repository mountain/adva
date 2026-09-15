"""Finite adapters to real Adva research helpers; no research search is resumed."""
import importlib.util
import sys
from collections import defaultdict
from dataclasses import replace
from fractions import Fraction as F

SOURCES = {
    "exp-cross-zero": ["experiments/integer_power_absurdity/calibration.py"],
    "constant-inverse": ["experiments/aeg_core_shell_multivariate/calibration.py"],
    "segmented-execution": ["experiments/keraia_read_machine/machine.py",
                            "experiments/keraia_read_machine/syntax.py"],
}


def module(root, path, name):
    spec = importlib.util.spec_from_file_location(name, root / path)
    obj = importlib.util.module_from_spec(spec)
    sys.modules[name] = obj
    spec.loader.exec_module(obj)
    return obj


def case(name, inputs, expected, actual, passed):
    return dict(name=name, inputs=inputs, expected=expected, actual=actual,
                verdict="Pass" if passed else "Violation")


def exp_boundary_ok(lo, hi):
    # For the exact input [-1, 1], exp(-1) < 1/2 because exp(1) > 2.
    # Necessary condition only: passing does not establish a full enclosure.
    return F(lo) < F(1, 2) and F(hi) > 2


def inverse_ok(c, coefficients):
    return coefficients == {"0,0": str(1 / F(c))}


def run(name, root):
    if name == "exp-cross-zero":
        m = module(root, SOURCES[name][0], "target_exp")
        m.LIMITS["max_assertions"] = 10000
        rows = []
        z = m.exp_interval(m.Interval(F(0), F(0)), 16)
        rows.append(case("zero-control", ["0", "0"], ["1", "1"],
                         [str(z.lo), str(z.hi)], z.lo == z.hi == 1))
        r = m.exp_interval(m.Interval(F(-1), F(1)), 16)
        rows.append(case("cross-zero", ["-1", "1"],
                         "lo < 1/2 and hi > 2 (necessary enclosure conditions)",
                         [str(r.lo), str(r.hi)], exp_boundary_ok(r.lo, r.hi)))
        return dict(invariant="exp([-1,1]) encloses exp(-1) and exp(1)",
                    oracle="Exact series fact exp(1) > 1+1=2; exp(-1)=1/exp(1)",
                    scope="Helper accepts crossing-zero intervals; retained branch experiment not rerun",
                    common_mode="CPython integer/Fraction arithmetic and host hardware remain shared",
                    cases=rows)
    if name == "constant-inverse":
        m = module(root, SOURCES[name][0], "target_inverse")
        m.LIMITS["max_assertions"] = 10000
        rows = []
        for c in (F(1), F(-1), F(2), F(3), F(1, 2)):
            for order in (1, 2):
                p = m.truncated_inverse(m.MPoly.constant(c, 2), order)
                actual = {",".join(map(str, k)): str(v) for k, v in p.terms.items()}
                rows.append(case(f"constant-{c}-order-{order}",
                                 dict(constant=str(c), order=order, nvars=2),
                                 {"0,0": str(1 / c)}, actual, inverse_ok(c, actual)))
        return dict(invariant="Constant polynomial c times its truncated inverse equals one",
                    oracle="Exact reciprocal of a nonzero rational constant; no polynomial inversion oracle",
                    scope="Helper-level domain extension; frozen x^2+1 experiment is not refuted",
                    common_mode="CPython/Fraction shared; expected result does not call MPoly arithmetic",
                    cases=rows)
    if name == "segmented-execution":
        module(root, SOURCES[name][1], "syntax")
        m = module(root, SOURCES[name][0], "target_machine")
        from syntax import Budget, I
        limits = dict(max_host_work=10000, wall_seconds=3, max_stack=64,
                      max_term_nodes=128, max_semantic_steps=64)
        def execute(frame, fuel):
            return m.pure_segment(frame, fuel, Budget(limits), defaultdict(int))
        rows = []
        terms = [I, ("a", I, I), ("a", I, ("a", I, I))]
        for depth, term in enumerate(terms):
            start = m.Frame(term, (), 0)
            full = execute(start, 32)
            for cut in (0, 1, 2, 3):
                first = execute(start, cut)
                second = execute(first.end, 32 - first.steps) if first.stop == "UnknownFuel" else None
                final = second if second else first
                steps = first.steps + (second.steps if second else 0)
                ok = final.end == full.end and final.stop == full.stop and steps == full.steps
                rows.append(case(f"segment-{depth}-{cut}", dict(depth=depth, cut=cut),
                                 dict(steps=full.steps, stop=full.stop),
                                 dict(steps=steps, stop=final.stop, same_frame=final.end == full.end), ok))
            accepted = m.check_receipt(full, start, Budget(limits), defaultdict(int))
            rows.append(case(f"valid-receipt-{depth}", dict(depth=depth), True, accepted, accepted))
            for field, forged in (("steps", replace(full, steps=True)),
                                  ("cursor", replace(full, end=replace(full.end, cursor=1))),
                                  ("profile", replace(full, end=replace(full.end, profile="other")))):
                accepted = m.check_receipt(forged, start, Budget(limits), defaultdict(int))
                rows.append(case(f"forged-{depth}-{field}", dict(depth=depth, mutation=field),
                                 False, accepted, not accepted))
        return dict(invariant="Fuel segmentation preserves endpoint and charged steps; forged receipts rejected",
                    oracle="Metamorphic relation and explicit receipt field mutations",
                    scope="Three finite closed terms, four cuts each; no prefix search or native Rust certificate",
                    common_mode="Both segments and receipt replay share pure_segment; correlated semantic errors escape",
                    cases=rows)
    raise ValueError("unknown probe")
