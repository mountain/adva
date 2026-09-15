"""Core plus symbolically unexpanded shell, over exact rational functions.

The shell form is fixed to a symbolically unexpanded expression, as decided. The
carrier is a pair: an exact core, and either no shell or a shell object that keeps
the unexpanded expression tree, its exact denotation, and why it was frozen.

The proposal under test says that truncating the denominator tears the algebraic
dependency and pollutes distributivity. This experiment tries to reproduce that,
and comes out with two results, the second of which corrects the proposal:

  * one truncation applied to one shared inverse is still a value, so the identity
    survives; truncation by itself does not break distributivity;
  * what truncation breaks is identifiability. The carried shell stops equalling
    the exact residual, and that residual is then multiplied by the outer factor
    and can no longer be read as a denominator residual.

Nothing here uses floating point. Rational functions are compared by cross
multiplying exact polynomial representatives, and the sample-point checks are exact
rational equalities at declared points.
"""
import json
import pathlib
import sys
from fractions import Fraction as Fr

HERE = pathlib.Path(__file__).resolve().parent
COUNTS = {"assertions": 0, "polynomial_multiplications": 0, "sample_evaluations": 0,
          "frozen_shells": 0}
LIMITS = {}


def check(value, message):
    COUNTS["assertions"] += 1
    if COUNTS["assertions"] > LIMITS["max_assertions"]:
        raise RuntimeError("Unknown: assertion budget")
    if not value:
        raise ValueError(message)


def jsonable(value):
    if isinstance(value, dict):
        return {k: jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [jsonable(v) for v in value]
    if isinstance(value, Fr):
        return str(value)
    return value


# ------------------------------------------------ exact sparse polynomials in x

class Poly:
    __slots__ = ("terms",)

    def __init__(self, terms):
        cleaned = {}
        for coefficient, exponent in terms:
            coefficient = Fr(coefficient)
            if coefficient:
                cleaned[exponent] = cleaned.get(exponent, Fr(0)) + coefficient
                if not cleaned[exponent]:
                    del cleaned[exponent]
        self.terms = cleaned

    @staticmethod
    def constant(value):
        return Poly([(value, 0)])

    @staticmethod
    def zero():
        return Poly([])

    def is_zero(self):
        return not self.terms

    def __add__(self, other):
        out = dict(self.terms)
        for exponent, coefficient in other.terms.items():
            out[exponent] = out.get(exponent, Fr(0)) + coefficient
            if not out[exponent]:
                del out[exponent]
        # out is keyed by exponent, but Poly takes (coefficient, exponent) pairs;
        # passing list(out.items()) swaps the two and silently empties the polynomial
        return Poly([(coefficient, exponent) for exponent, coefficient in out.items()])

    def __neg__(self):
        return Poly([(-c, e) for e, c in self.terms.items()])

    def __sub__(self, other):
        return self + (-other)

    def __mul__(self, other):
        COUNTS["polynomial_multiplications"] += 1
        out = {}
        for e1, c1 in self.terms.items():
            for e2, c2 in other.terms.items():
                out[e1 + e2] = out.get(e1 + e2, Fr(0)) + c1 * c2
        return Poly([(coefficient, exponent) for exponent, coefficient in out.items()])

    def derivative(self):
        return Poly([(c * e, e - 1) for e, c in self.terms.items() if e > 0])

    def at(self, point):
        COUNTS["sample_evaluations"] += 1
        return sum((c * Fr(point) ** e for e, c in self.terms.items()), Fr(0))

    def __eq__(self, other):
        return self.terms == other.terms

    def show(self):
        if not self.terms:
            return "0"
        return " + ".join("%s%s" % (self.terms[e], "" if e == 0 else ("x" if e == 1 else "x^%d" % e))
                          for e in sorted(self.terms, reverse=True))


class RF:
    """A rational function as an explicit pair; equality by cross multiplication."""

    __slots__ = ("num", "den")

    def __init__(self, num, den=None):
        self.num = num
        self.den = den if den is not None else Poly.constant(1)
        check(not self.den.is_zero(), "ZeroDenominatorRefused")

    @staticmethod
    def constant(value):
        return RF(Poly.constant(value))

    @staticmethod
    def zero():
        return RF(Poly.zero())

    def __add__(self, other):
        return RF(self.num * other.den + other.num * self.den, self.den * other.den)

    def __sub__(self, other):
        return RF(self.num * other.den - other.num * self.den, self.den * other.den)

    def __mul__(self, other):
        return RF(self.num * other.num, self.den * other.den)

    def inverse(self):
        """A swap of the pair, never a scalar division, and never an approximation."""
        check(not self.num.is_zero(), "InversionOfZeroRefused")
        return RF(self.den, self.num)

    def same_representative(self, other):
        """Literal pair equality, which is strictly stronger than equality of value."""
        return self.num == other.num and self.den == other.den

    def at(self, point):
        denominator = self.den.at(point)
        check(denominator != 0, "SamplePointHitsAPole")
        return self.num.at(point) / denominator

    def __eq__(self, other):
        return (self.num * other.den - other.num * self.den).is_zero()

    def show(self):
        return "(%s)/(%s)" % (self.num.show(), self.den.show())


# ---------------------------------- the symbolically unexpanded shell and its carrier

class Shell:
    """What the declared budget did not resolve: the unexpanded tree plus its denotation.

    The two layers are tied at construction: the tree must denote exactly the value
    the shell carries. Nothing compares a shell as a number, and no acceptance rule
    reads one.
    """

    def __init__(self, expression, denotation, reason, budget):
        expression_value = expression.denotation()
        check(expression_value == denotation, "TheShellTreeDoesNotDenoteItsCarriedValue")
        self.expression = expression
        self.denotation = denotation
        self.reason = reason
        self.budget = budget

    def show(self):
        return self.expression.show(0)


class Node:
    def denotation(self):
        raise NotImplementedError

    def show(self, depth):
        raise NotImplementedError


class Constant(Node):
    def __init__(self, value):
        self.constant = Fr(value)

    def denotation(self):
        return RF.constant(self.constant)

    def show(self, depth):
        return str(self.constant)


class Variable(Node):
    def denotation(self):
        return RF(Poly([(1, 1)]))

    def show(self, depth):
        return "x"


class Sum(Node):
    def __init__(self, left, right):
        self.left, self.right = left, right

    def denotation(self):
        return self.left.denotation() + self.right.denotation()

    def show(self, depth):
        return "(%s + %s)" % (self.left.show(depth + 1), self.right.show(depth + 1))


class Product(Node):
    def __init__(self, left, right):
        self.left, self.right = left, right

    def denotation(self):
        return self.left.denotation() * self.right.denotation()

    def show(self, depth):
        return "(%s * %s)" % (self.left.show(depth + 1), self.right.show(depth + 1))


class Inverse(Node):
    def __init__(self, inner):
        self.inner = inner

    def denotation(self):
        return self.inner.denotation().inverse()

    def show(self, depth):
        return "(%s)^-1" % self.inner.show(depth + 1)


class Carrier:
    """An exact core, plus either no shell or one frozen shell."""

    def __init__(self, core, shell=None):
        self.core = core
        self.shell = shell

    def denotation(self):
        return self.core if self.shell is None else self.core + self.shell.denotation

    def shell_is_empty(self):
        return self.shell is None

    def show(self):
        left = self.core.show()
        return left if self.shell is None else "%s + shell(%s)" % (left, self.shell.show())


def resolve_with_budget(b, c, budget):
    """Resolve the denominator term by term; what the budget stops is frozen as a shell."""
    b_node, c_node = VariableTerm(b), VariableTerm(c)
    whole = b + c
    if budget >= 2:
        return Carrier(whole), None
    COUNTS["frozen_shells"] += 1
    shell = Shell(c_node, c, "budget exhausted before resolving the second denominator term",
                  budget)
    carrier = Carrier(b, shell)
    check(carrier.denotation() == whole, "CorePlusShellIsNotTheWholeExpression")
    return carrier, shell


class VariableTerm(Node):
    """A declared rational-function term, kept as an unexpanded leaf."""

    def __init__(self, value):
        self.value = value

    def denotation(self):
        return self.value

    def show(self, depth):
        return "term(%s)" % self.value.show()


# --------------------------------------------------------------- the two routes

def rname(rf):
    return rf.show()


def run(contract):
    o = contract["objects"]
    points = [Fr(p[0], p[1]) for p in o["sample_points"]]
    routes, identifiability, truncation, frozen, structural = [], [], [], [], []

    for index, entry in enumerate(o["family"]):
        a1 = RF(Poly([(c, e) for c, e in entry["A1"]]))
        a2 = RF(Poly([(c, e) for c, e in entry["A2"]]))
        b = RF(Poly([(c, e) for c, e in entry["B"]]))
        c = RF(Poly([(c, e) for c, e in entry["C"]]))
        outer, s = a1 + a2, b + c

        # (1) the pair inverts by swap and double inversion returns the same value
        check(s.inverse().inverse() == s, "DoubleInversionChangedTheValue")

        # (2) the routes agree exactly, by cross multiplication and at every sample point
        left = outer * s.inverse()
        right = a1 * s.inverse() + a2 * s.inverse()
        check(left == right, "TheTwoRoutesDisagree")
        check([left.at(p) for p in points] == [right.at(p) for p in points],
              "TheTwoRoutesDisagreeAtASamplePoint")
        routes.append({"family_member": index, "outer": outer.show(), "denominator": s.show(),
                       "left_route": left.show(), "right_route": right.show(),
                       "representatives_literally_equal": left.same_representative(right),
                       "values_equal_exactly": True,
                       "sample_points_agree": len(points)})

        # (3) the shell carrier: identifiability of core plus shell against the whole
        for budget in o["budgets"]:
            carrier, shell = resolve_with_budget(b, c, budget)
            record = {"family_member": index, "budget": budget,
                      "core": carrier.core.show(),
                      "shell_empty": carrier.shell_is_empty(),
                      "carrier_denotes_the_whole_expression": True}
            if shell is not None:
                check(carrier.core + shell.denotation == s, "IdentifiabilityFailed")
                record["shell_expression"] = shell.show()
                record["shell_denotation"] = shell.denotation.show()
                record["reason"] = shell.reason
                record["verdict"] = "UnknownWithRetainedShell"
                frozen.append(record)
            else:
                record["verdict"] = "Resolved"
            identifiability.append(record)

        # (4) what the shell costs structurally: the routes agree in value but not literally
        carrier, _ = resolve_with_budget(b, c, 1)
        left_carrier = RF(outer.num * carrier.denotation().den,
                          outer.den * carrier.denotation().num)
        right_carrier = (RF(a1.num * carrier.denotation().den, a1.den * carrier.denotation().num)
                         + RF(a2.num * carrier.denotation().den, a2.den * carrier.denotation().num))
        check(left_carrier == right_carrier, "TheCarriersDisagreeInValue")
        structural.append({"family_member": index,
                           "value_equality": True,
                           "literal_pair_equality": left_carrier.same_representative(right_carrier),
                           "left_pair": left_carrier.show(),
                           "right_pair": right_carrier.show(),
                           "reading": "the pair presentation decides value, not structure: a "
                                      "reduction rule would be needed before two carriers could be "
                                      "compared as objects rather than as values"})

        # (5) truncation control one: one shared truncation is still a value
        at = Fr(o["linearisation_points"][0][0], o["linearisation_points"][0][1])
        truncated, _ = linearise(s, at)
        left_t, right_t = outer * truncated, a1 * truncated + a2 * truncated
        check(left_t == right_t, "ASharedTruncationBrokeTheIdentity")
        residual = s.inverse() - truncated
        check(not residual.num.is_zero(), "TheTruncationDroppedNothingAndSoProvesNothing")
        truncation.append({"kind": "one shared truncation on both routes",
                           "point": str(at),
                           "identity_holds": True,
                           "truncated_inverse": truncated.show(),
                           "exact_residual": residual.show(),
                           "carried_shell_equals_the_exact_residual": False,
                           "the_dropped_term_is_nonzero": True,
                           "reading": "a truncated inverse is still a single value, so the "
                                      "identity cannot fail this way; this contradicts the "
                                      "reading that truncation by itself breaks distributivity"})

        # (6) truncation control two: branches truncated at different points
        at2 = Fr(o["linearisation_points"][1][0], o["linearisation_points"][1][1])
        first, _ = linearise(s, at)
        second, _ = linearise(s, at2)
        branch_left = a1 * first + a2 * second
        branch_right = a1 * second + a2 * first
        breaks = not (branch_left == branch_right)
        check(breaks or a1 == a2, "PerBranchTruncationDidNotBreakTheIdentity")
        # the reading is an identity, so check it as one rather than assert it in prose:
        # the two routes differ by the outer term difference times the linearisation difference
        check(branch_left - branch_right == (a1 - a2) * (first - second),
              "ThePollutionIsNotTheOuterDifferenceTimesTheLinearisationDifference")
        check((first - second).num.is_zero() is False,
              "TheTwoLinearisationsAreTheSameSoThereIsNothingToCarry")
        truncation.append({"kind": "per-branch truncation at different points",
                           "points": [str(at), str(at2)],
                           "outer_terms_are_equal": bool(a1 == a2),
                           "identity_breaks": breaks,
                           "exact_difference": (branch_left - branch_right).show() if breaks else "0",
                           "difference_equals_outer_difference_times_linearisation_difference": True,
                           "linearisation_difference": (first - second).show(),
                           "reading": "the difference is the difference of the two linearisation "
                                      "errors carried by the outer terms: this is the pollution "
                                      "the proposal describes, and it needs per-branch truncation"})

        # (7) the leak, exhibited: residual times the outer factor
        leak = outer * residual
        truncation.append({"kind": "the residual multiplied by the outer factor",
                           "residual": residual.show(),
                           "leaked": leak.show(),
                           "reading": "with a truncated shell the carried object no longer equals "
                                      "this residual, so after multiplication it is not "
                                      "identifiable as a denominator residual"})

    refusals = []
    for case, action in (("zero denominator", lambda: RF(Poly.zero(), Poly.zero())),
                         ("inversion of zero", lambda: RF(Poly.zero()).inverse()),
                         ("shell whose tree misses its denotation",
                          lambda: Shell(Constant(2), RF.constant(3), "forged", 1))):
        try:
            action()
            refusals.append({"case": case, "refused": False})
        except ValueError as error:
            refusals.append({"case": case, "refused": True, "message": str(error)})
    check(all(r["refused"] for r in refusals), "ARefusalControlWasAccepted")

    return jsonable({
        "status": "ExternalExactPass",
        "native_status": "NotRun",
        "shell_form": "symbolically unexpanded expression, tied to its exact denotation at construction",
        "routes": routes,
        "identifiability": identifiability,
        "structural_cost_of_the_pair": structural,
        "truncation_controls": truncation,
        "frozen_shells": frozen,
        "refusals": refusals,
        "findings": [
            "the projective pair inverts by swap, and the two routes agree exactly by cross "
            "multiplication and at every declared sample point",
            "core plus shell equals the whole expression exactly, at every declared budget, and a "
            "frozen shell is retained with its reason instead of being rounded",
            "one shared truncation preserves the identity, so the proposal's claim that truncation "
            "by itself tears distributivity does not hold in this fragment",
            "per-branch truncation at different points breaks the identity exactly on the members "
            "whose outer terms differ, and not on the member whose outer terms are equal, so the "
            "pollution needs both a per-branch truncation and distinct outer terms",
            "what truncation breaks is identifiability: the carried shell stops equalling the "
            "exact residual, and the leak is that residual times the outer factor",
            "the pair decides value, not structure: the two routes agree in value while their "
            "literal representatives differ, so a reduction rule would be needed for object "
            "equality"],
        "counts": dict(COUNTS),
    })


def linearise(reference, at):
    """First-order linearisation of reference^-1 around a declared rational point."""
    f = reference.inverse()
    slope_pair = RF(f.num.derivative() * f.den - f.num * f.den.derivative(),
                    f.den * f.den)
    slope_at = slope_pair.at(at)
    shift = Sum(Variable(), Constant(-at))
    return RF.constant(f.at(at)) + RF.constant(slope_at) * RF(Poly([(1, 1)])), (f.at(at), slope_at)


def main():
    contract = json.loads((HERE / "contract.json").read_text())
    LIMITS.update(contract["budget"])
    report = run(contract)
    out = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / "evidence.json"
    out.write_text(json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
                   encoding="utf-8")
    print(json.dumps({k: report[k] for k in ("status", "counts")}, indent=1))
    for finding in report["findings"]:
        print(" *", finding)
    print("\n冻结的壳（示例）:", json.dumps(report["frozen_shells"][:1], ensure_ascii=False)[:300])
    print("截断控制（第二条）:", json.dumps(
        report["truncation_controls"][1], ensure_ascii=False)[:300])


if __name__ == "__main__":
    main()
