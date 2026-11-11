//! Research-local successor check for one accepted opaque fixture.
//! Codex (OpenAI), through Mingli Yuan's authorized account proxy, Unknown v0.3.
//! Workflow sequencing is not a native composed acceptance certificate.

use adva_ir::{DiagramValidationArtifact, Occurrence};
use adva_lisp::import_diagram_json;
use serde_json::{Value, json};
use std::{collections::BTreeSet, env, fs};

const FIXTURE: &str = include_str!(
    "../../../experiments/native_input_binding_serialized_leaf_request/canonical-request-20261031.json"
);

#[derive(Debug, PartialEq, Eq)]
enum SuccessorOutcome {
    SuccessorVerified,
    Refused(&'static str),
}

fn certificate_matches_result(artifact: &DiagramValidationArtifact) -> bool {
    let expected_nodes = artifact
        .result
        .nodes
        .iter()
        .map(|node| node.id)
        .collect::<Vec<_>>();
    artifact.certificate.certified()
        && artifact.certificate.node_ids == expected_nodes
        && artifact.certificate.source_partition_snapshot == artifact.result.source_partition()
        && usize::try_from(artifact.certificate.history_event_count).ok()
            == Some(artifact.result.history.prefix.len())
}

fn endpoint_json(context: &str, occurrence: &Occurrence) -> Value {
    json!({
        "context": context,
        "occurrence": occurrence.id.as_str(),
        "path": occurrence.path.0,
        "source": occurrence.source.as_str(),
    })
}

fn endpoint_exists(endpoint: &Value, artifact: &DiagramValidationArtifact) -> bool {
    let context = artifact.result.function.to_string();
    artifact
        .result
        .occurrences
        .iter()
        .any(|occurrence| endpoint == &endpoint_json(&context, occurrence))
}

fn verify_accepted_fixture(encoded: &str) -> SuccessorOutcome {
    if encoded != FIXTURE {
        return SuccessorOutcome::Refused("accepted fixture bytes changed");
    }
    let Ok(value) = serde_json::from_str::<Value>(encoded) else {
        return SuccessorOutcome::Refused("accepted fixture malformed");
    };
    let Some(root) = value.as_object() else {
        return SuccessorOutcome::Refused("accepted fixture shape mismatch");
    };
    let expected_keys = BTreeSet::from([
        "external_leaf",
        "native_occurrence_map",
        "profile",
        "residual_diagram_json",
        "source_diagram_json",
    ]);
    if root.keys().map(String::as_str).collect::<BTreeSet<_>>() != expected_keys {
        return SuccessorOutcome::Refused("accepted fixture shape mismatch");
    }

    let Some(source_json) = root.get("source_diagram_json").and_then(Value::as_str) else {
        return SuccessorOutcome::Refused("source diagram missing");
    };
    let Some(residual_json) = root.get("residual_diagram_json").and_then(Value::as_str) else {
        return SuccessorOutcome::Refused("residual diagram missing");
    };
    let Ok(source) = import_diagram_json(source_json) else {
        return SuccessorOutcome::Refused("source diagram import failed");
    };
    let Ok(residual) = import_diagram_json(residual_json) else {
        return SuccessorOutcome::Refused("residual diagram import failed");
    };
    if !certificate_matches_result(&source) || !certificate_matches_result(&residual) {
        return SuccessorOutcome::Refused("diagram certificate incomplete");
    }
    if source.result.to_json().ok().as_deref() != Some(source_json)
        || residual.result.to_json().ok().as_deref() != Some(residual_json)
    {
        return SuccessorOutcome::Refused("imported diagram snapshot mismatch");
    }

    let Some(mapping) = root
        .get("native_occurrence_map")
        .and_then(Value::as_array)
        .filter(|mapping| mapping.len() == 1)
    else {
        return SuccessorOutcome::Refused("native occurrence-map shape mismatch");
    };
    let Some(source_endpoint) = mapping[0].get("source") else {
        return SuccessorOutcome::Refused("native source endpoint missing");
    };
    let Some(target_endpoint) = mapping[0].get("target") else {
        return SuccessorOutcome::Refused("native target endpoint missing");
    };
    let expected_source = json!({
        "context": "native-binding-process/source",
        "occurrence": "occ:1",
        "path": [],
        "source": "source:native-binding-process/source:1:dynamic",
    });
    let expected_target = json!({
        "context": "native-binding-process/residual",
        "occurrence": "occ:0",
        "path": [],
        "source": "source:native-binding-process/residual:0:dynamic",
    });
    if source_endpoint != &expected_source || target_endpoint != &expected_target {
        return SuccessorOutcome::Refused("native occurrence-map value mismatch");
    }
    if !endpoint_exists(source_endpoint, &source) || !endpoint_exists(target_endpoint, &residual) {
        return SuccessorOutcome::Refused(
            "native occurrence endpoint absent from imported diagram",
        );
    }

    SuccessorOutcome::SuccessorVerified
}

#[test]
fn accepted_opaque_fixture_completes_the_native_successor() {
    let path = env::var("ADVA_ACCEPTED_FIXTURE_PATH").expect("accepted fixture path");
    let encoded = fs::read_to_string(path).expect("read accepted fixture");
    assert_eq!(
        verify_accepted_fixture(&encoded),
        SuccessorOutcome::SuccessorVerified
    );
}

#[test]
fn changed_bytes_cannot_reuse_the_successor_gate() {
    let changed = FIXTURE.replacen("\"occ:1\"", "\"occ:9\"", 1);
    assert_ne!(changed, FIXTURE);
    assert_eq!(
        verify_accepted_fixture(&changed),
        SuccessorOutcome::Refused("accepted fixture bytes changed")
    );
}
