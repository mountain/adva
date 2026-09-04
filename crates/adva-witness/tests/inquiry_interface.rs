use adva_witness::{
    ExplorationContractV0, HypothesisStateV0, InquiryErrorV0, InquiryInterfaceV0,
    InquiryObligationStateV0, MechanismV0, ResourceSnapshotV0, TypedUnitV0, VocabularyRoleV0,
    derive_inquiry_frontier_from_file_v0, learn_hypothesis_v0, load_exploration_contract_v0,
    load_hypothesis_transition_v0, load_inquiry_frontier_v0, load_resource_snapshot_v0,
    save_hypothesis_transition_v0, save_inquiry_frontier_v0,
};
use std::path::PathBuf;
use std::sync::atomic::{AtomicU64, Ordering};

static TEST_ORDINAL: AtomicU64 = AtomicU64::new(0);

fn fixture(name: &str) -> PathBuf {
    PathBuf::from(env!("CARGO_MANIFEST_DIR")).join(format!("../../programs/bootstrap-0/{name}"))
}

fn first_frontier() -> adva_witness::InquiryFrontierV0 {
    derive_inquiry_frontier_from_file_v0(fixture("first-trace-arithmetic.adva")).unwrap()
}

fn first_contract() -> ExplorationContractV0 {
    load_exploration_contract_v0(fixture("exploration.adva")).unwrap()
}

fn first_resource() -> ResourceSnapshotV0 {
    load_resource_snapshot_v0(fixture("resource.adva")).unwrap()
}

fn temporary_path(name: &str) -> PathBuf {
    let ordinal = TEST_ORDINAL.fetch_add(1, Ordering::Relaxed);
    let directory = std::env::temp_dir().join(format!(
        "adva-inquiry-interface-{}-{ordinal}",
        std::process::id()
    ));
    std::fs::create_dir_all(&directory).unwrap();
    directory.join(name)
}

#[test]
fn arithmetic_questions_become_five_open_typed_obligations() {
    let frontier = first_frontier();

    assert_eq!(frontier.interface, InquiryInterfaceV0::canonical());
    assert_eq!(frontier.lineage.sequence, 0);
    assert_eq!(frontier.obligations.len(), 5);
    assert!(
        frontier
            .obligations
            .iter()
            .all(|obligation| obligation.state == InquiryObligationStateV0::Open)
    );
    assert!(matches!(
        frontier.obligations[0].typed_unit,
        TypedUnitV0::CharacteristicWitness { .. }
    ));
    assert_eq!(
        frontier.obligations[3].typed_unit,
        TypedUnitV0::MultiplicativeIdentity
    );
    assert_eq!(
        frontier.obligations[4].typed_unit,
        TypedUnitV0::SharedTruthCoordinate
    );
    assert_eq!(frontier.vocabulary.len(), 1);
    assert_eq!(frontier.vocabulary[0].local_name, "frontier");
    frontier.check().unwrap();
}

#[test]
fn one_learning_edge_preserves_the_interface_and_all_open_questions() {
    let frontier = first_frontier();
    let contract = first_contract();
    let resource = first_resource();
    let transition = learn_hypothesis_v0(&frontier, &contract, &resource).unwrap();
    let next = &transition.output.evidence.next_frontier;

    assert_eq!(contract.mechanism, MechanismV0::Learn);
    assert_eq!(transition.interface, InquiryInterfaceV0::canonical());
    assert_eq!(transition.input.subject, frontier);
    assert_eq!(transition.input.method, contract);
    assert_eq!(transition.input.object, resource);
    assert_eq!(transition.output.result.local_name, "representation");
    assert_eq!(transition.output.result.state, HypothesisStateV0::Proposed);
    assert_eq!(next.lineage.sequence, 1);
    assert_eq!(next.obligations, transition.input.subject.obligations);
    assert!(
        next.obligations
            .iter()
            .all(|obligation| obligation.state == InquiryObligationStateV0::Open)
    );
    assert_eq!(
        transition.output.history.introduced_words,
        ["hypothesis", "representation"]
    );
    assert!(next.vocabulary.iter().any(|entry| {
        entry.local_name == "hypothesis" && entry.role == VocabularyRoleV0::Hypothesis
    }));
    assert!(next.vocabulary.iter().any(|entry| {
        entry.local_name == "representation" && entry.role == VocabularyRoleV0::Candidate
    }));
    transition.check().unwrap();
}

#[test]
fn committed_first_inquiry_outputs_replay_exactly() {
    let frontier = first_frontier();
    let recorded_frontier = load_inquiry_frontier_v0(fixture("frontier.adva")).unwrap();
    assert_eq!(recorded_frontier, frontier);
    assert_eq!(
        frontier.digest().unwrap(),
        "blake3:fc9ab7afe284ac122e67bf6fa659318a8c264f5dbaed654fd2540fad6f3e1e1f"
    );

    let transition =
        learn_hypothesis_v0(&frontier, &first_contract(), &first_resource()).unwrap();
    let recorded_transition =
        load_hypothesis_transition_v0(fixture("hypothesis.adva")).unwrap();
    assert_eq!(recorded_transition, transition);
    assert_eq!(
        transition.digest().unwrap(),
        "blake3:cd93301f498db9b118a820ef2f90522b85caadd676e25a8d387ca32222cc2cd0"
    );

    let recorded_next = load_inquiry_frontier_v0(fixture("frontier-1.adva")).unwrap();
    assert_eq!(recorded_next, transition.output.evidence.next_frontier);
    assert_eq!(
        recorded_next.digest().unwrap(),
        "blake3:2b0c3440a8dafda28880cea92d9d87d0158d49a08d2cd9a20d4406990d0786de"
    );
    assert_eq!(
        first_resource().digest().unwrap(),
        "blake3:41b2260753e4df9ee94918604bfead06b353390f41c6adf981c7bcbd12686858"
    );
}

#[test]
fn candidate_identity_does_not_depend_on_its_local_name() {
    let frontier = first_frontier();
    let contract = first_contract();
    let resource = first_resource();
    let first = learn_hypothesis_v0(&frontier, &contract, &resource).unwrap();
    let mut renamed_resource = resource;
    renamed_resource.candidates[0].local_name = "rho-candidate".to_owned();
    let renamed = learn_hypothesis_v0(&frontier, &contract, &renamed_resource).unwrap();

    assert_eq!(
        first.output.result.identity_digest,
        renamed.output.result.identity_digest
    );
    assert_ne!(
        first.output.result.local_name,
        renamed.output.result.local_name
    );
    assert_ne!(
        first.output.result.resource_digest,
        renamed.output.result.resource_digest
    );
}

#[test]
fn a_transition_rejects_post_hoc_randomness_edits() {
    let mut transition =
        learn_hypothesis_v0(&first_frontier(), &first_contract(), &first_resource()).unwrap();
    transition.input.object.entropy.value = "0".repeat(64);

    assert!(matches!(
        transition.check(),
        Err(InquiryErrorV0::InvalidArtifact(_))
    ));
}

#[test]
fn a_continuation_rejects_resource_replay_and_algorithm_drift() {
    let resource = first_resource();
    let transition = learn_hypothesis_v0(&first_frontier(), &first_contract(), &resource).unwrap();
    let next = transition.output.evidence.next_frontier;

    assert!(matches!(
        learn_hypothesis_v0(&next, &first_contract(), &resource),
        Err(InquiryErrorV0::ResourceReplay(_))
    ));

    let mut drifted = next;
    drifted.lineage.algorithm_contract_digest = Some(format!("blake3:{}", "0".repeat(64)));
    drifted.check().unwrap();
    assert!(matches!(
        learn_hypothesis_v0(&drifted, &first_contract(), &first_resource()),
        Err(InquiryErrorV0::AlgorithmDrift { .. })
    ));
}

#[test]
fn question_coordinates_cannot_be_renamed_at_the_interface() {
    let mut frontier = first_frontier();
    frontier.obligations[0].id =
        adva_witness::ArtifactKeyV0::cache_label("renamed-question").unwrap();

    assert!(matches!(
        frontier.check(),
        Err(InquiryErrorV0::InvalidArtifact(_))
    ));
}

#[test]
fn frontier_and_transition_round_trip_as_checked_adva_files() {
    let frontier = first_frontier();
    let transition = learn_hypothesis_v0(&frontier, &first_contract(), &first_resource()).unwrap();
    let frontier_path = temporary_path("frontier.adva");
    let transition_path = temporary_path("hypothesis.adva");

    let frontier_receipt = save_inquiry_frontier_v0(&frontier_path, &frontier).unwrap();
    let transition_receipt = save_hypothesis_transition_v0(&transition_path, &transition).unwrap();
    assert_eq!(load_inquiry_frontier_v0(&frontier_path).unwrap(), frontier);
    assert_eq!(
        load_hypothesis_transition_v0(&transition_path).unwrap(),
        transition
    );
    assert!(frontier_receipt.artifact_digest.starts_with("blake3:"));
    assert!(transition_receipt.artifact_digest.starts_with("blake3:"));

    std::fs::remove_file(&frontier_path).unwrap();
    std::fs::remove_dir(frontier_path.parent().unwrap()).unwrap();
    std::fs::remove_file(&transition_path).unwrap();
    std::fs::remove_dir(transition_path.parent().unwrap()).unwrap();
}
