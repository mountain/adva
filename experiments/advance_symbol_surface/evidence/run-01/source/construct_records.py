"""Write a fixed symbolic presentation. No expression evaluation or game search."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def write(name, value):
    raw = (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode()
    (ROOT / name).write_bytes(raw)
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def main():
    obligation_names = ["negative-one-derivation", "occurrence-preservation", "prefix-decode",
                        "cantor-prefix-interpretation", "csb-injections", "tarski-carrier-and-monotonicity",
                        "nested-interval-premises", "pi-branch-and-derivation", "game-turn-and-exit"]
    obligations = {"schema": "adva.symbol-surface.obligations.proposed", "version": 0,
                   "items": [{"id": name, "status": "Open", "document_frontier_coordinate":
                              {"role": "construction", "hole": i, "occurrence": 0}}
                             for i, name in enumerate(obligation_names)],
                   "coordinate_boundary": "These document-local frontier coordinates only index annotations; they are not logical holes or native proof obligations."}
    obligation_ref = write("obligations.json", obligations)
    contract_ref = write("contract.json", {
        "schema": "adva.symbol-surface.contract.proposed", "version": 0,
        "scope": "Representation only; no evaluation, theorem proving, expression search, Nim play, or benchmark",
        "base_commit": "17fe19e283011f3c4361112f2fe25e4cdae9407e",
        "representation": "External symbolic AST and references; no new Rust scalar type or primitive",
        "division_guard": "denominator nonzero must be justified before any later evaluation",
        "log_branch": {"index": 0, "negative_real_argument": "+pi", "scope": "principal argument value, not a holomorphic branch through its cut"},
        "constant_boundary": "Names i, pi, e, zero, one and four denote exact symbolic objects, not floating-point approximations",
        "native_payload_resolution": "NotImplemented; carrier structure strings are documentary integrity references",
        "proof_status": "NotRun", "native_load_status": "NotRun",
        "limits": {"max_file_bytes": 32768, "static_check_timeout_seconds": 5,
                   "arithmetic_steps": 0, "search_nodes": 0, "game_moves": 0,
                   "automatic_continuations": 0}})
    surface = {
        "schema": "adva.symbol-surface.presentation.proposed", "version": 0,
        "symbols": [
            {"id": "imaginary-unit", "display": "i", "lexical_kind": "named_atom", "mathematical_type": "Complex", "address_code": "0"},
            {"id": "pi", "display": "π", "lexical_kind": "named_atom", "mathematical_type": "Real", "address_code": "20"},
            {"id": "negative-one", "display": "-1", "lexical_kind": "name_with_expansion", "mathematical_type": "Integer", "address_code": "22"}],
        "address_boundary": "Codes are words over {0,2}, not numerical values of the named constants. Preserve code length and a finite-word end marker. No infinite zero padding identifies a finite word with a Cantor point.",
        "collections": [
            {"id": "S", "kind": "symbolic_value_catalog", "description": "Previously declared finite values; proposed insertion of pi is not executed here"},
            {"id": "S-bar", "kind": "symbolic_value_catalog", "relation": "complex conjugation of S; exact operation remains external"},
            {"id": "S-wedge", "kind": "construction_journal", "description": "Witness records, not another scalar set or exterior algebra"}],
        "template": {"id": "H", "type": "Complex x Complex x Complex -> Complex",
                     "holes": ["a", "b", "c"],
                     "body": {"op": "sub", "args": [{"hole": "a"}, {"op": "mul", "args": [{"hole": "b"}, {"hole": "c"}]}]},
                     "operator_boundary": "Subtraction and multiplication are proposed symbolic constructors; no native builtin changes"},
        "occurrences": [{"id": "a-zero", "constant": "zero", "type": "Complex"},
                        {"id": "b-one", "constant": "one", "type": "Complex"},
                        {"id": "c-one", "constant": "one", "type": "Complex"}],
        "fill": {"a": "a-zero", "b": "b-one", "c": "c-one"},
        "coercion_boundary": {"target": "Complex", "embeddings": ["Integer -> Real", "Real -> Complex"],
                              "status": "DeclaredNotExecuted", "meaning": "Comparisons with negative-one and pi use their canonical embedded values; this declares no native coercion"},
        "result_claim": {"expression": "H[a:=a-zero,b:=b-one,c:=c-one]", "equals_symbol": "negative-one",
                         "status": "DeclaredNotExecuted", "proof_obligation": "negative-one-derivation"},
        "pi_record": {"id": "r-pi", "home": "S-wedge", "status": "DeclaredNotExecuted",
                      "inputs": ["u = 2*(i-e), cited from S", "conjugate(u), cited from S-bar", "four"],
                      "steps": ["d := u - conjugate(u)", "a := d/four", "b := a*a", "c := Log_0(b)", "x := c/a"],
                      "result_symbol": "pi", "branch_index": 0, "proof_obligation": "pi-branch-and-derivation",
                      "remaining": "Repeated references do not imply native copy; this is an external equation journal"},
        "cantor_presentation": {"alphabet": ["0", "2"], "seed": "[0,1]",
                                "maps": ["L(x)=x/3", "R(x)=(2+x)/3"],
                                "finite_address": {"digits": ["0", "2", "0"], "length": 3, "terminated": True},
                                "interval_schema": "I(d)=[sum_j d_j/3^j, sum_j d_j/3^j+3^(-length(d))]",
                                "status": "SchemaOnly", "residual": "Two retained branches; not a three-way assignment of the three collections. No Cantor stage or real interval evaluated."},
        "theorem_interfaces": [
            {"name": "Cantor-Schroeder-Bernstein", "requires": ["sets A,B", "injections f:A->B and g:B->A"],
             "conclusion": "existence of a bijection A->B", "application_status": "Open",
             "missing": "No injections supplied for value catalogs versus construction journals; structural faithfulness is separate"},
            {"name": "Knaster-Tarski", "requires": ["fixed complete lattice L", "monotone Phi:L->L"],
             "candidate": "P(U), U a fixed symbolic term universe; Phi(A)=A union seeds union typed constructions from A",
             "conclusion": "least and greatest fixed points", "application_status": "Open",
             "missing": "U, admissibility and monotonicity are not instantiated; no finite convergence or perpetual execution follows"},
            {"name": "Nested closed intervals", "requires": ["nonempty closed bounded real intervals", "nestedness", "lengths tend to zero for uniqueness"],
             "conclusion": "a unique point when all listed premises hold", "application_status": "Open",
             "missing": "Only an interval schema is supplied; no infinite path or premise proof is installed"}],
        "game": {"status": "ProtocolProposal", "registration": "retain expression, origin, branch and proof status",
                 "continuation": "attach an open next question or DirectionMissing; never invent progress",
                 "fuel": "symbolic finite parameter B; not allocated or consumed",
                 "missing_rules": ["players", "turn order", "legal move relation", "winning condition"],
                 "evaluation": "NotRun", "search": "NotRun", "proof_replay": "NotRun"},
        "obligation_ids": obligation_names,
    }
    surface_ref = write("presentation.json", surface)
    sites = [item["document_frontier_coordinate"] for item in obligations["items"]]
    document = {"schema": "adva.neutral-carrier-graph.research", "version": 0,
                "carriers": [{"id": 0, "carrier": {"structure": surface_ref, "frontier": {"sites": sites}}},
                             {"id": 1, "carrier": {"structure": contract_ref, "frontier": {"sites": []}}},
                             {"id": 2, "carrier": {"structure": obligation_ref, "frontier": {"sites": []}}}],
                "frames": [{"id": 0, "input": {"subject": 0, "method": 1, "object": 2},
                            "mechanism": {"kind": "verify", "declared_subject": {"sites": sites}, "discharges": []},
                            "output": {"history": None, "result": None, "evidence": None}}],
                "entrypoints": [{"name": "inspect", "frame": 0}]}
    write("symbol-surface.adva", document)


if __name__ == "__main__":
    main()
