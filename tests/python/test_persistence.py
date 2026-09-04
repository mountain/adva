"""The tests use temporary files only; no first `.adva` program is committed."""

from __future__ import annotations

from pathlib import Path

import pytest
from adva.persistence import (
    CarrierRouteV0,
    InputLabelV0,
    OutputLabelV0,
    load_adva_document,
    save_adva_document,
)


def output(prefix: str) -> dict[str, object]:
    return {
        "history": {
            "structure": f"test:{prefix}-history",
            "frontier": {
                "sites": [{"role": "time", "hole": 2, "occurrence": 0}]
            },
        },
        "result": {
            "structure": f"test:{prefix}-result",
            "frontier": {"sites": []},
        },
        "evidence": {
            "structure": f"test:{prefix}-evidence",
            "frontier": {
                "sites": [{"role": "construction", "hole": 0, "occurrence": 1}]
            },
        },
    }


def routes() -> tuple[CarrierRouteV0, ...]:
    return (
        CarrierRouteV0(OutputLabelV0.EVIDENCE, InputLabelV0.METHOD),
        CarrierRouteV0(OutputLabelV0.HISTORY, InputLabelV0.OBJECT),
        CarrierRouteV0(OutputLabelV0.RESULT, InputLabelV0.SUBJECT),
    )


def test_python_file_adapter_preserves_slots_and_returns_rust_certificate(
    tmp_path: Path,
) -> None:
    path = tmp_path / "round-trip.adva"
    receipt = save_adva_document(path, output("python"))
    loaded = load_adva_document(path, routes())

    assert receipt.path == path
    assert receipt.bytes_written > 0
    assert loaded.input["subject"]["structure"] == "test:python-result"
    assert loaded.input["method"]["structure"] == "test:python-evidence"
    assert loaded.input["object"]["structure"] == "test:python-history"
    assert loaded.certificate["document_digest"] == receipt.document_digest
    assert loaded.certificate["schema_and_version"] == "checked"
    assert loaded.certificate["canonical_frontiers"] == "checked"
    assert loaded.certificate["exact_slot_bijection"] == "checked"


def test_python_cannot_copy_one_stored_slot_into_two_inputs(tmp_path: Path) -> None:
    path = tmp_path / "copy.adva"
    save_adva_document(path, output("copy"))
    repeated = (
        CarrierRouteV0(OutputLabelV0.RESULT, InputLabelV0.SUBJECT),
        CarrierRouteV0(OutputLabelV0.RESULT, InputLabelV0.METHOD),
        CarrierRouteV0(OutputLabelV0.HISTORY, InputLabelV0.OBJECT),
    )
    with pytest.raises(ValueError, match="uses output slot Result more than once"):
        load_adva_document(path, repeated)


def test_python_cannot_bypass_the_adva_suffix(tmp_path: Path) -> None:
    path = tmp_path / "wrong.json"
    with pytest.raises(ValueError, match="path must use the .adva suffix"):
        save_adva_document(path, output("wrong"))
    assert not path.exists()
