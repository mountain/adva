#!/usr/bin/env python3
"""Bounded external calibration over the staged golden-ratio resources.

The run consumes the delivered resource set, replays the delivered external
checker, and then does its own exact work in a different encoding of the same
quadratic field. It is an external oracle under AGENTS.md: it creates no Rust
witness, no native word and no proof authority. Plates and the captured PDF are
checked as bytes and structure only; no proportion is read out of a picture.

Usage:
  python3 -S experiments/golden_ratio/calibration.py --output target/fresh.json

The output path must not already exist. Exit codes: 0 Passed, 2 Invalid,
3 Unknown (a declared bound or the child budget stopped the run).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
import subprocess
import sys
import time
import zipfile
from fractions import Fraction
from pathlib import Path

HOME = "adva-library/golden-ratio"
INDEX_PATH = HOME + "/index.json"
CONTRACT_PATH = "experiments/golden_ratio/contract.json"
RECEIPT_CONTRACT_PATH = "docs/terminology/golden-ratio-receipt-v0.json"

BUDGET = {
    "max_seconds": 30.0,
    "max_checks": 20_000,
    "max_nodes": 200_000,
    "max_staged_bytes": 8 * 1024 * 1024,
    "child_timeout_seconds": 30,
    "max_output_file_bytes": 1024 * 1024,
    "fibonacci_index_max": 24,
    "rectangle_steps_max": 16,
    "search_steps": 12,
    "lattice_box": 20,
}

RECEIPT_FIELDS = (
    "question_id",
    "object_type",
    "arithmetic_domain",
    "embedding",
    "expression_or_word",
    "evaluation_order",
    "frame",
    "assumptions",
    "fuel_used",
    "claim_scope",
    "witness",
    "residual",
)

RECEIPT_KINDS = ("fixed-seed", "unknown-tail", "exact-closure", "finite-precision-stop")


class Bound(Exception):
    """A declared bound stopped the run: Unknown, never partial acceptance."""


class Invalid(Exception):
    """A checked requirement failed: the run is invalid, not merely unfinished."""


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
# Exact field K = Q(sqrt 5), encoded as (p + q*sqrt 5)/2 with rational p and q.
# This is deliberately not the delivered (a + b*phi) rational-pair encoding.
# --------------------------------------------------------------------------


class K:
    __slots__ = ("p", "q")

    def __init__(self, p: object = 0, q: object = 0) -> None:
        self.p = Fraction(p)
        self.q = Fraction(q)

    def __add__(self, other: "K") -> "K":
        return K(self.p + other.p, self.q + other.q)

    __radd__ = __add__

    def __neg__(self) -> "K":
        return K(-self.p, -self.q)

    def __sub__(self, other: "K") -> "K":
        return self + (-other)

    def __rsub__(self, other: "K") -> "K":
        return -self + other

    def __mul__(self, other: "K") -> "K":
        return K(
            (self.p * other.p + 5 * self.q * other.q) / 2,
            (self.p * other.q + other.p * self.q) / 2,
        )

    __rmul__ = __mul__

    def __truediv__(self, other: "K") -> "K":
        return self * other.inverse()

    def __eq__(self, other: object) -> bool:
        return isinstance(other, K) and self.p == other.p and self.q == other.q

    def __hash__(self) -> int:
        return hash((self.p, self.q))

    def __repr__(self) -> str:  # pragma: no cover - diagnostics only
        return f"K({self.p},{self.q})"

    def conjugate(self) -> "K":
        """Field conjugation: sqrt 5 maps to -sqrt 5."""
        return K(self.p, -self.q)

    def norm(self) -> Fraction:
        return (self.p * self.p - 5 * self.q * self.q) / 4

    def inverse(self) -> "K":
        element_norm = self.norm()
        if element_norm == 0:
            raise ZeroDivisionError("zero has no inverse in K")
        return K(self.p / element_norm, -self.q / element_norm)

    def __pow__(self, exponent: int) -> "K":
        if exponent < 0:
            return self.inverse() ** (-exponent)
        result, base = ONE, self
        while exponent:
            if exponent & 1:
                result = result * base
            base = base * base
            exponent >>= 1
        return result

    def sign(self) -> int:
        """Exact comparison; no floating-point detour is used for a decision."""
        p, q = self.p, self.q
        if q == 0:
            return (p > 0) - (p < 0)
        if p == 0 or ((p > 0) == (q > 0)):
            return (q > 0) - (q < 0)
        return ((p > 0) - (p < 0)) * ((p * p - 5 * q * q > 0) - (p * p - 5 * q * q < 0))

    def __lt__(self, other: "K") -> bool:
        return (self - other).sign() < 0

    def __le__(self, other: "K") -> bool:
        return (self - other).sign() <= 0

    def in_integer_ring(self) -> bool:
        """Z[phi] = {(p + q*sqrt 5)/2 : p, q integers and p = q mod 2}."""
        return (
            self.p.denominator == 1
            and self.q.denominator == 1
            and (self.p.numerator - self.q.numerator) % 2 == 0
        )

    def pair(self) -> list[str]:
        return [str(self.p), str(self.q)]


ZERO = K(0, 0)
ONE = K(2, 0)
HALF = K(1, 0)
PHI = K(1, 1)
RHO = K(-1, 1)          # 1/phi
SQRT5 = K(0, 2)


def rational(value: object) -> K:
    """Embed a rational as (2v + 0*sqrt 5)/2."""
    return K(2 * Fraction(value), 0)


class Affine:
    """x -> t*x + c over K; after() composes self after its argument."""

    __slots__ = ("t", "c")

    def __init__(self, t: K, c: K) -> None:
        self.t = t
        self.c = c

    def after(self, other: "Affine") -> "Affine":
        return Affine(self.t * other.t, self.t * other.c + self.c)

    def inverse(self) -> "Affine":
        inverse = self.t.inverse()
        return Affine(inverse, -(inverse * self.c))

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Affine) and self.t == other.t and self.c == other.c

    def __repr__(self) -> str:  # pragma: no cover - diagnostics only
        return f"Affine({self.t!r},{self.c!r})"


IDENTITY = Affine(ONE, ZERO)
LETTER_EXPONENT = {"a": 1, "A": -1, "b": 0, "B": 0}
LETTER_CONSTANT = {"a": 0, "A": 0, "b": 1, "B": -1}


def letter(character: str, parameter: K) -> Affine:
    if character == "a":
        return Affine(parameter, ZERO)
    if character == "A":
        return Affine(parameter.inverse(), ZERO)
    if character == "b":
        return Affine(ONE, ONE)
    if character == "B":
        return Affine(ONE, -ONE)
    raise ValueError(f"unknown letter: {character}")


def affine_word(parameter: K, word: str) -> Affine:
    """Read left to right; the leftmost letter acts last."""
    result = IDENTITY
    for character in word:
        result = result.after(letter(character, parameter))
    return result


def word_residual_polynomial(word: str) -> dict[int, int]:
    """Residual constant of the word as an exact Laurent polynomial in t.

    Multipliers are monomials, so composition stays exact: the constant is a
    dictionary from exponent to integer coefficient. A word that uses a and A
    equally often leaves no negative exponent at the end.
    """
    # The multiplier stays a monomial t^exponent, so composing f after g gives
    # t' = t*t_g and c' = t^exponent * c_g + c: only the letter constant is
    # shifted, never the accumulated constant.
    exponent = 0
    constant: dict[int, int] = {}
    for character in word:
        updated = dict(constant)
        letter_constant = LETTER_CONSTANT[character]
        if letter_constant:
            updated[exponent] = updated.get(exponent, 0) + letter_constant
        exponent += LETTER_EXPONENT[character]
        constant = {power: coefficient for power, coefficient in updated.items() if coefficient}
    return constant


def evaluate_polynomial(polynomial: dict[int, int], parameter: K) -> K:
    total = ZERO
    for power, coefficient in polynomial.items():
        total = total + rational(coefficient) * parameter ** power
    return total


def fibonacci(count: int) -> list[int]:
    values = [0, 1]
    while len(values) <= count:
        values.append(values[-1] + values[-2])
    return values


def lucas(count: int) -> list[int]:
    values = [2, 1]
    while len(values) <= count:
        values.append(values[-1] + values[-2])
    return values


def mobius_power(steps: int) -> tuple[int, int, int, int]:
    """Compose F(x) = (x + 1)/x exactly as an integer matrix product."""
    result = (1, 0, 0, 1)
    step = (1, 1, 1, 0)
    for _ in range(steps):
        result = (
            result[0] * step[0] + result[1] * step[2],
            result[0] * step[1] + result[1] * step[3],
            result[2] * step[0] + result[3] * step[2],
            result[2] * step[1] + result[3] * step[3],
        )
    return result


def media_and_size(blob: bytes) -> dict:
    if blob[:8] == b"\x89PNG\r\n\x1a\n":
        width, height = struct.unpack(">II", blob[16:24])
        return {"media_type": "image/png", "width": width, "height": height}
    if blob[:4] == b"RIFF" and blob[8:12] == b"WEBP":
        index, info = 12, {"media_type": "image/webp", "chunks": []}
        while index + 8 <= len(blob):
            fourcc = blob[index:index + 4].decode("ascii", "replace")
            size = struct.unpack("<I", blob[index + 4:index + 8])[0]
            body = blob[index + 8:index + 8 + size]
            info["chunks"].append(fourcc)
            if fourcc == "VP8X":
                info["width"] = 1 + int.from_bytes(body[4:7], "little")
                info["height"] = 1 + int.from_bytes(body[7:10], "little")
            elif fourcc == "VP8 ":
                info["width"] = struct.unpack("<H", body[6:8])[0] & 0x3FFF
                info["height"] = struct.unpack("<H", body[8:10])[0] & 0x3FFF
            elif fourcc == "VP8L":
                b0, b1, b2, b3 = body[1], body[2], body[3], body[4]
                info["width"] = 1 + (((b1 & 0x3F) << 8) | b0)
                info["height"] = 1 + (((b3 & 0xF) << 10) | (b2 << 2) | ((b1 & 0xC0) >> 6))
            index += 8 + size + (size & 1)
        return info
    if blob[:2] == b"\xff\xd8":
        index = 2
        while index < len(blob):
            if blob[index] != 0xFF:
                index += 1
                continue
            marker = blob[index + 1]
            if marker in (0xD8, 0x01) or 0xD0 <= marker <= 0xD7:
                index += 2
                continue
            length = int.from_bytes(blob[index + 2:index + 4], "big")
            if 0xC0 <= marker <= 0xCF and marker not in (0xC4, 0xC8, 0xCC):
                return {
                    "media_type": "image/jpeg",
                    "width": int.from_bytes(blob[index + 7:index + 9], "big"),
                    "height": int.from_bytes(blob[index + 5:index + 7], "big"),
                }
            index += 2 + length
        return {"media_type": "image/jpeg"}
    return {"media_type": "application/octet-stream"}


def read_bytes(path: Path, run: Run) -> bytes:
    run.tick()
    blob = path.read_bytes()
    if len(blob) > BUDGET["max_staged_bytes"]:
        raise Bound(f"staged artifact exceeds the byte budget: {path}")
    return blob


# --------------------------------------------------------------------------
# Tier 0: staged resource integrity
# --------------------------------------------------------------------------


def resource_integrity(root: Path, run: Run) -> dict:
    index = json.loads(read_bytes(root / INDEX_PATH, run).decode("utf-8"))
    run.check("index-schema", index["schema"] == "adva.golden-ratio-resource-index.research")
    run.check("index-status", index["status"] == "StagedExternalResourcesNotAdmitted")
    run.check("index-admission", index["authority"]["native_admission"] == "not-granted")
    run.check("index-plates-not-evidence", index["authority"]["plates_are_evidence"] is False)
    run.check("index-pdf-not-evidence", index["authority"]["pdf_is_evidence"] is False)
    run.check("index-excluded-entries", len(index["delivery"]["excluded_delivered_entries"]) >= 1)

    total = 0
    plate_headers = []
    pdf_probe = None
    by_name = {}
    for artifact in index["artifacts"]:
        relative = artifact["staged_path"]
        blob = read_bytes(root / relative, run)
        total += len(blob)
        by_name[artifact["delivered_name"]] = artifact
        run.check(f"artifact-bytes::{relative}", len(blob) == artifact["bytes"])
        run.check(
            f"artifact-digest::{relative}",
            hashlib.sha256(blob).hexdigest() == artifact["sha256"],
        )
        declared = artifact.get("delivered_structure")
        if declared is None:
            continue
        if declared.get("media_type", "").startswith("image/"):
            observed = media_and_size(blob)
            run.check(f"artifact-media::{relative}", observed["media_type"] == declared["media_type"])
            run.check(
                f"artifact-pixels::{relative}",
                (observed["width"], observed["height"]) == (declared["width"], declared["height"]),
            )
            plate_headers.append(
                {
                    "staged_path": relative,
                    "media_type": observed["media_type"],
                    "width": observed["width"],
                    "height": observed["height"],
                }
            )
        else:
            run.check(f"artifact-pdf-header::{relative}", blob[:8] == b"%PDF-1.4")
            run.check(f"artifact-pdf-revision::{relative}", blob.find(b"oldid=1370346489") >= 0)
            run.check(f"artifact-pdf-trailer::{relative}", blob.rstrip().endswith(b"%%EOF"))
            pdf_probe = {
                "staged_path": relative,
                "bytes": len(blob),
                "declared_title": declared.get("title"),
                "declared_creation_date": declared.get("creation_date"),
                "cited_revision": "oldid=1370346489",
                "cited_revision_present": True,
            }
    run.check("staged-bytes-budget", total <= BUDGET["max_staged_bytes"])

    record = json.loads(read_bytes(root / (HOME + "/source/SHA256.json"), run).decode("utf-8"))
    for member, digest in sorted(record.items()):
        run.check(f"delivered-digest::{member}", by_name[member]["sha256"] == digest)
    run.check("delivered-digest-count", len(record) == 5)

    container_path = root / HOME / "source/golden_ratio_reproducible.zip"
    with zipfile.ZipFile(container_path) as archive:
        run.check(
            "container-member-count",
            len(archive.namelist()) == len(index["digest_records"]["container_members"]),
        )
        for entry in index["digest_records"]["container_members"]:
            blob = archive.read(entry["name"])
            run.check(
                f"container-member-digest::{entry['name']}",
                hashlib.sha256(blob).hexdigest() == entry["sha256"],
            )
            staged = by_name.get(entry["name"])
            run.check(
                f"container-member-staged::{entry['name']}",
                staged is not None and blob == (root / staged["staged_path"]).read_bytes(),
            )

    return {
        "artifacts": len(index["artifacts"]),
        "bytes": total,
        "delivered_digest_claims": len(record),
        "container_members": len(index["digest_records"]["container_members"]),
        "plates": plate_headers,
        "pdf": pdf_probe,
        "digest_policy": "byte integrity only; not authentication, identity or proof",
    }


# --------------------------------------------------------------------------
# Tier 4: replay the delivered external checker in a bounded child process
# --------------------------------------------------------------------------


def external_replay(root: Path, run: Run) -> dict:
    checker = root / HOME / "source/verify_golden.py"
    recorded = json.loads(read_bytes(root / (HOME + "/source/evidence.json"), run).decode("utf-8"))
    run.tick()
    try:
        completed = subprocess.run(
            [sys.executable, "-S", str(checker)],
            cwd=str(checker.parent),
            capture_output=True,
            text=True,
            timeout=BUDGET["child_timeout_seconds"],
            check=False,
        )
    except subprocess.TimeoutExpired:
        raise Bound("the delivered checker exceeded the child budget")
    if completed.returncode != 0:
        raise Invalid(f"the delivered checker exited {completed.returncode}: {completed.stderr[:400]}")
    replayed = json.loads(completed.stdout)

    run.check("replay-status", replayed["status"] == recorded["status"])
    run.check("replay-check-count", replayed["check_count"] == recorded["check_count"])
    run.check("replay-check-names", replayed["checks"] == recorded["checks"])
    compared = (
        "budget",
        "field",
        "word_cases",
        "continued_fraction_seed_1_six_steps",
        "positive_unknown_tail_six_prefix_interval",
        "rational_reverse",
        "rectangle_center",
        "rectangle_diameter_squared_after_12",
        "icosahedron",
        "hyperbolic",
        "substitution_words",
        "residuals",
    )
    for key in compared:
        run.check(f"replay-field::{key}", replayed[key] == recorded[key])
    for old, new in zip(recorded["golden_search"], replayed["golden_search"]):
        run.check("replay-search-root", old["root"] == new["root"])
        run.check("replay-search-calls", old["baseline"]["calls"] == new["baseline"]["calls"])
        run.check("replay-search-intervals", old["baseline"]["intervals"] == new["baseline"]["intervals"])
        run.check("replay-search-reuse-intervals", old["reuse"]["intervals"] == new["reuse"]["intervals"])
    return {
        "status": "ReplayedAgreement",
        "checker": HOME + "/source/verify_golden.py",
        "recorded_evidence": HOME + "/source/evidence.json",
        "check_count": replayed["check_count"],
        "compared_fields": len(compared),
        "excluded_fields": [
            "cost",
            "cost.peak_rss_raw",
            "cost.peak_rss_unit",
            "golden_search[*].baseline_ms",
            "golden_search[*].reuse_ms",
        ],
        "note": (
            "Replay reproduces a supplied implementation; it is not an independent oracle. "
            "Timing and platform fields are excluded rather than compared."
        ),
    }


# --------------------------------------------------------------------------
# Tier 1: independent exact derivations in the (p + q*sqrt 5)/2 encoding
# --------------------------------------------------------------------------


def field_and_sequence_checks(run: Run, limit: int) -> None:
    fib = fibonacci(limit + 3)
    luc = lucas(limit + 3)

    run.check("phi-minimal-polynomial", PHI * PHI - PHI - ONE == ZERO)
    run.check("phi-positive-embedding", ZERO < PHI and PHI < rational(2))
    run.check("phi-in-integer-ring", PHI.in_integer_ring())
    run.check("conjugate-is-minus-reciprocal", PHI.conjugate() == -RHO)
    run.check("conjugate-is-not-reciprocal", PHI.conjugate() != RHO)
    run.check("norm-phi-minus-one", PHI.norm() == -1)
    run.check("norm-phi-squared-one", (PHI ** 2).norm() == 1)
    run.check("reciprocal-product", PHI ** 2 * PHI ** -2 == ONE)
    run.check("reciprocal-sum-three", PHI ** 2 + PHI ** -2 == rational(3))
    run.check("sqrt5-square", SQRT5 * SQRT5 == rational(5))
    run.check("phi-times-conjugate", PHI * PHI.conjugate() == -ONE)

    for a in range(-2, 3):
        for b in range(-2, 3):
            element = rational(a) + rational(b) * PHI
            run.check(f"integer-ring::{a}::{b}", element.in_integer_ring())
            if element != ZERO:
                run.check(f"field-inverse::{a}::{b}", element * element.inverse() == ONE)
    try:
        ZERO.inverse()
        raise Invalid("zero was accepted as invertible")
    except ZeroDivisionError:
        run.check("zero-inverse-refused", True)

    non_unit = rational(3) - PHI
    run.check("non-unit-in-ring", non_unit.in_integer_ring())
    run.check("non-unit-norm-five", non_unit.norm() == 5)
    run.check("non-unit-inverse-leaves-ring", not non_unit.inverse().in_integer_ring())
    run.check("unit-norm-one-stays", (PHI ** 2).inverse().in_integer_ring())

    for n in range(1, limit + 1):
        run.tick()
        run.check(f"phi-power-fibonacci::{n}", PHI ** n == rational(fib[n]) * PHI + rational(fib[n - 1]))
        run.check(f"cassini::{n}", fib[n + 1] * fib[n - 1] - fib[n] * fib[n] == (-1) ** n)
        # Convergents alternate around the limit; the ordered pair is the bracket.
        low, high = sorted(
            (Fraction(fib[n + 1], fib[n]), Fraction(fib[n + 2], fib[n + 1]))
        )
        run.check(f"bracket-straddles::{n}", rational(low) < PHI < rational(high))
        run.check(f"bracket-gap::{n}", high - low == Fraction(1, fib[n] * fib[n + 1]))
        run.check(f"binet::{n}", PHI ** n - PHI.conjugate() ** n == SQRT5 * rational(fib[n]))
        run.check(f"lucas-value::{n}", PHI ** n + PHI.conjugate() ** n == rational(luc[n]))
        run.check(f"lucas-fibonacci-identity::{n}", luc[n] * luc[n] - 5 * fib[n] * fib[n] == 4 * (-1) ** n)
        run.check(f"conjugate-power::{n}", PHI.conjugate() ** n == rational((-1) ** n) * PHI ** -n)
        if n >= 2:
            run.check(f"near-integer-residual::{n}", ZERO < PHI ** -n and PHI ** -n < HALF)

    matrix = (1, 1, 1, 0)
    power = (1, 0, 0, 1)
    for n in range(1, limit + 1):
        run.tick()
        power = (
            power[0] * matrix[0] + power[1] * matrix[2],
            power[0] * matrix[1] + power[1] * matrix[3],
            power[2] * matrix[0] + power[3] * matrix[2],
            power[2] * matrix[1] + power[3] * matrix[3],
        )
        run.check(f"matrix-power::{n}", power == (fib[n + 1], fib[n], fib[n], fib[n - 1]))

    run.check("phinary-same-value", PHI ** 2 == PHI + ONE and "100" != "011")


def word_checks(run: Run) -> dict:
    word = "abbbaBAAB"
    run.check("word-identity-at-phi-squared", affine_word(PHI ** 2, word) == IDENTITY)
    run.check("word-identity-at-phi-minus-squared", affine_word(PHI ** -2, word) == IDENTITY)
    # New instance: the inverse word closes at the same parameter, while a
    # non-root parameter leaves a residual, so the closure is parameter-specific.
    inverse_letters = {"a": "A", "A": "a", "b": "B", "B": "b"}
    inverse_word = "".join(inverse_letters[c] for c in reversed(word))
    run.check("word-new-instance-inverse-word", affine_word(PHI ** 2, inverse_word) == IDENTITY)
    run.check("word-non-root-parameter", affine_word(PHI ** 4, word) != IDENTITY)
    run.check(
        "word-wrong-parameter",
        affine_word(PHI, word) == Affine(ONE, rational(2) * PHI - rational(2)),
    )
    run.check("word-deleted-letter", affine_word(PHI ** 2, "abbaBAAB") == Affine(ONE, -(PHI ** 2)))

    polynomial = word_residual_polynomial(word)
    run.check("word-residual-polynomial", polynomial == {2: -1, 1: 3, 0: -1})
    run.check("word-polynomial-at-phi-squared", evaluate_polynomial(polynomial, PHI ** 2) == ZERO)
    run.check(
        "word-polynomial-matches-concrete",
        evaluate_polynomial(polynomial, PHI) == affine_word(PHI, word).c,
    )
    deleted = word_residual_polynomial("abbaBAAB")
    run.check(
        "deleted-polynomial-matches-concrete",
        evaluate_polynomial(deleted, PHI ** 2) == -(PHI ** 2),
    )

    six = mobius_power(6)
    run.check("mobius-six-step", six == (13, 8, 8, 5))
    run.check("mobius-determinant", six[0] * six[3] - six[1] * six[2] == 1)

    squared = (2, 1, 1, 1)
    characteristic = (
        1,
        -(squared[0] + squared[3]),
        squared[0] * squared[3] - squared[1] * squared[2],
    )
    run.check("charpoly-of-M-squared", characteristic == (1, -3, 1))
    run.check(
        "charpoly-shared-with-residual",
        characteristic == (-polynomial[0], -polynomial[1], -polynomial[2]),
    )

    u = Affine(ONE, ONE)
    v = Affine(ONE, PHI)
    scale = Affine(PHI ** -2, ZERO)
    run.check("hnn-u-relation", scale.inverse().after(u).after(scale) == u.after(v))
    run.check("hnn-v-relation", scale.inverse().after(v).after(scale) == v.after(u).after(v))
    run.check("hnn-commuting-shadow", u.after(v) == v.after(u))
    run.check(
        "commutator-erased-by-closure",
        u.after(v).after(u.inverse()).after(v.inverse()) == IDENTITY,
    )
    return {"word": word, "residual_polynomial": {str(k): v for k, v in polynomial.items()}}


def rectangle_checks(run: Run) -> dict:
    def step(point: tuple[K, K]) -> tuple[K, K]:
        x, y = point
        return (PHI - y * RHO, x * RHO)

    corners = ((ZERO, ZERO), (PHI, ZERO), (PHI, ONE), (ZERO, ONE))
    run.check(
        "rectangle-one-step-image",
        {step(corner) for corner in corners} == {(ONE, ZERO), (PHI, ZERO), (PHI, ONE), (ONE, ONE)},
    )

    center_x = (ONE + rational(3) * PHI) / rational(5)
    center_y = (rational(2) + PHI) / rational(5)
    run.check("rectangle-fixed-point", step((center_x, center_y)) == (center_x, center_y))
    run.check("rectangle-fixed-point-inner", ONE < center_x < PHI and ZERO < center_y < ONE)
    run.check("rectangle-fixed-point-closed-form", (ONE + PHI ** -2) * center_y == ONE)

    taken = ZERO
    previous = None
    for n in range(0, BUDGET["rectangle_steps_max"] + 1):
        run.tick()
        images = corners
        for _ in range(n):
            images = tuple(step(point) for point in images)
        xs = [point[0] for point in images]
        ys = [point[1] for point in images]
        low_x, high_x = min(xs), max(xs)
        low_y, high_y = min(ys), max(ys)
        width, height = high_x - low_x, high_y - low_y
        run.check(f"rectangle-area::{n}", width * height == PHI ** (1 - 2 * n))
        run.check(
            f"rectangle-diameter::{n}",
            width * width + height * height == (PHI ** 2 + ONE) * PHI ** (-2 * n),
        )
        run.check(
            f"rectangle-contains-center::{n}",
            low_x <= center_x <= high_x and low_y <= center_y <= high_y,
        )
        if previous is not None:
            run.check(
                f"rectangle-nested::{n}",
                previous[0] <= low_x
                and high_x <= previous[1]
                and previous[2] <= low_y
                and high_y <= previous[3],
            )
        previous = (low_x, high_x, low_y, high_y)
        if n >= 1:
            taken = taken + PHI ** (-2 * (n - 1))
            run.check(f"rectangle-coverage::{n}", taken + PHI ** (1 - 2 * n) == PHI)
            run.check(f"rectangle-residual-positive::{n}", ZERO < PHI ** (1 - 2 * n))
    run.check(
        "rectangle-resolution-stop",
        (PHI ** 2 + ONE) * PHI ** -24 < rational(Fraction(1, 10000)),
    )
    run.check("rectangle-stop-is-not-empty", ZERO < PHI ** -23)

    reverse = [Fraction(13, 8)]
    while reverse[-1] != 1 and len(reverse) < 10:
        reverse.append(1 / (reverse[-1] - 1))
    run.check(
        "rational-reverse-terminates",
        reverse
        == [
            Fraction(13, 8),
            Fraction(8, 5),
            Fraction(5, 3),
            Fraction(3, 2),
            Fraction(2),
            Fraction(1),
        ],
    )
    new_instance = [Fraction(21, 13)]
    while new_instance[-1] != 1 and len(new_instance) < 10:
        new_instance.append(1 / (new_instance[-1] - 1))
    run.check(
        "rational-reverse-new-instance",
        new_instance[:4]
        == [Fraction(21, 13), Fraction(13, 8), Fraction(8, 5), Fraction(5, 3)],
    )
    return {
        "fixed_point": [center_x.pair(), center_y.pair()],
        "steps": BUDGET["rectangle_steps_max"],
    }


def icosahedron_checks(run: Run) -> dict:
    # The twelve vertices are the cyclic arrangements of (0, +/-1, +/-phi).
    vertices = []
    for first in (-1, 1):
        for second in (-1, 1):
            vertices.append((ZERO, rational(first), rational(second) * PHI))
            vertices.append((rational(first), rational(second) * PHI, ZERO))
            vertices.append((rational(second) * PHI, ZERO, rational(first)))
    run.check("icosahedron-twelve-vertices", len(set(vertices)) == 12)
    squared = {}
    for i in range(12):
        for j in range(i + 1, 12):
            run.tick()
            total = ZERO
            for a, b in zip(vertices[i], vertices[j]):
                total = total + (a - b) * (a - b)
            squared[(i, j)] = total
            run.check(f"icosahedron-minimum::{i}::{j}", rational(4) <= total)
    edges = {pair for pair, value in squared.items() if value == rational(4)}
    run.check("icosahedron-thirty-edges", len(edges) == 30)
    run.check(
        "icosahedron-degree-five",
        all(sum(i in edge for edge in edges) == 5 for i in range(12)),
    )
    faces = [
        (i, j, k)
        for i in range(12)
        for j in range(i + 1, 12)
        for k in range(j + 1, 12)
        if (i, j) in edges and (i, k) in edges and (j, k) in edges
    ]
    run.check("icosahedron-twenty-faces", len(faces) == 20)
    return {"vertices": 12, "edges": len(edges), "faces": len(faces), "pairs": len(squared)}


def hyperbolic_checks(run: Run) -> dict:
    closeness = (PHI ** 2 + PHI ** -2) / rational(2)
    run.check("cosh-two-log-phi", closeness == rational(Fraction(3, 2)))
    run.check(
        "cosh-four-log-phi",
        (PHI ** 4 + PHI ** -4) / rational(2) == rational(Fraction(7, 2)),
    )
    run.check("matrix-trace-two-cosh", PHI ** 2 + PHI ** -2 == rational(3))
    run.check(
        "three-lengths-distinct",
        len({closeness * closeness, Fraction(49, 4), Fraction(2)}) == 3,
    )
    tangent = (
        (Fraction(0), Fraction(1)),
        (Fraction(1), Fraction(1)),
        (Fraction(1, 2), Fraction(1, 2)),
    )
    for i in range(3):
        for j in range(i + 1, 3):
            first, second = tangent[i], tangent[j]
            value = 1 + sum((a - b) ** 2 for a, b in zip(first, second)) / (
                2 * first[1] * second[1]
            )
            run.check(f"tangency-cosh::{i}::{j}", value == Fraction(3, 2))
    return {
        "translation_length": "4*log(phi)",
        "tangency_side": "2*log(phi)",
        "ideal_triangle_thinness": "log(1 + sqrt 2)",
        "comparison": "exact cosh values 3/2, 7/2 and sqrt 2; no transcendental evaluator",
    }


def substitution_checks(run: Run) -> dict:
    fib = fibonacci(12)
    word = "A"
    words = []
    for n in range(1, 9):
        run.tick()
        word = "".join("AB" if character == "A" else "A" for character in word)
        run.check(
            f"substitution-count::{n}",
            (word.count("A"), word.count("B")) == (fib[n + 1], fib[n]),
        )
        run.check(f"substitution-length::{n}", len(word) == fib[n + 2])
        words.append(word)
    run.check("substitution-six-step-length", len(words[5]) == 21)
    scrambled = "A" * words[5].count("A") + "B" * words[5].count("B")
    run.check(
        "counts-do-not-determine-word",
        (scrambled.count("A"), scrambled.count("B")) == (13, 8) and scrambled != words[5],
    )
    return {"steps": 8, "six_step_counts": {"A": 13, "B": 8}}


def golden_search(run: Run, target: K, steps: int, reuse: bool) -> tuple[int, list]:
    calls = 0

    def evaluate(point: K) -> K:
        nonlocal calls
        calls += 1
        return (point - target) * (point - target)

    low, high = ZERO, ONE
    left = low + (ONE - RHO) * (high - low)
    right = low + RHO * (high - low)
    left_value, right_value = evaluate(left), evaluate(right)
    trace = []
    for step in range(steps):
        run.tick()
        if left_value <= right_value:
            high = right
            if step + 1 < steps:
                if reuse:
                    right, right_value = left, left_value
                    left = low + (ONE - RHO) * (high - low)
                    left_value = evaluate(left)
                else:
                    left = low + (ONE - RHO) * (high - low)
                    right = low + RHO * (high - low)
                    left_value, right_value = evaluate(left), evaluate(right)
        else:
            low = left
            if step + 1 < steps:
                if reuse:
                    left, left_value = right, right_value
                    right = low + RHO * (high - low)
                    right_value = evaluate(right)
                else:
                    left = low + (ONE - RHO) * (high - low)
                    right = low + RHO * (high - low)
                    left_value, right_value = evaluate(left), evaluate(right)
        run.check(f"search-coverage::{target.p}::{int(reuse)}::{step}", low <= target <= high)
        run.check(
            f"search-width::{target.p}::{int(reuse)}::{step}",
            high - low == RHO ** (step + 1),
        )
        trace.append([low.pair(), high.pair()])
    return calls, trace


def search_checks(run: Run) -> list[dict]:
    results = []
    for target in (
        rational(Fraction(3, 7)),
        rational(Fraction(2, 3)),
        rational(Fraction(5, 8)),
    ):
        baseline_calls, baseline = golden_search(run, target, BUDGET["search_steps"], False)
        reuse_calls, reused = golden_search(run, target, BUDGET["search_steps"], True)
        run.check(f"search-baseline-calls::{target.p}", baseline_calls == 24)
        run.check(f"search-reuse-calls::{target.p}", reuse_calls == 13)
        run.check(f"search-identical-trace::{target.p}", baseline == reused)
        results.append(
            {
                "target": target.pair(),
                "baseline_calls": baseline_calls,
                "reuse_calls": reuse_calls,
                "identical_trace": True,
                "steps": BUDGET["search_steps"],
            }
        )
    return results


# --------------------------------------------------------------------------
# Tier 2: the eight source corrections as executable refusals
# --------------------------------------------------------------------------


def refusal_controls(run: Run) -> list[dict]:
    controls = []

    def control(identifier: str, correction: str, statement: str, value: bool, detail: str) -> None:
        run.check(f"refusal::{identifier}", value)
        controls.append(
            {
                "id": identifier,
                "correction": correction,
                "control": statement,
                "outcome": "Refused",
                "detail": detail,
            }
        )

    control(
        "R1-icosahedron-area",
        "A unit-edge icosahedron area of 10*phi^2 cannot be imported.",
        "the cited closed form differs from the twenty-face area",
        (rational(10) * PHI ** 2) ** 2 != rational(75),
        "squared comparison: 100*phi^4 = 300*phi + 200 differs from 75 = (5*sqrt 3)^2",
    )
    control(
        "R2-hyperbolic-distances",
        "Three distinct hyperbolic length objects were mixed.",
        "the three exact cosh values are pairwise distinct",
        len({Fraction(3, 2) ** 2, Fraction(7, 2) ** 2, Fraction(2, 1)}) == 3,
        "squares 9/4, 49/4 and 2 separate 2*log(phi), 4*log(phi) and log(1 + sqrt 2)",
    )
    decimal = rational(Fraction(2618, 1000))
    control(
        "R3-decimal-root",
        "A finite decimal is not an exact root.",
        "the decimal parameter fails the relation the exact root satisfies",
        affine_word(decimal, "abbbaBAAB") != IDENTITY
        and Fraction(1618, 1000) * Fraction(618, 1000) != 1,
        "t = 2.618 leaves a nonzero affine residual and 1.618*0.618 = 0.999924 is not 1",
    )
    control(
        "R4-epsilon-is-not-empty",
        "A boundary below epsilon is not an empty intersection.",
        "the residual stays strictly positive while the diameter bound is met",
        all(ZERO < PHI ** (1 - 2 * n) for n in range(1, BUDGET["rectangle_steps_max"] + 1))
        and (PHI ** 2 + ONE) * PHI ** -24 < rational(Fraction(1, 10000)),
        "diam^2 < 1e-4 at n = 12 while the residual area phi^-23 stays positive",
    )
    control(
        "R5-arc-is-not-spiral",
        "A quarter-circle arc is not the analytic logarithmic spiral.",
        "the radius ratio over one quarter turn differs exactly",
        ONE != PHI ** -1,
        "an arc keeps ratio 1 from its own centre; the spiral contracts by phi^-1",
    )
    box = BUDGET["lattice_box"]
    minimum = None
    nonzero = 0
    witness = None
    for m in range(-box, box + 1):
        for n in range(-box, box + 1):
            run.tick()
            value = rational(m) + rational(n) * PHI
            if value == ZERO:
                continue
            nonzero += 1
            size = value if value.sign() > 0 else -value
            if minimum is None or size < minimum:
                minimum, witness = size, (m, n)
    control(
        "R6-lattice-versus-projection",
        "A two-dimensional discrete lattice is not a one-dimensional dense projection.",
        "the box has a positive separation while the projection keeps approaching zero",
        nonzero == (2 * box + 1) ** 2 - 1
        and minimum == PHI ** -6
        and abs(witness[0]) == 13
        and abs(witness[1]) == 8,
        f"the closest of {nonzero} nonzero values m + n*phi in the box is phi^-6 at {witness}",
    )
    squared = (2, 1, 1, 1)
    control(
        "R7-polynomial-is-not-object",
        "An equal characteristic polynomial does not prove the same space or semantics.",
        "the shared polynomial coexists with two different actions",
        word_residual_polynomial("abbbaBAAB") == {2: -1, 1: 3, 0: -1}
        and affine_word(PHI ** 2, "abbbaBAAB") == IDENTITY
        and squared != (1, 0, 0, 1),
        "the residual polynomial is -(t^2 - 3t + 1) and M^2 has characteristic polynomial "
        "t^2 - 3t + 1, while the word acts trivially on a line and M^2 is not the identity",
    )
    u = Affine(ONE, ONE)
    v = Affine(ONE, PHI)
    scale = Affine(PHI ** -2, ZERO)
    control(
        "R8-closure-erases-history",
        "Operator closure does not erase history or grant native free.",
        "the HNN realization satisfies its relations while its commutator vanishes",
        scale.inverse().after(u).after(scale) == u.after(v)
        and scale.inverse().after(v).after(scale) == v.after(u).after(v)
        and u.after(v) == v.after(u)
        and u.after(v).after(u.inverse()).after(v.inverse()) == IDENTITY,
        "the nonempty commutator word maps to the identity affine, so this representation forgets it",
    )
    run.check("refusal-count", len(controls) == 8)
    return controls


# --------------------------------------------------------------------------
# Tier 3: four receipt kinds and their relabeling refusals
# --------------------------------------------------------------------------


def build_receipts(run: Run) -> tuple[list[dict], list[dict]]:
    seed = Fraction(1)
    orbit = [seed]
    for _ in range(6):
        orbit.append(1 + 1 / orbit[-1])
    run.check("seed-orbit-endpoint", orbit[-1] == Fraction(21, 13))
    run.check("seed-orbit-predecessor", orbit[-2] == Fraction(13, 8))
    lower, upper = sorted((orbit[-1], orbit[-2]))
    run.check("seed-bracket-width", upper - lower == Fraction(1, 104))
    run.check("seed-bracket-straddles", rational(lower) < PHI < rational(upper))

    numerator, constant, denominator, determinant = mobius_power(6)
    run.check("tail-image-map", (numerator, constant, denominator, determinant) == (13, 8, 8, 5))
    run.check("tail-lower-limit", Fraction(constant, determinant) == Fraction(8, 5))
    run.check("tail-upper-limit", Fraction(numerator, denominator) == Fraction(13, 8))
    run.check("tail-increasing", numerator * determinant - constant * denominator == 1)

    probe = Fraction(1, 2)
    probe_image = Fraction(numerator * probe + constant, denominator * probe + determinant)
    run.check("relabel-counterexample-inside-image", Fraction(8, 5) < probe_image < Fraction(13, 8))
    run.check("relabel-counterexample-below-seed", probe_image < lower)

    receipts = [
        {
            "receipt_kind": "fixed-seed",
            "question_id": "golden.cf.seed-1.six-steps",
            "object_type": "finite rational orbit of x -> 1 + 1/x from the seed x0 = 1",
            "arithmetic_domain": "Q with exact fractions",
            "embedding": "rational; no root selection is required",
            "expression_or_word": "F;F;F;F;F;F",
            "evaluation_order": "left to right, six applications, seed fixed before the run",
            "frame": "positive real line, seed 1",
            "assumptions": [
                "the seed is supplied",
                "the operation count is fixed",
                "the tail is produced, not supplied",
            ],
            "fuel_used": 6,
            "claim_scope": "this seeded orbit only; the bracket concerns the two produced values",
            "witness": {"lower": "21/13", "upper": "13/8", "width": "1/104"},
            "residual": "none for this finite task",
        },
        {
            "receipt_kind": "unknown-tail",
            "question_id": "golden.cf.positive-tail.six-ops",
            "object_type": "Mobius image of an unconstrained positive tail under six fixed operations",
            "arithmetic_domain": "Q with exact fractions",
            "embedding": "rational; the tail stays a variable",
            "expression_or_word": "F;F;F;F;F;F with the final hole open",
            "evaluation_order": "six operations compiled to M^6 = [[13,8],[8,5]]",
            "frame": "positive tail x > 0",
            "assumptions": ["the tail is arbitrary", "no value of the tail is observed"],
            "fuel_used": 6,
            "claim_scope": "coverage of every positive tail image, not one produced value",
            "witness": {"image": "open interval (8/5, 13/8)", "monotone": "ad - bc = 1 > 0"},
            "residual": "the tail stays unconstrained and both endpoints are unattained",
        },
        {
            "receipt_kind": "exact-closure",
            "question_id": "golden.word.abbbaBAAB",
            "object_type": "affine word at the figure-eight arithmetic parameter",
            "arithmetic_domain": "Z[phi] inside K = Q(sqrt 5)",
            "embedding": "1 < phi < 2, the positive root",
            "expression_or_word": "abbbaBAAB",
            "evaluation_order": "left to right; the leftmost letter acts last",
            "frame": "affine line over K at the parameter t = phi^2",
            "assumptions": [
                "the word is read in the declared direction",
                "the parameter is the exact root",
            ],
            "fuel_used": 9,
            "claim_scope": "exact closure at this parameter and at its conjugate parameter",
            "witness": {
                "residual": "identity affine map",
                "polynomial": "-(t^2 - 3t + 1) vanishes at both roots",
            },
            "residual": "none; the closure is exact",
        },
        {
            "receipt_kind": "finite-precision-stop",
            "question_id": "golden.rectangle.diameter-epsilon",
            "object_type": "nested rectangle diameters with a retained residual area",
            "arithmetic_domain": "Z[phi] inside K = Q(sqrt 5)",
            "embedding": "1 < phi < 2",
            "expression_or_word": "diam^2 = (phi^2 + 1) * phi^(-2n)",
            "evaluation_order": "n = 0 .. 16 with the nesting chain retained",
            "frame": "complex plane under S(z) = phi + (i/phi) z",
            "assumptions": ["the frame is fixed", "a resolution target is declared, not a limit"],
            "fuel_used": 16,
            "claim_scope": "the stop rule at n = 12 for epsilon = 0.01",
            "witness": {"squared_diameter_at_12": "< 1/10000"},
            "residual": "the residual area phi^(1 - 2n) stays strictly positive",
        },
    ]
    for receipt in receipts:
        run.check(
            f"receipt-fields::{receipt['receipt_kind']}",
            set(receipt) == set(RECEIPT_FIELDS) | {"receipt_kind"},
        )
    run.check("receipt-kinds", [r["receipt_kind"] for r in receipts] == list(RECEIPT_KINDS))

    relabel = [
        {
            "id": "relabel-seed-as-tail",
            "control": "the seeded bracket lower endpoint 13/8 is not the unknown-tail image",
            "counterexample": f"the positive tail x = 1/2 has image {probe_image}, below 21/13",
            "holds": probe_image < lower,
        },
        {
            "id": "relabel-stop-as-empty",
            "control": "a diameter below epsilon is not an empty intersection",
            "counterexample": "the residual area stays strictly positive at every step",
            "holds": all(
                ZERO < PHI ** (1 - 2 * n) for n in range(1, BUDGET["rectangle_steps_max"] + 1)
            ),
        },
        {
            "id": "relabel-closure-as-coverage",
            "control": "an exact closure at one parameter is not a statement about other parameters",
            "counterexample": "the same word at t = phi has residual 2*phi - 2",
            "holds": affine_word(PHI, "abbbaBAAB") != IDENTITY,
        },
        {
            "id": "relabel-tail-as-seed",
            "control": "an open image interval is not a produced rational bracket",
            "counterexample": "13/8 is a limit of the image and is attained by no positive tail",
            "holds": Fraction(8, 5) < probe_image < Fraction(13, 8)
            and probe_image != Fraction(13, 8),
        },
    ]
    for entry in relabel:
        run.check(f"relabeling::{entry['id']}", entry["holds"])
    return receipts, relabel


# --------------------------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser(description="bounded golden-ratio resource calibration")
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
        "schema": "adva.golden-ratio-calibration.research",
        "version": 0,
        "status": "Invalid",
        "reason": None,
        "scope": (
            "staged resource integrity, one bounded replay of the delivered external checker, "
            "independent exact derivation in a second encoding, eight source refusals and four receipt kinds"
        ),
        "authority": {
            "authority": "external-oracle-and-documentary-only",
            "native_admission": "not-granted",
            "plates_are_evidence": False,
            "pdf_is_evidence": False,
            "recorded_claims_authenticated": False,
        },
        "budget": dict(BUDGET),
    }
    try:
        contract_bytes = (root / CONTRACT_PATH).read_bytes()
        contract = json.loads(contract_bytes.decode("utf-8"))
        report["contract"] = {
            "path": CONTRACT_PATH,
            "sha256": hashlib.sha256(contract_bytes).hexdigest(),
            "question": contract["question"],
            "base_commit": contract["base_commit"],
        }
        terminology = json.loads((root / RECEIPT_CONTRACT_PATH).read_text(encoding="utf-8"))
        run.check("receipt-fields-agree", tuple(terminology["fields"]) == RECEIPT_FIELDS)
        run.check("receipt-kinds-agree", tuple(terminology["kinds"]) == RECEIPT_KINDS)
        report["resources"] = resource_integrity(root, run)
        field_and_sequence_checks(run, BUDGET["fibonacci_index_max"])
        report["word"] = word_checks(run)
        report["rectangle"] = rectangle_checks(run)
        report["icosahedron"] = icosahedron_checks(run)
        report["hyperbolic"] = hyperbolic_checks(run)
        report["substitution"] = substitution_checks(run)
        report["search"] = search_checks(run)
        receipts, relabel = build_receipts(run)
        report["receipts"] = receipts
        report["relabeling_refusals"] = relabel
        report["refusals"] = refusal_controls(run)
        report["external_replay"] = external_replay(root, run)
        report["status"] = "Passed"
    except Bound as error:
        report.update(status="Unknown", reason=str(error))
    except (Invalid, KeyError, ValueError, OSError, ZeroDivisionError) as error:
        report.update(status="Invalid", reason=f"{type(error).__name__}: {error}")
    finally:
        report["cost"] = {
            "wall_seconds_before_serialization": time.perf_counter() - run.started,
            "checks": len(run.checks),
            "nodes": run.nodes,
            "child_processes": 1 if report.get("external_replay") else 0,
            "subprocesses_beyond_replay": 0,
        }
        report["check_names"] = run.checks
        report["residuals"] = [
            "No native Adva, Rust or Lisp operation, type or builtin is created.",
            "The replay reproduces a supplied implementation; it is not an independent oracle.",
            "The plates and the captured PDF are pinned and structurally described, never read as geometry.",
            "No general receipt calculus and no general field-translation theorem is established.",
            "The sphere-sampling generator, the Penrose patch matching and the Borromean link certificate were not executed.",
        ]
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
