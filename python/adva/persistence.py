"""File adapters for the Rust-checked neutral-carrier research document.

Python supplies paths and JSON-shaped values only. Rust owns schema checks,
frontier validation, exact slot routing, digests, and atomic persistence.
"""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from enum import StrEnum
from os import PathLike
from pathlib import Path
from typing import Any

from ._native import load_adva_document_json as _load_adva_document_json
from ._native import save_adva_document_json as _save_adva_document_json


class InputLabelV0(StrEnum):
    SUBJECT = "subject"
    METHOD = "method"
    OBJECT = "object"


class OutputLabelV0(StrEnum):
    HISTORY = "history"
    RESULT = "result"
    EVIDENCE = "evidence"


@dataclass(frozen=True, slots=True)
class CarrierRouteV0:
    """One requested output-to-input relabelling; Rust checks the full bijection."""

    source: OutputLabelV0
    target: InputLabelV0

    def to_dict(self) -> dict[str, str]:
        return {"from": self.source.value, "to": self.target.value}


@dataclass(frozen=True, slots=True)
class AdvaSaveReceiptV0:
    path: Path
    document_digest: str
    bytes_written: int


@dataclass(frozen=True, slots=True)
class AdvaReloadArtifactV0:
    input: Mapping[str, Any]
    certificate: Mapping[str, Any]


def save_adva_document(
    path: str | PathLike[str], output: Mapping[str, Any]
) -> AdvaSaveReceiptV0:
    """Persist three output-labelled neutral carriers through the Rust boundary."""

    destination = Path(path)
    digest, bytes_written = _save_adva_document_json(
        str(destination), json.dumps(output, sort_keys=True)
    )
    return AdvaSaveReceiptV0(
        path=destination,
        document_digest=digest,
        bytes_written=bytes_written,
    )


def load_adva_document(
    path: str | PathLike[str], routes: Sequence[CarrierRouteV0]
) -> AdvaReloadArtifactV0:
    """Load, revalidate, and explicitly relabel one neutral `.adva` document."""

    route_tuple = tuple(routes)
    if len(route_tuple) != 3 or any(
        not isinstance(route, CarrierRouteV0) for route in route_tuple
    ):
        raise TypeError("routes must contain exactly three CarrierRouteV0 values")
    input_json, certificate_json = _load_adva_document_json(
        str(Path(path)),
        json.dumps([route.to_dict() for route in route_tuple], sort_keys=True),
    )
    input_document = json.loads(input_json)
    certificate = json.loads(certificate_json)
    if not isinstance(input_document, dict) or not isinstance(certificate, dict):
        raise ValueError("Rust returned an invalid persistence artifact")
    return AdvaReloadArtifactV0(input=input_document, certificate=certificate)


__all__ = [
    "AdvaReloadArtifactV0",
    "AdvaSaveReceiptV0",
    "CarrierRouteV0",
    "InputLabelV0",
    "OutputLabelV0",
    "load_adva_document",
    "save_adva_document",
]
