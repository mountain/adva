"""A research commit must remain runnable without admitting changed kernel code."""

import json
import subprocess
from pathlib import Path

import pytest
from adva.quine_relay import Supervisor, check_source_base


@pytest.fixture
def checkout(tmp_path):
    root = tmp_path / "checkout"
    root.mkdir()

    def git(*args):
        return subprocess.check_output(["git", *args], cwd=root, text=True).strip()

    git("init", "-q")
    git("config", "user.name", "Boundary test")
    git("config", "user.email", "boundary@example.invalid")
    kernel = root / "crates/adva-lisp/src/lib.rs"
    kernel.parent.mkdir(parents=True)
    kernel.write_text("// frozen kernel\n")
    git("add", ".")
    git("commit", "-qm", "kernel baseline")
    contract = json.loads(
        (Path(__file__).resolve().parents[2] / "experiments/quine_relay/contract.json").read_text()
    )
    contract["base_commit"] = git("rev-parse", "HEAD")
    observer = root / "crates/adva-witness/examples/quine_relay.rs"
    observer.parent.mkdir(parents=True)
    observer.write_text("// new research observer\n")
    (root / "research.md").write_text("New research commit\n")
    git("add", ".")
    git("commit", "-qm", "research implementation")
    evidence = tmp_path / "evidence"
    evidence.mkdir()
    return root, kernel, git, contract, Supervisor(evidence, contract["limits"])


def test_research_descendant_is_admitted(checkout):
    root, _, _, contract, supervisor = checkout
    check_source_base(supervisor, root, contract)
    assert all(call["exit_code"] == 0 for call in supervisor.calls)


@pytest.mark.parametrize("committed", [False, True])
def test_changed_kernel_is_refused(checkout, committed):
    root, kernel, git, contract, supervisor = checkout
    kernel.write_text("// changed kernel\n")
    if committed:
        git("add", ".")
        git("commit", "-qm", "kernel change")
    with pytest.raises(ValueError, match="source-base-content failed"):
        check_source_base(supervisor, root, contract)


def test_unrelated_base_is_refused(checkout):
    root, _, git, contract, supervisor = checkout
    git("checkout", "--orphan", "unrelated", "-q")
    git("commit", "-qm", "unrelated root")
    with pytest.raises(ValueError, match="source-base-ancestor failed"):
        check_source_base(supervisor, root, contract)
