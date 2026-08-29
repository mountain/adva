use crate::LispError;
use crate::operation::{LineageRule, resolve_operation};
use adva_ir::{
    CertificateId, CheckStatus, DiagramValidationArtifact, DiagramValidationCertificate,
    HistoryEvent, NodeId, Occurrence, OccurrenceId, OperationRef, SharedProgramDiagram, SourceId,
    ValueType, WireProducer, WireRef,
};
use std::collections::{BTreeMap, BTreeSet};

#[derive(Clone, Debug, Eq, Ord, PartialEq, PartialOrd)]
enum Endpoint {
    Input(u32),
    Node(NodeId, u32),
}

#[derive(Clone, Debug, Eq, PartialEq)]
struct CanonicalWire {
    value_type: ValueType,
    lineage: Vec<OccurrenceId>,
}

#[derive(Clone, Debug)]
struct CopyRecord {
    parent: OccurrenceId,
    children: [OccurrenceId; 2],
}

/// Validate a decoded diagram against the complete finite PSC0 import scope.
///
/// # Errors
///
/// Returns [`LispError::Validation`] when any identifier, boundary, graph,
/// linear-use, occurrence, source, or history invariant fails. The current
/// scope rejects non-empty rewrite traces because no stable rewrite checker is
/// exposed yet.
pub fn validate_diagram(
    diagram: SharedProgramDiagram,
) -> Result<DiagramValidationArtifact, LispError> {
    let certificate = validate_diagram_ref(&diagram)?;
    Ok(DiagramValidationArtifact {
        result: diagram,
        certificate,
    })
}

/// Decode JSON and return a diagram only together with its validation
/// certificate.
///
/// # Errors
///
/// Returns an IR error for malformed or unsupported JSON and a validation
/// error for a well-shaped document that violates PSC0 semantic invariants.
pub fn import_diagram_json(source: &str) -> Result<DiagramValidationArtifact, LispError> {
    validate_diagram(SharedProgramDiagram::from_json(source)?)
}

pub(crate) fn validate_diagram_ref(
    diagram: &SharedProgramDiagram,
) -> Result<DiagramValidationCertificate, LispError> {
    diagram.validate_version()?;
    validate_identifiers(diagram)?;
    if !diagram.history.rewrite_trace.is_empty() {
        return invalid("non-empty rewrite_trace is outside the checked PSC0 import scope");
    }

    let occurrences = collect_occurrences(diagram)?;
    let history = collect_history(diagram, &occurrences)?;
    let node_rules = collect_node_rules(diagram, &history.operation_events)?;
    validate_copy_history(
        &history.copy_records,
        &node_rules,
        &occurrences,
        &history.root_occurrences,
    )?;
    validate_occurrence_origin(
        &occurrences,
        &history.root_occurrences,
        &history.copy_records,
    )?;
    validate_graph(diagram, &history.input_occurrences, &history.copy_records)?;

    let mut source_partition_snapshot = diagram.source_partition();
    for members in source_partition_snapshot.values_mut() {
        members.sort();
    }
    let history_event_count = u32::try_from(diagram.history.prefix.len())
        .map_err(|_| LispError::Validation("history event count exceeds u32".to_owned()))?;

    Ok(DiagramValidationCertificate {
        id: CertificateId::explicit(format!("validate:{}:v1", diagram.function)),
        scope: "PSC0 finite adva.ir v1 diagrams; canonical source/copy history; empty rewrite trace; call identifiers checked but callee provenance not replayed".to_owned(),
        boundary: diagram.signature.clone(),
        schema: CheckStatus::Checked,
        identifiers: CheckStatus::Checked,
        graph: CheckStatus::Checked,
        operation_boundaries: CheckStatus::Checked,
        linear_use: CheckStatus::Checked,
        occurrence_paths: CheckStatus::Checked,
        source_partition: CheckStatus::Checked,
        history: CheckStatus::Checked,
        rewrite_trace: CheckStatus::Checked,
        node_ids: diagram.nodes.iter().map(|node| node.id).collect(),
        source_partition_snapshot,
        history_event_count,
    })
}

fn validate_identifiers(diagram: &SharedProgramDiagram) -> Result<(), LispError> {
    require_non_empty("module", diagram.module.as_str())?;
    require_non_empty("function module", diagram.function.module.as_str())?;
    require_non_empty("function name", diagram.function.function.as_str())?;
    if diagram.module != diagram.function.module {
        return invalid(format!(
            "diagram module {} differs from function module {}",
            diagram.module, diagram.function.module
        ));
    }

    let mut input_names = BTreeSet::new();
    for port in diagram.signature.domain().ports() {
        require_non_empty("input port name", &port.name)?;
        if !input_names.insert(port.name.as_str()) {
            return invalid(format!("duplicate input port name {:?}", port.name));
        }
    }

    for occurrence in &diagram.occurrences {
        require_non_empty("OccurrenceId", occurrence.id.as_str())?;
        require_non_empty("SourceId", occurrence.source.as_str())?;
        if occurrence.path.0.iter().any(|branch| *branch > 1) {
            return invalid(format!(
                "occurrence {} has non-binary path {:?}",
                occurrence.id, occurrence.path.0
            ));
        }
    }
    for node in &diagram.nodes {
        validate_operation_identifier(&node.operation)?;
    }
    for event in &diagram.history.prefix {
        match event {
            HistoryEvent::Source { source, occurrence } => {
                require_non_empty("history SourceId", source.as_str())?;
                require_non_empty("history OccurrenceId", occurrence.as_str())?;
            }
            HistoryEvent::Copy {
                parent, children, ..
            } => {
                require_non_empty("copy parent OccurrenceId", parent.as_str())?;
                for child in children {
                    require_non_empty("copy child OccurrenceId", child.as_str())?;
                }
            }
            HistoryEvent::Operation { operation, .. } => {
                validate_operation_identifier(operation)?;
            }
            HistoryEvent::Call { function } => {
                require_non_empty("call module", function.module.as_str())?;
                require_non_empty("call function", function.function.as_str())?;
            }
        }
    }
    Ok(())
}

fn validate_operation_identifier(operation: &OperationRef) -> Result<(), LispError> {
    require_non_empty("operation namespace", &operation.namespace)?;
    require_non_empty("operation name", &operation.name)?;
    for (name, value) in &operation.parameters {
        require_non_empty("operation parameter name", name)?;
        let normalized =
            adva_ir::Rational::new(value.numerator, value.denominator).map_err(|error| {
                LispError::Validation(format!(
                    "operation {}:{} has invalid parameter {name:?}: {error}",
                    operation.namespace, operation.name
                ))
            })?;
        if normalized != *value {
            return invalid(format!(
                "operation {}:{} parameter {name:?} is not canonically normalized",
                operation.namespace, operation.name
            ));
        }
    }
    Ok(())
}

fn require_non_empty(label: &str, value: &str) -> Result<(), LispError> {
    if value.is_empty() {
        invalid(format!("{label} must not be empty"))
    } else {
        Ok(())
    }
}

fn collect_occurrences(
    diagram: &SharedProgramDiagram,
) -> Result<BTreeMap<OccurrenceId, &Occurrence>, LispError> {
    let mut occurrences = BTreeMap::new();
    let mut source_paths = BTreeSet::new();
    let mut expected_paths = BTreeMap::new();
    for occurrence in &diagram.occurrences {
        if occurrences
            .insert(occurrence.id.clone(), occurrence)
            .is_some()
        {
            return invalid(format!("duplicate OccurrenceId {}", occurrence.id));
        }
        if !source_paths.insert((occurrence.source.clone(), occurrence.path.clone())) {
            return invalid(format!(
                "duplicate occurrence path {:?} within source {}",
                occurrence.path.0, occurrence.source
            ));
        }
        expected_paths.insert(occurrence.id.clone(), occurrence.path.clone());
    }
    if expected_paths != diagram.history.occurrence_paths {
        return invalid("history occurrence_paths does not exactly match occurrence records");
    }
    Ok(occurrences)
}

struct CollectedHistory {
    input_occurrences: Vec<OccurrenceId>,
    root_occurrences: BTreeSet<OccurrenceId>,
    copy_records: BTreeMap<NodeId, Vec<CopyRecord>>,
    operation_events: Vec<(NodeId, OperationRef)>,
}

fn collect_history(
    diagram: &SharedProgramDiagram,
    occurrences: &BTreeMap<OccurrenceId, &Occurrence>,
) -> Result<CollectedHistory, LispError> {
    let mut input_occurrences = Vec::new();
    let mut root_occurrences = BTreeSet::new();
    let mut root_sources = BTreeSet::new();
    let mut copy_records: BTreeMap<NodeId, Vec<CopyRecord>> = BTreeMap::new();
    let mut operation_events = Vec::new();
    let mut left_source_prefix = false;
    let mut pending_copy_node = None;

    for event in &diagram.history.prefix {
        match event {
            HistoryEvent::Source { source, occurrence } => {
                if left_source_prefix {
                    return invalid("Source history events must form the initial prefix");
                }
                let record = occurrences.get(occurrence).ok_or_else(|| {
                    LispError::Validation(format!(
                        "Source history references missing occurrence {occurrence}"
                    ))
                })?;
                if &record.source != source || !record.path.0.is_empty() {
                    return invalid(format!(
                        "Source history for {occurrence} does not match its root occurrence"
                    ));
                }
                if !root_occurrences.insert(occurrence.clone()) {
                    return invalid(format!("duplicate source occurrence {occurrence}"));
                }
                if !root_sources.insert(source.clone()) {
                    return invalid(format!(
                        "independent input occurrences share SourceId {source}"
                    ));
                }
                input_occurrences.push(occurrence.clone());
            }
            HistoryEvent::Copy {
                node,
                parent,
                children,
            } => {
                left_source_prefix = true;
                if pending_copy_node.is_some_and(|pending| pending != *node) {
                    return invalid("copy records for different nodes are interleaved");
                }
                pending_copy_node = Some(*node);
                let [left, right] = children.as_slice() else {
                    return invalid(format!(
                        "copy history for node {} must contain exactly two children",
                        node.0
                    ));
                };
                copy_records.entry(*node).or_default().push(CopyRecord {
                    parent: parent.clone(),
                    children: [left.clone(), right.clone()],
                });
            }
            HistoryEvent::Operation { node, operation } => {
                left_source_prefix = true;
                if pending_copy_node.is_some_and(|pending| pending != *node) {
                    return invalid(format!(
                        "copy history is not immediately followed by operation node {}",
                        node.0
                    ));
                }
                pending_copy_node = None;
                operation_events.push((*node, operation.clone()));
            }
            HistoryEvent::Call { .. } => {
                left_source_prefix = true;
                if pending_copy_node.is_some() {
                    return invalid("call history interrupts pending copy records");
                }
            }
        }
    }

    if pending_copy_node.is_some() {
        return invalid("copy history is not followed by its operation event");
    }

    if input_occurrences.len() != diagram.signature.domain().ports().len() {
        return invalid(format!(
            "history has {} source roots for {} domain ports",
            input_occurrences.len(),
            diagram.signature.domain().ports().len()
        ));
    }

    Ok(CollectedHistory {
        input_occurrences,
        root_occurrences,
        copy_records,
        operation_events,
    })
}

fn collect_node_rules(
    diagram: &SharedProgramDiagram,
    operation_events: &[(NodeId, OperationRef)],
) -> Result<BTreeMap<NodeId, LineageRule>, LispError> {
    if operation_events.len() != diagram.nodes.len() {
        return invalid(format!(
            "history has {} operation events for {} nodes",
            operation_events.len(),
            diagram.nodes.len()
        ));
    }
    let mut node_rules = BTreeMap::new();
    for (index, node) in diagram.nodes.iter().enumerate() {
        if node_rules.contains_key(&node.id) {
            return invalid(format!("duplicate NodeId {}", node.id.0));
        }
        let spec = resolve_operation(&node.operation).map_err(as_validation_error)?;
        spec.validate_wires(&node.inputs)
            .map_err(as_validation_error)?;
        spec.validate_outputs(&node.output_types)
            .map_err(as_validation_error)?;
        let (event_node, event_operation) = &operation_events[index];
        if event_node != &node.id || event_operation != &node.operation {
            return invalid(format!(
                "operation history at position {index} does not match node {}",
                node.id.0
            ));
        }
        node_rules.insert(node.id, spec.lineage_rule);
    }
    Ok(node_rules)
}

fn validate_copy_history(
    copy_records: &BTreeMap<NodeId, Vec<CopyRecord>>,
    node_rules: &BTreeMap<NodeId, LineageRule>,
    occurrences: &BTreeMap<OccurrenceId, &Occurrence>,
    root_occurrences: &BTreeSet<OccurrenceId>,
) -> Result<(), LispError> {
    let mut claimed_children = BTreeSet::new();
    for (node, records) in copy_records {
        if node_rules.get(node) != Some(&LineageRule::Copy) {
            return invalid(format!(
                "copy history references non-copy or missing node {}",
                node.0
            ));
        }
        let mut parents = BTreeSet::new();
        for record in records {
            if !parents.insert(record.parent.clone()) {
                return invalid(format!(
                    "copy node {} repeats parent occurrence {}",
                    node.0, record.parent
                ));
            }
            if record.children[0] == record.children[1] {
                return invalid(format!(
                    "copy node {} reuses one child OccurrenceId",
                    node.0
                ));
            }
            let parent = occurrences.get(&record.parent).ok_or_else(|| {
                LispError::Validation(format!(
                    "copy node {} references missing parent {}",
                    node.0, record.parent
                ))
            })?;
            for (branch, child_id) in record.children.iter().enumerate() {
                if root_occurrences.contains(child_id) || !claimed_children.insert(child_id.clone())
                {
                    return invalid(format!(
                        "copy child {child_id} is a root or is claimed more than once"
                    ));
                }
                let child = occurrences.get(child_id).ok_or_else(|| {
                    LispError::Validation(format!(
                        "copy node {} references missing child {child_id}",
                        node.0
                    ))
                })?;
                if child.source != parent.source || child.path != parent.path.branch(branch as u32)
                {
                    return invalid(format!(
                        "copy child {child_id} does not preserve source and binary path"
                    ));
                }
            }
        }
    }
    Ok(())
}

fn validate_occurrence_origin(
    occurrences: &BTreeMap<OccurrenceId, &Occurrence>,
    root_occurrences: &BTreeSet<OccurrenceId>,
    copy_records: &BTreeMap<NodeId, Vec<CopyRecord>>,
) -> Result<(), LispError> {
    let copy_children = copy_records
        .values()
        .flatten()
        .flat_map(|record| record.children.iter().cloned())
        .collect::<BTreeSet<_>>();
    for (id, occurrence) in occurrences {
        if occurrence.path.0.is_empty() {
            if !root_occurrences.contains(id) {
                return invalid(format!("root occurrence {id} has no Source history event"));
            }
        } else if !copy_children.contains(id) {
            return invalid(format!("non-root occurrence {id} has no copy origin"));
        }
    }
    if occurrences.len() != root_occurrences.len() + copy_children.len() {
        return invalid("occurrence origins do not form a disjoint source/copy partition");
    }
    Ok(())
}

fn validate_graph(
    diagram: &SharedProgramDiagram,
    input_occurrences: &[OccurrenceId],
    copy_records: &BTreeMap<NodeId, Vec<CopyRecord>>,
) -> Result<(), LispError> {
    let mut available = BTreeMap::new();
    let mut uses = BTreeMap::new();
    for (index, (port, occurrence)) in diagram
        .signature
        .domain()
        .ports()
        .iter()
        .zip(input_occurrences)
        .enumerate()
    {
        let index = u32::try_from(index)
            .map_err(|_| LispError::Validation("domain frontier exceeds u32".to_owned()))?;
        let endpoint = Endpoint::Input(index);
        available.insert(
            endpoint.clone(),
            CanonicalWire {
                value_type: port.value_type,
                lineage: vec![occurrence.clone()],
            },
        );
        uses.insert(endpoint, 0_u32);
    }

    for node in &diagram.nodes {
        let spec = resolve_operation(&node.operation).map_err(as_validation_error)?;
        let inputs = node
            .inputs
            .iter()
            .map(|wire| consume_wire(wire, &available, &mut uses))
            .collect::<Result<Vec<_>, _>>()?;
        let output_lineages = match spec.lineage_rule {
            LineageRule::MergeInputs => {
                let merged = inputs
                    .iter()
                    .flat_map(|wire| wire.lineage.iter().cloned())
                    .collect::<Vec<_>>();
                vec![merged; spec.output_types.len()]
            }
            LineageRule::Discard => Vec::new(),
            LineageRule::Swap => vec![inputs[1].lineage.clone(), inputs[0].lineage.clone()],
            LineageRule::Copy => copy_lineages(node.id, &inputs[0].lineage, copy_records)?,
        };
        if output_lineages.len() != node.output_types.len() {
            return invalid(format!(
                "node {} lineage arity differs from its output boundary",
                node.id.0
            ));
        }
        for (output_index, (value_type, lineage)) in node
            .output_types
            .iter()
            .copied()
            .zip(output_lineages)
            .enumerate()
        {
            let endpoint = Endpoint::Node(node.id, output_index as u32);
            if available
                .insert(
                    endpoint.clone(),
                    CanonicalWire {
                        value_type,
                        lineage,
                    },
                )
                .is_some()
            {
                return invalid(format!("duplicate node output endpoint {endpoint:?}"));
            }
            uses.insert(endpoint, 0);
        }
    }

    let output_types = diagram
        .outputs
        .iter()
        .map(|wire| consume_wire(wire, &available, &mut uses).map(|item| item.value_type))
        .collect::<Result<Vec<_>, _>>()?;
    if output_types.as_slice() != diagram.signature.codomain().types() {
        return invalid(format!(
            "diagram frontier outputs {output_types:?} differ from codomain {:?}",
            diagram.signature.codomain().types()
        ));
    }

    let invalid_uses = uses
        .iter()
        .filter(|(_, count)| **count != 1)
        .map(|(endpoint, count)| format!("{endpoint:?} used {count} times"))
        .collect::<Vec<_>>();
    if !invalid_uses.is_empty() {
        return invalid(format!(
            "every frontier endpoint must be consumed exactly once: {invalid_uses:?}"
        ));
    }
    Ok(())
}

fn consume_wire(
    wire: &WireRef,
    available: &BTreeMap<Endpoint, CanonicalWire>,
    uses: &mut BTreeMap<Endpoint, u32>,
) -> Result<CanonicalWire, LispError> {
    let endpoint = match &wire.producer {
        WireProducer::Input { index } => {
            if wire.output_index != 0 {
                return invalid(format!(
                    "input {index} is referenced with nonzero output index {}",
                    wire.output_index
                ));
            }
            Endpoint::Input(*index)
        }
        WireProducer::Node { node } => Endpoint::Node(*node, wire.output_index),
    };
    let canonical = available.get(&endpoint).ok_or_else(|| {
        LispError::Validation(format!(
            "wire references missing or non-topological endpoint {endpoint:?}"
        ))
    })?;
    if wire.value_type != canonical.value_type || wire.lineage != canonical.lineage {
        return invalid(format!(
            "wire metadata for {endpoint:?} differs from its canonical producer"
        ));
    }
    let count = uses.get_mut(&endpoint).ok_or_else(|| {
        LispError::Validation(format!("wire endpoint {endpoint:?} has no use counter"))
    })?;
    *count = count
        .checked_add(1)
        .ok_or_else(|| LispError::Validation("wire use count overflow".to_owned()))?;
    Ok(canonical.clone())
}

fn copy_lineages(
    node: NodeId,
    parents: &[OccurrenceId],
    copy_records: &BTreeMap<NodeId, Vec<CopyRecord>>,
) -> Result<Vec<Vec<OccurrenceId>>, LispError> {
    let records = copy_records.get(&node).map(Vec::as_slice).unwrap_or(&[]);
    if records.len() != parents.len() {
        return invalid(format!(
            "copy node {} has {} lineage parents but {} copy history records",
            node.0,
            parents.len(),
            records.len()
        ));
    }
    let by_parent = records
        .iter()
        .map(|record| (record.parent.clone(), record.children.clone()))
        .collect::<BTreeMap<_, _>>();
    let mut outputs = [Vec::new(), Vec::new()];
    for parent in parents {
        let children = by_parent.get(parent).ok_or_else(|| {
            LispError::Validation(format!(
                "copy node {} has no history for lineage parent {parent}",
                node.0
            ))
        })?;
        outputs[0].push(children[0].clone());
        outputs[1].push(children[1].clone());
    }
    Ok(outputs.into_iter().collect())
}

fn invalid<T>(message: impl Into<String>) -> Result<T, LispError> {
    Err(LispError::Validation(message.into()))
}

fn as_validation_error(error: LispError) -> LispError {
    LispError::Validation(error.to_string())
}
