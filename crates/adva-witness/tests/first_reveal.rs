use adva_witness::{
    AdvaDocumentV0, FrameIdV0, M6NamingPlanV0, ObserverDomainV0, RelationFillingV0, RevealErrorV0,
    RevealQuestionKindV0, RevealRunStateV0, RevealWitnessV0, load_reveal_witness_v0,
    run_m6_reveal_v0, save_reveal_witness_v0,
};
use std::path::PathBuf;
use std::sync::atomic::{AtomicU64, Ordering};

static TEST_ORDINAL: AtomicU64 = AtomicU64::new(0);

fn first_program() -> AdvaDocumentV0 {
    let path =
        PathBuf::from(env!("CARGO_MANIFEST_DIR")).join("../../programs/bootstrap-0/reveal.adva");
    AdvaDocumentV0::from_json(&std::fs::read_to_string(path).unwrap()).unwrap()
}

fn first_witness_path() -> PathBuf {
    PathBuf::from(env!("CARGO_MANIFEST_DIR"))
        .join("../../programs/bootstrap-0/first-reveal-witness.adva")
}

fn temporary_witness_path() -> PathBuf {
    let ordinal = TEST_ORDINAL.fetch_add(1, Ordering::Relaxed);
    let directory = std::env::temp_dir().join(format!(
        "adva-first-reveal-{}-{ordinal}",
        std::process::id()
    ));
    std::fs::create_dir_all(&directory).unwrap();
    directory.join("first-reveal-witness.adva")
}

#[test]
fn first_program_forms_the_named_m6_boundary_and_retains_its_question() {
    let witness =
        run_m6_reveal_v0(&first_program(), M6NamingPlanV0::first_calibration(), 6).unwrap();

    assert_eq!(witness.state, RevealRunStateV0::Completed);
    assert_eq!(witness.fuel_used, 6);
    assert_eq!(
        witness.observed,
        ["run", "reveal", "name", "instantiate", "resume", "compile"]
    );
    assert!(witness.remaining.is_empty());
    assert_eq!(witness.questions.len(), 1);
    assert_eq!(
        witness.questions[0].kind,
        RevealQuestionKindV0::RelationFiller
    );
    let relation = witness.relation.as_ref().unwrap();
    assert_eq!(relation.left.steps.len(), 3);
    assert_eq!(relation.right.steps.len(), 3);
    assert!(matches!(
        relation.relation.filling,
        RelationFillingV0::Open { .. }
    ));
    assert!(relation.relation.transport().is_err());
    witness.check().unwrap();
}

#[test]
fn committed_first_witness_replays_the_first_run_exactly() {
    let recorded = load_reveal_witness_v0(first_witness_path()).unwrap();
    let derived =
        run_m6_reveal_v0(&first_program(), M6NamingPlanV0::first_calibration(), 6).unwrap();

    assert_eq!(recorded, derived);
    let persisted = format!("{}\n", recorded.to_json().unwrap());
    assert_eq!(
        format!("blake3:{}", blake3::hash(persisted.as_bytes()).to_hex()),
        "blake3:b03cee7f38c01f0a84fa3c71227955ce8c85ac01a844f8c47e74a06c45a0d007"
    );
}

#[test]
fn injected_names_cover_two_oppositely_oriented_domain_cycles() {
    let witness =
        run_m6_reveal_v0(&first_program(), M6NamingPlanV0::first_calibration(), 6).unwrap();

    assert_eq!(witness.forward[0].name, "run");
    assert_eq!(witness.forward[0].from, ObserverDomainV0::Construction);
    assert_eq!(witness.forward[0].to, ObserverDomainV0::Time);
    assert_eq!(witness.forward[1].name, "reveal");
    assert_eq!(witness.forward[2].name, "name");
    assert_eq!(witness.conjugate[0].name, "instantiate");
    assert_eq!(witness.conjugate[1].name, "resume");
    assert_eq!(witness.conjugate[2].name, "compile");
    assert_eq!(witness.conjugate[2].to, ObserverDomainV0::Construction);
}

#[test]
fn finite_fuel_publishes_a_suspended_witness_instead_of_claiming_failure() {
    let witness =
        run_m6_reveal_v0(&first_program(), M6NamingPlanV0::first_calibration(), 4).unwrap();

    assert_eq!(witness.state, RevealRunStateV0::Suspended);
    assert_eq!(witness.observed, ["run", "reveal", "name", "instantiate"]);
    assert_eq!(witness.remaining, ["resume", "compile"]);
    assert_eq!(witness.questions.len(), 1);
    assert_eq!(
        witness.questions[0].kind,
        RevealQuestionKindV0::FuelBoundary
    );
    assert!(witness.relation.is_none());
    witness.check().unwrap();
}

#[test]
fn a_reveal_witness_round_trips_as_a_checked_adva_file() {
    let witness =
        run_m6_reveal_v0(&first_program(), M6NamingPlanV0::first_calibration(), 6).unwrap();
    let path = temporary_witness_path();
    let receipt = save_reveal_witness_v0(&path, &witness).unwrap();
    let loaded = load_reveal_witness_v0(&path).unwrap();

    assert_eq!(loaded, witness);
    assert!(receipt.witness_digest.starts_with("blake3:"));
    assert!(receipt.bytes_written > 0);

    let mut tampered = serde_json::to_value(&witness).unwrap();
    tampered["observed"][0] = serde_json::json!("renamed-without-a-claim");
    assert!(RevealWitnessV0::from_json(&serde_json::to_string(&tampered).unwrap()).is_err());

    std::fs::remove_file(&path).unwrap();
    std::fs::remove_dir(path.parent().unwrap()).unwrap();
}

#[test]
fn malformed_or_frame_collapsing_name_injection_is_rejected() {
    let document = first_program();
    let mut malformed = M6NamingPlanV0::first_calibration();
    malformed.conjugate[2].to = ObserverDomainV0::Time;
    assert!(matches!(
        run_m6_reveal_v0(&document, malformed, 6),
        Err(RevealErrorV0::InvalidNamingPlan(_))
    ));

    let mut collapsed = first_program();
    collapsed
        .entrypoints
        .iter_mut()
        .find(|entrypoint| entrypoint.name == "compile")
        .unwrap()
        .frame = FrameIdV0::new(3);
    assert!(matches!(
        run_m6_reveal_v0(&collapsed, M6NamingPlanV0::first_calibration(), 6),
        Err(RevealErrorV0::InvalidNamingPlan(_))
    ));
}
