"""Exact external calibration; Python 3.11+, standard library only."""

from __future__ import annotations

import hashlib
import itertools
import json
import resource
import sys
import time
from dataclasses import dataclass
from fractions import Fraction as F
from pathlib import Path


@dataclass(frozen=True)
class QI:
    r: F
    i: F = F(0)

    @staticmethod
    def of(value):
        return value if isinstance(value, QI) else QI(F(value))

    def __add__(self, other):
        other = QI.of(other)
        return QI(self.r + other.r, self.i + other.i)

    __radd__ = __add__

    def __neg__(self):
        return QI(-self.r, -self.i)

    def __sub__(self, other):
        return self + -QI.of(other)

    def __rsub__(self, other):
        return QI.of(other) + -self

    def __mul__(self, other):
        other = QI.of(other)
        return QI(self.r * other.r - self.i * other.i,
                  self.r * other.i + self.i * other.r)

    __rmul__ = __mul__

    def __truediv__(self, other):
        other = QI.of(other)
        norm = other.r * other.r + other.i * other.i
        if norm == 0:
            raise ValueError("division by zero")
        value = self * QI(other.r, -other.i)
        return QI(value.r / norm, value.i / norm)

    def __pow__(self, exponent):
        if not isinstance(exponent, int) or not 0 <= exponent <= 6:
            raise ValueError("outside fixed polynomial grammar")
        result = QI(F(1))
        for _ in range(exponent):
            result = result * self
        return result

    def wire(self):
        return [str(self.r), str(self.i)]


ZERO = QI(F(0))
ONE = QI(F(1))


def encode(z, epsilon):
    if epsilon <= 0 or len(z) != 3:
        raise ValueError("positive scale and three ordered inputs required")
    return tuple(epsilon * (2 * z[k] + z[(k + 1) % 3]) / 3 for k in range(3))


def decode(lambdas, epsilon):
    if epsilon <= 0 or len(lambdas) != 3:
        raise ValueError("positive scale and three ordered outputs required")
    w = tuple(value / epsilon for value in lambdas)
    return tuple((4 * w[k] - 2 * w[(k + 1) % 3] + w[(k + 2) % 3]) / 3
                 for k in range(3))


def discriminant(value):
    if value in (ZERO, ONE):
        raise ValueError("singular Legendre parameter")
    return 16 * value**2 * (1 - value)**2


def j_invariant(value):
    discriminant(value)
    return 256 * (1 - value + value**2)**3 / (value**2 * (1 - value)**2)


def swapped(values, index):
    result = list(values)
    result[index], result[index + 1] = result[index + 1], result[index]
    return tuple(result)


def transport(values, epsilon, index):
    return encode(swapped(decode(values, epsilon), index), epsilon)


def word(values, epsilon, indices):
    for index in indices:
        values = transport(values, epsilon, index)
    return values


def wire(values):
    return [value.wire() for value in values]


def coverage(expected, observed):
    if len(observed) != len(set(observed)):
        return "RejectedDuplicate"
    if set(observed) - set(expected):
        return "RejectedForeign"
    return "Covered" if set(observed) == set(expected) else "Unknown"


def mm(a, b):
    return tuple(tuple(sum(a[i][k] * b[k][j] for k in range(2))
                       for j in range(2)) for i in range(2))


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def main():
    started = time.perf_counter()
    root = Path(__file__).resolve().parent
    contract_bytes = (root / "contract.json").read_bytes()
    contract = json.loads(contract_bytes)
    limit = contract["budget"]
    construct_start = time.perf_counter()
    # Gray order changes one real coordinate at each successive grid point.
    grid = []
    for k in range(64):
        g = k ^ (k >> 1)
        coords = [F(1 + ((g >> bit) & 1)) for bit in range(6)]
        grid.append(tuple(QI(coords[2 * i], coords[2 * i + 1]) for i in range(3)))
    fresh = list(itertools.product((QI(F(3, 2), F(3, 2)),
                                    QI(F(7, 4), F(5, 4))), repeat=3))
    scopes = [(F(1, 8), grid), (F(1, 16), grid), (F(1, 32), grid), (F(1, 64), fresh)]
    construction_seconds = time.perf_counter() - construct_start
    records = []
    naive_failures = 0
    first_failure = None
    max_bits = 0
    verification_seconds = 0.0
    reuse_seconds = 0.0
    for scope, (epsilon, directions) in enumerate(scopes):
        scope_start = time.perf_counter()
        for position, z in enumerate(directions):
            if time.perf_counter() - started > limit["max_seconds"]:
                raise TimeoutError("Unknown: finite deadline reached")
            require(len(records) < limit["max_states"], "Unknown: state cap reached")
            values = encode(z, epsilon)
            require(decode(values, epsilon) == z, "round-trip failed")
            ds, js = [], []
            for value in values:
                d = discriminant(value)
                # Independent cubic coefficient formula for x^3+b*x^2+c*x.
                b, c = -(1 + value), value
                cubic_d = b**2 * c**2 - 4 * c**3
                require(d == 16 * cubic_d and d != ZERO, "discriminant mismatch")
                j = j_invariant(value)
                require(j == j_invariant(1 - value), "relabel j mismatch")
                require(j == j_invariant(ONE / value), "inverse relabel j mismatch")
                ds.append(d)
                js.append(j)
            for index in (0, 1):
                expected = encode(swapped(z, index), epsilon)
                require(transport(values, epsilon, index) == expected, "transport mismatch")
                require(word(values, epsilon, (index, index)) == values, "swap inverse failed")
                naive = swapped(values, index)
                if naive != expected:
                    naive_failures += 1
                    if first_failure is None:
                        first_failure = {"scope": scope, "position": position,
                                         "epsilon": str(epsilon), "input": wire(z),
                                         "swap": index, "naive": wire(naive),
                                         "required": wire(expected)}
            require(word(values, epsilon, (0, 1, 0)) == word(values, epsilon, (1, 0, 1)),
                    "permutation braid relation failed")
            # A swap is an involution: this representation factors through S3.
            require((0, 1, 0) != (1, 0, 1), "raw histories must remain distinct")
            for value in (*values, *ds, *js):
                for part in (value.r, value.i):
                    max_bits = max(max_bits, abs(part.numerator).bit_length(),
                                   part.denominator.bit_length())
            require(max_bits <= limit["max_integer_bits"], "Unknown: integer bit cap")
            records.append({"scope": scope, "position": position, "epsilon": str(epsilon),
                            "directions": wire(z), "lambdas": wire(values),
                            "discriminants": wire(ds), "j": wire(js),
                            "history": {"compared_words": [[0, 1, 0], [1, 0, 1]],
                                        "comparison": "same output, different word"}})
        elapsed = time.perf_counter() - scope_start
        if scope == 3:
            reuse_seconds += elapsed
        else:
            verification_seconds += elapsed
    control_start = time.perf_counter()
    require(len(set(grid)) == 64 and len(set(fresh)) == 8, "direction cardinality")
    for a, b in zip(grid, grid[1:]):
        ar = [v for q in a for v in (q.r, q.i)]
        br = [v for q in b for v in (q.r, q.i)]
        require(sum(x != y for x, y in zip(ar, br)) == 1, "Gray adjacency")
    require(coverage(range(64), list(range(64))) == "Covered", "coverage positive")
    require(coverage(range(64), list(range(63))) == "Unknown", "coverage missing")
    require(coverage(range(64), [*range(64), 0]) == "RejectedDuplicate", "coverage duplicate")
    require(coverage(range(64), [*range(64), 64]) == "RejectedForeign", "coverage foreign")
    refused = []
    for name, operation in (("zero-scale", lambda: encode(grid[0], F(0))),
                            ("lambda-zero", lambda: discriminant(ZERO)),
                            ("lambda-one", lambda: discriminant(ONE))):
        try:
            operation()
        except ValueError:
            refused.append(name)
        else:
            raise AssertionError("boundary not refused: " + name)
    # Losing epsilon loses direction: these two different inputs have equal outputs.
    z = grid[0]
    double = tuple(2 * q for q in z)
    require(z != double and encode(z, F(1, 8)) == encode(double, F(1, 16)),
            "scale-erasure ambiguity")
    a = ((1, 2), (0, 1))
    b = ((1, 0), (-2, 1))
    u = ((-1, 2), (-2, 3))
    ident = ((1, 0), (0, 1))
    negative = ((-1, 0), (0, -1))
    require(mm(mm(a, b), u) == negative, "positive lift sign")
    require(mm(mm(a, b), tuple(tuple(-v for v in row) for row in u)) == ident,
            "actual monodromy closure")
    require(mm(a, b) != mm(b, a), "path order must matter")
    control_seconds = time.perf_counter() - control_start
    serialize_start = time.perf_counter()
    payload = json.dumps(records, sort_keys=True, separators=(",", ":"))
    serialization_seconds = time.perf_counter() - serialize_start
    replay_start = time.perf_counter()
    replay = json.loads(payload)
    require(replay == records, "wire replay mismatch")
    for row in replay:
        z = tuple(QI(F(r), F(i)) for r, i in row["directions"])
        require(wire(encode(z, F(row["epsilon"]))) == row["lambdas"], "execution replay")
    replay_seconds = time.perf_counter() - replay_start
    report = {
        "status": "FiniteChecksPassed", "contract_sha256": hashlib.sha256(contract_bytes).hexdigest(),
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "python": sys.version, "states": len(records), "smooth_curve_checks": 3 * len(records),
        "coverage_by_scope": [64, 64, 64, 8], "naive_swap_failures_of_400": naive_failures,
        "first_naive_swap_counterexample": first_failure, "boundary_refusals": refused,
        "controls": {"omission": "Unknown", "duplicate": "RejectedDuplicate",
                     "foreign": "RejectedForeign", "scale_erasure": "Ambiguous",
                     "positive_lift": "-I", "actual_monodromy": "I",
                     "swap_action": "S3 quotient, not faithful B3"},
        "observed_max_stored_rational_bits": max_bits,
        "cost_seconds": {"construction": construction_seconds,
                         "verification_192": verification_seconds, "reuse_8": reuse_seconds,
                         "controls": control_seconds, "serialization_records": serialization_seconds,
                         "replay": replay_seconds, "elapsed_before_report_write": time.perf_counter() - started},
        "max_rss_kib_linux": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        "unmeasured": ["authoring and network", "temporary integer bit maxima",
                       "native Rust execution", "analytic period evaluation", "total report write time"],
        "native_admission": "not-granted", "records": records,
    }
    require(time.perf_counter() - started <= limit["max_seconds"], "Unknown: final deadline")
    output = Path(sys.argv[1]) if len(sys.argv) > 1 else root / "evidence.json"
    output.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({k: v for k, v in report.items() if k != "records"}, indent=2))


if __name__ == "__main__":
    main()
