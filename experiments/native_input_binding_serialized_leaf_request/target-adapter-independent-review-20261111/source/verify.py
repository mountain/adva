#!/usr/bin/env python3
"""Structural completeness checker for a proposed adapter interface.

This checker never reads request or diagram bytes and has no Rust semantic
authority. Original tooling by Codex (OpenAI), contributed under Unknown v0.3.
"""
import json
from pathlib import Path
import re
import sys


class Invalid(ValueError):
    """A stable structural refusal."""

    def __init__(self, code, detail):
        super().__init__(f"{code}: {detail}")
        self.code = code
        self.detail = detail


def require(condition, code, detail):
    if not condition:
        raise Invalid(code, detail)


def sha256_text(value):
    return isinstance(value, str) and re.fullmatch(r"[0-9a-f]{64}", value) is not None


def expected_selector(diagram):
    endpoint = diagram["qualified_endpoint"]
    return {
        "diagram_role": diagram["role"],
        "diagram_sha256": diagram["serialized_sha256"],
        "source_id": endpoint["source_id"],
        "occurrence_id": endpoint["occurrence_id"],
        "path": endpoint["path"],
    }


def validate(document):
    require(document.get("schema") ==
            "adva.proposed.two-diagram-qualified-endpoint-adapter.v0",
            "E_SCHEMA", "unexpected interface schema")
    require(document.get("status") == "ProposedInterfaceOnly",
            "E_STATUS", "interface must not claim implementation")

    request = document.get("request_binding", {})
    require(isinstance(request.get("request_schema"), str) and
            request["request_schema"], "E_REQUEST", "missing request schema")
    require(sha256_text(request.get("canonical_bytes_sha256")) and
            sha256_text(request.get("receiver_context_sha256")),
            "E_REQUEST", "request and receiver context need SHA-256 pins")
    require(request.get("opaque_bytes_present") is False,
            "E_REQUEST_BYTES", "opaque bytes must stay outside this review")

    diagrams = document.get("ordered_diagrams")
    require(isinstance(diagrams, list) and len(diagrams) == 2,
            "E_DIAGRAM_COUNT", "exactly two ordered diagram slots required")
    require([item.get("role") for item in diagrams] == ["left", "right"],
            "E_DIAGRAM_ROLES", "diagram roles must be ordered left then right")
    for diagram in diagrams:
        require(sha256_text(diagram.get("serialized_sha256")),
                "E_DIAGRAM_PIN", "diagram slot needs a SHA-256 pin")
        admission = diagram.get("native_admission", {})
        require(admission.get("authority") == "Rust" and
                admission.get("status") == "RequiredNotImplemented" and
                isinstance(admission.get("obligation"), str) and
                admission["obligation"], "E_NATIVE_BOUNDARY_STATUS",
                "native admission must remain a Rust obligation, not a result")
        endpoint = diagram.get("qualified_endpoint", {})
        require(all(isinstance(endpoint.get(field), str) and endpoint[field]
                    for field in ("source_id", "occurrence_id", "path")),
                "E_ENDPOINT_FIELDS", "source, occurrence and path are all required")

    relation = document.get("relation", {})
    require(relation.get("kind") == "ordered_qualified_endpoint_pair" and
            relation.get("order") == ["left", "right"],
            "E_RELATION_ORDER", "cross-diagram relation order must be explicit")
    require(relation.get("left") == expected_selector(diagrams[0]),
            "E_RELATION_LEFT", "left selector must retain its diagram and endpoint")
    require(relation.get("right") == expected_selector(diagrams[1]),
            "E_RELATION_RIGHT", "right selector must retain its diagram and endpoint")
    require(relation.get("comparison") ==
            "exact tuple equality after each independent native admission",
            "E_RELATION_COMPARISON", "comparison must depend on both admissions")
    require(relation.get("local_image_equality_sufficient_for_m6") is False,
            "E_M6", "local image equality cannot supply M6")

    controls = document.get("controls")
    expected_controls = {
        "canonical-valid": "Accepted",
        "wrong-diagram-pin": "Refused",
        "wrong-path": "Refused",
        "same-value-different-origin": "Refused",
        "reversed-order": "Refused",
    }
    require(isinstance(controls, list) and
            {item.get("id") for item in controls} == set(expected_controls) and
            len(controls) == len(expected_controls),
            "E_CONTROL_SET", "complete positive and refusal control set required")
    require(all(item.get("expected") == expected_controls[item["id"]]
                for item in controls), "E_CONTROL_OUTCOME",
            "negative substitutions must remain Refused")

    outcomes = document.get("outcomes", {})
    require(set(outcomes) == {"Accepted", "Refused", "Unknown"},
            "E_OUTCOME_SET", "Accepted, Refused and Unknown are all required")
    required_checks = [
        "A-request-binding", "B-left-native-admission",
        "B-right-native-admission", "C-qualified-cross-diagram-relation",
        "D-recorded-receiver-outcome",
    ]
    require(outcomes["Accepted"].get("requires") == required_checks,
            "E_ACCEPTED_CHECKS", "Accepted must depend on exact A+B+B+C+D checks")
    require(all(isinstance(outcomes[name].get(field), str) and
                outcomes[name][field] for name in outcomes
                for field in ("interpretation", "residual")),
            "E_OUTCOME_RESIDUAL", "every outcome needs interpretation and residual")

    arithmetic = document.get("arithmetic_boundaries", {})
    additive = arithmetic.get("additive_zero", {})
    multiplicative = arithmetic.get("multiplicative_unit", {})
    require(additive.get("equation") == "A-B=0" and
            additive.get("carrier") == "typed additive carrier" and
            additive.get("zero_is_typed") is True,
            "E_ADDITIVE_BOUNDARY", "additive zero must retain its own typed carrier")
    require(multiplicative.get("equation") == "A/B=1" and
            multiplicative.get("carrier") == "typed multiplicative carrier",
            "E_MULTIPLICATIVE_BOUNDARY", "multiplicative unit needs its own carrier")
    require(additive.get("carrier") != multiplicative.get("carrier") and
            arithmetic.get("interchange_authorized") is False,
            "E_ARITHMETIC_SEPARATION", "additive and multiplicative carriers cannot merge")
    require(multiplicative.get("denominator_nonzero_required") is True and
            multiplicative.get("undefined_at_A_eq_B_eq_0") is True,
            "E_MULTIPLICATIVE_GUARD", "quotient needs nonzero guard and zero refusal")
    require(multiplicative.get("order_and_history_preserved") is True,
            "E_ORDER_HISTORY", "multiplicative order and history must remain explicit")

    prohibitions = document.get("prohibitions", {})
    required_false = {
        "m6_from_local_image_equality", "research_0090_coverage",
        "research_0092_promotion", "arithmetic_universality_proved",
        "hypothesized_arithmetic_truth_proved", "authentication_proved",
        "practical_value_proved",
    }
    require(all(prohibitions.get(name) is False for name in required_false),
            "E_PROHIBITIONS", "scope escalations must be explicitly false")
    require(prohibitions["m6_from_local_image_equality"] is False,
            "E_M6", "M6 prohibition changed")

    residuals = document.get("residual_obligations")
    required_residuals = {
        "adapter-implementation", "native-receiver-execution",
        "independent-review", "research-0090-coverage",
    }
    require(isinstance(residuals, list) and set(residuals) == required_residuals and
            len(residuals) == len(required_residuals),
            "E_RESIDUALS", "all implementation, execution, review and coverage gaps remain")
    return {
        "status": "StructurallyCompleteProposedInterface",
        "diagram_slots": 2,
        "qualified_endpoints": 2,
        "controls": len(controls),
        "semantic_authority": False,
        "opaque_request_reads": 0,
        "diagram_byte_reads": 0,
        "native_executions": 0,
        "words_formed_or_revised": 0,
    }


def main(path):
    document = json.loads(Path(path).read_text(encoding="utf-8"))
    print(json.dumps(validate(document), sort_keys=True))


if __name__ == "__main__":
    try:
        main(sys.argv[1])
    except (Invalid, KeyError, OSError, ValueError, json.JSONDecodeError) as error:
        if isinstance(error, Invalid):
            payload = {"status": "RefusedStructuralContract", "code": error.code,
                       "detail": error.detail}
        else:
            payload = {"status": "UnknownInvalidInput", "detail": str(error)}
        print(json.dumps(payload, sort_keys=True))
        raise SystemExit(1)
