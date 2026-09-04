use adva_witness::{
    InquiryObligationStateV0, VerificationActionV0, VerificationDecisionV0,
    VerificationFrontierStateV0, VerificationObligationRoleV0, VerificationObligationStateV0,
    VerificationSubjectV0, load_inquiry_frontier_v0, load_verification_contract_v0,
    load_verification_frontier_v0, load_verification_packet_v0, load_verification_transition_v0,
    save_verification_frontier_v0, save_verification_transition_v0, verify_obligations_v0,
};
use std::path::PathBuf;
use std::sync::atomic::{AtomicU64, Ordering};

static TEST_ORDINAL: AtomicU64 = AtomicU64::new(0);

fn fixture(name: &str) -> PathBuf {
    PathBuf::from(env!("CARGO_MANIFEST_DIR")).join(format!("../../programs/bootstrap-0/{name}"))
}

fn initial_subject() -> VerificationSubjectV0 {
    VerificationSubjectV0::InquiryFrontier(Box::new(
        load_inquiry_frontier_v0(fixture("frontier-2.adva")).unwrap(),
    ))
}

fn temporary_path(name: &str) -> PathBuf {
    let ordinal = TEST_ORDINAL.fetch_add(1, Ordering::Relaxed);
    let directory = std::env::temp_dir().join(format!(
        "adva-verification-boundary-{}-{ordinal}",
        std::process::id()
    ));
    std::fs::create_dir_all(&directory).unwrap();
    directory.join(name)
}

#[test]
fn first_verification_edge_refines_five_roots_into_eight_typed_leaves() {
    let subject = initial_subject();
    let contract = load_verification_contract_v0(fixture("verification.adva")).unwrap();
    let packet = load_verification_packet_v0(fixture("refinement-1.adva")).unwrap();
    let transition = verify_obligations_v0(&subject, &contract, &packet).unwrap();
    let next = &transition.output.evidence.residual_frontier;

    assert_eq!(transition.output.history.leaf_delta.semantic_before, 5);
    assert_eq!(transition.output.history.leaf_delta.semantic_after, 7);
    assert_eq!(transition.output.history.leaf_delta.custody_before, 0);
    assert_eq!(transition.output.history.leaf_delta.custody_after, 1);
    assert_eq!(next.obligations.len(), 13);
    assert_eq!(next.open_semantic_leaves(), 7);
    assert_eq!(next.open_custody_leaves(), 1);
    assert_eq!(next.state, VerificationFrontierStateV0::Open);
    assert!(transition.output.result.certificate.is_none());
    assert_eq!(transition.output.history.outcomes.len(), 1);
    assert_eq!(
        transition.output.history.outcomes[0].decision,
        VerificationDecisionV0::Refined
    );
    assert!(next.obligations[..5].iter().all(|obligation| matches!(
        obligation.state,
        VerificationObligationStateV0::Refined { .. }
    )));
    assert_eq!(
        next.obligations
            .iter()
            .filter(|obligation| obligation.role == VerificationObligationRoleV0::Custody)
            .count(),
        1
    );
    transition.check().unwrap();
}

#[test]
fn verification_layer_does_not_rewrite_the_inquiry_frontier() {
    let original = load_inquiry_frontier_v0(fixture("frontier-2.adva")).unwrap();
    let original_digest = original.digest().unwrap();
    let transition = verify_obligations_v0(
        &VerificationSubjectV0::InquiryFrontier(Box::new(original.clone())),
        &load_verification_contract_v0(fixture("verification.adva")).unwrap(),
        &load_verification_packet_v0(fixture("refinement-1.adva")).unwrap(),
    )
    .unwrap();
    let retained = &transition
        .output
        .evidence
        .residual_frontier
        .origin_inquiry_frontier;

    assert_eq!(retained, &original);
    assert_eq!(retained.digest().unwrap(), original_digest);
    assert!(
        retained
            .obligations
            .iter()
            .all(|obligation| { obligation.state == InquiryObligationStateV0::Open })
    );
}

#[test]
fn digest_only_discharge_is_recorded_and_refused() {
    let mut packet = load_verification_packet_v0(fixture("refinement-1.adva")).unwrap();
    packet.packet_coordinate = "test:unsupported-discharge".to_owned();
    packet.actions = vec![VerificationActionV0::Discharge {
        obligation_id: adva_witness::ArtifactKeyV0::cache_label(
            "experiment:first:m6-time-characteristic-required",
        )
        .unwrap(),
        witness_digest: format!("blake3:{}", "1".repeat(64)),
        scope_digest: format!("blake3:{}", "2".repeat(64)),
    }];
    let transition = verify_obligations_v0(
        &initial_subject(),
        &load_verification_contract_v0(fixture("verification.adva")).unwrap(),
        &packet,
    )
    .unwrap();

    assert_eq!(
        transition.output.history.outcomes[0].decision,
        VerificationDecisionV0::Rejected
    );
    assert_eq!(transition.output.result.open_semantic_leaves, 5);
    assert!(transition.output.result.certificate.is_none());
    assert!(
        transition
            .output
            .evidence
            .residual_frontier
            .obligations
            .iter()
            .all(|obligation| obligation.state == VerificationObligationStateV0::Open)
    );
    transition.check().unwrap();
}

#[test]
fn post_hoc_closure_edit_is_rejected() {
    let mut transition = verify_obligations_v0(
        &initial_subject(),
        &load_verification_contract_v0(fixture("verification.adva")).unwrap(),
        &load_verification_packet_v0(fixture("refinement-1.adva")).unwrap(),
    )
    .unwrap();
    transition.output.result.state = VerificationFrontierStateV0::ScopedClosed;

    assert!(transition.check().is_err());
}

#[test]
fn verification_transition_and_frontier_round_trip_as_adva_files() {
    let transition = verify_obligations_v0(
        &initial_subject(),
        &load_verification_contract_v0(fixture("verification.adva")).unwrap(),
        &load_verification_packet_v0(fixture("refinement-1.adva")).unwrap(),
    )
    .unwrap();
    let transition_path = temporary_path("verification.adva");
    let frontier_path = temporary_path("verification-frontier.adva");

    save_verification_transition_v0(&transition_path, &transition).unwrap();
    save_verification_frontier_v0(
        &frontier_path,
        &transition.output.evidence.residual_frontier,
    )
    .unwrap();
    assert_eq!(
        load_verification_transition_v0(&transition_path).unwrap(),
        transition
    );
    assert_eq!(
        load_verification_frontier_v0(&frontier_path).unwrap(),
        transition.output.evidence.residual_frontier
    );

    std::fs::remove_file(&transition_path).unwrap();
    std::fs::remove_dir(transition_path.parent().unwrap()).unwrap();
    std::fs::remove_file(&frontier_path).unwrap();
    std::fs::remove_dir(frontier_path.parent().unwrap()).unwrap();
}
