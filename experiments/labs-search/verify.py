#!/usr/bin/env python3
"""Independent standard-library verifier for Adva LABS witnesses.

The verifier deliberately shares no Rust search code. It accepts a complete
run report, an exhaustive report, or a bare witness object, recomputes every
aperiodic autocorrelation and the exact integer energy, and checks the stored
merit factor only as a derived display value.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True, slots=True)
class Evaluation:
    length: int
    correlations: tuple[int, ...]
    energy: int
    merit_factor: float
    sequence_sha256: str


def evaluate_sequence(sequence: list[int]) -> Evaluation:
    if len(sequence) < 2:
        raise ValueError("LABS requires at least two spins")
    if any(type(spin) is not int or spin not in (-1, 1) for spin in sequence):
        raise ValueError("every spin must be exactly -1 or +1")

    correlations = tuple(
        sum(sequence[index] * sequence[index + lag] for index in range(len(sequence) - lag))
        for lag in range(1, len(sequence))
    )
    energy = sum(correlation * correlation for correlation in correlations)
    if energy <= 0:
        raise ValueError("finite LABS witnesses must have positive energy")
    merit_factor = len(sequence) ** 2 / (2 * energy)
    encoded = "".join("+" if spin == 1 else "-" for spin in sequence).encode("ascii")
    return Evaluation(
        length=len(sequence),
        correlations=correlations,
        energy=energy,
        merit_factor=merit_factor,
        sequence_sha256=hashlib.sha256(encoded).hexdigest(),
    )


def extract_witness(payload: dict[str, Any]) -> dict[str, Any]:
    if "best" in payload:
        witness = payload["best"]
    elif "optimum" in payload:
        witness = payload["optimum"]
    else:
        witness = payload
    if not isinstance(witness, dict):
        raise ValueError("witness must be a JSON object")
    return witness


def verify_payload(payload: dict[str, Any]) -> Evaluation:
    witness = extract_witness(payload)
    sequence = witness.get("sequence")
    if not isinstance(sequence, list) or not all(type(value) is int for value in sequence):
        raise ValueError("witness.sequence must be an integer list")

    evaluation = evaluate_sequence(sequence)
    declared_length = witness.get("length")
    if declared_length != evaluation.length:
        raise ValueError(
            f"declared length {declared_length!r} differs from exact length {evaluation.length}"
        )

    declared_correlations = witness.get("correlations")
    if declared_correlations != list(evaluation.correlations):
        raise ValueError("stored autocorrelation vector is not exact")

    declared_energy = witness.get("energy")
    if declared_energy != evaluation.energy:
        raise ValueError(
            f"stored energy {declared_energy!r} differs from exact energy {evaluation.energy}"
        )

    declared_merit = witness.get("merit_factor")
    if not isinstance(declared_merit, (int, float)) or not math.isclose(
        float(declared_merit), evaluation.merit_factor, rel_tol=0.0, abs_tol=1e-12
    ):
        raise ValueError(
            f"stored merit factor {declared_merit!r} differs from {evaluation.merit_factor}"
        )

    return evaluation


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("report", type=Path, help="Rust run report or witness JSON")
    arguments = parser.parse_args()

    try:
        payload = json.loads(arguments.report.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise ValueError("top-level JSON value must be an object")
        evaluation = verify_payload(payload)
    except (OSError, json.JSONDecodeError, ValueError) as error:
        parser.exit(1, f"verification failed: {error}\n")

    print(
        json.dumps(
            {
                "verified": True,
                "length": evaluation.length,
                "energy": evaluation.energy,
                "correlations": evaluation.correlations,
                "merit_factor": evaluation.merit_factor,
                "sequence_sha256": evaluation.sequence_sha256,
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
