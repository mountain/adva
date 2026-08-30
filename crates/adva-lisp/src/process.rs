use crate::LispError;
use crate::validate::validate_diagram_ref;
use adva_ir::{
    CausalCut, CausalCutArtifact, CausalCutCertificate, CausalStep, CausalStepArtifact,
    CausalStepCertificate, CertificateId, CheckStatus, CutConsumer, CutWire, NodeId,
    SharedProgramDiagram, WireProducer, WireRef,
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
