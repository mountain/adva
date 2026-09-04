use adva_ir::CheckStatus;
use adva_witness::{
    ClosureFindingClassV0, ClosureFrontierStateV0, ClosureTransportContractV0,
    ClosureTransportPlanV0, LocalClosureCandidateV0, WitnessProofV0,
    load_closure_transport_frontier_v0, load_closure_transport_transition_v0,
    run_closure_transport_v0, save_closure_transport_frontier_v0,
    save_closure_transport_transition_v0,
};
use std::path::PathBuf;
use std::sync::atomic::{AtomicU64, Ordering};

static TEST_ORDINAL: AtomicU64 = AtomicU64::new(0);

fn first_transition() -> adva_witness::ClosureTransportTransitionV0 {
    run_closure_transport_v0(
        &LocalClosureCandidateV0::first_distributivity(),
        &ClosureTransportContractV0::first_exact_polynomial(),
        &ClosureTransportPlanV0::first_experiment(),
    )
    .unwrap()
}

fn temporary_path(name: &str) -> PathBuf {
    let ordinal = TEST_ORDINAL.fetch_add(1, Ordering::Relaxed);
    let directory = std::env::temp_dir().join(format!(
        "adva-closure-transport-{}-{ordinal}",
        std::process::id()
    ));
    std::fs::create_dir_all(&directory).unwrap();
    directory.join(name)
}

#[test]
fn distributivity_produces_a_replayable_two_node_closure_certificate() {
    let transition = first_transition();
    let local = &transition.output.result.local;

    assert_eq!(local.witness_graph.len(), 2);
    assert!(matches!(
        &local.witness_graph[0].proof,
        WitnessProofV0::ArithmeticTransition { .. }
    ));
    assert!(matches!(
        &local.witness_graph[1].proof,
        WitnessProofV0::Seal { .. }
    ));
    assert!(local.witness_graph[1].summary.is_formed());
    assert!(local.witness_graph[1].summary.is_multiplicatively_closed());
    local.check().unwrap();
}

#[test]
fn direct_and_staged_transport_share_a_result_but_not_a_history() {
    let transition = first_transition();
    let result = &transition.output.result;
    let history = &transition.output.history;

    assert_eq!(result.staged, result.direct);
    assert_eq!(result.coherence.direct_equals_staged, CheckStatus::Checked);
    assert_eq!(result.coherence.composed_scope_map, CheckStatus::Checked);
    assert_eq!(
        result.coherence.distinct_histories_retained,
        CheckStatus::Checked
    );
    assert_ne!(history.stage_two, history.direct);
    assert_ne!(history.stage_two.map_digest, history.direct.map_digest);
    assert_ne!(
        history.stage_two.source_certificate_digest,
        history.direct.source_certificate_digest
    );
    assert_eq!(
        history.stage_two.result_certificate_digest,
        history.direct.result_certificate_digest
    );
}

#[test]
fn typed_negative_controls_reject_polynomial_import_into_m6_obligations() {
    let transition = first_transition();
    let outcomes = &transition.output.result.negative_controls;

    assert!(outcomes.iter().all(|outcome| {
        !outcome.accepted && outcome.class == ClosureFindingClassV0::Incommensurate
    }));
    assert!(
        outcomes
            .iter()
            .all(|outcome| outcome.supplied_unit != outcome.target.required_unit)
    );
}

#[test]
fn arithmetic_adversary_is_named_separation_and_carries_a_counterexample() {
    let transition = first_transition();
    let separation = &transition.output.result.adversarial_separation;

    assert_eq!(separation.class, ClosureFindingClassV0::Separation);
    assert_ne!(separation.before_normal_form, separation.after_normal_form);
    assert_ne!(separation.before_value, separation.after_value);
    assert_eq!(separation.before_value.to_string(), "16");
    assert_eq!(separation.after_value.to_string(), "11");
    separation.check().unwrap();
}

#[test]
fn a_challenge_reopens_the_dependency_cone_without_erasing_certificates() {
    let transition = first_transition();
    let evidence = &transition.output.evidence;
    let frontier = &evidence.residual_frontier;

    assert_eq!(frontier.state, ClosureFrontierStateV0::Reopened);
    assert_eq!(frontier.closed_before_challenge.len(), 3);
    assert_eq!(
        frontier.closed_before_challenge,
        frontier.reopened_after_challenge
    );
    assert_eq!(frontier.retained_certificate_digests.len(), 4);
    assert_eq!(evidence.counterevidence_admitted, CheckStatus::Checked);
    assert_eq!(
        evidence.counterevidence_class,
        ClosureFindingClassV0::Challenge
    );
    assert_eq!(
        evidence.counterevidence_proves_falsity,
        CheckStatus::Unchecked
    );
    assert_eq!(
        evidence.certificates_remain_append_only,
        CheckStatus::Checked
    );
}

#[test]
fn post_hoc_acceptance_of_a_negative_control_is_rejected() {
    let mut transition = first_transition();
    transition.output.result.negative_controls[0].accepted = true;

    assert!(transition.check().is_err());
}

#[test]
fn frozen_method_rejects_semantic_drift() {
    let mut method = ClosureTransportContractV0::first_exact_polynomial();
    method.name.push_str(":drifted");

    assert!(method.check().is_err());
    assert!(
        run_closure_transport_v0(
            &LocalClosureCandidateV0::first_distributivity(),
            &method,
            &ClosureTransportPlanV0::first_experiment(),
        )
        .is_err()
    );
}

#[test]
fn transition_and_reopened_frontier_round_trip_as_adva_files() {
    let transition = first_transition();
    let transition_path = temporary_path("closure-transport.adva");
    let frontier_path = temporary_path("closure-frontier.adva");

    save_closure_transport_transition_v0(&transition_path, &transition).unwrap();
    save_closure_transport_frontier_v0(
        &frontier_path,
        &transition.output.evidence.residual_frontier,
    )
    .unwrap();
    assert_eq!(
        load_closure_transport_transition_v0(&transition_path).unwrap(),
        transition
    );
    assert_eq!(
        load_closure_transport_frontier_v0(&frontier_path).unwrap(),
        transition.output.evidence.residual_frontier
    );

    std::fs::remove_file(&transition_path).unwrap();
    std::fs::remove_dir(transition_path.parent().unwrap()).unwrap();
    std::fs::remove_file(&frontier_path).unwrap();
    std::fs::remove_dir(frontier_path.parent().unwrap()).unwrap();
}
