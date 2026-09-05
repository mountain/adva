use adva_ir::CheckStatus;
use adva_witness::{
    ContinuityComparisonV0, ImaginationResourceV0, ProblemAwarenessV0,
    ProblemFormationContractV0, ProblemFormationStateV0, ProblemValueFrontierStateV0,
    TrustInvariantV0, ValueFeatureV0, ValueSeekingContractV0, ValueSeekingResourceV0,
    ValueSeekingRunStateV0, load_imagination_resource_v0, load_problem_awareness_v0,
    load_problem_formation_contract_v0, load_value_seeking_contract_v0,
    load_value_seeking_resource_v0, run_problem_formation_v0, run_value_seeking_v0,
};
use std::path::PathBuf;

fn fixture(name: &str) -> PathBuf {
    PathBuf::from(env!("CARGO_MANIFEST_DIR")).join(format!("../../programs/bootstrap-0/{name}"))
}

fn formed_frontier() -> adva_witness::ProblemValueFrontierV0 {
    run_problem_formation_v0(
        &ProblemAwarenessV0::first(),
        &ProblemFormationContractV0::first(),
        &ImaginationResourceV0::first(),
    )
    .unwrap()
    .output
    .evidence
    .next_frontier
}

#[test]
fn committed_inputs_match_the_two_frozen_programs() {
    assert_eq!(
        load_problem_awareness_v0(fixture("problem-awareness.adva")).unwrap(),
        ProblemAwarenessV0::first()
    );
    assert_eq!(
        load_problem_formation_contract_v0(fixture("problem-formation.adva")).unwrap(),
        ProblemFormationContractV0::first()
    );
    assert_eq!(
        load_imagination_resource_v0(fixture("imagination-resource.adva")).unwrap(),
        ImaginationResourceV0::first()
    );
    assert_eq!(
        load_value_seeking_contract_v0(fixture("value-seeking.adva")).unwrap(),
        ValueSeekingContractV0::first()
    );
    assert_eq!(
        load_value_seeking_resource_v0(fixture("value-seeking-resource.adva")).unwrap(),
        ValueSeekingResourceV0::first()
    );
}

#[test]
fn problem_formation_turns_a_real_gap_and_external_directions_into_a_problem() {
    let transition = run_problem_formation_v0(
        &ProblemAwarenessV0::first(),
        &ProblemFormationContractV0::first(),
        &ImaginationResourceV0::first(),
    )
    .unwrap();
    let frontier = &transition.output.evidence.next_frontier;
    let counterexample = &frontier.problem.counterexample;

    assert_eq!(transition.output.result.state, ProblemFormationStateV0::Formed);
    assert_eq!(transition.output.history.quorum_fault_cases_examined, 21);
    assert_eq!(counterexample.left_receipts, [0, 1, 2]);
    assert_eq!(counterexample.right_receipts, [0, 3, 4]);
    assert_eq!(counterexample.shared_domains, [0]);
    assert_eq!(counterexample.adversarial_domains, [0]);
    assert!(counterexample.honest_shared_domains.is_empty());
    assert_eq!(
        transition.output.result.introduced_vocabulary,
        ["problem-formation", "problem"]
    );
    assert_eq!(frontier.state, ProblemValueFrontierStateV0::Open);
    assert_eq!(frontier.candidate_cursor, 0);
    assert_eq!(
        transition.output.evidence.current_policy_counterexample,
        CheckStatus::Checked
    );
    assert!(frontier.problem.external_need.contains("custodians"));
    assert!(
        frontier
            .problem
            .help_first_contribution
            .contains("counterexample")
    );
}

#[test]
fn value_seeking_finds_and_fixes_the_minimum_admitted_policy() {
    let frontier = formed_frontier();
    let contract = ValueSeekingContractV0::first();
    let resource = ValueSeekingResourceV0::first();
    let transition = run_value_seeking_v0(&frontier, &contract, &resource).unwrap();
    let witness = transition.output.result.witness.as_ref().unwrap();

    assert_eq!(transition.output.result.state, ValueSeekingRunStateV0::Witness);
    assert_eq!(transition.output.history.candidates_examined, 128);
    assert_eq!(transition.output.history.rejected_by_overlap, 96);
    assert_eq!(
        transition.output.history.rejected_by_invariant_coverage,
        29
    );
    assert_eq!(transition.output.history.rejected_by_reserve, 2);
    assert_eq!(witness.candidate_ordinal, 127);
    assert_eq!(witness.selected_threshold, 4);
    assert_eq!(witness.selected_features, ValueFeatureV0::ALL);
    assert_eq!(witness.successor_quorums.len(), 5);
    assert_eq!(witness.minimum_pair_intersection, 3);
    assert_eq!(witness.guaranteed_honest_overlap, 2);
    assert_eq!(witness.remaining_domains_after_fault, 4);
    assert_eq!(witness.typed_matching.len(), TrustInvariantV0::ALL.len());
    assert_eq!(
        witness.compatible_reserve,
        ValueFeatureV0::IndependentRemeasurement
    );
    assert_eq!(witness.merge_capacity, 5);
    assert_eq!(witness.rupture_load, 4);
    assert_eq!(witness.comparison, ContinuityComparisonV0::Greater);
    assert_eq!(witness.total_cost, 9);
    assert_eq!(
        witness.introduced_vocabulary,
        ["value-seeking", "value"]
    );
    assert_eq!(
        transition.output.evidence.next_frontier.state,
        ProblemValueFrontierStateV0::Completed
    );
    assert!(
        transition
            .output
            .evidence
            .next_frontier
            .witness_digest
            .is_some()
    );
}

#[test]
fn value_search_suspends_and_resumes_at_the_same_candidate() {
    let frontier = formed_frontier();
    let contract = ValueSeekingContractV0::first();
    let first = run_value_seeking_v0(
        &frontier,
        &contract,
        &ValueSeekingResourceV0::bounded(127, 9),
    )
    .unwrap();
    assert_eq!(first.output.result.state, ValueSeekingRunStateV0::Suspended);
    assert_eq!(first.output.evidence.next_frontier.candidate_cursor, 127);

    let resumed = run_value_seeking_v0(
        &first.output.evidence.next_frontier,
        &contract,
        &ValueSeekingResourceV0::first(),
    )
    .unwrap();
    assert_eq!(resumed.output.result.state, ValueSeekingRunStateV0::Witness);
    assert_eq!(resumed.output.history.candidates_examined, 1);
    assert_eq!(
        resumed
            .output
            .result
            .witness
            .as_ref()
            .unwrap()
            .candidate_ordinal,
        127
    );
}

#[test]
fn insufficient_cost_budget_exhausts_the_declared_space_without_a_witness() {
    let transition = run_value_seeking_v0(
        &formed_frontier(),
        &ValueSeekingContractV0::first(),
        &ValueSeekingResourceV0::bounded(160, 8),
    )
    .unwrap();

    assert_eq!(transition.output.result.state, ValueSeekingRunStateV0::NoWitness);
    assert!(transition.output.result.witness.is_none());
    assert_eq!(transition.output.history.candidates_examined, 160);
    assert_eq!(transition.output.history.rejected_by_budget, 1);
    assert_eq!(transition.output.history.rejected_by_availability, 32);
    assert_eq!(
        transition.output.evidence.next_frontier.state,
        ProblemValueFrontierStateV0::Completed
    );
}

#[test]
fn problem_and_value_witness_tampering_are_rejected() {
    let mut problem_transition = run_problem_formation_v0(
        &ProblemAwarenessV0::first(),
        &ProblemFormationContractV0::first(),
        &ImaginationResourceV0::first(),
    )
    .unwrap();
    problem_transition
        .output
        .evidence
        .next_frontier
        .problem
        .counterexample
        .honest_shared_domains
        .push(1);
    assert!(problem_transition.check().is_err());

    let frontier = formed_frontier();
    let mut value_transition = run_value_seeking_v0(
        &frontier,
        &ValueSeekingContractV0::first(),
        &ValueSeekingResourceV0::first(),
    )
    .unwrap();
    value_transition
        .output
        .result
        .witness
        .as_mut()
        .unwrap()
        .guaranteed_honest_overlap = 1;
    assert!(value_transition.check().is_err());
}
