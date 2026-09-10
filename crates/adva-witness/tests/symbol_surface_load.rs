//! Read-only loading of the symbol-surface envelope; no payload evaluation.

use adva_witness::AdvaDocumentV0;
use adva_witness::AdvaPersistenceErrorV0;
use adva_witness::FrameIdV0;
use adva_witness::LoadedFrameStateV0;
use adva_witness::MechanismAdmissionV0;
use adva_witness::VerificationStatusV0;
use adva_witness::load_adva_document_v0;
use std::path::PathBuf;

const SOURCE: &str = include_str!("../../../experiments/symbol_surface/symbol-surface.adva");

#[test]
fn load_keeps_the_nine_sites_conditional_and_outputs_absent() {
    let path = PathBuf::from(env!("CARGO_MANIFEST_DIR"))
        .join("../../experiments/symbol_surface/symbol-surface.adva");
    let before = std::fs::read(&path).unwrap();
    let loaded = load_adva_document_v0(&path, "inspect").unwrap();
    assert_eq!(loaded.transition.state, LoadedFrameStateV0::Ready);
    assert!(loaded.transition.recorded_output.is_none());
    match loaded.transition.admission {
        MechanismAdmissionV0::Verify {
            status,
            remaining_subject,
        } => {
            assert_eq!(status, VerificationStatusV0::Conditional);
            let original = AdvaDocumentV0::from_json(SOURCE).unwrap();
            assert_eq!(remaining_subject, original.carriers[0].carrier.frontier);
            assert_eq!(remaining_subject.sites().len(), 9);
        }
        other => panic!("expected conditional verification admission, got {other:?}"),
    }
    assert_eq!(before, std::fs::read(path).unwrap());
}

#[test]
fn omitting_a_declared_site_does_not_close_the_envelope() {
    let mut value: serde_json::Value = serde_json::from_str(SOURCE).unwrap();
    let _ = value["frames"][0]["mechanism"]["declared_subject"]["sites"]
        .as_array_mut()
        .unwrap()
        .pop();
    let changed = serde_json::to_string(&value).unwrap();
    assert!(matches!(
        AdvaDocumentV0::from_json(&changed),
        Err(AdvaPersistenceErrorV0::Mechanism(_))
    ));
}

#[test]
fn a_partial_recorded_output_is_rejected() {
    let mut value: serde_json::Value = serde_json::from_str(SOURCE).unwrap();
    value["frames"][0]["output"]["result"] = serde_json::json!(0);
    let changed = serde_json::to_string(&value).unwrap();
    assert!(matches!(
        AdvaDocumentV0::from_json(&changed),
        Err(AdvaPersistenceErrorV0::PartialFrameOutput(FrameIdV0(0)))
    ));
}

#[test]
fn loading_does_not_resolve_or_authenticate_payload_keys() {
    let mut value: serde_json::Value = serde_json::from_str(SOURCE).unwrap();
    value["carriers"][0]["carrier"]["structure"] =
        serde_json::json!("documentary-key-with-no-payload");
    let changed = serde_json::to_string(&value).unwrap();
    let document = AdvaDocumentV0::from_json(&changed).unwrap();
    let loaded = document.load_entrypoint("inspect").unwrap();
    assert_eq!(loaded.transition.state, LoadedFrameStateV0::Ready);
    assert!(loaded.transition.recorded_output.is_none());
    assert!(matches!(
        loaded.transition.admission,
        MechanismAdmissionV0::Verify {
            status: VerificationStatusV0::Conditional,
            ..
        }
    ));
}
