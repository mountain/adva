use crate::LispError;
use crate::compile::validate_graft_trace;
use crate::validate::validate_diagram_ref;
use adva_ir::{
    CausalCut, CausalCutArtifact, CausalCutCertificate, CausalStep, CausalStepArtifact,
    CausalStepCertificate, CertificateId, CheckStatus, CutConsumer, CutWire,
    GraftArgumentIntersection, GraftFrameIntersection, GraftTrace, HistoryEvent, NodeId,
    Occurrence, OccurrenceId, OperationNode, ProgramSlice, ProgramSliceArtifact,
    ProgramSliceCertificate, ProgramSliceCompositionArtifact, ProgramSliceCompositionCertificate,
    SharedProgramDiagram, SourceId, TriadicCutIncidenceV0, TriadicCutObservationV0,
    TriadicDomainV0, TriadicLineageLinkV0, TriadicObserverPolicyV0,
    TriadicObserverTransitionArtifactV0, TriadicObserverTransitionCertificateV0,
    TriadicObserverTransitionCompositionArtifactV0,
    TriadicObserverTransitionCompositionCertificateV0, TriadicObserverTransitionV0,
    TriadicOppositePairCutV0, TriadicOppositePairTransitionV0, WireProducer, WireRef,
};
use std::collections::{BTreeMap, BTreeSet};

/// Derive the open frontier of a downward-closed operation set.
///
/// The returned cut is a second reading of the same checked program DAG. It
/// neither evaluates the wires nor identifies equal values or occurrences.
///
/// # Errors
///
/// Returns a validation error if the diagram is invalid, a node is unknown,
/// a node is repeated, or the selected events are not past-closed.
pub fn analyze_causal_cut(
    diagram: &SharedProgramDiagram,
    completed: &[NodeId],
) -> Result<CausalCutArtifact, LispError> {
    validate_diagram_ref(diagram)?;
    let completed = checked_completed_past(diagram, completed)?;
    let completed_nodes = diagram
        .nodes
        .iter()
        .map(|node| node.id)
        .filter(|node| completed.contains(node))
        .collect::<Vec<_>>();
    let frontier = crossing_frontier(diagram, &completed)?;
    let suffix = if completed_nodes.is_empty() {
        "root".to_owned()
    } else {
        completed_nodes
            .iter()
            .map(|node| node.0.to_string())
            .collect::<Vec<_>>()
            .join("-")
    };
    Ok(CausalCutArtifact {
        result: CausalCut {
            completed: completed_nodes.clone(),
            frontier,
        },
        certificate: CausalCutCertificate {
            id: CertificateId::explicit(format!("cut:{}:{suffix}:v1", diagram.function)),
            scope: concat!(
                "finite checked operation DAG; past-closed node set; ",
                "exact crossing wires with unchanged lineage"
            )
            .to_owned(),
            diagram_integrity: CheckStatus::Checked,
            completed_past: CheckStatus::Checked,
            crossing_frontier: CheckStatus::Checked,
            lineage_preservation: CheckStatus::Checked,
            completed_nodes,
        },
    })
}

/// Move one enabled operation from the future across a checked causal cut.
///
/// # Errors
///
/// Returns a validation error if the starting cut is invalid or the selected
/// event is absent, already completed, or not enabled.
pub fn advance_causal_cut(
    diagram: &SharedProgramDiagram,
    completed: &[NodeId],
    event: NodeId,
) -> Result<CausalStepArtifact, LispError> {
    validate_diagram_ref(diagram)?;
    let completed_set = checked_completed_past(diagram, completed)?;
    let node = diagram
        .nodes
        .iter()
        .find(|node| node.id == event)
        .ok_or_else(|| invalid_error(format!("unknown causal event {}", event.0)))?;
    if completed_set.contains(&event) {
        return Err(invalid_error(format!(
            "causal event {} is already completed",
            event.0
        )));
    }
    let predecessors = direct_predecessors(&node.inputs);
    if !predecessors.is_subset(&completed_set) {
        return Err(invalid_error(format!(
            "causal event {} is not enabled; missing predecessors {:?}",
            event.0,
            predecessors
                .difference(&completed_set)
                .map(|node| node.0)
                .collect::<Vec<_>>()
        )));
    }

    let before = analyze_causal_cut(diagram, completed)?.result;
    let before_suffix = if before.completed.is_empty() {
        "root".to_owned()
    } else {
        before
            .completed
            .iter()
            .map(|node| node.0.to_string())
            .collect::<Vec<_>>()
            .join("-")
    };
    let mut after_nodes = completed_set;
    after_nodes.insert(event);
    let after_input = diagram
        .nodes
        .iter()
        .map(|item| item.id)
        .filter(|id| after_nodes.contains(id))
        .collect::<Vec<_>>();
    let after = analyze_causal_cut(diagram, &after_input)?.result;
    let consumed = before
        .frontier
        .iter()
        .filter(|wire| !after.frontier.contains(wire))
        .cloned()
        .collect();
    let produced = after
        .frontier
        .iter()
        .filter(|wire| !before.frontier.contains(wire))
        .cloned()
        .collect();

    Ok(CausalStepArtifact {
        result: CausalStep {
            event,
            before,
            after,
            consumed,
            produced,
        },
        certificate: CausalStepCertificate {
            id: CertificateId::explicit(format!(
                "causal-step:{}:{before_suffix}:{}:v1",
                diagram.function, event.0,
            )),
            scope: "one enabled event across two certified finite causal cuts".to_owned(),
            diagram_integrity: CheckStatus::Checked,
            event_enabled: CheckStatus::Checked,
            frontier_replacement: CheckStatus::Checked,
            event,
        },
    })
}

/// Derive the exact program interval between two nested causal pasts.
///
/// This analysis preserves original nodes, wires, occurrences, lineage, and
/// node-associated history. It never evaluates or lowers a fresh program.
///
/// # Errors
///
/// Returns a validation error if the diagram is invalid, either completed set
/// is not a causal past, or the lower past is not contained in the upper past.
pub fn analyze_program_slice(
    diagram: &SharedProgramDiagram,
    lower_completed: &[NodeId],
    upper_completed: &[NodeId],
) -> Result<ProgramSliceArtifact, LispError> {
    analyze_program_slice_impl(diagram, None, lower_completed, upper_completed)
}

/// Derive a program slice and link every nonempty frame-region intersection.
///
/// The graft trace is revalidated against the unchanged diagram before its
/// frame identifiers are admitted to the result.
///
/// # Errors
///
/// Returns the errors of [`analyze_program_slice`] and also rejects a graft
/// trace that is inconsistent with the supplied diagram.
pub fn analyze_program_slice_with_graft(
    diagram: &SharedProgramDiagram,
    graft_trace: &GraftTrace,
    lower_completed: &[NodeId],
    upper_completed: &[NodeId],
) -> Result<ProgramSliceArtifact, LispError> {
    analyze_program_slice_impl(diagram, Some(graft_trace), lower_completed, upper_completed)
}

/// Compose two adjacent program slices in one unchanged checked diagram.
///
/// Both inputs are rederived and compared exactly before their original event
/// sets are united. The composed view is then checked against the direct outer
/// slice. Use [`compose_program_slices_with_graft`] for slices carrying graft
/// intersections.
///
/// # Errors
///
/// Returns a validation error if either input is not the canonical slice of
/// this diagram, their middle cuts differ, or their event sets do not form the
/// exact outer interval.
pub fn compose_program_slices(
    diagram: &SharedProgramDiagram,
    left: &ProgramSlice,
    right: &ProgramSlice,
) -> Result<ProgramSliceCompositionArtifact, LispError> {
    if left.graft_intersections.is_some() || right.graft_intersections.is_some() {
        return Err(invalid_error(
            "graft-linked slices require compose_program_slices_with_graft",
        ));
    }
    compose_program_slices_impl(diagram, None, left, right)
}

/// Compose adjacent slices while preserving revalidated graft intersections.
///
/// # Errors
///
/// Returns the errors of [`compose_program_slices`] and also rejects a graft
/// trace inconsistent with the diagram or either input slice.
pub fn compose_program_slices_with_graft(
    diagram: &SharedProgramDiagram,
    graft_trace: &GraftTrace,
    left: &ProgramSlice,
    right: &ProgramSlice,
) -> Result<ProgramSliceCompositionArtifact, LispError> {
    compose_program_slices_impl(diagram, Some(graft_trace), left, right)
}

/// Derive three opposite-pair observer readings of one exact program slice.
///
/// The policy assigns the diagram's three input source fibres to construction,
/// space, and time. Domain labels remain observation metadata: exact Rust
/// source, occurrence, path, wire, and event identities are reused unchanged.
///
/// # Errors
///
/// Returns a validation error if the diagram or slice is invalid, the input
/// boundary is not an exact three-source permutation, or any cut incidence
/// cannot be resolved to the checked source partition.
pub fn analyze_triadic_observer_transition_v0(
    diagram: &SharedProgramDiagram,
    policy: &TriadicObserverPolicyV0,
    lower_completed: &[NodeId],
    upper_completed: &[NodeId],
) -> Result<TriadicObserverTransitionArtifactV0, LispError> {
    analyze_triadic_observer_transition_impl(
        diagram,
        None,
        policy,
        lower_completed,
        upper_completed,
    )
}

/// Derive a triadic observer transition while retaining graft-linked residuals.
///
/// # Errors
///
/// Returns the errors of [`analyze_triadic_observer_transition_v0`] and also
/// rejects a graft trace inconsistent with the unchanged diagram.
pub fn analyze_triadic_observer_transition_with_graft_v0(
    diagram: &SharedProgramDiagram,
    graft_trace: &GraftTrace,
    policy: &TriadicObserverPolicyV0,
    lower_completed: &[NodeId],
    upper_completed: &[NodeId],
) -> Result<TriadicObserverTransitionArtifactV0, LispError> {
    analyze_triadic_observer_transition_impl(
        diagram,
        Some(graft_trace),
        policy,
        lower_completed,
        upper_completed,
    )
}

/// Compose adjacent triadic observer transitions in one unchanged diagram.
///
/// Composition revalidates both inputs, composes their embedded exact slices,
/// and checks that occurrence ancestry is literal finite-relation composition
/// through the shared middle cut.
///
/// # Errors
///
/// Returns a validation error if either input is noncanonical, policies or
/// middle observations differ, or direct and relational composition disagree.
pub fn compose_triadic_observer_transitions_v0(
    diagram: &SharedProgramDiagram,
    policy: &TriadicObserverPolicyV0,
    left: &TriadicObserverTransitionV0,
    right: &TriadicObserverTransitionV0,
) -> Result<TriadicObserverTransitionCompositionArtifactV0, LispError> {
    if left.slice.graft_intersections.is_some() || right.slice.graft_intersections.is_some() {
        return Err(invalid_error(concat!(
            "graft-linked triadic transitions require ",
            "compose_triadic_observer_transitions_with_graft_v0"
        )));
    }
    compose_triadic_observer_transitions_impl(diagram, None, policy, left, right)
}

/// Compose adjacent graft-linked triadic observer transitions.
///
/// # Errors
///
/// Returns the errors of [`compose_triadic_observer_transitions_v0`] and also
/// rejects a graft trace inconsistent with the diagram or either input.
pub fn compose_triadic_observer_transitions_with_graft_v0(
    diagram: &SharedProgramDiagram,
    graft_trace: &GraftTrace,
    policy: &TriadicObserverPolicyV0,
    left: &TriadicObserverTransitionV0,
    right: &TriadicObserverTransitionV0,
) -> Result<TriadicObserverTransitionCompositionArtifactV0, LispError> {
    compose_triadic_observer_transitions_impl(diagram, Some(graft_trace), policy, left, right)
}

fn analyze_triadic_observer_transition_impl(
    diagram: &SharedProgramDiagram,
    graft_trace: Option<&GraftTrace>,
    policy: &TriadicObserverPolicyV0,
    lower_completed: &[NodeId],
    upper_completed: &[NodeId],
) -> Result<TriadicObserverTransitionArtifactV0, LispError> {
    validate_diagram_ref(diagram)?;
    if let Some(trace) = graft_trace {
        validate_graft_trace(diagram, trace)?;
    }
    let source_domains = checked_triadic_source_domains(diagram, policy)?;
    let slice_artifact = match graft_trace {
        Some(trace) => {
            analyze_program_slice_with_graft(diagram, trace, lower_completed, upper_completed)?
        }
        None => analyze_program_slice(diagram, lower_completed, upper_completed)?,
    };
    let result = build_triadic_observer_transition(
        diagram,
        policy.clone(),
        &source_domains,
        slice_artifact.result,
    )?;
    let lower_suffix = past_suffix(&result.lower.cut.completed);
    let upper_suffix = past_suffix(&result.upper.cut.completed);
    Ok(TriadicObserverTransitionArtifactV0 {
        certificate: TriadicObserverTransitionCertificateV0 {
            id: CertificateId::explicit(format!(
                "triadic-observer-transition:{}:{lower_suffix}:{upper_suffix}:v0",
                diagram.function
            )),
            scope: concat!(
                "one exact finite ProgramSlice; three input-source roles; ",
                "occurrence-level opposite-pair views and complete slice residual"
            )
            .to_owned(),
            diagram_integrity: CheckStatus::Checked,
            slice_revalidated: CheckStatus::Checked,
            total_triadic_policy: CheckStatus::Checked,
            exact_incidence_partition: CheckStatus::Checked,
            lineage_ancestry: CheckStatus::Checked,
            complete_slice_residual: CheckStatus::Checked,
            original_id_preservation: CheckStatus::Checked,
            graft_frame_consistency: graft_trace.map(|_| CheckStatus::Checked),
            lower_completed: result.lower.cut.completed.clone(),
            upper_completed: result.upper.cut.completed.clone(),
        },
        result,
    })
}

fn compose_triadic_observer_transitions_impl(
    diagram: &SharedProgramDiagram,
    graft_trace: Option<&GraftTrace>,
    policy: &TriadicObserverPolicyV0,
    left: &TriadicObserverTransitionV0,
    right: &TriadicObserverTransitionV0,
) -> Result<TriadicObserverTransitionCompositionArtifactV0, LispError> {
    validate_diagram_ref(diagram)?;
    if let Some(trace) = graft_trace {
        validate_graft_trace(diagram, trace)?;
    }
    if &left.policy != policy || &right.policy != policy {
        return Err(invalid_error(
            "triadic transition inputs use a different observer policy",
        ));
    }
    let canonical_left = analyze_triadic_observer_transition_impl(
        diagram,
        graft_trace,
        policy,
        &left.lower.cut.completed,
        &left.upper.cut.completed,
    )?
    .result;
    if &canonical_left != left {
        return Err(invalid_error(
            "left input is not the canonical triadic observer transition",
        ));
    }
    let canonical_right = analyze_triadic_observer_transition_impl(
        diagram,
        graft_trace,
        policy,
        &right.lower.cut.completed,
        &right.upper.cut.completed,
    )?
    .result;
    if &canonical_right != right {
        return Err(invalid_error(
            "right input is not the canonical triadic observer transition",
        ));
    }
    if left.upper != right.lower {
        return Err(invalid_error(
            "adjacent triadic transitions do not share one exact middle observation",
        ));
    }

    let composed_slice = match graft_trace {
        Some(trace) => {
            compose_program_slices_with_graft(diagram, trace, &left.slice, &right.slice)?
        }
        None => compose_program_slices(diagram, &left.slice, &right.slice)?,
    };
    let direct = analyze_triadic_observer_transition_impl(
        diagram,
        graft_trace,
        policy,
        &left.lower.cut.completed,
        &right.upper.cut.completed,
    )?
    .result;
    if composed_slice.result != direct.slice {
        return Err(invalid_error(
            "triadic transition slice residual differs from exact slice composition",
        ));
    }

    let mut relation_composite = BTreeSet::new();
    for left_link in &left.lineage_links {
        for right_link in &right.lineage_links {
            if left_link.upper_incidence_index == right_link.lower_incidence_index {
                relation_composite.insert((
                    left_link.lower_incidence_index,
                    right_link.upper_incidence_index,
                ));
            }
        }
    }
    let direct_relation = direct
        .lineage_links
        .iter()
        .map(|link| (link.lower_incidence_index, link.upper_incidence_index))
        .collect::<BTreeSet<_>>();
    if relation_composite != direct_relation {
        return Err(invalid_error(concat!(
            "triadic occurrence ancestry is not exact relational composition ",
            "through the middle cut"
        )));
    }

    let lower_completed = direct.lower.cut.completed.clone();
    let middle_completed = left.upper.cut.completed.clone();
    let upper_completed = direct.upper.cut.completed.clone();
    let lower_suffix = past_suffix(&lower_completed);
    let upper_suffix = past_suffix(&upper_completed);
    Ok(TriadicObserverTransitionCompositionArtifactV0 {
        result: direct,
        certificate: TriadicObserverTransitionCompositionCertificateV0 {
            id: CertificateId::explicit(format!(
                "triadic-observer-transition-compose:{}:{lower_suffix}:{upper_suffix}:v0",
                diagram.function
            )),
            scope: concat!(
                "two adjacent triadic observer views of exact finite slices; ",
                "same policy and unchanged checked diagram"
            )
            .to_owned(),
            diagram_integrity: CheckStatus::Checked,
            inputs_revalidated: CheckStatus::Checked,
            policy_agreement: CheckStatus::Checked,
            middle_observation_agreement: CheckStatus::Checked,
            slice_composition: CheckStatus::Checked,
            lineage_relation_composition: CheckStatus::Checked,
            exact_composition: CheckStatus::Checked,
            lower_completed,
            middle_completed,
            upper_completed,
        },
    })
}

fn compose_program_slices_impl(
    diagram: &SharedProgramDiagram,
    graft_trace: Option<&GraftTrace>,
    left: &ProgramSlice,
    right: &ProgramSlice,
) -> Result<ProgramSliceCompositionArtifact, LispError> {
    validate_diagram_ref(diagram)?;
    if let Some(trace) = graft_trace {
        validate_graft_trace(diagram, trace)?;
    }
    let canonical_left = analyze_program_slice_impl(
        diagram,
        graft_trace,
        &left.lower.completed,
        &left.upper.completed,
    )?
    .result;
    if &canonical_left != left {
        return Err(invalid_error(
            "left input is not the canonical slice of the supplied diagram",
        ));
    }
    let canonical_right = analyze_program_slice_impl(
        diagram,
        graft_trace,
        &right.lower.completed,
        &right.upper.completed,
    )?
    .result;
    if &canonical_right != right {
        return Err(invalid_error(
            "right input is not the canonical slice of the supplied diagram",
        ));
    }
    if left.upper != right.lower {
        return Err(invalid_error(
            "adjacent program slices do not have the same middle causal cut",
        ));
    }

    let left_events = left
        .events
        .iter()
        .map(|node| node.id)
        .collect::<BTreeSet<_>>();
    let right_events = right
        .events
        .iter()
        .map(|node| node.id)
        .collect::<BTreeSet<_>>();
    if !left_events.is_disjoint(&right_events) {
        return Err(invalid_error(
            "adjacent program slices have overlapping event sets",
        ));
    }
    let event_union = left_events
        .union(&right_events)
        .copied()
        .collect::<BTreeSet<_>>();
    let lower_set = checked_completed_past(diagram, &left.lower.completed)?;
    let upper_set = checked_completed_past(diagram, &right.upper.completed)?;
    let expected_union = upper_set
        .difference(&lower_set)
        .copied()
        .collect::<BTreeSet<_>>();
    if event_union != expected_union {
        return Err(invalid_error(
            "adjacent slice events do not conserve the exact outer interval",
        ));
    }

    let result = build_program_slice(
        diagram,
        graft_trace,
        left.lower.clone(),
        right.upper.clone(),
        &event_union,
    )?;
    let direct = analyze_program_slice_impl(
        diagram,
        graft_trace,
        &left.lower.completed,
        &right.upper.completed,
    )?
    .result;
    if result != direct {
        return Err(invalid_error(
            "composed program slice differs from the direct outer slice",
        ));
    }

    let left_event_ids = left.events.iter().map(|node| node.id).collect::<Vec<_>>();
    let right_event_ids = right.events.iter().map(|node| node.id).collect::<Vec<_>>();
    let result_event_ids = result.events.iter().map(|node| node.id).collect::<Vec<_>>();
    let lower_suffix = past_suffix(&result.lower.completed);
    let upper_suffix = past_suffix(&result.upper.completed);
    Ok(ProgramSliceCompositionArtifact {
        result,
        certificate: ProgramSliceCompositionCertificate {
            id: CertificateId::explicit(format!(
                "program-slice-compose:{}:{lower_suffix}:{upper_suffix}:v1",
                diagram.function
            )),
            scope: "two adjacent finite slices of one unchanged checked operation DAG".to_owned(),
            diagram_integrity: CheckStatus::Checked,
            inputs_revalidated: CheckStatus::Checked,
            boundary_agreement: CheckStatus::Checked,
            event_partition: CheckStatus::Checked,
            original_id_preservation: CheckStatus::Checked,
            lineage_preservation: CheckStatus::Checked,
            exact_composition: CheckStatus::Checked,
            left_event_ids,
            right_event_ids,
            result_event_ids,
        },
    })
}

fn analyze_program_slice_impl(
    diagram: &SharedProgramDiagram,
    graft_trace: Option<&GraftTrace>,
    lower_completed: &[NodeId],
    upper_completed: &[NodeId],
) -> Result<ProgramSliceArtifact, LispError> {
    validate_diagram_ref(diagram)?;
    if let Some(trace) = graft_trace {
        validate_graft_trace(diagram, trace)?;
    }
    let lower_set = checked_completed_past(diagram, lower_completed)?;
    let upper_set = checked_completed_past(diagram, upper_completed)?;
    if !lower_set.is_subset(&upper_set) {
        return Err(invalid_error(format!(
            "lower causal past is not contained in upper past; extra nodes {:?}",
            lower_set
                .difference(&upper_set)
                .map(|node| node.0)
                .collect::<Vec<_>>()
        )));
    }

    let lower = analyze_causal_cut(diagram, lower_completed)?.result;
    let upper = analyze_causal_cut(diagram, upper_completed)?.result;
    let event_set = upper_set
        .difference(&lower_set)
        .copied()
        .collect::<BTreeSet<_>>();
    let result = build_program_slice(diagram, graft_trace, lower, upper, &event_set)?;
    let event_ids = result.events.iter().map(|node| node.id).collect::<Vec<_>>();
    let lower_suffix = past_suffix(&result.lower.completed);
    let upper_suffix = past_suffix(&result.upper.completed);

    Ok(ProgramSliceArtifact {
        certificate: ProgramSliceCertificate {
            id: CertificateId::explicit(format!(
                "program-slice:{}:{lower_suffix}:{upper_suffix}:v1",
                diagram.function
            )),
            scope:
                "one finite checked operation DAG; nested causal pasts; exact original identities"
                    .to_owned(),
            diagram_integrity: CheckStatus::Checked,
            lower_past: CheckStatus::Checked,
            upper_past: CheckStatus::Checked,
            past_inclusion: CheckStatus::Checked,
            event_difference: CheckStatus::Checked,
            boundary_partition: CheckStatus::Checked,
            internal_events: CheckStatus::Checked,
            original_id_preservation: CheckStatus::Checked,
            lineage_preservation: CheckStatus::Checked,
            graft_frame_consistency: graft_trace.map(|_| CheckStatus::Checked),
            lower_completed: result.lower.completed.clone(),
            upper_completed: result.upper.completed.clone(),
            event_ids,
        },
        result,
    })
}

fn build_program_slice(
    diagram: &SharedProgramDiagram,
    graft_trace: Option<&GraftTrace>,
    lower: CausalCut,
    upper: CausalCut,
    event_set: &BTreeSet<NodeId>,
) -> Result<ProgramSlice, LispError> {
    let events = diagram
        .nodes
        .iter()
        .filter(|node| event_set.contains(&node.id))
        .cloned()
        .collect::<Vec<_>>();
    let lower_boundary = lower
        .frontier
        .iter()
        .filter(|cut_wire| match &cut_wire.consumer {
            CutConsumer::Node { node, .. } => event_set.contains(node),
            CutConsumer::Output { .. } => false,
        })
        .cloned()
        .collect::<Vec<_>>();
    let through_wires = lower
        .frontier
        .iter()
        .filter(|cut_wire| upper.frontier.contains(cut_wire))
        .cloned()
        .collect::<Vec<_>>();
    let upper_boundary = upper
        .frontier
        .iter()
        .filter(|cut_wire| match &cut_wire.wire.producer {
            WireProducer::Input { .. } => false,
            WireProducer::Node { node } => event_set.contains(node),
        })
        .cloned()
        .collect::<Vec<_>>();
    validate_boundary_partition(
        &lower,
        &upper,
        &lower_boundary,
        &upper_boundary,
        &through_wires,
    )?;

    let internal_events = events
        .iter()
        .map(|node| node.id)
        .filter(|node| {
            !upper
                .frontier
                .iter()
                .any(|cut_wire| cut_wire.wire.producer == WireProducer::Node { node: *node })
        })
        .collect::<Vec<_>>();
    let event_history = diagram
        .history
        .prefix
        .iter()
        .filter(|event| history_node(event).is_some_and(|node| event_set.contains(&node)))
        .cloned()
        .collect::<Vec<_>>();
    let occurrences =
        slice_occurrences(diagram, &lower, &upper, &events, event_set, &event_history)?;
    let graft_intersections = graft_trace.map(|trace| intersect_graft_frames(trace, event_set));
    Ok(ProgramSlice {
        lower,
        upper,
        events,
        lower_boundary,
        upper_boundary,
        through_wires,
        internal_events,
        occurrences,
        event_history,
        graft_intersections,
    })
}

fn validate_boundary_partition(
    lower: &CausalCut,
    upper: &CausalCut,
    lower_boundary: &[CutWire],
    upper_boundary: &[CutWire],
    through_wires: &[CutWire],
) -> Result<(), LispError> {
    let lower_is_partitioned = lower
        .frontier
        .iter()
        .all(|wire| lower_boundary.contains(wire) ^ through_wires.contains(wire));
    let upper_is_partitioned = upper
        .frontier
        .iter()
        .all(|wire| upper_boundary.contains(wire) ^ through_wires.contains(wire));
    if !lower_is_partitioned
        || !upper_is_partitioned
        || lower.frontier.len() != lower_boundary.len() + through_wires.len()
        || upper.frontier.len() != upper_boundary.len() + through_wires.len()
    {
        return Err(invalid_error(
            "program slice boundaries do not partition into changed and through wires",
        ));
    }
    Ok(())
}

fn history_node(event: &HistoryEvent) -> Option<NodeId> {
    match event {
        HistoryEvent::Copy { node, .. } | HistoryEvent::Operation { node, .. } => Some(*node),
        HistoryEvent::Source { .. } | HistoryEvent::Call { .. } => None,
    }
}

fn slice_occurrences(
    diagram: &SharedProgramDiagram,
    lower: &CausalCut,
    upper: &CausalCut,
    events: &[OperationNode],
    event_set: &BTreeSet<NodeId>,
    event_history: &[HistoryEvent],
) -> Result<Vec<Occurrence>, LispError> {
    let mut occurrence_ids = BTreeSet::new();
    for cut_wire in lower.frontier.iter().chain(upper.frontier.iter()) {
        occurrence_ids.extend(cut_wire.wire.lineage.iter().cloned());
    }
    for wire in events.iter().flat_map(|node| node.inputs.iter()) {
        occurrence_ids.extend(wire.lineage.iter().cloned());
    }
    for wire in diagram
        .nodes
        .iter()
        .flat_map(|node| node.inputs.iter())
        .chain(diagram.outputs.iter())
        .filter(|wire| match &wire.producer {
            WireProducer::Input { .. } => false,
            WireProducer::Node { node } => event_set.contains(node),
        })
    {
        occurrence_ids.extend(wire.lineage.iter().cloned());
    }
    for event in event_history {
        if let HistoryEvent::Copy {
            parent, children, ..
        } = event
        {
            occurrence_ids.insert(parent.clone());
            occurrence_ids.extend(children.iter().cloned());
        }
    }
    let occurrences = diagram
        .occurrences
        .iter()
        .filter(|occurrence| occurrence_ids.contains(&occurrence.id))
        .cloned()
        .collect::<Vec<_>>();
    let found = occurrences
        .iter()
        .map(|occurrence| occurrence.id.clone())
        .collect::<BTreeSet<OccurrenceId>>();
    if found != occurrence_ids {
        return Err(invalid_error(
            "program slice references occurrences absent from the diagram",
        ));
    }
    Ok(occurrences)
}

fn intersect_graft_frames(
    trace: &GraftTrace,
    event_set: &BTreeSet<NodeId>,
) -> Vec<GraftFrameIntersection> {
    trace
        .frames
        .iter()
        .filter_map(|frame| {
            let argument_events = frame
                .arguments
                .iter()
                .map(|argument| GraftArgumentIntersection {
                    argument_index: argument.argument_index,
                    events: argument
                        .nodes
                        .iter()
                        .copied()
                        .filter(|node| event_set.contains(node))
                        .collect(),
                })
                .collect::<Vec<_>>();
            let body_events = frame
                .body_region
                .iter()
                .copied()
                .filter(|node| event_set.contains(node))
                .collect::<Vec<_>>();
            let intersects = !body_events.is_empty()
                || argument_events
                    .iter()
                    .any(|argument| !argument.events.is_empty());
            intersects.then_some(GraftFrameIntersection {
                frame: frame.id.clone(),
                argument_events,
                body_events,
                call_history_index: frame.call_history_index,
            })
        })
        .collect()
}

fn triadic_domains() -> [TriadicDomainV0; 3] {
    [
        TriadicDomainV0::Construction,
        TriadicDomainV0::Space,
        TriadicDomainV0::Time,
    ]
}

fn checked_triadic_source_domains(
    diagram: &SharedProgramDiagram,
    policy: &TriadicObserverPolicyV0,
) -> Result<BTreeMap<SourceId, TriadicDomainV0>, LispError> {
    let input_count = diagram.signature.domain().ports().len();
    if input_count != 3 || policy.input_domains.len() != input_count {
        return Err(invalid_error(concat!(
            "triadic observer policy v0 requires exactly three input ports ",
            "and three input-domain assignments"
        )));
    }
    let assigned = policy
        .input_domains
        .iter()
        .copied()
        .collect::<BTreeSet<_>>();
    let required = triadic_domains().into_iter().collect::<BTreeSet<_>>();
    if assigned != required {
        return Err(invalid_error(concat!(
            "triadic observer policy v0 must assign construction, space, ",
            "and time exactly once"
        )));
    }

    let initial = analyze_causal_cut(diagram, &[])?.result;
    let mut source_domains = BTreeMap::new();
    let mut input_indices = BTreeSet::new();
    for cut_wire in &initial.frontier {
        let WireProducer::Input { index } = &cut_wire.wire.producer else {
            return Err(invalid_error(
                "the initial causal cut contains a non-input producer",
            ));
        };
        let input_index = usize::try_from(*index)
            .map_err(|_| invalid_error("input index cannot be represented by usize"))?;
        let Some(domain) = policy.input_domains.get(input_index).copied() else {
            return Err(invalid_error(
                "initial cut input lies outside the triadic policy boundary",
            ));
        };
        if !input_indices.insert(*index) {
            return Err(invalid_error(
                "one triadic input crosses the initial cut more than once",
            ));
        }
        if cut_wire.wire.lineage.len() != 1 || cut_wire.sources.len() != 1 {
            return Err(invalid_error(concat!(
                "triadic observer policy v0 requires one checked root ",
                "occurrence and source per input"
            )));
        }
        let source = cut_wire.sources[0].clone();
        if source_domains.insert(source, domain).is_some() {
            return Err(invalid_error(
                "one checked source was assigned to two triadic input roles",
            ));
        }
    }
    if input_indices.len() != input_count || source_domains.len() != input_count {
        return Err(invalid_error(
            "the initial cut does not expose the complete triadic input boundary",
        ));
    }
    let checked_sources = diagram
        .source_partition()
        .into_keys()
        .collect::<BTreeSet<_>>();
    if source_domains.keys().cloned().collect::<BTreeSet<_>>() != checked_sources {
        return Err(invalid_error(concat!(
            "triadic input assignments do not cover the exact checked ",
            "source partition"
        )));
    }
    Ok(source_domains)
}

fn build_triadic_cut_observation(
    diagram: &SharedProgramDiagram,
    source_domains: &BTreeMap<SourceId, TriadicDomainV0>,
    cut: CausalCut,
) -> Result<TriadicCutObservationV0, LispError> {
    let occurrences = diagram
        .occurrences
        .iter()
        .map(|occurrence| (occurrence.id.clone(), occurrence))
        .collect::<BTreeMap<_, _>>();
    if occurrences.len() != diagram.occurrences.len() {
        return Err(invalid_error(
            "triadic cut observation found repeated checked occurrence IDs",
        ));
    }

    let mut incidences = Vec::new();
    let mut source_free_wire_indices = Vec::new();
    for (cut_wire_index, cut_wire) in cut.frontier.iter().enumerate() {
        let cut_wire_index = checked_u32_index(cut_wire_index, "causal cut frontier")?;
        if cut_wire.wire.lineage.len() != cut_wire.sources.len() {
            return Err(invalid_error(
                "cut lineage and source incidence lengths disagree",
            ));
        }
        if cut_wire.wire.lineage.is_empty() {
            if !cut_wire.sources.is_empty() {
                return Err(invalid_error(
                    "source-free cut wire carries a nonempty source sequence",
                ));
            }
            source_free_wire_indices.push(cut_wire_index);
            continue;
        }
        for (lineage_index, (occurrence_id, source)) in cut_wire
            .wire
            .lineage
            .iter()
            .zip(&cut_wire.sources)
            .enumerate()
        {
            let occurrence = occurrences.get(occurrence_id).ok_or_else(|| {
                invalid_error(format!(
                    "triadic cut references missing occurrence {occurrence_id}"
                ))
            })?;
            if &occurrence.source != source {
                return Err(invalid_error(
                    "triadic cut source disagrees with its checked occurrence",
                ));
            }
            let domain = source_domains.get(source).copied().ok_or_else(|| {
                invalid_error(format!(
                    "triadic policy does not classify checked source {source}"
                ))
            })?;
            incidences.push(TriadicCutIncidenceV0 {
                cut_wire_index,
                lineage_index: checked_u32_index(lineage_index, "wire lineage")?,
                occurrence: (*occurrence).clone(),
                domain,
            });
        }
    }

    let mut opposite_pair_views = Vec::new();
    for observer in triadic_domains() {
        let mut visible_incidence_indices = Vec::new();
        let mut hidden_own_incidence_indices = Vec::new();
        for (index, incidence) in incidences.iter().enumerate() {
            let index = checked_u32_index(index, "triadic cut incidence")?;
            if incidence.domain == observer {
                hidden_own_incidence_indices.push(index);
            } else {
                visible_incidence_indices.push(index);
            }
        }
        opposite_pair_views.push(TriadicOppositePairCutV0 {
            observer,
            visible_incidence_indices,
            hidden_own_incidence_indices,
        });
    }
    validate_opposite_pair_partition(&incidences, &opposite_pair_views)?;

    Ok(TriadicCutObservationV0 {
        cut,
        incidences,
        source_free_wire_indices,
        opposite_pair_views,
    })
}

fn validate_opposite_pair_partition(
    incidences: &[TriadicCutIncidenceV0],
    views: &[TriadicOppositePairCutV0],
) -> Result<(), LispError> {
    if views.len() != 3
        || views
            .iter()
            .map(|view| view.observer)
            .collect::<BTreeSet<_>>()
            != triadic_domains().into_iter().collect::<BTreeSet<_>>()
    {
        return Err(invalid_error(
            "triadic cut does not contain exactly three opposite-pair views",
        ));
    }
    for (index, incidence) in incidences.iter().enumerate() {
        let index = checked_u32_index(index, "triadic cut incidence")?;
        let visible_count = views
            .iter()
            .filter(|view| view.visible_incidence_indices.contains(&index))
            .count();
        let hidden = views
            .iter()
            .filter(|view| view.hidden_own_incidence_indices.contains(&index))
            .map(|view| view.observer)
            .collect::<Vec<_>>();
        if visible_count != 2 || hidden.as_slice() != [incidence.domain] {
            return Err(invalid_error(concat!(
                "each triadic incidence must be visible from its two opposite ",
                "roles and hidden from its own role exactly once"
            )));
        }
    }
    Ok(())
}

fn build_triadic_observer_transition(
    diagram: &SharedProgramDiagram,
    policy: TriadicObserverPolicyV0,
    source_domains: &BTreeMap<SourceId, TriadicDomainV0>,
    slice: ProgramSlice,
) -> Result<TriadicObserverTransitionV0, LispError> {
    let lower = build_triadic_cut_observation(diagram, source_domains, slice.lower.clone())?;
    let upper = build_triadic_cut_observation(diagram, source_domains, slice.upper.clone())?;
    let mut lineage_links = Vec::new();
    for (lower_index, lower_incidence) in lower.incidences.iter().enumerate() {
        for (upper_index, upper_incidence) in upper.incidences.iter().enumerate() {
            if lower_incidence.domain == upper_incidence.domain
                && lower_incidence.occurrence.source == upper_incidence.occurrence.source
                && upper_incidence
                    .occurrence
                    .path
                    .0
                    .starts_with(&lower_incidence.occurrence.path.0)
            {
                lineage_links.push(TriadicLineageLinkV0 {
                    lower_incidence_index: checked_u32_index(
                        lower_index,
                        "lower triadic incidence",
                    )?,
                    upper_incidence_index: checked_u32_index(
                        upper_index,
                        "upper triadic incidence",
                    )?,
                });
            }
        }
    }

    let mut opposite_pair_transitions = Vec::new();
    for observer in triadic_domains() {
        let mut visible_lineage_link_indices = Vec::new();
        for (link_index, link) in lineage_links.iter().enumerate() {
            let lower_index = usize::try_from(link.lower_incidence_index)
                .map_err(|_| invalid_error("lower incidence index exceeds usize"))?;
            let Some(lower_incidence) = lower.incidences.get(lower_index) else {
                return Err(invalid_error(
                    "lineage link references a missing lower incidence",
                ));
            };
            if lower_incidence.domain != observer {
                visible_lineage_link_indices
                    .push(checked_u32_index(link_index, "triadic lineage link")?);
            }
        }
        opposite_pair_transitions.push(TriadicOppositePairTransitionV0 {
            observer,
            visible_lineage_link_indices,
        });
    }

    Ok(TriadicObserverTransitionV0 {
        policy,
        slice,
        lower,
        upper,
        lineage_links,
        opposite_pair_transitions,
    })
}

fn checked_u32_index(index: usize, name: &str) -> Result<u32, LispError> {
    u32::try_from(index).map_err(|_| invalid_error(format!("{name} exceeds u32")))
}

fn past_suffix(completed: &[NodeId]) -> String {
    if completed.is_empty() {
        "root".to_owned()
    } else {
        completed
            .iter()
            .map(|node| node.0.to_string())
            .collect::<Vec<_>>()
            .join("-")
    }
}

fn checked_completed_past(
    diagram: &SharedProgramDiagram,
    completed: &[NodeId],
) -> Result<BTreeSet<NodeId>, LispError> {
    let completed_set = completed.iter().copied().collect::<BTreeSet<_>>();
    if completed_set.len() != completed.len() {
        return Err(invalid_error("a completed past repeats a node"));
    }
    let known = diagram
        .nodes
        .iter()
        .map(|node| node.id)
        .collect::<BTreeSet<_>>();
    if !completed_set.is_subset(&known) {
        return Err(invalid_error(format!(
            "completed past contains unknown nodes {:?}",
            completed_set
                .difference(&known)
                .map(|node| node.0)
                .collect::<Vec<_>>()
        )));
    }
    for node in diagram
        .nodes
        .iter()
        .filter(|node| completed_set.contains(&node.id))
    {
        let predecessors = direct_predecessors(&node.inputs);
        if !predecessors.is_subset(&completed_set) {
            return Err(invalid_error(format!(
                "completed past contains node {} without predecessors {:?}",
                node.id.0,
                predecessors
                    .difference(&completed_set)
                    .map(|predecessor| predecessor.0)
                    .collect::<Vec<_>>()
            )));
        }
    }
    Ok(completed_set)
}

fn direct_predecessors(inputs: &[WireRef]) -> BTreeSet<NodeId> {
    inputs
        .iter()
        .filter_map(|wire| match &wire.producer {
            WireProducer::Input { .. } => None,
            WireProducer::Node { node } => Some(*node),
        })
        .collect()
}

fn crossing_frontier(
    diagram: &SharedProgramDiagram,
    completed: &BTreeSet<NodeId>,
) -> Result<Vec<CutWire>, LispError> {
    let occurrence_sources = diagram
        .occurrences
        .iter()
        .map(|occurrence| (occurrence.id.clone(), occurrence.source.clone()))
        .collect::<BTreeMap<_, _>>();
    let mut consumers = Vec::new();
    for node in &diagram.nodes {
        for (input_index, wire) in node.inputs.iter().enumerate() {
            consumers.push((
                CutConsumer::Node {
                    node: node.id,
                    input_index: u32::try_from(input_index)
                        .map_err(|_| invalid_error("operation input frontier exceeds u32"))?,
                },
                wire,
            ));
        }
    }
    for (index, wire) in diagram.outputs.iter().enumerate() {
        consumers.push((
            CutConsumer::Output {
                index: u32::try_from(index)
                    .map_err(|_| invalid_error("codomain frontier exceeds u32"))?,
            },
            wire,
        ));
    }

    consumers
        .into_iter()
        .filter(|(consumer, wire)| {
            let producer_ready = match &wire.producer {
                WireProducer::Input { .. } => true,
                WireProducer::Node { node } => completed.contains(node),
            };
            let consumer_waiting = match consumer {
                CutConsumer::Node { node, .. } => !completed.contains(node),
                CutConsumer::Output { .. } => true,
            };
            producer_ready && consumer_waiting
        })
        .map(|(consumer, wire)| {
            let sources = wire
                .lineage
                .iter()
                .map(|occurrence| {
                    occurrence_sources.get(occurrence).cloned().ok_or_else(|| {
                        invalid_error(format!(
                            "cut wire references missing occurrence {occurrence}"
                        ))
                    })
                })
                .collect::<Result<Vec<_>, _>>()?;
            Ok(CutWire {
                wire: (*wire).clone(),
                sources,
                consumer,
            })
        })
        .collect()
}

fn invalid_error(message: impl Into<String>) -> LispError {
    LispError::Validation(message.into())
}
