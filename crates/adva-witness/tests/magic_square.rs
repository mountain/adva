use adva_ir::CheckStatus;
use adva_witness::{
    ClosureFindingClassV0, MagicSquareCertificateV0, MagicSquareFrontierV0, MagicSquareResourceV0,
    MagicSquareSearchContractV0, MagicSquareSearchNodeV0, MagicSquareSearchStateV0,
    load_magic_square_frontier_v0, load_magic_square_resource_v0,
    load_magic_square_search_contract_v0, load_magic_square_transition_v0,
    run_magic_square_search_v0, save_magic_square_frontier_v0, save_magic_square_transition_v0,
};
use std::path::PathBuf;
use std::sync::atomic::{AtomicU64, Ordering};

static TEST_ORDINAL: AtomicU64 = AtomicU64::new(0);

fn fixture(name: &str) -> PathBuf {
    PathBuf::from(env!("CARGO_MANIFEST_DIR")).join(format!("../../programs/bootstrap-0/{name}"))
}

fn first_transition() -> adva_witness::MagicSquareTransitionV0 {
    run_magic_square_search_v0(
        &MagicSquareFrontierV0::initial(),
        &MagicSquareSearchContractV0::first(),
        &MagicSquareResourceV0::first(),
    )
    .unwrap()
}

fn temporary_path(name: &str) -> PathBuf {
    let ordinal = TEST_ORDINAL.fetch_add(1, Ordering::Relaxed);
    let directory = std::env::temp_dir().join(format!(
        "adva-magic-square-{}-{ordinal}",
        std::process::id()
    ));
    std::fs::create_dir_all(&directory).unwrap();
    directory.join(name)
}

#[test]
fn committed_inputs_match_the_frozen_experiment() {
    assert_eq!(
        load_magic_square_frontier_v0(fixture("magic-square-frontier.adva")).unwrap(),
        MagicSquareFrontierV0::initial()
    );
    assert_eq!(
        load_magic_square_search_contract_v0(fixture("magic-square-search.adva")).unwrap(),
        MagicSquareSearchContractV0::first()
    );
    assert_eq!(
        load_magic_square_resource_v0(fixture("magic-square-resource.adva")).unwrap(),
        MagicSquareResourceV0::first()
    );
}

#[test]
fn committed_first_outputs_replay_byte_for_byte() {
    let transition = first_transition();
    let recorded = load_magic_square_transition_v0(fixture("magic-square-1.adva")).unwrap();
    let frontier =
        load_magic_square_frontier_v0(fixture("magic-square-frontier-1.adva")).unwrap();

    assert_eq!(recorded, transition);
    assert_eq!(
        transition.digest().unwrap(),
        "blake3:1fe21780fec9d7efaa4c69f98705ca5bc1f64bc400ac4dfb40ddcb3de7beebad"
    );
    assert_eq!(frontier, transition.output.evidence.next_frontier);
    assert_eq!(
        frontier.digest().unwrap(),
        "blake3:7140af03d6ccbc6aaf4037618f7719ce479dd1de45a4cdb8eece72784128dbfd"
    );
    let solution = transition.output.result.solution.as_ref().unwrap();
    assert_eq!(
        solution.digest().unwrap(),
        "blake3:9eb00959f3ad3d0074114f5c3466e82595c4aa66473002ca7a1f53c107b57434"
    );
    assert_eq!(
        solution.content.digest().unwrap(),
        "blake3:53d2ca93ed78c56c3d63110c348ca3ede62c478e7dd0990f209604b6ec61a5f3"
    );
}

#[test]
fn search_finds_a_maximally_unfolding_exact_closure() {
    let transition = first_transition();
    let solution = transition.output.result.solution.as_ref().unwrap();

    assert_eq!(
        transition.output.result.state,
        MagicSquareSearchStateV0::Identity
    );
    assert_eq!(transition.output.history.nodes_expanded, 12_517);
    assert_eq!(
        transition.output.history.unselected_closure_digests.len(),
        2
    );
    assert_eq!(
        solution.content.cells,
        [1, 2, 16, 15, 13, 14, 4, 3, 12, 7, 9, 6, 8, 11, 5, 10]
    );
    assert!(solution.content.characteristic_residual.is_one());
    assert!(
        solution
            .content
            .line_witnesses
            .iter()
            .all(|line| line.additive_residual == 0 && line.sum == 34)
    );
    solution.check().unwrap();
}

#[test]
fn one_closure_unfolds_into_a_checked_interacting_family() {
    let transition = first_transition();
    let family = transition.output.evidence.closure_family.as_ref().unwrap();

    assert_eq!(family.members.len(), 16);
    assert_eq!(family.edges.len(), 48);
    assert_eq!(family.line_occurrences, 160);
    assert_eq!(family.unique_line_contents.len(), 12);
    assert_eq!(family.influences.len(), 32);
    assert_eq!(family.coherences.len(), 6);
    assert!(family.coherences.iter().all(
        |coherence| coherence.status == CheckStatus::Checked && coherence.checked_members == 16
    ));
    let occurrences = family
        .members
        .iter()
        .map(|member| member.closure.occurrence.clone())
        .collect::<std::collections::BTreeSet<_>>();
    assert_eq!(occurrences.len(), 16);
}

#[test]
fn two_fill_orders_share_an_endpoint_without_sharing_history() {
    let transition = first_transition();
    let row = transition.output.history.row_major_trace.as_ref().unwrap();
    let column = transition
        .output
        .history
        .column_major_trace
        .as_ref()
        .unwrap();

    assert_ne!(row, column);
    assert_ne!(row.assignments, column.assignments);
    assert_eq!(row.endpoint_content_digest, column.endpoint_content_digest);
    assert_eq!(
        row.remaining_factor_digests.last(),
        column.remaining_factor_digests.last()
    );
    assert_eq!(
        transition.output.evidence.common_endpoint_retained,
        CheckStatus::Checked
    );
    assert_eq!(
        transition.output.evidence.distinct_histories_retained,
        CheckStatus::Checked
    );
}

#[test]
fn arithmetic_separation_preserves_the_value_multiset_but_breaks_incidence() {
    let transition = first_transition();
    let separation = transition
        .output
        .result
        .adversarial_separation
        .as_ref()
        .unwrap();

    assert_eq!(separation.class, ClosureFindingClassV0::Separation);
    assert!(separation.characteristic_residual.is_one());
    assert!(!separation.failed_lines.is_empty());
    assert_eq!(
        transition
            .output
            .evidence
            .separation_preserves_multiset_only,
        CheckStatus::Checked
    );
}

#[test]
fn fuel_exhaustion_can_be_resumed_to_the_same_content() {
    let initial = MagicSquareFrontierV0::initial();
    let method = MagicSquareSearchContractV0::first();
    let first =
        run_magic_square_search_v0(&initial, &method, &MagicSquareResourceV0::new(5_000)).unwrap();
    assert_eq!(
        first.output.result.state,
        MagicSquareSearchStateV0::Frontier
    );
    assert!(first.output.result.solution.is_none());

    let resumed = run_magic_square_search_v0(
        &first.output.evidence.next_frontier,
        &method,
        &MagicSquareResourceV0::new(10_000),
    )
    .unwrap();
    let direct = first_transition();
    assert_eq!(
        resumed.output.result.state,
        MagicSquareSearchStateV0::Identity
    );
    assert_eq!(
        resumed.output.result.solution.as_ref().unwrap().content,
        direct.output.result.solution.as_ref().unwrap().content
    );
    assert_ne!(
        resumed.output.history.subject_digest,
        direct.output.history.subject_digest
    );
    assert_eq!(
        first.output.history.nodes_expanded + resumed.output.history.nodes_expanded,
        direct.output.history.nodes_expanded
    );
}

#[test]
fn a_known_control_closes_without_becoming_the_search_answer() {
    let control = MagicSquareCertificateV0::from_cells(
        [16, 2, 3, 13, 5, 11, 10, 8, 9, 7, 6, 12, 4, 14, 15, 1],
        "test:duerer-control",
    )
    .unwrap();
    control.check().unwrap();
    assert_ne!(
        control.content,
        first_transition().output.result.solution.unwrap().content
    );
}

#[test]
fn malformed_frontier_and_method_drift_are_rejected() {
    let mut frontier = MagicSquareFrontierV0::initial();
    frontier.pending = vec![MagicSquareSearchNodeV0 {
        cells: [1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    }];
    assert!(frontier.check().is_err());

    let mut method = MagicSquareSearchContractV0::first();
    method.pruning.push_str(":drift");
    assert!(method.check().is_err());
    assert!(
        run_magic_square_search_v0(
            &MagicSquareFrontierV0::initial(),
            &method,
            &MagicSquareResourceV0::first(),
        )
        .is_err()
    );
}

#[test]
fn transition_tampering_is_rejected() {
    let mut transition = first_transition();
    transition.output.history.nodes_expanded += 1;
    assert!(transition.check().is_err());
}

#[test]
fn transition_and_frontier_round_trip_as_adva_files() {
    let transition = first_transition();
    let transition_path = temporary_path("magic-square-transition.adva");
    let frontier_path = temporary_path("magic-square-frontier.adva");

    save_magic_square_transition_v0(&transition_path, &transition).unwrap();
    save_magic_square_frontier_v0(&frontier_path, &transition.output.evidence.next_frontier)
        .unwrap();
    assert_eq!(
        load_magic_square_transition_v0(&transition_path).unwrap(),
        transition
    );
    assert_eq!(
        load_magic_square_frontier_v0(&frontier_path).unwrap(),
        transition.output.evidence.next_frontier
    );

    std::fs::remove_file(&transition_path).unwrap();
    std::fs::remove_dir(transition_path.parent().unwrap()).unwrap();
    std::fs::remove_file(&frontier_path).unwrap();
    std::fs::remove_dir(frontier_path.parent().unwrap()).unwrap();
}
