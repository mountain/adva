use serde_json::{Value, json};
use std::{collections::BTreeSet, env, fs};

const PROFILE: &str = "adva.research.native-input-binding-open-line-leaf-request.v0";
const FIXTURE: &str = include_str!(
    "../../../experiments/native_input_binding_serialized_leaf_request/canonical-request-20261031.json"
);

#[derive(Debug, PartialEq, Eq)]
enum Outcome {
    AcceptedCurrentFixture,
    Refused(&'static str),
    Unknown(&'static str),
}

fn structural_items(value: &Value) -> usize {
    match value {
        Value::Array(items) => 1 + items.iter().map(structural_items).sum::<usize>(),
        Value::Object(items) => 1 + items.values().map(structural_items).sum::<usize>(),
        _ => 1,
    }
}

fn diagram_matches_module(encoded: &str, module: &str) -> bool {
    let Ok(diagram) = serde_json::from_str::<Value>(encoded) else {
        return false;
    };
    diagram.get("module").and_then(Value::as_str) == Some(module)
        && diagram
            .get("function")
            .and_then(Value::as_object)
            .and_then(|function| function.get("module"))
            .and_then(Value::as_str)
            == Some(module)
}

fn receive(
    expected_module: &str,
    encoded: &str,
    byte_budget: usize,
    work_budget: usize,
) -> Outcome {
    if encoded.len() > byte_budget {
        return Outcome::Unknown("request byte budget exhausted");
    }
    let Ok(value) = serde_json::from_str::<Value>(encoded) else {
        return Outcome::Refused("malformed request");
    };
    let Some(root) = value.as_object() else {
        return Outcome::Refused("request shape mismatch");
    };
    let expected_keys = BTreeSet::from([
        "external_leaf",
        "native_occurrence_map",
        "profile",
        "residual_diagram_json",
        "source_diagram_json",
    ]);
    if root.keys().map(String::as_str).collect::<BTreeSet<_>>() != expected_keys {
        return Outcome::Refused("request shape mismatch");
    }
    if structural_items(&value) > work_budget {
        return Outcome::Unknown("structural work budget exhausted");
    }
    if root.get("profile").and_then(Value::as_str) != Some(PROFILE) {
        return Outcome::Refused("profile mismatch");
    }

    let expected_leaf = json!({
        "source": "s-KX-L",
        "occurrence": "occ-KX-L",
        "target_source": "t-KX-L",
        "target_occurrence": "tocc-KX-L",
    });
    if root.get("external_leaf") != Some(&expected_leaf) {
        return Outcome::Refused("external leaf mismatch");
    }
    if root
        .get("native_occurrence_map")
        .and_then(Value::as_array)
        .is_none_or(|entries| entries.len() != 1)
    {
        return Outcome::Refused("native occurrence-map shape mismatch");
    }

    let Ok(canonical) = serde_json::from_str::<Value>(FIXTURE) else {
        return Outcome::Unknown("checked-in fixture is invalid");
    };
    for key in [
        "external_leaf",
        "native_occurrence_map",
        "source_diagram_json",
        "residual_diagram_json",
    ] {
        if root.get(key) != canonical.get(key) {
            return Outcome::Refused("canonical snapshot mismatch");
        }
    }

    let Some(source) = root.get("source_diagram_json").and_then(Value::as_str) else {
        return Outcome::Refused("request shape mismatch");
    };
    let Some(residual) = root.get("residual_diagram_json").and_then(Value::as_str) else {
        return Outcome::Refused("request shape mismatch");
    };
    if !diagram_matches_module(source, expected_module)
        || !diagram_matches_module(residual, expected_module)
    {
        return Outcome::Refused("module mismatch");
    }
    if encoded != FIXTURE {
        return Outcome::Refused("noncanonical request bytes");
    }
    Outcome::AcceptedCurrentFixture
}

#[test]
fn opaque_consumer_accepts_only_the_current_fixture() {
    let case = env::var("ADVA_SERIALIZED_LEAF_CONSUMER_CASE").unwrap_or_else(|_| "matching".into());
    let path = env::var("ADVA_SERIALIZED_LEAF_REQUEST_PATH").unwrap();
    let original = fs::read_to_string(path).unwrap();
    let encoded = if case == "changed-profile" {
        let changed = original.replacen(PROFILE, "future-profile", 1);
        assert_ne!(original, changed);
        changed
    } else {
        original
    };
    let expected_module = if case == "renamed-module" {
        "native-binding-process-renamed"
    } else {
        "native-binding-process"
    };
    let outcome = receive(expected_module, &encoded, 65_536, 512);
    match case.as_str() {
        "matching" => assert_eq!(outcome, Outcome::AcceptedCurrentFixture),
        "renamed-module" => assert_eq!(outcome, Outcome::Refused("module mismatch")),
        "changed-profile" => assert_eq!(outcome, Outcome::Refused("profile mismatch")),
        _ => panic!("unexpected consumer case: {case}"),
    }
}
