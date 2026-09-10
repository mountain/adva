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
CONTRACT_V1_PATH = "experiments/golden_ratio/contract-v1.json"
REVIEW_PATH = "docs/research/golden-ratio-receiving-review.md"
RECEIPT_CONTRACT_PATH = "docs/terminology/golden-ratio-receipt-v0.json"

BUDGET = {
    "max_seconds": 30.0,
    "cpu_seconds": 25,
    "address_space_bytes": 268435456,
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
    """Translation component of the word as an exact Laurent polynomial in t.

    Multipliers are monomials, so composition stays exact: the translation is a
    dictionary from exponent to integer coefficient. Equal counts of a and A
    restore multiplier one; they do not in general remove negative powers from
    the translation, which is why both the nine-letter word and a two-letter
    control are checked. Only the translation component is returned. This is an
    external research routine: it is not a Rust witness or a general calculator.
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


def pdf_metadata(blob: bytes) -> dict:
    """Read the title and creation date out of the PDF's information dictionary.

    This is a byte probe of the uncompressed trailer object, not a PDF parser:
    it establishes that the declared metadata really is in the staged bytes, and
    nothing about the document's structure or content.
    """

    def between(tag: bytes) -> str | None:
        start = blob.find(tag)
        if start < 0:
            return None
        end = blob.find(b")", start)
        if end < 0:
            return None
        return blob[start + len(tag):end].decode("latin-1")

    return {"title": between(b"/Title ("), "creation_date": between(b"/CreationDate (")}


def install_limits(run: Run) -> dict:
    """Attempt the declared process limits and record what actually happened.

    A recorded refusal is not enforcement: where the platform refuses to install
    a limit, the caller owns that bound and the evidence says so.
    """
    import resource as resource_module

    outcome: dict = {"installed": {}, "refused": {}}
    for name, limit, value in (
        ("cpu_seconds", resource_module.RLIMIT_CPU, BUDGET["cpu_seconds"]),
        ("address_space_bytes", resource_module.RLIMIT_AS, BUDGET["address_space_bytes"]),
    ):
        try:
            resource_module.setrlimit(limit, (value, value))
            outcome["installed"][name] = value
        except (ValueError, OSError) as error:
            outcome["refused"][name] = f"{type(error).__name__}: {error}"[:160]
    run.check("limits-attempted", len(outcome["installed"]) + len(outcome["refused"]) == 2)
    run.check(
        "limits-not-overclaimed",
        all(
            name not in outcome["refused"]
            for name in outcome["installed"]
        )
        and set(outcome["installed"]).isdisjoint(outcome["refused"]),
    )
    return outcome


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
            metadata = pdf_metadata(blob)
            run.check(f"artifact-pdf-header::{relative}", blob[:8] == b"%PDF-1.4")
            run.check(f"artifact-pdf-revision::{relative}", blob.find(b"oldid=1370346489") >= 0)
            run.check(f"artifact-pdf-trailer::{relative}", blob.rstrip().endswith(b"%%EOF"))
            run.check(
                f"artifact-pdf-title-parsed::{relative}",
                metadata["title"] == declared.get("title"),
            )
            run.check(
                f"artifact-pdf-creation-parsed::{relative}",
                metadata["creation_date"] == declared.get("creation_date"),
            )
            pdf_probe = {
                "staged_path": relative,
                "bytes": len(blob),
                "declared_title": declared.get("title"),
                "declared_creation_date": declared.get("creation_date"),
                "parsed_title": metadata["title"],
                "parsed_creation_date": metadata["creation_date"],
                "metadata_source": "parsed from the staged bytes during this run",
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

    # The encoding is a rational pair, not an integer pair: this element is in
    # the field and outside the integer ring.
    fractional = (rational(2) + PHI) / rational(5)
    run.check("field-fractional-coefficient", fractional * rational(5) == rational(2) + PHI)
    run.check("field-fractional-not-in-integer-ring", not fractional.in_integer_ring())
    run.check(
        "field-rational-pair-required",
        fractional.p.denominator != 1 or fractional.q.denominator != 1,
    )

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

    # The guard is real: the bound is stated for n >= 2 because it fails at n = 1.
    run.check("near-integer-bound-guard", HALF < PHI ** -1 and ZERO < PHI ** -1)


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
    # Balanced ratio letters do not by themselves clear negative powers: the
    # nine-letter word has none, and a two-letter control has one.
    run.check("word-translation-has-no-negative-power", min(polynomial) >= 0)
    run.check("word-translation-negative-power-control", word_residual_polynomial("Ab") == {-1: 1})
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


def icosahedron_vertices() -> list[tuple[K, K, K]]:
    """The twelve vertices are the cyclic arrangements of (0, +/-1, +/-phi)."""
    vertices = []
    for first in (-1, 1):
        for second in (-1, 1):
            vertices.append((ZERO, rational(first), rational(second) * PHI))
            vertices.append((rational(first), rational(second) * PHI, ZERO))
            vertices.append((rational(second) * PHI, ZERO, rational(first)))
    return vertices


def icosahedron_checks(run: Run) -> dict:
    vertices = icosahedron_vertices()
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


def rectangle_corners(rectangle: dict) -> list[tuple[K, K, K]]:
    fixed = rectangle["fixed"]
    axes = [axis for axis in range(3) if axis != fixed]
    corners = []
    for first in (-1, 1):
        for second in (-1, 1):
            point = list(rectangle["center"])
            point[fixed] = rectangle["value"]
            point[axes[0]] = point[axes[0]] + rational(first) * rectangle["extents"][axes[0]]
            point[axes[1]] = point[axes[1]] + rational(second) * rectangle["extents"][axes[1]]
            corners.append(tuple(point))
    return corners


def rectangle_segments(rectangle: dict) -> list[tuple[tuple[K, K, K], tuple[K, K, K]]]:
    fixed = rectangle["fixed"]
    axes = [axis for axis in range(3) if axis != fixed]
    corners = rectangle_corners(rectangle)
    segments = []
    for axis in axes:
        for sign in (-1, 1):
            target = rectangle["center"][axis] + rational(sign) * rectangle["extents"][axis]
            chosen = [point for point in corners if point[axis] == target]
            if len(chosen) != 2:
                raise Invalid("a rectangle edge must join exactly two of its corners")
            segments.append((chosen[0], chosen[1]))
    return segments


def boundary_on_line(first: dict, second: dict) -> tuple[list[K], list[tuple[K, K]]]:
    """Where the first boundary meets the intersection line of the two planes.

    Each rectangle lies in its own coordinate plane, so any point shared by the
    two boundaries lies on the line where those planes meet. The candidates are
    therefore the crossings of that line by the first rectangle's four edges,
    plus a closed interval for any edge that lies inside the second plane.
    """
    if first["fixed"] == second["fixed"]:
        raise Invalid("boundary comparison needs two different coordinate planes")
    along = 3 - first["fixed"] - second["fixed"]
    value = second["value"]
    points: list[K] = []
    intervals: list[tuple[K, K]] = []
    for start, end in rectangle_segments(first):
        low, high = start[second["fixed"]], end[second["fixed"]]
        if low == high:
            if low == value:
                first_along, second_along = start[along], end[along]
                intervals.append((min(first_along, second_along), max(first_along, second_along)))
            continue
        parameter = (value - low) / (high - low)
        if ZERO <= parameter <= ONE:
            point = tuple(
                coordinate + parameter * (end_coordinate - coordinate)
                for coordinate, end_coordinate in zip(start, end)
            )
            points.append(point[along])
    return points, intervals


def boundaries_meet(first: dict, second: dict) -> bool:
    """Exact meeting test for two rectangle boundaries in perpendicular planes."""
    first_points, first_intervals = boundary_on_line(first, second)
    second_points, second_intervals = boundary_on_line(second, first)
    if any(a == b for a in first_points for b in second_points):
        return True
    if any(low <= point <= high for low, high in first_intervals for point in second_points):
        return True
    if any(low <= point <= high for low, high in second_intervals for point in first_points):
        return True
    return any(
        low <= other_high and other_low <= high
        for low, high in first_intervals
        for other_low, other_high in second_intervals
    )


def oriented_boundary(rectangle: dict) -> list[tuple[tuple, tuple]]:
    """The four edges in one consistent cyclic traversal.

    The corner enumeration used elsewhere is not a traversal, and an
    inconsistent one makes a signed crossing count meaningless, so the cycle is
    built explicitly as (+,+), (+,-), (-,-), (-,+) on the two free axes.
    """
    fixed = rectangle["fixed"]
    axes = [axis for axis in range(3) if axis != fixed]
    corners = []
    for first, second in ((1, 1), (1, -1), (-1, -1), (-1, 1)):
        point = list(rectangle["center"])
        point[fixed] = rectangle["value"]
        point[axes[0]] = (
            rectangle["center"][axes[0]] + rational(first) * rectangle["extents"][axes[0]]
        )
        point[axes[1]] = (
            rectangle["center"][axes[1]] + rational(second) * rectangle["extents"][axes[1]]
        )
        corners.append(tuple(point))
    return [(corners[step], corners[(step + 1) % 4]) for step in range(4)]


def linking_number(disk: dict, curve: dict) -> tuple[int, int]:
    """Signed crossings of one boundary with a spanning disk of the other.

    The disk is the filled rectangle, whose normal is the positive coordinate
    axis, and the curve is traversed by oriented_boundary. A curve disjoint from
    the disk is unlinked from its boundary, so an empty count is a certificate
    and not a default; the crossing count is returned beside the signed sum so
    that a cancellation cannot be mistaken for an empty intersection.
    """
    plane_axis = disk["fixed"]
    value = disk["value"]
    crossings = 0
    total = 0
    for start, end in oriented_boundary(curve):
        low, high = start[plane_axis], end[plane_axis]
        if low == high:
            continue
        parameter = (value - low) / (high - low)
        if not (ZERO <= parameter <= ONE):
            continue
        point = tuple(
            coordinate + parameter * (other - coordinate)
            for coordinate, other in zip(start, end)
        )
        inside = True
        for axis in range(3):
            if axis == plane_axis:
                continue
            offset = point[axis] - disk["center"][axis]
            size = offset if offset.sign() >= 0 else -offset
            if not size <= disk["extents"][axis]:
                inside = False
                break
        if not inside:
            continue
        crossings += 1
        total += (high - low).sign()
    return total, crossings


def golden_rectangle_checks(run: Run) -> dict:
    """Filled sets meet, boundaries do not: the figure's combinatorial content."""
    rectangles = {
        "z0": {"fixed": 2, "value": ZERO, "center": (ZERO, ZERO, ZERO), "extents": {0: ONE, 1: PHI}},
        "x0": {"fixed": 0, "value": ZERO, "center": (ZERO, ZERO, ZERO), "extents": {1: ONE, 2: PHI}},
        "y0": {"fixed": 1, "value": ZERO, "center": (ZERO, ZERO, ZERO), "extents": {2: ONE, 0: PHI}},
    }
    corners: set = set()
    for rectangle in rectangles.values():
        corners.update(rectangle_corners(rectangle))
    run.check("golden-rectangles-twelve-corners", len(corners) == 12)
    run.check("golden-rectangles-corners-are-the-vertices", corners == set(icosahedron_vertices()))
    run.check(
        "golden-rectangles-ratio",
        all(
            max(rectangle["extents"].values()) == PHI * min(rectangle["extents"].values())
            for rectangle in rectangles.values()
        ),
    )

    def inside(rectangle: dict, point: tuple[K, K, K], strict: bool) -> bool:
        if point[rectangle["fixed"]] != rectangle["value"]:
            return False
        for axis in range(3):
            if axis == rectangle["fixed"]:
                continue
            offset = point[axis] - rectangle["center"][axis]
            size = offset if offset.sign() >= 0 else -offset
            if strict:
                if not size < rectangle["extents"][axis]:
                    return False
            elif not size <= rectangle["extents"][axis]:
                return False
        return True

    origin = (ZERO, ZERO, ZERO)
    run.check(
        "golden-rectangles-filled-sets-meet",
        all(inside(rectangle, origin, True) for rectangle in rectangles.values()),
    )

    pairs = (("z0", "x0"), ("z0", "y0"), ("x0", "y0"))
    for first, second in pairs:
        run.tick()
        run.check(
            f"golden-rectangles-boundaries-disjoint::{first}::{second}",
            not boundaries_meet(rectangles[first], rectangles[second]),
        )

    # Controls: the same test must detect a meeting, and must not report one for
    # a nearby copy whose crossings fall at the other golden half-extent.
    translated_x = {
        "fixed": 0,
        "value": ONE,
        "center": (ONE, ZERO, ZERO),
        "extents": {1: ONE, 2: PHI},
    }
    translated_y = {
        "fixed": 2,
        "value": ZERO,
        "center": (ZERO, ONE, ZERO),
        "extents": {0: ONE, 1: PHI},
    }
    run.check(
        "golden-rectangles-control-translated-meets",
        boundaries_meet(rectangles["z0"], translated_x),
    )
    run.check(
        "golden-rectangles-control-nearby-misses",
        not boundaries_meet(rectangles["y0"], translated_y),
    )
    # Pairwise linking numbers. Disjoint boundaries are not yet unlinked
    # curves: the linking number is a separate judgment, computed here as the
    # signed count of one boundary's crossings with a spanning disk of the
    # other, in both directions.
    linking = {}
    for first, second in pairs:
        forward = linking_number(rectangles[first], rectangles[second])
        backward = linking_number(rectangles[second], rectangles[first])
        run.check(f"linking-zero::{first}::{second}", forward[0] == 0 and backward[0] == 0)
        run.check(f"linking-agrees::{first}::{second}", abs(forward[0]) == abs(backward[0]))
        run.check(f"linking-accounted::{first}::{second}", forward[1] + backward[1] >= 2)
        linking[f"{first}|{second}"] = {
            "forward_crossings": forward[1],
            "forward_sum": forward[0],
            "backward_crossings": backward[1],
            "backward_sum": backward[0],
        }
    # Control: a ring threaded once through a spanning disk must be counted as
    # linked, so a table of zeros cannot be an artefact of the test.
    threaded = {
        "fixed": 0,
        "value": ZERO,
        "center": (ZERO, rational(Fraction(5, 2)), ZERO),
        "extents": {1: ONE, 2: rational(2)},
    }
    signed, count = linking_number(rectangles["z0"], threaded)
    run.check("linking-control-threaded-once", count == 1 and abs(signed) == 1)

    return {
        "rectangles": sorted(rectangles),
        "corners": len(corners),
        "boundary_segments_each": 4,
        "boundary_pairs_checked": len(pairs),
        "filled_intersection": "the origin, interior to all three",
        "boundary_intersection": "empty for every pair",
        "controls": {"translated_copy_meets": True, "nearby_copy_misses": True},
        "linking_numbers": linking,
        "linking_control": {"crossings": count, "signed_sum": signed},
        "link_certificate": borromean_checks(run, rectangles),
    }


def heron_sixteen_area_squared(sides: tuple[K, K, K]) -> K:
    """16 * area^2 by Heron's identity, exactly, without a square root."""
    first, second, third = sides
    return (
        (first + second + third)
        * (-first + second + third)
        * (first - second + third)
        * (first + second - third)
    )


def golden_triangle_checks(run: Run) -> dict:
    """The golden triangle, its gnomon, and the exact self-similar subdivision."""
    # cos 36 is verified, not assumed: it is the root of the Chebyshev relation
    # cos(5x) = -1 inside the admissible range.
    cos36 = PHI / rational(2)
    cos72 = (PHI - ONE) / rational(2)
    run.check("cos36-in-range", ZERO < cos36 and cos36 < ONE)
    run.check(
        "cos36-chebyshev-root",
        rational(16) * cos36 ** 5 - rational(20) * cos36 ** 3 + rational(5) * cos36 + ONE == ZERO,
    )
    run.check("cos72-double-angle", cos72 == rational(2) * cos36 * cos36 - ONE)
    run.check("cos72-closed-form", cos72 == ONE / (rational(2) * PHI))

    # Golden triangle: legs phi, base 1. Angles are identified by the cosine law,
    # which stays inside the field where a sine would not.
    leg, base = PHI, ONE
    run.check(
        "golden-triangle-apex-cosine",
        (leg * leg + leg * leg - base * base) / (rational(2) * leg * leg) == cos36,
    )
    run.check(
        "golden-triangle-base-cosine",
        (leg * leg + base * base - leg * leg) / (rational(2) * leg * base) == cos72,
    )

    # Bisecting a base angle cuts the opposite leg into 1/phi and 1.
    far, near = PHI.inverse(), ONE
    run.check("subdivision-splits-the-leg", far + near == leg)
    # Tile ACD: sides AC = phi, CD = 1 and AD by the cosine law at C = 36 degrees.
    ad_squared = leg * leg + near * near - rational(2) * leg * near * cos36
    run.check("subdivision-third-side", ad_squared == ONE)
    ad = ONE

    gnomon = tuple(sorted((leg, near, ad)))
    run.check("gnomon-is-1-1-phi", gnomon == (ONE, ONE, PHI))
    run.check(
        "gnomon-apex-cosine",
        (gnomon[0] * gnomon[0] + gnomon[1] * gnomon[1] - gnomon[2] * gnomon[2])
        / (rational(2) * gnomon[0] * gnomon[1])
        == -cos72,
    )
    smaller = tuple(sorted((base, ad, far)))
    run.check("smaller-tile-is-1-1-phi-inverse", smaller == (PHI.inverse(), ONE, ONE))
    run.check(
        "smaller-tile-apex-cosine",
        (smaller[1] * smaller[1] + smaller[2] * smaller[2] - smaller[0] * smaller[0])
        / (rational(2) * smaller[1] * smaller[2])
        == cos36,
    )

    # Similarity: the smaller tile is the original scaled by 1/phi.
    original_sides = tuple(sorted((base, leg, leg)))
    run.check(
        "subdivision-self-similar",
        all(
            larger == PHI * piece
            for larger, piece in zip(reversed(original_sides), reversed(smaller))
        ),
    )
    whole = heron_sixteen_area_squared(original_sides)
    part_small = heron_sixteen_area_squared(smaller)
    part_gnomon = heron_sixteen_area_squared(gnomon)
    run.check(
        "subdivision-areas-positive", ZERO < whole and ZERO < part_small and ZERO < part_gnomon
    )
    run.check("subdivision-area-ratio-copy", part_small * PHI ** 4 == whole)
    run.check("subdivision-area-ratio-gnomon", part_gnomon * PHI ** 2 == whole)
    return {
        "tiles": {"golden-triangle": "1 : phi : phi", "golden-gnomon": "1 : 1 : phi"},
        "subdivision": "one golden triangle -> one copy at scale 1/phi plus one gnomon",
        "cos36": cos36.pair(),
        "cos72": cos72.pair(),
    }


def vector_dot(first: tuple, second: tuple) -> K:
    total = ZERO
    for a, b in zip(first, second):
        total = total + a * b
    return total


def vector_cross(first: tuple, second: tuple) -> tuple:
    return (
        first[1] * second[2] - first[2] * second[1],
        first[2] * second[0] - first[0] * second[2],
        first[0] * second[1] - first[1] * second[0],
    )


def squared_distance(first: tuple, second: tuple) -> K:
    total = ZERO
    for a, b in zip(first, second):
        total = total + (a - b) * (a - b)
    return total


def dodecahedron_checks(run: Run) -> dict:
    """The dual dodecahedron, its two spheres, and the inscribed cube."""
    vertices = icosahedron_vertices()
    edges = {
        (i, j)
        for i in range(12)
        for j in range(i + 1, 12)
        if squared_distance(vertices[i], vertices[j]) == rational(4)
    }
    faces = [
        (i, j, k)
        for i in range(12)
        for j in range(i + 1, 12)
        for k in range(j + 1, 12)
        if (i, j) in edges and (i, k) in edges and (j, k) in edges
    ]
    run.check("dual-face-count", len(faces) == 20)

    centroids = []
    for i, j, k in faces:
        total = tuple(
            vertices[i][axis] + vertices[j][axis] + vertices[k][axis] for axis in range(3)
        )
        centroids.append(tuple(coordinate / rational(3) for coordinate in total))
    run.check("dual-twenty-vertices", len(set(centroids)) == 20)

    radii = {vector_dot(centroid, centroid) for centroid in centroids}
    run.check("dual-equal-radius", len(radii) == 1)
    inradius_squared = next(iter(radii))
    run.check(
        "inradius-closed-form",
        inradius_squared == (rational(7) + rational(3) * SQRT5) / rational(6),
    )
    circumradius_squared = vector_dot(vertices[0], vertices[0])
    run.check(
        "circumradius-closed-form",
        circumradius_squared == (rational(5) + SQRT5) / rational(2),
    )
    run.check("circumradius-phi-form", circumradius_squared == PHI ** 2 + ONE)
    run.check(
        "sphere-ratio-closed-form",
        circumradius_squared / inradius_squared == rational(15) - rational(6) * SQRT5,
    )

    # The centroid is the foot of the perpendicular: its squared norm equals the
    # squared distance from the origin to the face plane, computed independently.
    for index, face in enumerate(faces):
        run.tick()
        first, second, third = (vertices[vertex] for vertex in face)
        first_edge = tuple(b - a for a, b in zip(second, first))
        second_edge = tuple(c - a for a, c in zip(third, first))
        normal = vector_cross(first_edge, second_edge)
        plane_squared = vector_dot(first, normal) ** 2 / vector_dot(normal, normal)
        run.check(f"face-plane-distance::{index}", plane_squared == inradius_squared)

    face_of_edge: dict = {}
    for index, face in enumerate(faces):
        for i in range(3):
            for j in range(i + 1, 3):
                key = tuple(sorted((face[i], face[j])))
                face_of_edge.setdefault(key, []).append(index)
    run.check(
        "dual-edge-source",
        len(face_of_edge) == 30 and all(len(owners) == 2 for owners in face_of_edge.values()),
    )
    dual_edges = {tuple(sorted(owners)) for owners in face_of_edge.values()}
    run.check("dual-thirty-edges", len(dual_edges) == 30)
    run.check(
        "dual-degree-three",
        all(sum(index in edge for edge in dual_edges) == 3 for index in range(20)),
    )
    run.check(
        "dual-equal-edge-length",
        len({squared_distance(centroids[i], centroids[j]) for i, j in dual_edges}) == 1,
    )

    pentagons = []
    for vertex in range(12):
        around = [index for index, face in enumerate(faces) if vertex in face]
        run.check(f"pentagon-arity::{vertex}", len(around) == 5)
        # The five faces around a vertex form a 5-cycle in the dual graph. The
        # collected order is by face index, so the induced degree is what is
        # checked, not the order of the list.
        induced = [
            tuple(sorted((first, second)))
            for position, first in enumerate(around)
            for second in around[position + 1:]
            if tuple(sorted((first, second))) in dual_edges
        ]
        run.check(
            f"pentagon-cycle::{vertex}",
            len(induced) == 5
            and all(
                sum(index in edge for edge in induced) == 2 for index in around
            ),
        )
        pentagons.append(around)
    run.check("dual-twelve-faces", len({frozenset(pentagon) for pentagon in pentagons}) == 12)

    # Each face is a regular pentagon: five equal sides, five equal diagonals,
    # and the diagonal-to-side ratio phi. The cyclic order is reconstructed from
    # the induced 5-cycle, so no enumeration order is assumed.
    dual_edge_lengths = {
        squared_distance(centroids[i], centroids[j]) for i, j in dual_edges
    }
    side_squared = next(iter(dual_edge_lengths))
    run.check(
        "dual-edge-closed-form",
        side_squared == rational(2) * (rational(3) + SQRT5) / rational(9),
    )
    run.check(
        "dual-circumradius-over-edge",
        inradius_squared / side_squared == (rational(9) + rational(3) * SQRT5) / rational(8),
    )
    for vertex, around in enumerate(pentagons):
        run.tick()
        induced = {
            tuple(sorted((first, second)))
            for position, first in enumerate(around)
            for second in around[position + 1:]
            if tuple(sorted((first, second))) in dual_edges
        }
        order = [around[0]]
        previous = None
        while len(order) < 5:
            following = next(
                other
                for edge in induced
                if order[-1] in edge
                for other in edge
                if other != order[-1] and other != previous
            )
            order.append(following)
            previous = order[-2]
        sides = [tuple(sorted((order[step], order[(step + 1) % 5]))) for step in range(5)]
        diagonals = [
            tuple(sorted((around[first], around[second])))
            for first in range(5)
            for second in range(first + 1, 5)
            if tuple(sorted((around[first], around[second]))) not in induced
        ]
        run.check(f"pentagon-five-sides::{vertex}", len(set(sides)) == 5 and len(diagonals) == 5)
        run.check(
            f"pentagon-regular::{vertex}",
            {squared_distance(centroids[i], centroids[j]) for i, j in sides} == {side_squared}
            and len(
                {squared_distance(centroids[i], centroids[j]) for i, j in diagonals}
            )
            == 1,
        )
        diagonal_squared = squared_distance(centroids[diagonals[0][0]], centroids[diagonals[0][1]])
        run.check(
            f"pentagon-diagonal-ratio::{vertex}",
            diagonal_squared == PHI ** 2 * side_squared,
        )

    # Inscribed cube: eight of the twenty vertices whose squared distances take
    # exactly the cube spectrum a^2, 2a^2, 3a^2 with multiplicities 3, 3, 1.
    # Inscribed cube. A cube vertex has one body-diagonal partner, three edge
    # neighbours and three face-diagonal neighbours, so a cube is determined by
    # any vertex and its body-diagonal partner.
    # The cube edge is the pentagon diagonal, so its square is phi^2 * side^2.
    cube_edge_squared = PHI ** 2 * side_squared
    cube = None
    for first in range(20):
        run.tick()
        partners = [
            other
            for other in range(20)
            if other != first
            and squared_distance(centroids[first], centroids[other])
            == rational(3) * cube_edge_squared
        ]
        # Two inscribed cubes share a body diagonal, so the partner is unique.
        run.check(f"cube-body-diagonal-partners::{first}", len(partners) == 1)
        for second in partners:
            # Three corner neighbours of a cube vertex are mutually a face
            # diagonal apart; the remaining four follow from that triple.
            near = [
                other
                for other in range(20)
                if other not in (first, second)
                and squared_distance(centroids[first], centroids[other]) == cube_edge_squared
                and squared_distance(centroids[second], centroids[other])
                == rational(2) * cube_edge_squared
            ]
            for i in range(len(near)):
                for j in range(i + 1, len(near)):
                    for k in range(j + 1, len(near)):
                        triple = [near[i], near[j], near[k]]
                        if not all(
                            squared_distance(centroids[a], centroids[b])
                            == rational(2) * cube_edge_squared
                            for position, a in enumerate(triple)
                            for b in triple[position + 1:]
                        ):
                            continue
                        rest = [
                            other
                            for other in range(20)
                            if other not in (first, second, *triple)
                            and sum(
                                squared_distance(centroids[member], centroids[other])
                                == cube_edge_squared
                                for member in triple
                            )
                            == 2
                        ]
                        chosen = [first, second, *triple, *rest]
                        if len(chosen) != 8:
                            continue
                        profile = sorted(
                            squared_distance(centroids[a], centroids[b])
                            for a in chosen
                            for b in chosen
                            if a < b
                        )
                        if profile == sorted(
                            [cube_edge_squared] * 12
                            + [rational(2) * cube_edge_squared] * 12
                            + [rational(3) * cube_edge_squared] * 4
                        ):
                            cube = chosen
                            break
                    if cube:
                        break
                if cube:
                    break
            if cube:
                break
        if cube:
            break
    run.check("cube-eight-vertices", cube is not None and len(cube) == 8)
    cube_edges = {
        (i, j)
        for i in cube
        for j in cube
        if i < j and squared_distance(centroids[i], centroids[j]) == cube_edge_squared
    }
    run.check("cube-twelve-edges", len(cube_edges) == 12)
    run.check(
        "cube-degree-three",
        all(sum(index in edge for edge in cube_edges) == 3 for index in cube),
    )
    run.check("cube-edges-are-not-dodecahedron-edges", cube_edges.isdisjoint(dual_edges))
    for first, second in sorted(cube_edges):
        containing = [
            pentagon for pentagon in pentagons if set(pentagon) >= {first, second}
        ]
        run.check("cube-edge-in-exactly-one-pentagon", len(containing) == 1)
        run.check(
            "cube-edge-is-a-pentagon-diagonal",
            len(containing) == 1
            and all(
                tuple(sorted((index, other))) not in dual_edges
                for pentagon in containing
                for index in pentagon
                for other in pentagon
                if index != other and {index, other} == {first, second}
            ),
        )
    # The dual of the inscribed cube: its six face centres form a regular
    # octahedron, and a cube face is a four-subset whose induced edges form a
    # square.
    cube_faces = []
    for first in range(8):
        for second in range(first + 1, 8):
            for third in range(second + 1, 8):
                for fourth in range(third + 1, 8):
                    face = [cube[first], cube[second], cube[third], cube[fourth]]
                    induced = [
                        (a, b)
                        for position, a in enumerate(face)
                        for b in face[position + 1:]
                        if squared_distance(centroids[a], centroids[b]) == cube_edge_squared
                    ]
                    if len(induced) == 4 and all(
                        sum(node in edge for edge in induced) == 2 for node in face
                    ):
                        cube_faces.append(face)
    run.check("octahedron-six-cube-faces", len(cube_faces) == 6)
    octahedron = [
        tuple(
            sum((centroids[index][axis] for index in face), ZERO) / rational(4)
            for axis in range(3)
        )
        for face in cube_faces
    ]
    run.check("octahedron-six-vertices", len(set(octahedron)) == 6)
    run.check(
        "octahedron-equal-radius",
        len({vector_dot(point, point) for point in octahedron}) == 1,
    )
    octahedron_edge_squared = cube_edge_squared / rational(2)
    octahedron_edges = {
        (i, j)
        for i in range(6)
        for j in range(i + 1, 6)
        if squared_distance(octahedron[i], octahedron[j]) == octahedron_edge_squared
    }
    run.check("octahedron-twelve-edges", len(octahedron_edges) == 12)
    run.check(
        "octahedron-degree-four",
        all(sum(index in edge for edge in octahedron_edges) == 4 for index in range(6)),
    )
    run.check(
        "octahedron-eight-triangular-faces",
        len(
            [
                (i, j, k)
                for i in range(6)
                for j in range(i + 1, 6)
                for k in range(j + 1, 6)
                if (i, j) in octahedron_edges
                and (i, k) in octahedron_edges
                and (j, k) in octahedron_edges
            ]
        )
        == 8,
    )
    run.check(
        "octahedron-dual-of-the-cube",
        all(
            sum(
                squared_distance(octahedron[index], centroids[vertex])
                == octahedron_edge_squared
                for index in range(6)
            )
            == 3
            for vertex in cube
        ),
    )

    # No octahedron has all six vertices among the twelve icosahedron vertices:
    # the compound of five octahedra lives on the thirty edge midpoints instead.
    octahedra_on_vertices = 0
    for a in range(12):
        for b in range(a + 1, 12):
            for c in range(b + 1, 12):
                for d in range(c + 1, 12):
                    for e in range(d + 1, 12):
                        for f in range(e + 1, 12):
                            run.tick()
                            chosen = (a, b, c, d, e, f)
                            pairs_of: dict = {}
                            for position, i in enumerate(chosen):
                                for j in chosen[position + 1:]:
                                    value = squared_distance(vertices[i], vertices[j])
                                    pairs_of[value] = pairs_of.get(value, 0) + 1
                            if sorted(pairs_of.values()) == [3, 12]:
                                octahedra_on_vertices += 1
    run.check("octahedron-none-on-icosahedron-vertices", octahedra_on_vertices == 0)

    return {
        "vertices": 20,
        "edges": 30,
        "faces": 12,
        "inradius_squared": inradius_squared.pair(),
        "circumradius_squared": circumradius_squared.pair(),
        "dual_edge_squared": side_squared.pair(),
        "cube_edge_squared": cube_edge_squared.pair(),
        "inscribed_cube_vertices": len(cube) if cube else 0,
        "inscribed_cube_relation": "cube edges are pentagon diagonals, not dodecahedron edges",
        "inscribed_octahedron": "the dual of the inscribed cube, its six face centres",
        "octahedra_on_icosahedron_vertices": octahedra_on_vertices,
    }


def golden_angle_checks(run: Run) -> dict:
    """The golden angle as a fraction of a turn, exactly.

    Only the combinatorial content is checked: the gap structure of the finite
    rotation set and the equal-area latitude rule. No minimal-distance, energy
    or coverage optimality is asserted, and no transcendental value is evaluated.
    """
    alpha = PHI ** -2
    run.check("golden-angle-in-range", ZERO < alpha and alpha < ONE)
    run.check("golden-angle-complement", alpha + PHI.inverse() == ONE)

    fib = fibonacci(14)
    structures = {}
    for index in (5, 9, 13):
        count = fib[index]
        points = []
        for n in range(count):
            run.tick()
            point = rational(n) * alpha
            whole = rational(n)
            while point < whole:
                whole = whole - ONE
            points.append(point - whole)
        points.sort()
        gaps = [points[step + 1] - points[step] for step in range(count - 1)]
        gaps.append(points[0] + ONE - points[-1])
        lengths = sorted(set(gaps))
        run.check(f"golden-angle-two-gaps::{count}", len(lengths) == 2)
        run.check(
            f"golden-angle-gap-ratio::{count}",
            lengths[1] == PHI * lengths[0],
        )
        run.check(
            f"golden-angle-gap-partition::{count}",
            sum(
                (gap for gap in gaps),
                ZERO,
            )
            == ONE,
        )
        structures[str(count)] = {
            "short_gap": lengths[0].pair(),
            "long_gap": lengths[1].pair(),
            "short_count": gaps.count(lengths[0]),
            "long_count": gaps.count(lengths[1]),
        }

    for divisor in (8, 13, 21):
        bands = [ONE - rational(2 * n + 1) / rational(divisor) for n in range(divisor)]
        differences = {bands[step] - bands[step + 1] for step in range(divisor - 1)}
        run.check(
            f"golden-angle-equal-bands::{divisor}",
            len(differences) == 1
            and next(iter(differences)) == rational(2) / rational(divisor),
        )
    return {
        "alpha": alpha.pair(),
        "rotation_structures": structures,
        "latitude_rule": "equal z steps give equal band areas",
        "not_asserted": "minimal separation, energy or coverage optimality",
    }


def penrose_checks(run: Run) -> dict:
    """The two Penrose prototiles and their inflation, without sine values.

    The rhombus angles are multiples of 36 degrees whose cosines lie in the
    field while their sines do not, so every statement below uses cosine values,
    squared diagonal ratios and integer counts. Matching-rule acceptance,
    aperiodicity and any full-plane tiling are not verified here.
    """
    cos36 = PHI / rational(2)
    cos72 = rational(2) * cos36 * cos36 - ONE
    run.check("penrose-cos72-closed-form", cos72 == (PHI - ONE) / rational(2))
    run.check("penrose-cos144-from-cos72", rational(2) * cos72 * cos72 - ONE == -cos36)
    run.check("penrose-cos36-chebyshev", rational(16) * cos36 ** 5 - rational(20) * cos36 ** 3 + rational(5) * cos36 + ONE == ZERO)

    # A rhombus with acute angle theta and side s has diagonals 2s sin(theta/2)
    # and 2s cos(theta/2), so the squared diagonal ratio is (1 + cos)/(1 - cos).
    def diagonal_ratio_squared(cosine: K) -> K:
        return (ONE + cosine) / (ONE - cosine)

    thick = diagonal_ratio_squared(cos72)
    thin = diagonal_ratio_squared(cos36)
    run.check("penrose-thick-diagonal-ratio-squared", ONE < thick)
    run.check("penrose-thin-diagonal-ratio-squared", ONE < thin)
    # The atlas warns that the golden rhombus is a different family: its
    # diagonal ratio is phi, and neither prototile has that property.
    golden_cosine = PHI / (PHI + rational(2))
    run.check("golden-rhombus-diagonal-ratio", diagonal_ratio_squared(golden_cosine) == PHI ** 2)
    run.check("penrose-thick-is-not-the-golden-rhombus", thick != PHI ** 2)
    run.check("penrose-thin-is-not-the-golden-rhombus", thin != PHI ** 2)
    run.check("golden-cosine-differs", golden_cosine != cos72 and golden_cosine != cos36)

    # Inflation: thick -> 2 thick + 1 thin, thin -> 1 thick + 1 thin.
    matrix = ((2, 1), (1, 1))
    trace = matrix[0][0] + matrix[1][1]
    determinant = matrix[0][0] * matrix[1][1] - matrix[0][1] * matrix[1][0]
    run.check("penrose-inflation-characteristic-polynomial",
              (trace, determinant) == (3, 1)
              and PHI ** 4 - rational(trace) * PHI ** 2 + rational(determinant) == ZERO)
    run.check("penrose-inflation-eigenvalues", PHI ** 2 * PHI ** -2 == ONE
              and PHI ** 2 + PHI ** -2 == rational(trace))
    fib = fibonacci(14)
    counts = (1, 0)
    totals = [1]
    for step in range(1, 7):
        run.tick()
        counts = (
            matrix[0][0] * counts[0] + matrix[0][1] * counts[1],
            matrix[1][0] * counts[0] + matrix[1][1] * counts[1],
        )
        totals.append(counts[0] + counts[1])
        run.check(
            f"penrose-inflation-counts::{step}",
            counts == (fib[2 * step + 1], fib[2 * step]),
        )
    run.check(
        "penrose-inflation-total-recurrence",
        all(
            totals[step + 1] == 3 * totals[step] - totals[step - 1]
            for step in range(1, len(totals) - 1)
        ),
    )
    return {
        "prototiles": {"thick": "72/108", "thin": "36/144"},
        "inflation_matrix": [[2, 1], [1, 1]],
        "counts_after_six_steps": list(counts),
        "shared_polynomial": "t^2 - 3t + 1, which the affine word residual and M^2 also carry",
        "not_verified": "matching-rule acceptance, aperiodicity, full-plane tiling",
    }


def filled_intersection_segment(first: dict, second: dict) -> tuple:
    """The segment where two filled rectangles meet.

    Both lie in coordinate planes, so their intersection is the overlap of two
    intervals along the remaining axis, returned as an ordered endpoint pair.
    """
    along = 3 - first["fixed"] - second["fixed"]
    low = max(
        first["center"][along] - first["extents"][along],
        second["center"][along] - second["extents"][along],
    )
    high = min(
        first["center"][along] + first["extents"][along],
        second["center"][along] + second["extents"][along],
    )
    if high < low:
        return None
    endpoints = []
    for value in (low, high):
        coordinates = [ZERO, ZERO, ZERO]
        coordinates[first["fixed"]] = first["value"]
        coordinates[second["fixed"]] = second["value"]
        coordinates[along] = value
        endpoints.append(tuple(coordinates))
    return tuple(endpoints)


def triple_intersection(first: dict, second: dict, third: dict) -> tuple[int, int]:
    """Signed crossings of the segment (first and second) with the third disk."""
    segment = filled_intersection_segment(first, second)
    if segment is None:
        return 0, 0
    plane_axis = third["fixed"]
    value = third["value"]
    start, end = segment
    low, high = start[plane_axis], end[plane_axis]
    if low == high:
        return 0, 0
    parameter = (value - low) / (high - low)
    if not (ZERO <= parameter <= ONE):
        return 0, 0
    point = tuple(
        coordinate + parameter * (other - coordinate)
        for coordinate, other in zip(start, end)
    )
    inside = True
    for axis in range(3):
        if axis == plane_axis:
            continue
        offset = point[axis] - third["center"][axis]
        size = offset if offset.sign() >= 0 else -offset
        if not size <= third["extents"][axis]:
            inside = False
            break
    if not inside:
        return 0, 0
    return (high - low).sign(), 1


def borromean_checks(run: Run, rectangles: dict) -> dict:
    """The triple linking judgement, with its imported theorem named.

    The fills are disks whose boundaries are the three components, and their
    pairwise linking numbers are zero, so the classical identification of
    Milnor's invariant with the triple intersection number of Seifert surfaces
    applies. That theorem is imported, not re-proved here; what is computed is
    the signed triple intersection itself, in all three cyclic orders.
    """
    names = ("z0", "x0", "y0")
    for name in names:
        rectangle = rectangles[name]
        run.check(
            f"borromean-disk-spans::{name}",
            {tuple(sorted((start, end))) for start, end in rectangle_segments(rectangle)}
            == {tuple(sorted((start, end))) for start, end in oriented_boundary(rectangle)},
        )

    segments = {}
    for first, second in (("z0", "x0"), ("z0", "y0"), ("x0", "y0")):
        segment = filled_intersection_segment(rectangles[first], rectangles[second])
        run.check(f"borromean-pair-segment::{first}::{second}", segment is not None)
        along = 3 - rectangles[first]["fixed"] - rectangles[second]["fixed"]
        for endpoint in segment:
            on_boundary = any(
                endpoint[axis] - rectangles[board]["center"][axis] == rectangles[board]["extents"][axis]
                or endpoint[axis] - rectangles[board]["center"][axis] == -rectangles[board]["extents"][axis]
                for board in (first, second)
                for axis in range(3)
                if axis != rectangles[board]["fixed"]
                and axis != along
            ) or any(
                endpoint[axis] == rectangles[board]["value"]
                for board in (first, second)
                for axis in range(3)
                if axis == rectangles[board]["fixed"]
            )
            run.check(f"borromean-endpoint-on-a-component::{first}::{second}", on_boundary)
        segments[f"{first}|{second}"] = segment

    orders = (("z0", "x0", "y0"), ("x0", "y0", "z0"), ("y0", "z0", "x0"))
    results = {}
    for first, second, third in orders:
        run.tick()
        signed, points = triple_intersection(
            rectangles[first], rectangles[second], rectangles[third]
        )
        run.check(f"borromean-triple-point-count::{first}", points == 1)
        run.check(f"borromean-triple-unit::{first}", abs(signed) == 1)
        results[f"{first},{second},{third}"] = {"signed_sum": signed, "points": points}
    signs = {entry["signed_sum"] for entry in results.values()}
    run.check("borromean-triple-order-consistent", len(signs) == 1)
    return {
        "seifert_surfaces": "the three filled rectangles, boundaries verified against the components",
        "pairwise_linking_numbers": "zero, computed in the previous round",
        "triple_intersection": results,
        "triple_point": "the origin, the single common point of the three disks",
        "identification": "pairwise unlinked with unit triple linking, the Borromean pattern",
        "imported": "the classical theorem identifying the triple intersection number of Seifert surfaces with Milnor's invariant mu-bar(123) when pairwise linking numbers vanish",
        "not_computed": "the invariant itself from the link complement, and any Reidemeister or diagram-level certificate",
        "controls": borromean_control_checks(run, rectangles),
    }


def borromean_control_checks(run: Run, rectangles: dict) -> dict:
    """Controls that make the Borromean judgement falsifiable.

    A positive number means nothing unless the method can also return zero, can
    return the unit again on a fresh instance, and refuses when its pairwise
    hypothesis fails.
    """
    # Control 1: unlink. The third disk is moved clear, so the segment where the
    # first two meet misses it entirely and the judgement must be zero.
    far = dict(rectangles["y0"])
    far["center"] = (rational(3), ZERO, ZERO)
    run.check(
        "borromean-control-unlink-pairwise",
        all(
            linking_number(disk, curve)[0] == 0
            for disk, curve in (
                (rectangles["z0"], far),
                (rectangles["x0"], far),
                (far, rectangles["z0"]),
            )
        ),
    )
    signed, points = triple_intersection(rectangles["z0"], rectangles["x0"], far)
    run.check("borromean-control-unlink-triple-zero", points == 0 and signed == 0)

    # Control 2: a fresh instance of the same pattern, scaled by two. The link
    # type is unchanged, so the judgement must return the unit again.
    scaled = {
        name: {
            "fixed": rectangle["fixed"],
            "value": rectangle["value"],
            "center": tuple(coordinate * rational(2) for coordinate in rectangle["center"]),
            "extents": {
                axis: extent * rational(2) for axis, extent in rectangle["extents"].items()
            },
        }
        for name, rectangle in rectangles.items()
    }
    scaled_signed, scaled_points = triple_intersection(
        scaled["z0"], scaled["x0"], scaled["y0"]
    )
    run.check(
        "borromean-control-scaled-instance",
        scaled_points == 1 and abs(scaled_signed) == 1,
    )

    # Control 3: a configuration whose pairwise linking number does not vanish.
    # The hypothesis of the imported theorem fails, so the run must not report a
    # triple judgement for it.
    threaded = {
        "fixed": 0,
        "value": ZERO,
        "center": (ZERO, rational(Fraction(5, 2)), ZERO),
        "extents": {1: ONE, 2: rational(2)},
    }
    pairwise = [
        linking_number(disk, curve)[0]
        for disk, curve in (
            (rectangles["z0"], threaded),
            (rectangles["x0"], threaded),
            (threaded, rectangles["z0"]),
        )
    ]
    run.check(
        "borromean-control-precondition-fails",
        any(value != 0 for value in pairwise),
    )
    return {
        "unlink": {"pairwise_zero": True, "triple_points": points, "signed": signed},
        "scaled_instance": {"triple_points": scaled_points, "signed": scaled_signed},
        "failing_precondition": {"pairwise_values": pairwise, "judgement": "withheld"},
    }


def projection_basis(direction: tuple) -> tuple:
    """Two vectors spanning the plane perpendicular to a declared direction."""
    unit = None
    for candidate in range(3):
        if direction[candidate] != ZERO:
            axis = [ZERO, ZERO, ZERO]
            axis[candidate] = ONE
            unit = tuple(axis)
            break
    if unit is None:
        raise Invalid("a projection direction needs a non-zero component")
    first = vector_cross(direction, unit)
    if first == (ZERO, ZERO, ZERO):
        raise Invalid("degenerate projection basis")
    second = vector_cross(direction, first)
    return first, second


def projected(point: tuple, basis: tuple) -> tuple:
    return (vector_dot(point, basis[0]), vector_dot(point, basis[1]))


def cross_two(first: tuple, second: tuple) -> K:
    return first[0] * second[1] - first[1] * second[0]


def complement_diagram_checks(run: Run, rectangles: dict) -> dict:
    """A declared regular projection of the three components, exactly.

    Crossings are found by exact orientation signs in the projection plane and
    the over/under strand by the declared direction's coordinate, so nothing here
    is read off a rendering. The pairwise signed sums give the linking numbers by
    the diagram route, independently of the spanning-disk counts of section 4.
    """
    direction = (ONE, PHI, PHI ** 2)
    basis = projection_basis(direction)
    names = ("z0", "x0", "y0")
    segments = []
    for name in names:
        for start, end in oriented_boundary(rectangles[name]):
            segments.append((name, projected(start, basis), projected(end, basis), start, end))

    vertices = [entry[3] for entry in segments] + [entry[4] for entry in segments]
    degenerate = []
    crossings = []
    for index, (first_name, first_start, first_end, first_a, first_b) in enumerate(segments):
        for second_name, second_start, second_end, second_a, second_b in segments[index + 1:]:
            run.tick()
            denominator = cross_two(
                (first_end[0] - first_start[0], first_end[1] - first_start[1]),
                (second_end[0] - second_start[0], second_end[1] - second_start[1]),
            )
            if denominator == ZERO:
                continue
            first_side = cross_two(
                (second_start[0] - first_start[0], second_start[1] - first_start[1]),
                (second_end[0] - second_start[0], second_end[1] - second_start[1]),
            )
            second_side = cross_two(
                (second_start[0] - first_start[0], second_start[1] - first_start[1]),
                (first_end[0] - first_start[0], first_end[1] - first_start[1]),
            )
            first_parameter = first_side / denominator
            second_parameter = second_side / denominator
            if not (ZERO < first_parameter < ONE and ZERO < second_parameter < ONE):
                continue
            first_point = tuple(
                coordinate + first_parameter * (other - coordinate)
                for coordinate, other in zip(first_a, first_b)
            )
            second_point = tuple(
                coordinate + second_parameter * (other - coordinate)
                for coordinate, other in zip(second_a, second_b)
            )
            first_height = vector_dot(first_point, direction)
            second_height = vector_dot(second_point, direction)
            if first_height == second_height:
                degenerate.append((first_name, second_name))
                continue
            over_first = ZERO < first_height - second_height
            direction_first = (first_end[0] - first_start[0], first_end[1] - first_start[1])
            direction_second = (second_end[0] - second_start[0], second_end[1] - second_start[1])
            sign = cross_two(
                direction_first if over_first else direction_second,
                direction_second if over_first else direction_first,
            ).sign()
            crossings.append(
                {
                    "over": first_name if over_first else second_name,
                    "under": second_name if over_first else first_name,
                    "sign": sign,
                    "point": [coordinate.pair() for coordinate in first_point],
                }
            )
    run.check("complement-diagram-generic", not degenerate)
    run.check("complement-diagram-crossings", len(crossings) > 0)
    run.check(
        "complement-diagram-over-under-decided",
        all(entry["over"] != entry["under"] for entry in crossings),
    )

    sums = {}
    for first, second in (("z0", "x0"), ("z0", "y0"), ("x0", "y0")):
        pair = {first, second}
        selected = [entry for entry in crossings if {entry["over"], entry["under"]} == pair]
        sums[f"{first}|{second}"] = {
            "crossings": len(selected),
            "signed_sum": sum(entry["sign"] for entry in selected),
        }
    run.check(
        "complement-diagram-linking-zero",
        all(entry["signed_sum"] == 0 for entry in sums.values()),
    )
    run.check(
        "complement-diagram-crossing-counts",
        all(entry["crossings"] >= 2 for entry in sums.values()),
    )
    return {
        "direction": [coordinate.pair() for coordinate in direction],
        "crossings_total": len(crossings),
        "per_pair": sums,
        "crossings": crossings,
        "note": (
            "the halved signed sum is the pairwise linking number by the diagram route, "
            "whose global sign depends on the declared projection direction"
        ),
    }


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
    run.check("seed-bracket-naming", lower == Fraction(21, 13) and upper == Fraction(13, 8))
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
            "control": "the seeded bracket lower endpoint 21/13 is not the unknown-tail lower image",
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
        # The successor contract is active; the frozen version-zero file stays
        # byte identical and is checked by digest rather than reinterpreted.
        frozen_bytes = (root / CONTRACT_PATH).read_bytes()
        contract_bytes = (root / CONTRACT_V1_PATH).read_bytes()
        contract = json.loads(contract_bytes.decode("utf-8"))
        run.check("contract-version", contract["version"] == 1)
        run.check(
            "contract-supersedes-frozen",
            contract["supersedes"]["sha256"] == hashlib.sha256(frozen_bytes).hexdigest(),
        )
        run.check(
            "contract-frozen-path",
            contract["supersedes"]["path"] == CONTRACT_PATH,
        )
        review_bytes = (root / REVIEW_PATH).read_bytes()
        run.check(
            "review-pinned",
            contract["review"]["sha256"] == hashlib.sha256(review_bytes).hexdigest(),
        )
        report["limits"] = install_limits(run)
        report["contract"] = {
            "path": CONTRACT_V1_PATH,
            "sha256": hashlib.sha256(contract_bytes).hexdigest(),
            "version": contract["version"],
            "supersedes": contract["supersedes"]["path"],
            "supersedes_sha256": contract["supersedes"]["sha256"],
            "review": contract["review"]["path"],
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
        report["golden_rectangles"] = golden_rectangle_checks(run)
        report["golden_triangle"] = golden_triangle_checks(run)
        report["dodecahedron"] = dodecahedron_checks(run)
        report["golden_angle"] = golden_angle_checks(run)
        report["penrose"] = penrose_checks(run)
        report["complement_diagram"] = complement_diagram_checks(run, {
            "z0": {"fixed": 2, "value": ZERO, "center": (ZERO, ZERO, ZERO), "extents": {0: ONE, 1: PHI}},
            "x0": {"fixed": 0, "value": ZERO, "center": (ZERO, ZERO, ZERO), "extents": {1: ONE, 2: PHI}},
            "y0": {"fixed": 1, "value": ZERO, "center": (ZERO, ZERO, ZERO), "extents": {2: ONE, 0: PHI}},
        })
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
            "The rotation set's optimality, the Penrose patch acceptance and the Borromean triple "
            "linking invariant were not established.",
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
