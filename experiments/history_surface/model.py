"""Original finite boundary-code model, contributed under Unknown v0.3.

Authored by Codex (OpenAI), through Mingli Yuan's authorized account proxy;
account use is not his authorship, review or endorsement.
This is external arithmetic research, not Adva semantic authority.
"""

from dataclasses import dataclass
from itertools import combinations

P = 7
MAX_LENGTH = 5
VERSION = "history-surface-v0"


@dataclass(frozen=True)
class Surface:
    k: int
    points: tuple
    values: tuple
    prime: int = P
    version: str = VERSION


@dataclass
class Work:
    decode_calls: int = 0
    candidate_subsets: int = 0
    max_decode_calls: int = 40000
    max_candidate_subsets: int = 250000

    def decode(self):
        if self.decode_calls >= self.max_decode_calls:
            raise RuntimeError("decode-call budget exhausted")
        self.decode_calls += 1

    def candidate(self):
        if self.candidate_subsets >= self.max_candidate_subsets:
            raise RuntimeError("candidate-subset budget exhausted")
        self.candidate_subsets += 1


def field_symbol(a):
    return type(a) is int and 0 <= a < P


def evaluate(coefficients, x):
    value = 0
    for coefficient in reversed(coefficients):
        value = (value * x + coefficient) % P
    return value


def encode(history):
    history = tuple(history)
    if len(history) > MAX_LENGTH:
        raise ValueError("CapacityExceeded")
    if not all(field_symbol(a) for a in history):
        raise ValueError("InvalidSymbol")
    points = tuple(i % P for i in range(1, len(history) + 3))
    return Surface(len(history), points, tuple(evaluate(history, x) for x in points))


def validate(surface):
    if surface.version != VERSION or surface.prime != P:
        return "UnsupportedHeader"
    if type(surface.k) is not int or not 0 <= surface.k <= MAX_LENGTH:
        return "InvalidLength"
    expected = tuple(i % P for i in range(1, surface.k + 3))
    if surface.points != expected or len(set(surface.points)) != len(expected):
        return "InvalidSampleLocations"
    if len(surface.values) != len(expected):
        return "InvalidSampleCount"
    if not all(a is None or field_symbol(a) for a in surface.values):
        return "InvalidSymbol"
    return None


def interpolate(points, values):
    """Vandermonde elimination in F_7; returned length retains zero coefficients."""
    n = len(points)
    matrix = [[pow(x, j, P) for j in range(n)] + [y]
              for x, y in zip(points, values)]
    for j in range(n):
        pivot = next((i for i in range(j, n) if matrix[i][j]), None)
        if pivot is None:
            raise ValueError("SingularSampleSet")
        matrix[j], matrix[pivot] = matrix[pivot], matrix[j]
        inverse = pow(matrix[j][j], -1, P)
        matrix[j] = [(x * inverse) % P for x in matrix[j]]
        for i in range(n):
            if i != j:
                multiplier = matrix[i][j]
                matrix[i] = [(a - multiplier*b) % P
                             for a, b in zip(matrix[i], matrix[j])]
    return tuple(matrix[i][-1] for i in range(n))


def decode(surface, errors=1, candidate_budget=21, work=None):
    """Return a word within the stated radius, not an authenticity judgment."""
    if work is not None:
        work.decode()
    invalid = validate(surface)
    if invalid:
        return {"status": "Rejected", "reason": invalid}
    if type(errors) is not int or errors not in (0, 1):
        return {"status": "Rejected", "reason": "UnsupportedErrorRadius"}
    if type(candidate_budget) is not int or candidate_budget < 0:
        return {"status": "Rejected", "reason": "InvalidBudget"}
    known = tuple(i for i, value in enumerate(surface.values) if value is not None)
    if len(known) < surface.k + 2*errors:
        return {"status": "Rejected", "reason": "InsufficientRedundancy"}
    tried = 0
    for selected in combinations(known, surface.k):
        if tried >= candidate_budget:
            return {"status": "Unknown", "reason": "CandidateBudget",
                    "candidates_tried": tried}
        if work is not None:
            work.candidate()
        tried += 1
        history = interpolate(tuple(surface.points[i] for i in selected),
                              tuple(surface.values[i] for i in selected))
        predicted = tuple(evaluate(history, x) for x in surface.points)
        mismatch = tuple(i for i in known if predicted[i] != surface.values[i])
        if len(mismatch) <= errors:
            return {
                "status": "DecodedWithinRadius", "history": history,
                "mismatch_sites": mismatch, "erased_sites": tuple(
                    i for i, value in enumerate(surface.values) if value is None),
                "candidates_tried": tried,
                "authenticity": "NotEstablished",
            }
    return {"status": "NoCodewordWithinRadius", "candidates_tried": tried,
            "scope": "this finite code, header, received word and radius"}


def append(surface, token, allowed=tuple(range(P)), work=None):
    if not field_symbol(token) or token not in allowed:
        return {"status": "Rejected", "reason": "OutsideContinuationScope"}
    if surface.k == MAX_LENGTH:
        return {"status": "Rejected", "reason": "CapacityExceeded"}
    result = decode(surface, work=work)
    if result["status"] != "DecodedWithinRadius":
        return result
    history = result["history"] + (token,)
    return {"status": "Extended", "surface": encode(history),
            "channel_assumption": "input differs from authentic code by at most one symbol"}


def readback(surface, length, work=None):
    if type(length) is not int or not 0 <= length <= surface.k:
        return {"status": "Rejected", "reason": "InvalidPrefixLength"}
    result = decode(surface, work=work)
    if result["status"] != "DecodedWithinRadius":
        return result
    return {"status": "ReadBack", "surface": encode(result["history"][:length])}


def domain_views(history):
    return {
        "T": tuple(x for x in history if x in (0, 1)),
        "X": tuple(x for x in history if x in (2, 3)),
        "K": tuple(x for x in history if x in (4, 5, 6)),
    }
