"""The tests use temporary files only; no first `.adva` program is committed."""

from __future__ import annotations

from pathlib import Path

import pytest
from adva.persistence import MechanismV0, load_adva_document, save_adva_document


def carrier(structure: str, sites: list[dict[str, object]] | None = None) -> dict[str, object]:
    return {"structure": structure, "frontier": {"sites": sites or []}}


def document(prefix: str) -> dict[str, object]:
    return {
        "schema": "adva.neutral-carrier-graph.research",
        "version": 0,
        "carriers": [
            {"id": 0, "carrier": carrier(f"test:{prefix}-subject")},
            {
                "id": 1,
                "carrier": carrier(
                    f"test:{prefix}-method",
                    [{"role": "time", "hole": 2, "occurrence": 0}],
                ),
            },
            {"id": 2, "carrier": carrier(f"test:{prefix}-object")},
            {"id": 3, "carrier": carrier(f"test:{prefix}-history")},
            {"id": 4, "carrier": carrier(f"test:{prefix}-result")},
            {
                "id": 5,
                "carrier": carrier(
                    f"test:{prefix}-evidence",
                    [{"role": "construction", "hole": 0, "occurrence": 1}],
                ),
            },
        ],
        "frames": [
            {
                "id": 0,
                "input": {"subject": 0, "method": 1, "object": 2},
                "mechanism": {"kind": MechanismV0.COMPUTE.value},
                "output": {"history": 3, "result": 4, "evidence": 5},
            },
            {
                "id": 1,
                "input": {"subject": 4, "method": 5, "object": 3},
                "mechanism": {"kind": MechanismV0.COMPUTE.value},
                "output": {"history": None, "result": None, "evidence": None},
            },
        ],
        "entrypoints": [
            {"name": "replay", "frame": 1},
            {"name": "start", "frame": 0},
        ],
    }


def test_python_adapter_loads_named_frame_and_reuses_recorded_carriers(
    tmp_path: Path,
) -> None:
    path = tmp_path / "round-trip.adva"
    receipt = save_adva_document(path, document("python"))
    loaded = load_adva_document(path, "replay")

    assert receipt.path == path
    assert receipt.bytes_written > 0
    assert loaded.transition["frame"] == 1
    assert loaded.transition["state"] == "ready"
    assert loaded.transition["form"]["mechanism"] == MechanismV0.COMPUTE.value
    assert (
        loaded.transition["form"]["input"]["subject"]["structure"]
        == "test:python-result"
    )
    assert (
        loaded.transition["form"]["input"]["method"]["structure"]
        == "test:python-evidence"
    )
    assert (
        loaded.transition["form"]["input"]["object"]["structure"]
        == "test:python-history"
    )
    assert loaded.certificate["document_digest"] == receipt.document_digest
    assert loaded.certificate["entrypoint"] == "replay"
    assert loaded.certificate["canonical_tables"] == "checked"
    assert loaded.certificate["resolved_references"] == "checked"
    assert loaded.certificate["mechanism_forms"] == "checked"


def test_python_cannot_load_an_unknown_carrier_reference(tmp_path: Path) -> None:
    path = tmp_path / "unknown.adva"
    malformed = document("unknown")
    malformed["frames"][0]["input"]["subject"] = 99  # type: ignore[index]
    with pytest.raises(ValueError, match="references unknown carrier"):
        save_adva_document(path, malformed)
    assert not path.exists()


def test_python_cannot_bypass_the_adva_suffix(tmp_path: Path) -> None:
    path = tmp_path / "wrong.json"
    with pytest.raises(ValueError, match=r"path must use the \.adva suffix"):
        save_adva_document(path, document("wrong"))
    assert not path.exists()
