"""The symbol-surface advance profile must carry its contract chain and live pins.

This is a regression test for a real breakage. The symbol-surface README was
edited to withhold an unearned label, and the pins binding it were not moved:
the catalogue reported InvalidCatalog and four catalogue tests failed, while the
contract pin in the advance profile broke silently because the existing test for
this module imports only `FILES`, `check_loaded` and `check_payload_bindings`
and never reaches the pin-checking path. Nothing here re-runs the profile; it
checks the bindings that a run would enforce at preflight.
"""

import hashlib
import json
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
DIR = ROOT / "experiments/advance_symbol_surface"
ACTIVE = DIR / "contract-v1.json"
FROZEN = DIR / "contract.json"
MODULE = ROOT / "python/adva/advance_surface.py"


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def test_the_successor_names_the_frozen_contract_by_digest():
    active = load(ACTIVE)
    assert active["version"] == 1
    supersedes = active["supersedes"]
    assert supersedes["path"] == "experiments/advance_symbol_surface/contract.json"
    assert supersedes["sha256"] == hashlib.sha256(FROZEN.read_bytes()).hexdigest()
    assert supersedes["note"].strip()


def test_the_frozen_contract_still_describes_the_first_run():
    """The frozen version keeps its original identity rather than being updated."""
    frozen = load(FROZEN)
    assert frozen["version"] == 0
    assert frozen["date"] == "2026-09-10"
    assert "supersedes" not in frozen
    assert frozen["pins"]["experiments/symbol_surface/README.md"] == (
        "e5a38e5745de316fbba026705230ee9d090221a1a0fb836c0b31b80af73eab37"
    )


def test_every_pin_in_the_active_contract_matches_the_live_file():
    """This is the check whose absence let the breakage through."""
    active = load(ACTIVE)
    assert active["pins"], "the contract must pin its inputs"
    for relative, expected in active["pins"].items():
        path = ROOT / relative
        assert path.exists(), relative
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        assert actual == expected, f"{relative} changed without the pin moving"


def test_the_module_uses_the_successor_and_verifies_the_frozen_digest():
    source = MODULE.read_text(encoding="utf-8")
    assert 'CONTRACT = ROOT / "experiments/advance_symbol_surface/contract-v1.json"' in source
    assert 'FROZEN_CONTRACT = ROOT / "experiments/advance_symbol_surface/contract.json"' in source
    assert 'contract.get("version") != 1' in source
    assert 'contract["supersedes"]["sha256"] != frozen' in source


def test_the_base_commit_boundary_holds_at_this_commit():
    """The profile requires nothing under crates to have changed since its base."""
    active = load(ACTIVE)
    base = active["base_commit"]
    ancestor = subprocess.run(
        ["git", "merge-base", "--is-ancestor", base, "HEAD"], cwd=ROOT, capture_output=True
    )
    assert ancestor.returncode == 0, "the base commit is not an ancestor of HEAD"
    diff = subprocess.run(
        ["git", "diff", "--exit-code", "--no-ext-diff", base, "--",
         "Cargo.toml", "Cargo.lock", "crates"],
        cwd=ROOT,
        capture_output=True,
    )
    assert diff.returncode == 0, (
        "the Rust boundary moved since the successor's base commit; the successor "
        "needs a new base commit rather than a relaxed check"
    )


def test_the_frozen_contract_is_expected_to_fail_on_its_edited_input():
    """Replaying the frozen contract now fails, and that is by design, not a drift.

    Asserting this keeps the divergence visible: if the README ever returned to
    the frozen bytes, this test would say so rather than let the note in the
    successor quietly become false.
    """
    frozen = load(FROZEN)
    live = hashlib.sha256(
        (ROOT / "experiments/symbol_surface/README.md").read_bytes()
    ).hexdigest()
    assert frozen["pins"]["experiments/symbol_surface/README.md"] != live
