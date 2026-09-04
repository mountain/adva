use adva_ir::CheckStatus;
use adva_witness::{
    ADVA_DOCUMENT_SCHEMA_V0, ADVA_DOCUMENT_VERSION_V0, AdvaDocumentV0, AdvaPersistenceErrorV0,
    ArtifactKeyV0, CarrierRouteV0, FrontierSiteV0, InputLabelV0, MechanismInputV0,
    MechanismOutputV0, NeutralCarrierV0, OpenFrontierV0, OutputLabelV0, ReloadPlanV0, RoleV0,
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

fn output(prefix: &str) -> MechanismOutputV0 {
    MechanismOutputV0 {
        history: carrier(
            &format!("{prefix}-history"),
            [FrontierSiteV0::new(RoleV0::Time, 2, 0)],
        ),
        result: carrier(&format!("{prefix}-result"), []),
        evidence: carrier(
            &format!("{prefix}-evidence"),
            [FrontierSiteV0::new(RoleV0::Construction, 0, 1)],
        ),
    }
}

fn route_plan() -> ReloadPlanV0 {
    ReloadPlanV0::from_routes([
        CarrierRouteV0::new(OutputLabelV0::Evidence, InputLabelV0::Method),
        CarrierRouteV0::new(OutputLabelV0::History, InputLabelV0::Object),
        CarrierRouteV0::new(OutputLabelV0::Result, InputLabelV0::Subject),
    ])
    .unwrap()
}

fn expected_input(prefix: &str) -> MechanismInputV0 {
    let output = output(prefix);
    MechanismInputV0 {
        subject: output.result,
        method: output.evidence,
        object: output.history,
    }
}

fn temporary_path(name: &str) -> PathBuf {
    let ordinal = TEST_DIRECTORY_ORDINAL.fetch_add(1, Ordering::Relaxed);
    let directory = std::env::temp_dir().join(format!(
        "adva-neutral-persistence-{}-{ordinal}",
        std::process::id()
    ));
    std::fs::create_dir_all(&directory).unwrap();
    directory.join(name)
}

#[test]
fn document_round_trip_requires_an_explicit_exact_slot_bijection() {
    let document = AdvaDocumentV0::from_output(output("first")).unwrap();
    let encoded = document.to_json().unwrap();
    let decoded = AdvaDocumentV0::from_json(&encoded).unwrap();
    let loaded = decoded.reload(&route_plan()).unwrap();

    assert_eq!(decoded, document);
    assert_eq!(loaded.input, expected_input("first"));
    assert_eq!(loaded.certificate.schema, ADVA_DOCUMENT_SCHEMA_V0);
    assert_eq!(loaded.certificate.version, ADVA_DOCUMENT_VERSION_V0);
    assert_eq!(loaded.certificate.schema_and_version, CheckStatus::Checked);
    assert_eq!(loaded.certificate.canonical_frontiers, CheckStatus::Checked);
    assert_eq!(
        loaded.certificate.exact_slot_bijection,
        CheckStatus::Checked
    );
    assert!(loaded.certificate.document_digest.starts_with("blake3:"));
    assert_eq!(
        loaded
            .certificate
            .routes
            .map(|route| (route.from, route.to)),
        [
            (OutputLabelV0::Result, InputLabelV0::Subject),
            (OutputLabelV0::Evidence, InputLabelV0::Method),
            (OutputLabelV0::History, InputLabelV0::Object),
        ]
    );
}

#[test]
fn reload_rejects_copy_and_contraction_at_the_slot_boundary() {
    let repeated_output = ReloadPlanV0 {
        routes: [
            CarrierRouteV0::new(OutputLabelV0::Result, InputLabelV0::Subject),
            CarrierRouteV0::new(OutputLabelV0::Result, InputLabelV0::Method),
            CarrierRouteV0::new(OutputLabelV0::History, InputLabelV0::Object),
        ],
    };
    assert!(matches!(
        AdvaDocumentV0::from_output(output("copy"))
            .unwrap()
            .reload(&repeated_output),
        Err(AdvaPersistenceErrorV0::RepeatedOutputRoute(
            OutputLabelV0::Result
        ))
    ));

    let repeated_input = ReloadPlanV0 {
        routes: [
            CarrierRouteV0::new(OutputLabelV0::Result, InputLabelV0::Subject),
            CarrierRouteV0::new(OutputLabelV0::Evidence, InputLabelV0::Subject),
            CarrierRouteV0::new(OutputLabelV0::History, InputLabelV0::Object),
        ],
    };
    assert!(matches!(
        AdvaDocumentV0::from_output(output("contraction"))
            .unwrap()
            .reload(&repeated_input),
        Err(AdvaPersistenceErrorV0::RepeatedInputRoute(
            InputLabelV0::Subject
        ))
    ));
}

#[test]
fn decoding_rejects_wrong_versions_empty_keys_and_noncanonical_frontiers() {
    let document = AdvaDocumentV0::from_output(output("tamper")).unwrap();
    let mut wrong_version = serde_json::to_value(&document).unwrap();
    wrong_version["version"] = serde_json::json!(1);
    assert!(matches!(
        AdvaDocumentV0::from_json(&serde_json::to_string(&wrong_version).unwrap()),
        Err(AdvaPersistenceErrorV0::UnsupportedDocument { .. })
    ));

    let mut empty_key = serde_json::to_value(&document).unwrap();
    empty_key["output"]["result"]["structure"] = serde_json::json!("");
    assert!(matches!(
        AdvaDocumentV0::from_json(&serde_json::to_string(&empty_key).unwrap()),
        Err(AdvaPersistenceErrorV0::EmptyArtifactKey(
            OutputLabelV0::Result
        ))
    ));

    let mut noncanonical = serde_json::to_value(&document).unwrap();
    noncanonical["output"]["history"]["frontier"]["sites"] = serde_json::json!([
        {"role": "time", "hole": 2, "occurrence": 1},
        {"role": "construction", "hole": 0, "occurrence": 0}
    ]);
    assert!(matches!(
        AdvaDocumentV0::from_json(&serde_json::to_string(&noncanonical).unwrap()),
        Err(AdvaPersistenceErrorV0::NonCanonicalFrontier(
            OutputLabelV0::History
        ))
    ));
}

#[test]
fn file_save_is_atomic_replace_and_load_revalidates_before_relabelling() {
    let path = temporary_path("round-trip.adva");
    let first = save_adva_document_v0(&path, output("first")).unwrap();
    assert_eq!(first.path, path);
    assert!(first.bytes_written > 0);
    let first_loaded = load_adva_document_v0(&path, &route_plan()).unwrap();
    assert_eq!(first_loaded.input, expected_input("first"));
    assert_eq!(
        first_loaded.certificate.document_digest,
        first.document_digest
    );

    let second = save_adva_document_v0(&path, output("second")).unwrap();
    let second_loaded = load_adva_document_v0(&path, &route_plan()).unwrap();
    assert_eq!(second_loaded.input, expected_input("second"));
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
        save_adva_document_v0(&path, output("wrong-suffix")),
        Err(AdvaPersistenceErrorV0::InvalidExtension(_))
    ));
    assert!(!path.exists());
    let directory = path.parent().unwrap().to_path_buf();
    std::fs::remove_dir(directory).unwrap();
}
