"""File adapters for Rust-checked neutral-carrier document graphs.

Python supplies paths, entry-point names, and JSON-shaped values only. Rust
owns graph references, frontier and mechanism checks, digests, and atomic
persistence.
"""

from __future__ import annotations

import json
from collections.abc import Mapping
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


class MechanismV0(StrEnum):
    COMPUTE = "compute"
    VERIFY = "verify"
    LEARN = "learn"


class OutputLabelV0(StrEnum):
    HISTORY = "history"
    RESULT = "result"
    EVIDENCE = "evidence"


@dataclass(frozen=True, slots=True)
class AdvaSaveReceiptV0:
    path: Path
    document_digest: str
    bytes_written: int


@dataclass(frozen=True, slots=True)
class AdvaLoadArtifactV0:
    transition: Mapping[str, Any]
    certificate: Mapping[str, Any]


def save_adva_document(
    path: str | PathLike[str], document: Mapping[str, Any]
) -> AdvaSaveReceiptV0:
    """Persist one complete carrier-table/frame/entry-point document graph."""

    destination = Path(path)
    digest, bytes_written = _save_adva_document_json(
        str(destination), json.dumps(document, sort_keys=True)
    )
    return AdvaSaveReceiptV0(
        path=destination,
        document_digest=digest,
        bytes_written=bytes_written,
    )


def load_adva_document(
    path: str | PathLike[str], entrypoint: str
) -> AdvaLoadArtifactV0:
    """Load, revalidate, and resolve one named transition frame in Rust."""

    if not isinstance(entrypoint, str) or not entrypoint:
        raise TypeError("entrypoint must be a nonempty string")
    transition_json, certificate_json = _load_adva_document_json(
        str(Path(path)), entrypoint
    )
    transition = json.loads(transition_json)
    certificate = json.loads(certificate_json)
    if not isinstance(transition, dict) or not isinstance(certificate, dict):
        raise ValueError("Rust returned an invalid persistence artifact")
    return AdvaLoadArtifactV0(transition=transition, certificate=certificate)


__all__ = [
    "AdvaLoadArtifactV0",
    "AdvaSaveReceiptV0",
    "InputLabelV0",
    "MechanismV0",
    "OutputLabelV0",
    "load_adva_document",
    "save_adva_document",
]
