use adva_ir::CheckStatus;
use adva_witness::{
    HypothesisFormationContractV0, HypothesisFormationFrontierStateV0,
    HypothesisFormationFrontierV0, HypothesisFormationResourceV0,
    HypothesisFormationRunStateV0, load_hypothesis_formation_contract_v0,
    load_hypothesis_formation_frontier_v0, load_hypothesis_formation_resource_v0,
    run_hypothesis_formation_v0,
};
use std::path::PathBuf;

fn fixture(name: &str) -> PathBuf {
    PathBuf::from(env!("CARGO_MANIFEST_DIR")).join(format!("../../programs/bootstrap-0/{name}"))
}

#[test]
fn committed_inputs_match_the_frozen_hypothesis_formation_program() {
    assert_eq!(
        load_hypothesis_formation_frontier_v0(fixture("hypothesis-formation-frontier.adva"))
            .unwrap(),
        HypothesisFormationFrontierV0::initial()
    );
    assert_eq!(
        load_hypothesis_formation_contract_v0(fixture("hypothesis-formation.adva")).unwrap(),
        HypothesisFormationContractV0::first()
    );
    assert_eq!(
        load_hypothesis_formation_resource_v0(fixture("hypothesis-formation-resource.adva"))
            .unwrap(),
        HypothesisFormationResourceV0::first()
    );
}

#[test]
fn six_runs_find_five_witnesses_and_form_search_as_a_verb() {
    let method = HypothesisFormationContractV0::first();
    let resource = HypothesisFormationResourceV0::first();
    let mut frontier = HypothesisFormationFrontierV0::initial();
    let expected = [
        ("run", HypothesisFormationRunStateV0::Witness, 1_279),
        ("compile", HypothesisFormationRunStateV0::Witness, 1_976),
        ("reveal", HypothesisFormationRunStateV0::Witness, 1_324),
        ("resume", HypothesisFormationRunStateV0::Witness, 1_248),
        ("name", HypothesisFormationRunStateV0::NoWitness, 3_360),
        ("instantiate", HypothesisFormationRunStateV0::Witness, 1_208),
    ];

    for (sequence, (crossing, state, examined)) in expected.into_iter().enumerate() {
        let transition = run_hypothesis_formation_v0(&frontier, &method, &resource).unwrap();
        assert_eq!(transition.output.history.crossing.name, crossing);
        assert_eq!(transition.output.result.state, state);
        assert_eq!(transition.output.history.candidates_examined, examined);
        assert_eq!(
            transition.output.evidence.six_shards_partition_20160_candidates,
            CheckStatus::Checked
        );
        if let Some(word) = &transition.output.result.search_word {
            assert_eq!(word.local_name, "search");
            assert_eq!(word.display_name_zh, "搜索");
            assert_eq!(word.retained_vocabulary, method.retained_vocabulary);
            assert_eq!(word.introduced_vocabulary, ["search"]);
            assert_eq!(word.witness.xor_gate_count, 4);
            assert_eq!(word.witness.xor_lower_bound, 4);
            assert_eq!(word.witness.transport_orbit_size, 16);
            assert!(word.witness.closure.content.characteristic_residual.is_one());
            assert!(word
                .witness
                .closure
                .content
                .line_witnesses
                .iter()
                .all(|line| line.additive_residual == 0));
        } else {
            assert_eq!(state, HypothesisFormationRunStateV0::NoWitness);
            assert_eq!(transition.output.history.unvisited_candidates, 0);
        }
        frontier = transition.output.evidence.next_frontier;
        assert_eq!(frontier.sequence, sequence as u64 + 1);
    }

    assert_eq!(frontier.state, HypothesisFormationFrontierStateV0::Completed);
    assert_eq!(frontier.next_crossing, 6);
    assert_eq!(frontier.formed_words.len(), 5);
    assert_eq!(
        frontier
            .formed_words
            .iter()
            .map(|word| word.crossing.name.as_str())
            .collect::<Vec<_>>(),
        ["run", "compile", "reveal", "resume", "instantiate"]
    );
    frontier.check().unwrap();
}

#[test]
fn the_shortest_found_linear_path_is_four_xors_in_the_frozen_model() {
    let transition = run_hypothesis_formation_v0(
        &HypothesisFormationFrontierV0::initial(),
        &HypothesisFormationContractV0::first(),
        &HypothesisFormationResourceV0::first(),
    )
    .unwrap();
    let witness = &transition.output.result.search_word.as_ref().unwrap().witness;

    assert_eq!(witness.global_candidate_ordinal, 7_668);
    assert_eq!(witness.crossing_candidate_ordinal, 1_278);
    assert_eq!(witness.output_forms, [6, 11, 14, 9]);
    assert_eq!(
        witness.cells,
        [1, 11, 8, 14, 6, 16, 3, 9, 15, 5, 10, 4, 12, 2, 13, 7]
    );
}

#[test]
fn fuel_suspension_retains_the_same_crossing_and_cursor() {
    let small = HypothesisFormationResourceV0 {
        candidate_fuel: 100,
        ..HypothesisFormationResourceV0::first()
    };
    let first = run_hypothesis_formation_v0(
        &HypothesisFormationFrontierV0::initial(),
        &HypothesisFormationContractV0::first(),
        &small,
    )
    .unwrap();
    assert_eq!(
        first.output.result.state,
        HypothesisFormationRunStateV0::Suspended
    );
    assert_eq!(first.output.evidence.next_frontier.next_crossing, 0);
    assert_eq!(first.output.evidence.next_frontier.crossing_cursor, 100);

    let resumed = run_hypothesis_formation_v0(
        &first.output.evidence.next_frontier,
        &HypothesisFormationContractV0::first(),
        &HypothesisFormationResourceV0::first(),
    )
    .unwrap();
    assert_eq!(
        resumed.output.result.state,
        HypothesisFormationRunStateV0::Witness
    );
    assert_eq!(resumed.output.history.candidates_examined, 1_179);
    assert_eq!(
        resumed
            .output
            .result
            .search_word
            .as_ref()
            .unwrap()
            .witness
            .global_candidate_ordinal,
        7_668
    );
}

#[test]
fn contract_and_witness_tampering_are_rejected() {
    let mut method = HypothesisFormationContractV0::first();
    method.shard_rule.push_str(":drift");
    assert!(method.check().is_err());

    let mut transition = run_hypothesis_formation_v0(
        &HypothesisFormationFrontierV0::initial(),
        &HypothesisFormationContractV0::first(),
        &HypothesisFormationResourceV0::first(),
    )
    .unwrap();
    transition
        .output
        .result
        .search_word
        .as_mut()
        .unwrap()
        .witness
        .xor_lower_bound = 3;
    assert!(transition.check().is_err());
}
