"""Finite models of a declared modal property system; external evidence only.

The assertions here are about what the retained checker decided by exhaustion.
They are not claims about any text, and they promote no native identity.
"""

import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "experiments/modal_property_systems"
CHECKER = HERE / "checker.py"
CONTRACT = HERE / "contract.json"
EVIDENCE = HERE / "evidence.json"
NOTE = ROOT / "docs/research/0221-which-readings-of-a-modal-property-argument-are-impossible.md"
CLAIM_ID = "adva.bounded-experiment.modal-property-systems.v0"
TIMING_KEYS = ("installed_limits",)


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def payload(report):
    """The mathematical payload, with timings and platform facts removed."""
    return {
        key: value
        for key, value in report.items()
        if not key.endswith("_ns")
        and not key.startswith("rss_high_water")
        and key not in TIMING_KEYS
    }


def invoke(checker, output, timeout=600):
    return subprocess.run(
        [sys.executable, "-S", str(checker), "--output", str(output)],
        capture_output=True,
        text=True,
        timeout=timeout,
        check=False,
    )


def section(name):
    return load(EVIDENCE)["sections"][name]


def test_retained_evidence_is_an_external_pass_inside_the_contract():
    report = load(EVIDENCE)
    contract = load(CONTRACT)
    assert report["status"] == "ExternalExactPass"
    assert report["checker_sha256"] == digest(CHECKER)
    assert report["contract_sha256"] == digest(CONTRACT)
    assert report["assertions"] <= contract["budget"]["max_assertions"]
    assert report["limits"] == contract["budget"]


def test_fresh_run_reproduces_the_retained_mathematical_payload(tmp_path):
    output = tmp_path / "fresh.json"
    completed = invoke(CHECKER, output)
    assert completed.returncode == 0, completed.stderr
    assert payload(load(output)) == payload(load(EVIDENCE))


def test_an_existing_output_is_never_overwritten(tmp_path):
    output = tmp_path / "keep.json"
    output.write_text("retained", encoding="utf-8")
    completed = invoke(CHECKER, output)
    assert completed.returncode != 0
    assert output.read_text(encoding="utf-8") == "retained"


def test_the_declared_semantics_and_the_necessity_lemma():
    s = section("S1_semantics")
    assert s["world_bound"] == 3 and s["domain_size"] == 1
    assert s["property_algebra_is_complete"] is True
    assert s["positivity_may_vary_by_world"] is True
    assert s["frames_are_declared_as_relations_not_as_a_proof_calculus"] is True
    assert s["models_enumerated"] == 18508
    assert s["necessity_lemma_exceptions"] == 0
    assert "sees only itself" in s["necessity_lemma"]
    shapes = s["frames_per_class_and_worlds"]
    assert shapes["equivalence:1"] == 1 and shapes["equivalence:2"] == 2
    assert shapes["equivalence:3"] == 5
    assert shapes["preorder:2"] == 4 and shapes["preorder:3"] == 29
    assert shapes["reflexive:2"] == 4 and shapes["reflexive:3"] == 64
    assert shapes["universal:1"] == shapes["universal:2"] == shapes["universal:3"] == 1


def test_the_first_two_axioms_do_not_force_the_conclusion():
    s = section("S2_table")
    row = s["rows"]["universal:3:A1+A2"]
    assert row["axioms"] == ["A1", "A2"]
    assert row["models"] == 1728 and row["conclusion"] == 216
    assert row["conclusion_holds_in_every_model"] is False
    assert row["conclusion_holds_in_no_model"] is False
    assert row["collapse"] == 0
    assert "universal:3:first_two_axioms" in s["retained_countermodels"]
    assert "equivalence:3:first_two_axioms" in s["retained_countermodels"]
    assert len(s["retained_countermodels"]) == 12
    assert s["a_refutation_is_one_model"] is True
    assert s["forcing_is_reported_only_where_models_exist"] is True


def test_the_axiom_table_has_the_declared_number_of_rows():
    s = section("S2_table")
    contract = load(CONTRACT)
    # the checker reports the number of rows it actually wrote, and it is the
    # declared one: 1536 subset-and-block combinations less the 128 that no model
    # satisfies, because A5 has no model under the universal frame above one world
    assert s["axiom_table_rows"] == len(s["rows"])
    assert s["axiom_table_rows"] == contract["objects"]["expected_axiom_table_rows"] == 1408
    assert s["subset_and_block_combinations"] == 1536 == 12 * 128
    assert s["rows_missing"] == 128 == 1536 - 1408
    assert s["blocks_with_rows_missing"] == ["universal:2", "universal:3"]
    universal = [row for key, row in s["rows"].items()
                 if key.startswith("universal:2:") or key.startswith("universal:3:")]
    assert len(universal) == 128
    assert all("A5" not in row["axioms"] for row in universal)
    # the model counts of the first two axioms come from the pruning, not a scan
    assert "pruned enumeration" in s["the_first_two_axioms_are_pruning_conditions"]


def test_no_axiom_set_forces_the_conclusion_outside_the_symmetric_frames():
    s = section("S2_table")
    minimal = s["minimal_forcing"]
    for key in ("preorder:2", "preorder:3", "reflexive:2", "reflexive:3",
                "universal:2", "universal:3"):
        assert minimal[key]["forcing_sets"] == 0, key
        assert minimal[key]["smallest_forcing_set"] is None, key
    for key in ("equivalence:2", "equivalence:3"):
        assert minimal[key]["forcing_sets"] == 64, key
        assert minimal[key]["smallest_forcing_set"] == "A5", key
        assert minimal[key]["models_under_that_set"] == 1, key
    # every world count degenerates when there is only one world
    for key in ("universal:1", "equivalence:1", "preorder:1", "reflexive:1"):
        assert minimal[key]["forcing_sets"] == 128, key
        assert minimal[key]["smallest_forcing_set"] == "no axioms", key
    assert s["the_conclusion_is_forced_only_over_symmetric_frames"] is True
    assert s["the_smallest_forcing_set_is_one_axiom"] is True
    # forcing the conclusion and forcing the essence to be vacuous are the same rows
    assert s["rows_forcing_the_conclusion"] == 640
    assert s["rows_in_which_every_model_makes_the_essence_vacuous"] == 640
    assert s["forcing_the_conclusion_forces_the_essence_to_be_vacuous"] is True
    # the countermodel under every axiom is retained for the frames that fail
    for key in ("preorder:3:all_seven_axioms", "reflexive:3:all_seven_axioms"):
        witness = s["retained_countermodels"][key]
        assert witness["worlds"] == 3
        relation = [tuple(pair) for pair in witness["relation"]]
        assert all((w, w) in relation for w in range(3)), key
        assert (1, 0) not in relation or (0, 1) not in relation, key


def test_the_retained_countermodel_is_not_symmetric():
    s = section("S2_table")
    witness = s["retained_countermodels"]["preorder:3:all_seven_axioms"]
    relation = {tuple(pair) for pair in witness["relation"]}
    assert relation == {(0, 0), (0, 1), (1, 1), (2, 2)}
    assert (1, 0) not in relation
    assert witness["godlike_worlds"] == [1, 2]
    assert witness["successors"]["0"] == [0, 1]
    assert witness["successors"]["1"] == [1] and witness["successors"]["2"] == [2]


def test_the_conclusion_holds_exactly_where_the_modality_collapses():
    s = section("S3_necessary_existence")
    assert s["the_three_axioms"] == ["A1", "A2", "A5"]
    assert s["models_of_the_three_axioms"] == 86
    assert s["models_where_the_conclusion_agrees_with_the_constancy_of_every_property"] == 86
    assert s["models_that_also_satisfy_the_other_four"] == 50
    assert s["the_conclusion_holds_exactly_where_every_property_is_constant"] is True
    unique = s["the_one_equivalence_model"]
    assert unique["worlds"] == 3
    assert unique["relation_is_the_identity"] is True
    assert unique["godlike_worlds"] == [0, 1, 2]
    assert unique["necessary_existence_worlds"] == [0, 1, 2]
    assert unique["conclusion"] is True
    assert unique["every_property_constant"] is True
    assert unique["essence_vacuous"] is True
    assert s["positivity_carries_no_information_in_that_model"] is True


def test_the_converse_of_the_first_axiom_is_not_free():
    s = section("S2_table")
    base = s["rows"]["equivalence:3:A1+A2"]
    converse = s["rows"]["equivalence:3:A1+A1c+A2"]
    assert base["models"] == 1832 and converse["models"] == 77
    assert base["conclusion"] == 278 and converse["conclusion"] == 5
    assert converse["models"] < base["models"]
    assert converse["conclusion"] < base["conclusion"]


def test_the_declared_family_cannot_express_uniqueness():
    s = section("S4_vocabulary")
    assert s["identity_occurs_in_the_declared_family"] is False
    assert s["uniqueness_cannot_be_derived_from_this_family"] is True
    assert s["uniqueness_is_an_untested_residual"] is True
    assert "identity" not in s["declared_vocabulary"]
    assert set(s["declared_notions"]) == {"godlikeness", "essence",
                                         "necessary_existence", "conclusion"}


def test_the_one_world_case_is_vacuous():
    s = section("S5_degenerate")
    assert s["models_with_every_axiom"] == 1
    assert s["conclusion_with_every_axiom"] == 1
    assert s["collapse_with_every_axiom"] == 1
    assert s["declared_sets_forcing_the_conclusion_with_one_world"] == 128
    assert s["every_declared_subset_forces_the_conclusion_with_one_world"] is True
    assert s["with_one_world_necessity_is_the_identity"] is True
    assert s["the_degenerate_case_is_not_evidence_for_the_argument"] is True


def test_the_contract_states_its_protected_boundaries():
    contract = load(CONTRACT)
    protected = " ".join(contract["protected"])
    for phrase in (
        "No agreement with a published verdict is imported as evidence",
        "This is a declared finite semantics and not a proof calculus",
        "Transfer to an unrestricted system is not claimed",
        "A countermodel is a refutation and one model is enough",
        "no numbering from any edition is used",
        "No floating-point value",
        "No native Rust witness",
    ):
        assert phrase in protected, phrase
    assert contract["input_document"] == (
        "docs/research/0221-which-readings-of-a-modal-property-argument-are-impossible.md"
    )
    assert contract["level"].startswith("External exact")
    assert contract["interface"]["justification"].startswith("The translation is justified")
    objects = contract["objects"]
    assert objects["world_bound"] == 3 and objects["domain_size"] == 1
    assert objects["expected_axiom_table_rows"] == 1408
    assert objects["expected_subset_and_block_combinations"] == 1536
    assert objects["expected_rows_missing_because_A5_has_no_model"] == 128
    assert objects["blocks_with_rows_missing"] == ["universal:2", "universal:3"]
    assert objects["expected_models_for_the_lemma"] == 18508
    assert objects["expected_non_degenerate_forcing_rows"] == 128
    assert objects["expected_models_of_the_three_axioms"] == 86
    assert objects["expected_agreements_of_the_conclusion_with_constancy"] == 86
    assert objects["expected_subsets_forcing_with_one_world"] == 128
    assert objects["expected_retained_countermodels"] == 12
    assert NOTE.is_file()


def test_the_note_states_the_residual_and_imports_no_text():
    text = NOTE.read_text(encoding="utf-8")
    assert "Residual" in text
    flat = " ".join(text.split()).lower()
    for phrase in ("no text and no corpus count is imported",
                   "is not imported as evidence",
                   "transfer to an unrestricted system is not claimed",
                   "the conclusion and the collapse are the same condition",
                   "recorded as an **untested residual**"):
        assert phrase in flat, phrase


def test_the_registered_claim_points_at_existing_artifacts():
    import tomllib

    claims = tomllib.loads((ROOT / "docs/claims.toml").read_text(encoding="utf-8"))["claim"]
    matches = [c for c in claims if c["claim_id"] == CLAIM_ID]
    assert len(matches) == 1
    claim = matches[0]
    assert claim["status"] == "bounded-experiment"
    assert claim["dimension"].startswith("external")
    assert claim["dependencies"] == []
    assert len(claim["forbidden_conflations"]) >= 8
    assert any("countermodel" in item for item in claim["forbidden_conflations"])
    for symbol in claim["code_symbol"].split("; "):
        assert (ROOT / symbol).is_file(), symbol
    assert claim["counterexample_boundary"].startswith("No text")
