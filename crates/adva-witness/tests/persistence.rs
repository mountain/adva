use adva_ir::CheckStatus;
use adva_witness::{
    ADVA_DOCUMENT_SCHEMA_V0, ADVA_DOCUMENT_VERSION_V0, AdvaDocumentV0,
    AdvaPersistenceErrorV0, ArtifactKeyV0, CarrierIdV0, EntryPointV0, FrameIdV0,
    FrameInputV0, FrameMechanismV0, FrameOutputV0, FrontierSiteV0, LoadedFrameStateV0,
    MechanismAdmissionV0, MechanismFormV0, NeutralCarrierV0, OpenFrontierV0, RoleV0,
    StoredCarrierV0, StoredFillAssignmentV0, StoredFillPlanV0, TransitionFrameV0,
    load_adva_document_v0, save_adva_document_v0,
};
use std::path::PathBuf;
use std::sync::atomic::{AtomicU64, Ordering};

static TEST_DIRECTORY_ORDINAL: AtomicU64 = AtomicU64::new(0);

fn key(name: &str) -> ArtifactKeyV0 {
    ArtifactKeyV0::cache_label(format!("test:{name}")).unwrap()
}

fn carrier(name: &str, sites: impl IntoIterator<Item = FrontierSiteV0>) -> NeutralCarrierV0 {
    NeutralCarrierV0 {
        structure: key(name),
        frontier: OpenFrontierV0::from_sites(sites).unwrap(),
    }
}

fn stored(id: u32, name: &str, sites: impl IntoIterator<Item = FrontierSiteV0>) -> StoredCarrierV0 {
    StoredCarrierV0::new(CarrierIdV0::new(id), carrier(name, sites))
}

fn reusable_document(prefix: &str) -> AdvaDocumentV0 {
    AdvaDocumentV0::new(
        vec![
            stored(0, &format!("{prefix}-subject"), []),
            stored(
                1,
                &format!("{prefix}-method"),
                [FrontierSiteV0::new(RoleV0::Time, 2, 0)],
            ),
            stored(2, &format!("{prefix}-object"), []),
            stored(3, &format!("{prefix}-history"), []),
            stored(4, &format!("{prefix}-result"), []),
            stored(
                5,
                &format!("{prefix}-evidence"),
                [FrontierSiteV0::new(RoleV0::Construction, 0, 1)],
            ),
        ],
        vec![
            TransitionFrameV0 {
                id: FrameIdV0::new(0),
                input: FrameInputV0::new(
                    CarrierIdV0::new(0),
                    CarrierIdV0::new(1),
                    CarrierIdV0::new(2),
                ),
                mechanism: FrameMechanismV0::Compute,
                output: FrameOutputV0::recorded(
                    CarrierIdV0::new(3),
                    CarrierIdV0::new(4),
                    CarrierIdV0::new(5),
                ),
            },
            TransitionFrameV0 {
                id: FrameIdV0::new(1),
                input: FrameInputV0::new(
                    CarrierIdV0::new(4),
                    CarrierIdV0::new(5),
                    CarrierIdV0::new(3),
                ),
                mechanism: FrameMechanismV0::Compute,
                output: FrameOutputV0::ready(),
            },
        ],
        vec![
            EntryPointV0 {
                name: "replay".to_owned(),
                frame: FrameIdV0::new(1),
            },
            EntryPointV0 {
                name: "start".to_owned(),
                frame: FrameIdV0::new(0),
            },
        ],
    )
    .unwrap()
}

fn temporary_path(name: &str) -> PathBuf {
    let ordinal = TEST_DIRECTORY_ORDINAL.fetch_add(1, Ordering::Relaxed);
    let directory = std::env::temp_dir().join(format!(
        "adva-neutral-graph-persistence-{}-{ordinal}",
        std::process::id()
    ));
    std::fs::create_dir_all(&directory).unwrap();
    directory.join(name)
}

#[test]
fn document_round_trip_keeps_carriers_neutral_and_mechanisms_on_frames() {
    let document = reusable_document("round-trip");
    let encoded = document.to_json().unwrap();
    let decoded = AdvaDocumentV0::from_json(&encoded).unwrap();
    let loaded = decoded.load_entrypoint("start").unwrap();

    assert_eq!(decoded, document);
    assert_eq!(loaded.transition.frame, FrameIdV0::new(0));
    assert_eq!(loaded.transition.state, LoadedFrameStateV0::Recorded);
    assert!(matches!(
        loaded.transition.admission,
        MechanismAdmissionV0::Compute { .. }
    ));
    assert!(loaded.transition.recorded_output.is_some());
    assert_eq!(loaded.certificate.schema, ADVA_DOCUMENT_SCHEMA_V0);
    assert_eq!(loaded.certificate.version, ADVA_DOCUMENT_VERSION_V0);
    assert_eq!(loaded.certificate.schema_and_version, CheckStatus::Checked);
    assert_eq!(loaded.certificate.canonical_tables, CheckStatus::Checked);
    assert_eq!(loaded.certificate.resolved_references, CheckStatus::Checked);
    assert_eq!(loaded.certificate.mechanism_forms, CheckStatus::Checked);
    assert!(loaded.certificate.document_digest.starts_with("blake3:"));

    let value = serde_json::to_value(document).unwrap();
    assert!(value["carriers"][0]["carrier"].get("mechanism").is_none());
    assert_eq!(value["frames"][0]["mechanism"]["kind"], "compute");
}

#[test]
fn a_recorded_output_triple_can_be_reused_by_a_later_ready_frame() {
    let loaded = reusable_document("reuse").load_entrypoint("replay").unwrap();
    assert_eq!(loaded.transition.state, LoadedFrameStateV0::Ready);
    assert!(loaded.transition.recorded_output.is_none());
    let MechanismFormV0::Compute { input } = loaded.transition.form else {
        panic!("expected compute form");
    };
    assert_eq!(input.subject.structure.as_str(), "test:reuse-result");
    assert_eq!(input.method.structure.as_str(), "test:reuse-evidence");
    assert_eq!(input.object.structure.as_str(), "test:reuse-history");
}

#[test]
fn learning_replacement_is_resolved_from_the_same_neutral_carrier_table() {
    let open = FrontierSiteV0::new(RoleV0::Space, 1, 0);
    let document = AdvaDocumentV0::new(
        vec![
            stored(0, "learn-subject", [open.clone()]),
            stored(1, "learn-method", []),
            stored(2, "learn-object", []),
            stored(3, "learn-replacement", []),
        ],
        vec![TransitionFrameV0 {
            id: FrameIdV0::new(0),
            input: FrameInputV0::new(
                CarrierIdV0::new(0),
                CarrierIdV0::new(1),
                CarrierIdV0::new(2),
            ),
            mechanism: FrameMechanismV0::Learn {
                plan: StoredFillPlanV0 {
                    assignments: vec![StoredFillAssignmentV0 {
                        target: open,
                        replacement: CarrierIdV0::new(3),
                        evidence: None,
                    }],
                },
            },
            output: FrameOutputV0::ready(),
        }],
        vec![EntryPointV0 {
            name: "learn".to_owned(),
            frame: FrameIdV0::new(0),
        }],
    )
    .unwrap();

    let loaded = document.load_entrypoint("learn").unwrap();
    assert!(matches!(
        loaded.transition.admission,
        MechanismAdmissionV0::Learn { .. }
    ));
    let MechanismFormV0::Learn { plan, .. } = loaded.transition.form else {
        panic!("expected learn form");
    };
    assert_eq!(
        plan.assignments[0].replacement.structure.as_str(),
        "test:learn-replacement"
    );
}

#[test]
fn graph_validation_rejects_unknown_repeated_and_partial_boundary_references() {
    let mut unknown = reusable_document("unknown");
    unknown.frames[0].input.subject = CarrierIdV0::new(99);
    assert!(matches!(
        AdvaDocumentV0::from_json(&serde_json::to_string(&unknown).unwrap()),
        Err(AdvaPersistenceErrorV0::UnknownCarrierReference { .. })
    ));

    let mut repeated = reusable_document("repeated");
    repeated.frames[0].input.method = repeated.frames[0].input.subject;
    assert!(matches!(
        AdvaDocumentV0::from_json(&serde_json::to_string(&repeated).unwrap()),
        Err(AdvaPersistenceErrorV0::RepeatedBoundaryCarrier { .. })
    ));

    let mut partial = reusable_document("partial");
    partial.frames[0].output.evidence = None;
    assert!(matches!(
        AdvaDocumentV0::from_json(&serde_json::to_string(&partial).unwrap()),
        Err(AdvaPersistenceErrorV0::PartialFrameOutput(FrameIdV0(0)))
    ));
}

#[test]
fn decoding_rejects_wrong_versions_empty_keys_and_noncanonical_tables() {
    let document = reusable_document("tamper");
    let mut wrong_version = serde_json::to_value(&document).unwrap();
    wrong_version["version"] = serde_json::json!(1);
    assert!(matches!(
        AdvaDocumentV0::from_json(&serde_json::to_string(&wrong_version).unwrap()),
        Err(AdvaPersistenceErrorV0::UnsupportedDocument { .. })
    ));

    let mut empty_key = serde_json::to_value(&document).unwrap();
    empty_key["carriers"][0]["carrier"]["structure"] = serde_json::json!("");
    assert!(matches!(
        AdvaDocumentV0::from_json(&serde_json::to_string(&empty_key).unwrap()),
        Err(AdvaPersistenceErrorV0::EmptyArtifactKey(CarrierIdV0(0)))
    ));

    let mut noncanonical = document;
    noncanonical.carriers.swap(0, 1);
    assert!(matches!(
        AdvaDocumentV0::from_json(&serde_json::to_string(&noncanonical).unwrap()),
        Err(AdvaPersistenceErrorV0::NonCanonicalCarrierTable { .. })
    ));
}

#[test]
fn file_save_is_atomic_replace_and_load_selects_a_checked_entrypoint() {
    let path = temporary_path("round-trip.adva");
    let first = save_adva_document_v0(&path, reusable_document("first")).unwrap();
    assert_eq!(first.path, path);
    assert!(first.bytes_written > 0);
    let first_loaded = load_adva_document_v0(&path, "replay").unwrap();
    assert_eq!(first_loaded.transition.frame, FrameIdV0::new(1));
    assert_eq!(
        first_loaded.certificate.document_digest,
        first.document_digest
    );

    let second = save_adva_document_v0(&path, reusable_document("second")).unwrap();
    let second_loaded = load_adva_document_v0(&path, "start").unwrap();
    assert_eq!(second_loaded.transition.frame, FrameIdV0::new(0));
    assert_eq!(
        second_loaded.certificate.document_digest,
        second.document_digest
    );
    assert_ne!(first.document_digest, second.document_digest);

    let directory = path.parent().unwrap().to_path_buf();
    std::fs::remove_file(path).unwrap();
    std::fs::remove_dir(directory).unwrap();
}

#[test]
fn file_boundary_refuses_non_adva_paths_without_creating_them() {
    let path = temporary_path("not-a-program.json");
    assert!(matches!(
        save_adva_document_v0(&path, reusable_document("wrong-suffix")),
        Err(AdvaPersistenceErrorV0::InvalidExtension(_))
    ));
    assert!(!path.exists());
    let directory = path.parent().unwrap().to_path_buf();
    std::fs::remove_dir(directory).unwrap();
}
