use adva_ir::{CutConsumer, GraftFrameKind, NodeId};
use adva_lisp::{
    advance_causal_cut, analyze_causal_cut, analyze_program_slice,
    analyze_program_slice_with_graft, compile_function, compose_program_slices,
    compose_program_slices_with_graft, link_modules, parse_module,
};

const PROCESS_MODULE: &str = r#"
(module process
  (export
    shared-sum identity hidden-history wrapper identity-call chain-three
    independent-diamond)

  (def shared-sum
    (fn ((x Real)) Real
      (add (copy (use x)))))

  (def identity
    (fn ((x Real)) Real
      (use x)))

  (def hidden-history
    (fn ((x Real)) Real
      (frontier
        (discard 1)
        (use x))))

  (def neg-one
    (fn ((x Real)) Real
      (neg (use x))))

  (def wrapper
    (fn ((x Real)) Real
      (call neg-one (use x))))

  (def id-callee
    (fn ((x Real)) Real
      (use x)))

  (def identity-call
    (fn ((x Real)) Real
      (call id-callee (use x))))

  (def chain-three
    (fn ((x Real)) Real
      (neg (neg (neg (use x))))))

  (def independent-diamond
    (fn ((left Real) (right Real)) Real
      (add
        (frontier
          (neg (use left))
          (id (use right))))))
)
"#;

fn compile(name: &str) -> adva_ir::CompilationArtifact {
    let module = parse_module(PROCESS_MODULE).unwrap();
    let linked = link_modules(vec![module]).unwrap();
    compile_function(&linked, "process", name).unwrap()
}

fn shared_sum() -> adva_ir::SharedProgramDiagram {
    compile("shared-sum").result
}

fn independent_pasts() -> Vec<Vec<NodeId>> {
    vec![
        vec![],
        vec![NodeId(0)],
        vec![NodeId(1)],
        vec![NodeId(0), NodeId(1)],
        vec![NodeId(0), NodeId(1), NodeId(2)],
    ]
}

fn is_subset(left: &[NodeId], right: &[NodeId]) -> bool {
    left.iter().all(|node| right.contains(node))
}

#[test]
fn causal_cuts_are_derived_from_the_checked_operation_dag() {
    let diagram = shared_sum();

    let initial = analyze_causal_cut(&diagram, &[]).unwrap();
    assert!(initial.certificate.certified());
    assert!(initial.result.completed.is_empty());
    assert_eq!(initial.result.frontier.len(), 1);
    assert_eq!(
        initial.result.frontier[0].consumer,
        CutConsumer::Node {
            node: NodeId(0),
            input_index: 0
        }
    );

    let branched = analyze_causal_cut(&diagram, &[NodeId(0)]).unwrap();
    assert!(branched.certificate.certified());
    assert_eq!(branched.result.frontier.len(), 2);
    let left = &branched.result.frontier[0].wire.lineage[0];
    let right = &branched.result.frontier[1].wire.lineage[0];
    assert_ne!(left, right);
    assert_eq!(
        branched.result.frontier[0].sources,
        branched.result.frontier[1].sources
    );
    let partition = diagram.source_partition();
    let source_members = partition.values().next().unwrap();
    assert!(source_members.contains(left));
    assert!(source_members.contains(right));

    let final_cut = analyze_causal_cut(&diagram, &[NodeId(0), NodeId(1)]).unwrap();
    assert_eq!(final_cut.result.frontier.len(), 1);
    assert_eq!(
        final_cut.result.frontier[0].consumer,
        CutConsumer::Output { index: 0 }
    );
}

#[test]
fn one_causal_step_records_frontier_replacement_without_evaluation() {
    let diagram = shared_sum();
    let step = advance_causal_cut(&diagram, &[], NodeId(0)).unwrap();
    assert!(step.certificate.certified());
    assert_eq!(step.result.consumed.len(), 1);
    assert_eq!(step.result.produced.len(), 2);
    assert_eq!(step.result.before.frontier.len(), 1);
    assert_eq!(step.result.after.frontier.len(), 2);
}

#[test]
fn a_cut_cannot_contain_an_event_without_its_causal_past() {
    let error = analyze_causal_cut(&shared_sum(), &[NodeId(1)]).unwrap_err();
    assert!(error.to_string().contains("without predecessors"));
}

#[test]
fn identity_slice_retains_the_same_through_wire() {
    let artifact = compile("identity");
    let slice = analyze_program_slice(&artifact.result, &[], &[]).unwrap();

    assert!(slice.certificate.certified());
    assert!(slice.result.events.is_empty());
    assert_eq!(slice.result.lower.frontier, slice.result.upper.frontier);
    assert!(slice.result.lower_boundary.is_empty());
    assert!(slice.result.upper_boundary.is_empty());
    assert_eq!(slice.result.through_wires, slice.result.lower.frontier);
    assert!(slice.result.internal_events.is_empty());
    assert_eq!(slice.result.occurrences, artifact.result.occurrences);
    assert!(slice.result.event_history.is_empty());
    assert!(slice.result.graft_intersections.is_none());
}

#[test]
fn explicit_copy_preserves_parent_and_distinct_child_occurrences() {
    let artifact = compile("shared-sum");
    let slice = analyze_program_slice(&artifact.result, &[], &[NodeId(0)]).unwrap();

    assert!(slice.certificate.certified());
    assert_eq!(slice.result.events.len(), 1);
    assert_eq!(slice.result.lower_boundary.len(), 1);
    assert_eq!(slice.result.upper_boundary.len(), 2);
    assert!(slice.result.through_wires.is_empty());
    assert!(slice.result.internal_events.is_empty());
    assert_eq!(slice.result.event_history.len(), 2);
    assert_eq!(slice.result.occurrences.len(), 3);
    let children = slice
        .result
        .upper_boundary
        .iter()
        .map(|wire| wire.wire.lineage[0].clone())
        .collect::<Vec<_>>();
    assert_ne!(children[0], children[1]);
    assert_eq!(
        slice.result.upper_boundary[0].sources,
        slice.result.upper_boundary[1].sources
    );
}

#[test]
fn equal_frontiers_do_not_erase_internal_constant_and_discard() {
    let artifact = compile("hidden-history");
    let slice = analyze_program_slice(&artifact.result, &[], &[NodeId(0), NodeId(1)]).unwrap();

    assert!(slice.certificate.certified());
    assert_eq!(slice.result.lower.frontier, slice.result.upper.frontier);
    assert_eq!(
        slice
            .result
            .events
            .iter()
            .map(|node| node.id)
            .collect::<Vec<_>>(),
        vec![NodeId(0), NodeId(1)]
    );
    assert!(slice.result.lower_boundary.is_empty());
    assert!(slice.result.upper_boundary.is_empty());
    assert_eq!(slice.result.through_wires, slice.result.lower.frontier);
    assert_eq!(slice.result.internal_events, vec![NodeId(0), NodeId(1)]);
    assert_eq!(slice.result.event_history.len(), 2);
}

#[test]
fn slice_requires_nested_causal_pasts() {
    let artifact = compile("hidden-history");
    let error = analyze_program_slice(&artifact.result, &[NodeId(0)], &[]).unwrap_err();
    assert!(error.to_string().contains("not contained"));
}

#[test]
fn slice_links_exact_nonempty_graft_frame_regions() {
    let artifact = compile("wrapper");
    let slice = analyze_program_slice_with_graft(
        &artifact.result,
        &artifact.graft_trace.result,
        &[],
        &[NodeId(0)],
    )
    .unwrap();

    assert!(slice.certificate.certified());
    assert!(slice.certificate.graft_frame_consistency.is_some());
    let intersections = slice.result.graft_intersections.unwrap();
    assert_eq!(intersections.len(), 2);
    let root = artifact
        .graft_trace
        .result
        .frames
        .iter()
        .find(|frame| frame.kind == GraftFrameKind::Root)
        .unwrap();
    let call = artifact
        .graft_trace
        .result
        .frames
        .iter()
        .find(|frame| frame.kind == GraftFrameKind::Call)
        .unwrap();
    assert_eq!(intersections[0].frame, root.id);
    assert_eq!(intersections[0].body_events, vec![NodeId(0)]);
    assert_eq!(intersections[1].frame, call.id);
    assert_eq!(intersections[1].body_events, vec![NodeId(0)]);
}

#[test]
fn zero_event_call_frame_has_no_canonical_slice_intersection() {
    let artifact = compile("identity-call");
    assert_eq!(artifact.graft_trace.result.frames.len(), 2);
    let slice =
        analyze_program_slice_with_graft(&artifact.result, &artifact.graft_trace.result, &[], &[])
            .unwrap();

    assert!(slice.result.events.is_empty());
    assert_eq!(slice.result.graft_intersections, Some(Vec::new()));
}

#[test]
fn adjacent_composition_retains_hidden_constant_and_discard_history() {
    let artifact = compile("hidden-history");
    let left = analyze_program_slice(&artifact.result, &[], &[NodeId(0)])
        .unwrap()
        .result;
    let right = analyze_program_slice(&artifact.result, &[NodeId(0)], &[NodeId(0), NodeId(1)])
        .unwrap()
        .result;
    let composed = compose_program_slices(&artifact.result, &left, &right).unwrap();
    let direct = analyze_program_slice(&artifact.result, &[], &[NodeId(0), NodeId(1)])
        .unwrap()
        .result;

    assert!(composed.certificate.certified());
    assert_eq!(composed.result, direct);
    assert_eq!(
        composed.result.lower.frontier,
        composed.result.upper.frontier
    );
    assert_eq!(composed.result.internal_events, vec![NodeId(0), NodeId(1)]);
    assert_eq!(composed.certificate.left_event_ids, vec![NodeId(0)]);
    assert_eq!(composed.certificate.right_event_ids, vec![NodeId(1)]);
}

#[test]
fn three_nonempty_slice_composition_is_exact_and_associative() {
    let artifact = compile("chain-three");
    let a = analyze_program_slice(&artifact.result, &[], &[NodeId(0)])
        .unwrap()
        .result;
    let b = analyze_program_slice(&artifact.result, &[NodeId(0)], &[NodeId(0), NodeId(1)])
        .unwrap()
        .result;
    let c = analyze_program_slice(
        &artifact.result,
        &[NodeId(0), NodeId(1)],
        &[NodeId(0), NodeId(1), NodeId(2)],
    )
    .unwrap()
    .result;

    let ab = compose_program_slices(&artifact.result, &a, &b)
        .unwrap()
        .result;
    let left_associated = compose_program_slices(&artifact.result, &ab, &c)
        .unwrap()
        .result;
    let bc = compose_program_slices(&artifact.result, &b, &c)
        .unwrap()
        .result;
    let right_associated = compose_program_slices(&artifact.result, &a, &bc)
        .unwrap()
        .result;
    let direct = analyze_program_slice(&artifact.result, &[], &[NodeId(0), NodeId(1), NodeId(2)])
        .unwrap()
        .result;

    assert_eq!(left_associated, right_associated);
    assert_eq!(left_associated, direct);
}

#[test]
fn identity_slices_are_left_and_right_units() {
    let artifact = compile("chain-three");
    let identity_before = analyze_program_slice(&artifact.result, &[], &[])
        .unwrap()
        .result;
    let whole = analyze_program_slice(&artifact.result, &[], &[NodeId(0), NodeId(1), NodeId(2)])
        .unwrap()
        .result;
    let identity_after = analyze_program_slice(
        &artifact.result,
        &[NodeId(0), NodeId(1), NodeId(2)],
        &[NodeId(0), NodeId(1), NodeId(2)],
    )
    .unwrap()
    .result;

    assert_eq!(
        compose_program_slices(&artifact.result, &identity_before, &whole)
            .unwrap()
            .result,
        whole
    );
    assert_eq!(
        compose_program_slices(&artifact.result, &whole, &identity_after)
            .unwrap()
            .result,
        whole
    );
}

#[test]
fn graft_linked_slice_composition_rederives_outer_intersections() {
    let artifact = compile("wrapper");
    let identity =
        analyze_program_slice_with_graft(&artifact.result, &artifact.graft_trace.result, &[], &[])
            .unwrap()
            .result;
    let event = analyze_program_slice_with_graft(
        &artifact.result,
        &artifact.graft_trace.result,
        &[],
        &[NodeId(0)],
    )
    .unwrap()
    .result;
    let composed = compose_program_slices_with_graft(
        &artifact.result,
        &artifact.graft_trace.result,
        &identity,
        &event,
    )
    .unwrap();

    assert!(composed.certificate.certified());
    assert_eq!(composed.result, event);
}

#[test]
fn independent_diamond_exhausts_nested_slice_composition_laws() {
    let artifact = compile("independent-diamond");
    let pasts = independent_pasts();

    for past in &pasts {
        assert!(analyze_causal_cut(&artifact.result, past)
            .unwrap()
            .certificate
            .certified());
    }

    let mut pair_count = 0;
    let mut triple_count = 0;
    let mut quadruple_count = 0;
    for lower in &pasts {
        for middle in &pasts {
            if !is_subset(lower, middle) {
                continue;
            }
            pair_count += 1;
            assert!(analyze_program_slice(&artifact.result, lower, middle)
                .unwrap()
                .certificate
                .certified());

            for upper in &pasts {
                if !is_subset(middle, upper) {
                    continue;
                }
                triple_count += 1;
                let left = analyze_program_slice(&artifact.result, lower, middle)
                    .unwrap()
                    .result;
                let right = analyze_program_slice(&artifact.result, middle, upper)
                    .unwrap()
                    .result;
                let composed = compose_program_slices(&artifact.result, &left, &right).unwrap();
                let direct = analyze_program_slice(&artifact.result, lower, upper)
                    .unwrap()
                    .result;
                assert!(composed.certificate.certified());
                assert_eq!(composed.result, direct);

                for final_past in &pasts {
                    if !is_subset(upper, final_past) {
                        continue;
                    }
                    quadruple_count += 1;
                    let third = analyze_program_slice(&artifact.result, upper, final_past)
                        .unwrap()
                        .result;
                    let left_associated =
                        compose_program_slices(&artifact.result, &composed.result, &third)
                            .unwrap()
                            .result;
                    let right_pair =
                        compose_program_slices(&artifact.result, &right, &third)
                            .unwrap()
                            .result;
                    let right_associated =
                        compose_program_slices(&artifact.result, &left, &right_pair)
                            .unwrap()
                            .result;
                    let direct = analyze_program_slice(&artifact.result, lower, final_past)
                        .unwrap()
                        .result;
                    assert_eq!(left_associated, right_associated);
                    assert_eq!(left_associated, direct);
                }
            }
        }
    }

    assert_eq!(pair_count, 14);
    assert_eq!(triple_count, 30);
    assert_eq!(quadruple_count, 55);
}

#[test]
fn independent_schedules_keep_distinct_paths_but_share_the_exact_outer_slice() {
    let artifact = compile("independent-diamond");

    let schedule_a = [NodeId(0), NodeId(1), NodeId(2)];
    let schedule_b = [NodeId(1), NodeId(0), NodeId(2)];
    assert_ne!(schedule_a, schedule_b);

    let a0 = advance_causal_cut(&artifact.result, &[], schedule_a[0]).unwrap();
    let a1 =
        advance_causal_cut(&artifact.result, &a0.result.after.completed, schedule_a[1]).unwrap();
    let a2 = advance_causal_cut(
        &artifact.result,
        &a1.result.after.completed,
        schedule_a[2],
    )
    .unwrap();
    let b0 = advance_causal_cut(&artifact.result, &[], schedule_b[0]).unwrap();
    let b1 =
        advance_causal_cut(&artifact.result, &b0.result.after.completed, schedule_b[1]).unwrap();
    let b2 = advance_causal_cut(
        &artifact.result,
        &b1.result.after.completed,
        schedule_b[2],
    )
    .unwrap();

    assert_ne!(a0.result.after.completed, b0.result.after.completed);
    assert_eq!(a2.result.after, b2.result.after);

    let a_first = analyze_program_slice(&artifact.result, &[], &a0.result.after.completed)
        .unwrap()
        .result;
    let a_second = analyze_program_slice(
        &artifact.result,
        &a0.result.after.completed,
        &a1.result.after.completed,
    )
    .unwrap()
    .result;
    let a_third = analyze_program_slice(
        &artifact.result,
        &a1.result.after.completed,
        &a2.result.after.completed,
    )
    .unwrap()
    .result;
    let a_prefix = compose_program_slices(&artifact.result, &a_first, &a_second)
        .unwrap()
        .result;
    let a_whole = compose_program_slices(&artifact.result, &a_prefix, &a_third)
        .unwrap()
        .result;

    let b_first = analyze_program_slice(&artifact.result, &[], &b0.result.after.completed)
        .unwrap()
        .result;
    let b_second = analyze_program_slice(
        &artifact.result,
        &b0.result.after.completed,
        &b1.result.after.completed,
    )
    .unwrap()
    .result;
    let b_third = analyze_program_slice(
        &artifact.result,
        &b1.result.after.completed,
        &b2.result.after.completed,
    )
    .unwrap()
    .result;
    assert_eq!(
        b_first
            .events
            .iter()
            .chain(&b_second.events)
            .map(|node| node.id)
            .collect::<Vec<_>>(),
        vec![NodeId(1), NodeId(0)]
    );
    let b_prefix = compose_program_slices(&artifact.result, &b_first, &b_second)
        .unwrap()
        .result;
    assert_eq!(
        b_prefix
            .events
            .iter()
            .map(|node| node.id)
            .collect::<Vec<_>>(),
        vec![NodeId(0), NodeId(1)]
    );
    let b_whole = compose_program_slices(&artifact.result, &b_prefix, &b_third)
        .unwrap()
        .result;

    let direct = analyze_program_slice(
        &artifact.result,
        &[],
        &[NodeId(0), NodeId(1), NodeId(2)],
    )
    .unwrap()
    .result;
    assert_eq!(a_whole, direct);
    assert_eq!(b_whole, direct);
}
