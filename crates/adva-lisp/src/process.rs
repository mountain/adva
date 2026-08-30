use crate::LispError;
use crate::compile::validate_graft_trace;
use crate::validate::validate_diagram_ref;
use adva_ir::{
    CausalCut, CausalCutArtifact, CausalCutCertificate, CausalStep, CausalStepArtifact,
    CausalStepCertificate, CertificateId, CheckStatus, CutConsumer, CutWire,
    GraftArgumentIntersection, GraftFrameIntersection, GraftTrace, HistoryEvent, NodeId,
    Occurrence, OccurrenceId, OperationNode, ProgramSlice, ProgramSliceArtifact,
    ProgramSliceCertificate, SharedProgramDiagram, WireProducer, WireRef,
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
            scope: "finite checked operation DAG; past-closed node set; exact crossing wires with unchanged lineage".to_owned(),
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
        slice_occurrences(diagram, &lower, &upper, &events, &event_set, &event_history)?;
    let graft_intersections = graft_trace.map(|trace| intersect_graft_frames(trace, &event_set));
    let event_ids = events.iter().map(|node| node.id).collect::<Vec<_>>();
    let lower_suffix = past_suffix(&lower.completed);
    let upper_suffix = past_suffix(&upper.completed);

    Ok(ProgramSliceArtifact {
        result: ProgramSlice {
            lower: lower.clone(),
            upper: upper.clone(),
            events,
            lower_boundary,
            upper_boundary,
            through_wires,
            internal_events,
            occurrences,
            event_history,
            graft_intersections,
        },
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
            lower_completed: lower.completed,
            upper_completed: upper.completed,
            event_ids,
        },
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
