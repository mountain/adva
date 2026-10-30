//! Research-local native PSC0 input binding; no stable type or schema promotion.
//! Codex (OpenAI), through Mingli Yuan's authorized account proxy, Unknown v0.3.
//! The observer law compares exact decorated structure, never Real evaluation.

use adva_ir::{
    CompilationArtifact, CutConsumer, CutWire, GraftFrameKind, HistoryEvent, NodeId, Occurrence,
    OccurrenceId, OccurrencePath, OperationRef, QualifiedName, Rational, SharedProgramDiagram,
    SourceId, ValueType, WireProducer, WireRef,
};
use adva_lisp::{
    analyze_program_slice_with_graft, compile_function, import_diagram_json, link_modules,
    parse_module, validate_diagram,
};
use serde_json::{Value, json};
use std::{
    collections::{BTreeMap, BTreeSet},
    env, fs,
    path::Path,
    process::{self, Command, Stdio},
    thread,
    time::{Duration, Instant},
};

const MODULE: &str = "native-binding";
const BODY: &str = "(frontier (add (copy (use static))) (add (copy (use dynamic))) (discard 1))";

// The current parser freezes literals at builtin constant@2. The retained
// OperationRef::constant helper names historical constant@1; do not conflate
// either exact operation declaration with numerical value equality.
fn literal_operation(value: Rational) -> OperationRef {
    OperationRef {
        version: 2,
        ..OperationRef::constant(value)
    }
}

// Context qualification is explicit. Local occ:N/node indices are not globally fresh.
#[derive(Clone, Debug, Eq, PartialEq)]
struct QualifiedOccurrence {
    context: QualifiedName,
    source: SourceId,
    local_id: OccurrenceId,
    path: OccurrencePath,
}

#[derive(Clone, Debug, Eq, PartialEq)]
struct ResearchCertificate {
    source_snapshot: SharedProgramDiagram,
    residual_snapshot: SharedProgramDiagram,
    static_value: Rational,
    bound_source: SourceId,
    dynamic_source: (SourceId, SourceId),
    event_map: Vec<(NodeId, NodeId)>,
    occurrence_map: Vec<(QualifiedOccurrence, Option<QualifiedOccurrence>)>,
    forgotten_static_occurrences: Vec<Occurrence>,
    forgotten_static_history: Vec<HistoryEvent>,
    binding_node: NodeId,
}

// This request is fixed independently of the proposed certificate. IDs alone
// cannot bind the source body, and changing a certificate cannot change the task.
#[derive(Clone)]
struct ExpectedRequest {
    source_snapshot: SharedProgramDiagram,
    residual_context: QualifiedName,
    static_value: Rational,
}

#[derive(Clone, Debug, Eq, PartialEq)]
struct ExpectedExternalLeaf {
    source: String,
    occurrence: String,
    target_source: String,
    target_occurrence: String,
}

#[derive(Debug, Eq, PartialEq)]
enum Outcome {
    Certified(Box<ResearchCertificate>),
    Refused(&'static str),
    Unknown(&'static str),
}

struct Budget(usize);

impl Budget {
    fn charge(&mut self, work: usize) -> Result<(), Outcome> {
        if self.0 < work {
            return Err(Outcome::Unknown("structural checker budget exhausted"));
        }
        self.0 -= work;
        Ok(())
    }
}

fn qualified(diagram: &SharedProgramDiagram, occurrence: &Occurrence) -> QualifiedOccurrence {
    QualifiedOccurrence {
        context: diagram.function.clone(),
        source: occurrence.source.clone(),
        local_id: occurrence.id.clone(),
        path: occurrence.path.clone(),
    }
}

fn fixtures(body: &str, value: Rational) -> (CompilationArtifact, CompilationArtifact) {
    fixtures_in(MODULE, body, value)
}

fn fixtures_in(
    module: &str,
    body: &str,
    value: Rational,
) -> (CompilationArtifact, CompilationArtifact) {
    let text = format!(
        "(module {module} (export source residual)\n\
         (def source (fn ((static Real) (dynamic Real)) (outputs Real Real) {body}))\n\
         (def residual (fn ((dynamic Real)) (outputs Real Real)\n\
           (call source {}/{} (use dynamic)))))",
        value.numerator, value.denominator
    );
    let linked = link_modules(vec![parse_module(&text).unwrap()]).unwrap();
    (
        compile_function(&linked, module, "source").unwrap(),
        compile_function(&linked, module, "residual").unwrap(),
    )
}

fn input_source(artifact: &CompilationArtifact, index: usize) -> SourceId {
    let root = &artifact.graft_trace.result.frames[0];
    let id = &root.holes[index].entry_wire.lineage[0];
    artifact
        .result
        .occurrences
        .iter()
        .find(|occurrence| &occurrence.id == id)
        .unwrap()
        .source
        .clone()
}

// Proposal construction uses the compiler's call-body region. The receiver
// below separately checks coverage, each wire, lineage, history and slice.
fn propose(
    source: &CompilationArtifact,
    residual: &CompilationArtifact,
    static_value: Rational,
) -> ResearchCertificate {
    let bound_source = input_source(source, 0);
    let dynamic_source = (input_source(source, 1), input_source(residual, 0));
    let call = &residual.graft_trace.result.frames[1];
    let occurrence_map = source
        .result
        .occurrences
        .iter()
        .map(|occurrence| {
            let target = residual.result.occurrences.iter().find(|target| {
                occurrence.source == dynamic_source.0
                    && target.source == dynamic_source.1
                    && occurrence.path == target.path
            });
            (
                qualified(&source.result, occurrence),
                target.map(|target| qualified(&residual.result, target)),
            )
        })
        .collect();
    let static_ids: BTreeSet<_> = source
        .result
        .occurrences
        .iter()
        .filter(|occurrence| occurrence.source == bound_source)
        .map(|occurrence| occurrence.id.clone())
        .collect();
    ResearchCertificate {
        source_snapshot: source.result.clone(),
        residual_snapshot: residual.result.clone(),
        static_value,
        bound_source,
        dynamic_source,
        event_map: source
            .result
            .nodes
            .iter()
            .map(|node| node.id)
            .zip(call.body_region.iter().copied())
            .collect(),
        occurrence_map,
        forgotten_static_occurrences: source
            .result
            .occurrences
            .iter()
            .filter(|occurrence| static_ids.contains(&occurrence.id))
            .cloned()
            .collect(),
        forgotten_static_history: source
            .result
            .history
            .prefix
            .iter()
            .filter(|event| match event {
                HistoryEvent::Source { occurrence, .. } => static_ids.contains(occurrence),
                HistoryEvent::Copy { parent, .. } => static_ids.contains(parent),
                _ => false,
            })
            .cloned()
            .collect(),
        binding_node: residual.result.nodes[0].id,
    }
}

fn receive(
    source: &CompilationArtifact,
    residual: &CompilationArtifact,
    certificate: &ResearchCertificate,
    request: &ExpectedRequest,
    work: usize,
) -> Outcome {
    match check(source, residual, certificate, request, &mut Budget(work)) {
        Ok(()) => Outcome::Certified(Box::new(certificate.clone())),
        Err(outcome) => outcome,
    }
}

fn require(condition: bool, reason: &'static str) -> Result<(), Outcome> {
    if condition {
        Ok(())
    } else {
        Err(Outcome::Refused(reason))
    }
}

fn check(
    source: &CompilationArtifact,
    residual: &CompilationArtifact,
    certificate: &ResearchCertificate,
    request: &ExpectedRequest,
    budget: &mut Budget,
) -> Result<(), Outcome> {
    budget.charge(1)?;
    let source_diagram = &source.result;
    let residual_diagram = &residual.result;
    // Finite admission before kernel validation; this test-local profile accepts
    // only two Real inputs, one bound literal, and at most sixteen body events.
    for diagram in [source_diagram, residual_diagram] {
        if diagram.nodes.len() > 17
            || diagram.occurrences.len() > 32
            || diagram.history.prefix.len() > 64
            || diagram.signature.outputs.len() > 2
            || diagram.signature.inputs.len() > 2
            || diagram.nodes.iter().any(|node| node.inputs.len() > 2)
        {
            return Err(Outcome::Unknown(
                "outside the fixed finite structural profile",
            ));
        }
        budget.charge(
            1 + diagram.nodes.len() + diagram.occurrences.len() + diagram.history.prefix.len(),
        )?;
        validate_diagram(diagram.clone())
            .map_err(|_| Outcome::Refused("native diagram validation failed"))?;
    }
    require(
        *source_diagram == request.source_snapshot
            && certificate.source_snapshot == *source_diagram
            && certificate.residual_snapshot == *residual_diagram,
        "source or residual snapshot does not bind the caller's question",
    )?;
    require(
        residual_diagram.function == request.residual_context
            && source_diagram.function != residual_diagram.function,
        "residual must have the independently declared distinct checked context",
    )?;
    require(
        certificate.static_value == request.static_value
            && Rational::new(
                request.static_value.numerator,
                request.static_value.denominator,
            )
            .ok()
                == Some(request.static_value),
        "static rational is changed or noncanonical",
    )?;
    require(
        source_diagram.signature.inputs.len() == 2
            && residual_diagram.signature.inputs.len() == 1
            && source_diagram.signature.inputs[0].value_type == ValueType::Real
            && source_diagram.signature.inputs[1].value_type == ValueType::Real
            && source_diagram.signature.inputs[1] == residual_diagram.signature.inputs[0]
            && source_diagram.signature.outputs == residual_diagram.signature.outputs,
        "input-binding boundary mismatch",
    )?;
    require(
        source.graft_trace.result.frames.len() == 1
            && residual.graft_trace.result.frames.len() == 2,
        "only call-free source and one wrapper call are admitted",
    )?;
    // These calls revalidate the supplied graft data; booleans on supplied
    // compilation/graft certificates are not taken as authorization.
    let source_past: Vec<_> = source_diagram.nodes.iter().map(|node| node.id).collect();
    let residual_past: Vec<_> = residual_diagram.nodes.iter().map(|node| node.id).collect();
    budget.charge(3)?;
    let source_slice = analyze_program_slice_with_graft(
        source_diagram,
        &source.graft_trace.result,
        &[],
        &source_past,
    )
    .map_err(|_| Outcome::Refused("source graft/slice validation failed"))?;
    let residual_full = analyze_program_slice_with_graft(
        residual_diagram,
        &residual.graft_trace.result,
        &[],
        &residual_past,
    )
    .map_err(|_| Outcome::Refused("residual graft/slice validation failed"))?;
    require(
        source_slice.certificate.certified() && residual_full.certificate.certified(),
        "native slice certificate not checked",
    )?;
    let call = &residual.graft_trace.result.frames[1];
    require(
        call.kind == GraftFrameKind::Call
            && call.callee == source_diagram.function
            && call.boundary == source_diagram.signature
            && call.holes.len() == 2
            && call.body_region.len() == source_diagram.nodes.len()
            && residual_diagram.nodes.len() == source_diagram.nodes.len() + 1,
        "graft is not the complete declared source body",
    )?;
    let binding = &residual_diagram.nodes[0];
    require(
        certificate.binding_node == binding.id
            && binding.operation == literal_operation(request.static_value)
            && binding.inputs.is_empty()
            && binding.output_types == vec![ValueType::Real],
        "binding prefix is not the declared exact literal",
    )?;
    require(
        certificate.bound_source == input_source(source, 0)
            && certificate.dynamic_source == (input_source(source, 1), input_source(residual, 0)),
        "source correspondence mismatch",
    )?;
    require(
        certificate.event_map
            == source_diagram
                .nodes
                .iter()
                .map(|node| node.id)
                .zip(call.body_region.iter().copied())
                .collect::<Vec<_>>(),
        "incomplete or reordered body event correspondence",
    )?;
    let events: BTreeMap<_, _> = certificate.event_map.iter().copied().collect();
    let mut occurrences = BTreeMap::new();
    require(
        certificate.occurrence_map.len() == source_diagram.occurrences.len(),
        "occurrence correspondence is incomplete",
    )?;
    let mut seen_residual = BTreeSet::new();
    let mut static_occurrences = Vec::new();
    for (source_occurrence, (declared, target)) in source_diagram
        .occurrences
        .iter()
        .zip(&certificate.occurrence_map)
    {
        budget.charge(1)?;
        require(
            *declared == qualified(source_diagram, source_occurrence),
            "qualified source occurrence mismatch",
        )?;
        if source_occurrence.source == certificate.bound_source {
            require(
                target.is_none(),
                "static lineage was silently retained or identified",
            )?;
            static_occurrences.push(source_occurrence.clone());
            occurrences.insert(source_occurrence.id.clone(), None);
        } else {
            let target = target
                .as_ref()
                .ok_or(Outcome::Refused("dynamic occurrence was forgotten"))?;
            require(
                source_occurrence.source == certificate.dynamic_source.0
                    && target.context == residual_diagram.function
                    && target.source == certificate.dynamic_source.1
                    && target.path == source_occurrence.path,
                "dynamic source, context or copy path changed",
            )?;
            let actual = residual_diagram
                .occurrences
                .iter()
                .find(|occurrence| occurrence.id == target.local_id)
                .ok_or(Outcome::Refused("target occurrence is absent"))?;
            require(
                qualified(residual_diagram, actual) == *target
                    && seen_residual.insert(target.local_id.clone()),
                "target occurrence is altered or reused",
            )?;
            occurrences.insert(source_occurrence.id.clone(), Some(target.local_id.clone()));
        }
    }
    require(
        seen_residual.len() == residual_diagram.occurrences.len()
            && certificate.forgotten_static_occurrences == static_occurrences,
        "static ledger or residual occurrence coverage is incomplete",
    )?;
    let static_ids: BTreeSet<_> = static_occurrences.iter().map(|o| o.id.clone()).collect();
    let forgotten: Vec<_> = source_diagram
        .history
        .prefix
        .iter()
        .filter(|event| match event {
            HistoryEvent::Source { occurrence, .. } => static_ids.contains(occurrence),
            HistoryEvent::Copy { parent, .. } => static_ids.contains(parent),
            _ => false,
        })
        .cloned()
        .collect();
    require(
        certificate.forgotten_static_history == forgotten,
        "static source/copy history ledger is incomplete",
    )?;
    let project_wire = |wire: &WireRef| -> Result<WireRef, Outcome> {
        let mut mapped = wire.clone();
        mapped.producer = match wire.producer {
            WireProducer::Input { index } => match index {
                0 => WireProducer::Node { node: binding.id },
                1 => WireProducer::Input { index: 0 },
                _ => return Err(Outcome::Refused("unsupported source input")),
            },
            WireProducer::Node { node } => WireProducer::Node {
                node: *events
                    .get(&node)
                    .ok_or(Outcome::Refused("unmapped body producer"))?,
            },
        };
        mapped.lineage = wire
            .lineage
            .iter()
            .map(|id| {
                occurrences
                    .get(id)
                    .cloned()
                    .ok_or(Outcome::Refused("unmapped lineage"))
            })
            .collect::<Result<Vec<_>, _>>()?
            .into_iter()
            .flatten()
            .collect();
        Ok(mapped)
    };
    require(
        project_wire(&source.graft_trace.result.frames[0].holes[0].entry_wire)?
            == call.holes[0].entry_wire
            && project_wire(&source.graft_trace.result.frames[0].holes[1].entry_wire)?
                == call.holes[1].entry_wire,
        "ordered graft hole correspondence changed",
    )?;
    for node in &source_diagram.nodes {
        budget.charge(1 + node.inputs.len())?;
        let target = residual_diagram
            .nodes
            .iter()
            .find(|target| target.id == events[&node.id])
            .ok_or(Outcome::Refused("mapped body event absent"))?;
        require(
            node.operation == target.operation
                && node.output_types == target.output_types
                && node
                    .inputs
                    .iter()
                    .map(&project_wire)
                    .collect::<Result<Vec<_>, _>>()?
                    == target.inputs,
            "ordered body operation/wire correspondence changed",
        )?;
    }
    require(
        source_diagram
            .outputs
            .iter()
            .map(&project_wire)
            .collect::<Result<Vec<_>, _>>()?
            == residual_diagram.outputs,
        "ordered output correspondence changed",
    )?;
    let body_slice = analyze_program_slice_with_graft(
        residual_diagram,
        &residual.graft_trace.result,
        &[binding.id],
        &residual_past,
    )
    .map_err(|_| Outcome::Refused("residual body slice validation failed"))?;
    require(
        body_slice.certificate.certified()
            && body_slice.result.internal_events
                == source_slice
                    .result
                    .internal_events
                    .iter()
                    .map(|id| events[id])
                    .collect::<Vec<_>>(),
        "hidden body events were erased",
    )?;
    let project_cut = |cut: &CutWire| -> Result<CutWire, Outcome> {
        Ok(CutWire {
            wire: project_wire(&cut.wire)?,
            sources: cut
                .sources
                .iter()
                .filter(|source| **source != certificate.bound_source)
                .map(|source| {
                    if *source == certificate.dynamic_source.0 {
                        Ok(certificate.dynamic_source.1.clone())
                    } else {
                        Err(Outcome::Refused("unmapped cut source"))
                    }
                })
                .collect::<Result<Vec<_>, _>>()?,
            consumer: match cut.consumer {
                CutConsumer::Node { node, input_index } => CutConsumer::Node {
                    node: events[&node],
                    input_index,
                },
                CutConsumer::Output { index } => CutConsumer::Output { index },
            },
        })
    };
    // Cut vectors use each diagram's canonical producer order. Compare exact
    // incidences without pretending that the two vector orders are identical.
    for (left, right) in [
        (
            &source_slice.result.lower.frontier,
            &body_slice.result.lower.frontier,
        ),
        (
            &source_slice.result.upper.frontier,
            &body_slice.result.upper.frontier,
        ),
        (
            &source_slice.result.through_wires,
            &body_slice.result.through_wires,
        ),
        (
            &source_slice.result.lower_boundary,
            &body_slice.result.lower_boundary,
        ),
        (
            &source_slice.result.upper_boundary,
            &body_slice.result.upper_boundary,
        ),
    ] {
        budget.charge(left.len())?;
        let projected = left
            .iter()
            .map(&project_cut)
            .collect::<Result<Vec<_>, _>>()?;
        require(
            projected.len() == right.len() && projected.iter().all(|wire| right.contains(wire)),
            "decorated cut observation does not commute",
        )?;
    }
    let mut projected_history = Vec::new();
    for event in &source_slice.result.event_history {
        budget.charge(1)?;
        match event {
            HistoryEvent::Copy {
                node,
                parent,
                children,
            } if !static_ids.contains(parent) => {
                projected_history.push(HistoryEvent::Copy {
                    node: events[node],
                    parent: occurrences[parent]
                        .clone()
                        .ok_or(Outcome::Refused("copy parent missing"))?,
                    children: children
                        .iter()
                        .map(|id| {
                            occurrences[id]
                                .clone()
                                .ok_or(Outcome::Refused("copy child missing"))
                        })
                        .collect::<Result<Vec<_>, _>>()?,
                });
            }
            HistoryEvent::Copy { .. } => {}
            HistoryEvent::Operation { node, operation } => {
                projected_history.push(HistoryEvent::Operation {
                    node: events[node],
                    operation: operation.clone(),
                });
            }
            _ => return Err(Outcome::Refused("unsupported body history event")),
        }
    }
    require(
        projected_history == body_slice.result.event_history,
        "body history observation does not commute",
    )?;
    Ok(())
}

fn request(
    source: &CompilationArtifact,
    residual: &CompilationArtifact,
    value: Rational,
) -> ExpectedRequest {
    ExpectedRequest {
        source_snapshot: source.result.clone(),
        residual_context: residual.result.function.clone(),
        static_value: value,
    }
}

fn qualified_json(occurrence: &QualifiedOccurrence) -> Value {
    json!({
        "context": occurrence.context.to_string(),
        "source": occurrence.source.as_str(),
        "occurrence": occurrence.local_id.as_str(),
        "path": &occurrence.path.0,
    })
}

fn external_leaf_json(leaf: &ExpectedExternalLeaf) -> Value {
    json!({
        "source": leaf.source,
        "occurrence": leaf.occurrence,
        "target_source": leaf.target_source,
        "target_occurrence": leaf.target_occurrence,
    })
}

fn only_dynamic_pair(
    certificate: &ResearchCertificate,
) -> Result<(&QualifiedOccurrence, &QualifiedOccurrence), Outcome> {
    let dynamic = certificate
        .occurrence_map
        .iter()
        .filter_map(|(source, target)| target.as_ref().map(|target| (source, target)))
        .collect::<Vec<_>>();
    if dynamic.len() != 1 {
        return Err(Outcome::Unknown(
            "outside the one-dynamic-occurrence request profile",
        ));
    }
    Ok(dynamic[0])
}

fn serialized_leaf_request(
    source: &CompilationArtifact,
    residual: &CompilationArtifact,
    certificate: &ResearchCertificate,
    leaf: &ExpectedExternalLeaf,
) -> String {
    let (native_source, native_target) = only_dynamic_pair(certificate).unwrap();
    json!({
        "profile": "adva.research.native-input-binding-open-line-leaf-request.v0",
        "source_diagram_json": source.result.to_json().unwrap(),
        "residual_diagram_json": residual.result.to_json().unwrap(),
        "external_leaf": external_leaf_json(leaf),
        "native_occurrence_map": [{
            "source": qualified_json(native_source),
            "target": qualified_json(native_target),
        }],
    })
    .to_string()
}

// This research-only boundary keeps the independently supplied current
// artifacts, expected request, external leaf, and both budgets explicit.
#[allow(clippy::too_many_arguments)]
fn receive_serialized_leaf_request(
    source: &CompilationArtifact,
    residual: &CompilationArtifact,
    certificate: &ResearchCertificate,
    request: &ExpectedRequest,
    expected_leaf: &ExpectedExternalLeaf,
    encoded: &str,
    byte_budget: usize,
    structural_work: usize,
) -> Outcome {
    if encoded.len() > byte_budget {
        return Outcome::Unknown("serialized request byte budget exhausted");
    }
    let value: Value = match serde_json::from_str(encoded) {
        Ok(value) => value,
        Err(_) => return Outcome::Refused("serialized request malformed"),
    };
    let root = match value.as_object() {
        Some(root) => root,
        None => return Outcome::Refused("serialized request shape mismatch"),
    };
    let expected_root = BTreeSet::from([
        "external_leaf",
        "native_occurrence_map",
        "profile",
        "residual_diagram_json",
        "source_diagram_json",
    ]);
    if root.keys().map(String::as_str).collect::<BTreeSet<_>>() != expected_root {
        return Outcome::Refused("serialized request shape mismatch");
    }
    if root.get("profile").and_then(Value::as_str)
        != Some("adva.research.native-input-binding-open-line-leaf-request.v0")
    {
        return Outcome::Refused("serialized request profile mismatch");
    }
    let source_json = match root.get("source_diagram_json").and_then(Value::as_str) {
        Some(source_json) => source_json,
        None => return Outcome::Refused("serialized request shape mismatch"),
    };
    let residual_json = match root.get("residual_diagram_json").and_then(Value::as_str) {
        Some(residual_json) => residual_json,
        None => return Outcome::Refused("serialized request shape mismatch"),
    };
    let imported_source = match import_diagram_json(source_json) {
        Ok(diagram) => diagram,
        Err(_) => return Outcome::Refused("serialized native diagram invalid"),
    };
    let imported_residual = match import_diagram_json(residual_json) {
        Ok(diagram) => diagram,
        Err(_) => return Outcome::Refused("serialized native diagram invalid"),
    };
    if imported_source.result != source.result
        || imported_residual.result != residual.result
        || source_json != source.result.to_json().unwrap()
        || residual_json != residual.result.to_json().unwrap()
    {
        return Outcome::Refused("serialized source or residual snapshot mismatch");
    }
    if root.get("external_leaf") != Some(&external_leaf_json(expected_leaf)) {
        return Outcome::Refused("serialized external leaf binding mismatch");
    }
    let (native_source, native_target) = match only_dynamic_pair(certificate) {
        Ok(pair) => pair,
        Err(outcome) => return outcome,
    };
    let expected_mapping = json!([{
        "source": qualified_json(native_source),
        "target": qualified_json(native_target),
    }]);
    if root.get("native_occurrence_map") != Some(&expected_mapping) {
        return Outcome::Refused("serialized native occurrence mismatch");
    }
    receive(source, residual, certificate, request, structural_work)
}

#[test]
fn certified_binding_preserves_dynamic_copy_and_all_body_events_without_evaluation() {
    for value in [
        Rational::ZERO,
        Rational::new(7, 3).unwrap(),
        Rational::new(-5, 2).unwrap(),
    ] {
        let (source, residual) = fixtures(BODY, value);
        let certificate = propose(&source, &residual, value);
        let expected = request(&source, &residual, value);
        assert_eq!(
            receive(&source, &residual, &certificate, &expected, 512),
            Outcome::Certified(Box::new(certificate.clone()))
        );
        assert_eq!(certificate.event_map.len(), 6);
        assert_eq!(certificate.forgotten_static_occurrences.len(), 3);
        assert_eq!(certificate.forgotten_static_history.len(), 2);
        assert_eq!(
            certificate
                .occurrence_map
                .iter()
                .filter(|(_, target)| target.is_some())
                .count(),
            3
        );
        assert!(
            source
                .result
                .nodes
                .iter()
                .any(|node| node.operation.name == "discard")
        );
        assert!(
            residual
                .result
                .nodes
                .iter()
                .any(|node| node.operation.name == "discard")
        );
        // Both contexts deliberately reuse local occ:0; equality of this local
        // coordinate must not identify source and residual semantic objects.
        assert_eq!(
            source.result.occurrences[0].id,
            residual.result.occurrences[0].id
        );
        assert_ne!(source.result.function, residual.result.function);
    }
}

#[test]
fn forgotten_static_root_is_retained_when_the_bound_input_is_discarded() {
    let (source, residual) = fixtures(
        "(frontier (discard (use static)) (copy (use dynamic)))",
        Rational::ONE,
    );
    let certificate = propose(&source, &residual, Rational::ONE);
    assert_eq!(certificate.forgotten_static_occurrences.len(), 1);
    assert_eq!(certificate.forgotten_static_history.len(), 1);
    assert!(matches!(
        receive(
            &source,
            &residual,
            &certificate,
            &request(&source, &residual, Rational::ONE),
            512
        ),
        Outcome::Certified(_)
    ));
}

#[test]
fn zero_event_source_keeps_ordered_through_wires_under_binding() {
    let (source, residual) = fixtures("(frontier (use static) (use dynamic))", Rational::ONE);
    let certificate = propose(&source, &residual, Rational::ONE);
    assert!(certificate.event_map.is_empty());
    assert!(matches!(
        receive(
            &source,
            &residual,
            &certificate,
            &request(&source, &residual, Rational::ONE),
            512
        ),
        Outcome::Certified(_)
    ));
}

#[test]
fn external_open_line_leaf_labels_cannot_repin_the_native_request() {
    let (source, residual) = fixtures("(frontier (use static) (use dynamic))", Rational::ONE);
    let original = propose(&source, &residual, Rational::ONE);
    let expected = request(&source, &residual, Rational::ONE);
    assert_eq!(
        receive(&source, &residual, &original, &expected, 512),
        Outcome::Certified(Box::new(original.clone()))
    );
    let dynamic_indices = original
        .occurrence_map
        .iter()
        .enumerate()
        .filter_map(|(index, (_, target))| target.as_ref().map(|_| index))
        .collect::<Vec<_>>();
    assert_eq!(dynamic_indices.len(), 1);
    let dynamic_index = dynamic_indices[0];

    for (source_name, occurrence_name, target_source, target_occurrence) in [
        ("s-KX-L", "o-KX-L", "open-reuse-s-KX-L", "open-reuse-o-KX-L"),
        ("s-tK-R", "o-tK-R", "open-reuse-s-tK-R", "open-reuse-o-tK-R"),
    ] {
        let mut changed = original.clone();
        changed.occurrence_map[dynamic_index].0.source = SourceId::explicit(source_name);
        changed.occurrence_map[dynamic_index].0.local_id = OccurrenceId::explicit(occurrence_name);
        let target = changed.occurrence_map[dynamic_index].1.as_mut().unwrap();
        target.source = SourceId::explicit(target_source);
        target.local_id = OccurrenceId::explicit(target_occurrence);
        assert_eq!(
            receive(&source, &residual, &changed, &expected, 512),
            Outcome::Refused("qualified source occurrence mismatch")
        );
    }
}

#[test]
fn serialized_open_line_leaf_request_binds_validated_complete_native_diagrams() {
    let (source, residual) = fixtures("(frontier (use static) (use dynamic))", Rational::ONE);
    let certificate = propose(&source, &residual, Rational::ONE);
    let expected = request(&source, &residual, Rational::ONE);
    let leaves = [
        ExpectedExternalLeaf {
            source: "s-KX-L".into(),
            occurrence: "occ-KX-L".into(),
            target_source: "t-KX-L".into(),
            target_occurrence: "tocc-KX-L".into(),
        },
        ExpectedExternalLeaf {
            source: "s-tK-R".into(),
            occurrence: "occ-tK-R".into(),
            target_source: "t-tK-R".into(),
            target_occurrence: "tocc-tK-R".into(),
        },
    ];
    for leaf in &leaves {
        let encoded = serialized_leaf_request(&source, &residual, &certificate, leaf);
        assert!(encoded.len() < 65_536);
        assert_eq!(
            receive_serialized_leaf_request(
                &source,
                &residual,
                &certificate,
                &expected,
                leaf,
                &encoded,
                65_536,
                512,
            ),
            Outcome::Certified(Box::new(certificate.clone()))
        );
    }

    let leaf = &leaves[0];
    let encoded = serialized_leaf_request(&source, &residual, &certificate, leaf);
    let mutate = |change: &dyn Fn(&mut Value)| {
        let mut value: Value = serde_json::from_str(&encoded).unwrap();
        change(&mut value);
        value.to_string()
    };
    let controls = [
        (
            mutate(&|value| value["external_leaf"]["occurrence"] = json!("occ-rebound")),
            Outcome::Refused("serialized external leaf binding mismatch"),
        ),
        (
            mutate(&|value| {
                value["native_occurrence_map"][0]["source"]["source"] = json!("s-KX-L")
            }),
            Outcome::Refused("serialized native occurrence mismatch"),
        ),
        (
            mutate(&|value| value["native_occurrence_map"][0]["target"]["path"] = json!([9])),
            Outcome::Refused("serialized native occurrence mismatch"),
        ),
        (
            mutate(&|value| {
                let (changed_source, _) =
                    fixtures("(frontier (id (use static)) (use dynamic))", Rational::ONE);
                value["source_diagram_json"] = json!(changed_source.result.to_json().unwrap());
            }),
            Outcome::Refused("serialized source or residual snapshot mismatch"),
        ),
        (
            mutate(&|value| value["source_diagram_json"] = json!("{}")),
            Outcome::Refused("serialized native diagram invalid"),
        ),
        (
            mutate(&|value| value["unexpected"] = json!(true)),
            Outcome::Refused("serialized request shape mismatch"),
        ),
        (
            mutate(&|value| value["profile"] = json!("future-profile")),
            Outcome::Refused("serialized request profile mismatch"),
        ),
    ];
    for (changed, expected_outcome) in controls {
        assert_eq!(
            receive_serialized_leaf_request(
                &source,
                &residual,
                &certificate,
                &expected,
                leaf,
                &changed,
                65_536,
                512,
            ),
            expected_outcome
        );
    }
    assert_eq!(
        receive_serialized_leaf_request(
            &source,
            &residual,
            &certificate,
            &expected,
            leaf,
            &encoded,
            encoded.len() - 1,
            512,
        ),
        Outcome::Unknown("serialized request byte budget exhausted")
    );
}

#[test]
fn serialized_leaf_request_requires_each_fresh_native_instance_to_bind_itself() {
    let body = "(frontier (use static) (use dynamic))";
    let leaf = ExpectedExternalLeaf {
        source: "s-KX-L".into(),
        occurrence: "occ-KX-L".into(),
        target_source: "t-KX-L".into(),
        target_occurrence: "tocc-KX-L".into(),
    };
    let (source, residual) = fixtures(body, Rational::ONE);
    let certificate = propose(&source, &residual, Rational::ONE);
    let encoded = serialized_leaf_request(&source, &residual, &certificate, &leaf);

    let (fresh_source, fresh_residual) = fixtures_in("native-binding-fresh", body, Rational::ONE);
    let fresh_certificate = propose(&fresh_source, &fresh_residual, Rational::ONE);
    let fresh_expected = request(&fresh_source, &fresh_residual, Rational::ONE);

    assert_ne!(source.result.function, fresh_source.result.function);
    assert_ne!(residual.result.function, fresh_residual.result.function);
    assert_eq!(source.result.nodes.len(), fresh_source.result.nodes.len());
    assert_eq!(
        source.result.occurrences.len(),
        fresh_source.result.occurrences.len()
    );
    assert!(encoded.len() < 65_536);
    assert_eq!(
        receive_serialized_leaf_request(
            &fresh_source,
            &fresh_residual,
            &fresh_certificate,
            &fresh_expected,
            &leaf,
            &encoded,
            65_536,
            512,
        ),
        Outcome::Refused("serialized source or residual snapshot mismatch")
    );

    let fresh_encoded =
        serialized_leaf_request(&fresh_source, &fresh_residual, &fresh_certificate, &leaf);
    assert!(fresh_encoded.len() < 65_536);
    assert_eq!(
        receive_serialized_leaf_request(
            &fresh_source,
            &fresh_residual,
            &fresh_certificate,
            &fresh_expected,
            &leaf,
            &fresh_encoded,
            65_536,
            512,
        ),
        Outcome::Certified(Box::new(fresh_certificate.clone()))
    );
}

#[test]
fn serialized_leaf_request_replays_across_processes_only_for_matching_identity() {
    const ROLE: &str = "ADVA_SERIALIZED_LEAF_PROCESS_ROLE";
    const REQUEST_PATH: &str = "ADVA_SERIALIZED_LEAF_REQUEST_PATH";
    const TEST_NAME: &str =
        "serialized_leaf_request_replays_across_processes_only_for_matching_identity";
    const PROFILE: &str = "adva.research.native-input-binding-open-line-leaf-request.v0";
    const CHANGED_PROFILE: &str = "adva.research.native-input-binding-open-line-leaf-request.v1";

    let body = "(frontier (use static) (use dynamic))";
    let leaf = ExpectedExternalLeaf {
        source: "s-KX-L".into(),
        occurrence: "occ-KX-L".into(),
        target_source: "t-KX-L".into(),
        target_occurrence: "tocc-KX-L".into(),
    };
    if let Ok(role) = env::var(ROLE) {
        let path = env::var(REQUEST_PATH).unwrap();
        let module = if role == "receive-renamed" {
            "native-binding-process-renamed"
        } else {
            "native-binding-process"
        };
        let (source, residual) = fixtures_in(module, body, Rational::ONE);
        let certificate = propose(&source, &residual, Rational::ONE);
        if role == "emit" {
            let encoded = serialized_leaf_request(&source, &residual, &certificate, &leaf);
            assert!(encoded.len() < 65_536);
            fs::write(path, encoded).unwrap();
            return;
        }

        let expected = request(&source, &residual, Rational::ONE);
        let encoded = fs::read_to_string(path).unwrap();
        let outcome = receive_serialized_leaf_request(
            &source,
            &residual,
            &certificate,
            &expected,
            &leaf,
            &encoded,
            65_536,
            512,
        );
        match role.as_str() {
            "receive-matching" => {
                assert_eq!(outcome, Outcome::Certified(Box::new(certificate.clone())))
            }
            "receive-renamed" => assert_eq!(
                outcome,
                Outcome::Refused("serialized source or residual snapshot mismatch")
            ),
            "receive-tampered-profile" => assert_eq!(
                outcome,
                Outcome::Refused("serialized request profile mismatch")
            ),
            _ => panic!("unexpected process role: {role}"),
        }
        return;
    }

    let directory = env::temp_dir().join(format!(
        "adva-serialized-leaf-process-replay-{}",
        process::id()
    ));
    fs::create_dir(&directory).unwrap();
    let request_path = directory.join("request.json");
    let tampered_path = directory.join("tampered-profile.json");
    let executable = env::current_exe().unwrap();
    let run_child = |role: &str, path: &Path| {
        let mut child = Command::new(&executable)
            .arg("--exact")
            .arg(TEST_NAME)
            .env(ROLE, role)
            .env(REQUEST_PATH, path)
            .stdout(Stdio::piped())
            .stderr(Stdio::piped())
            .spawn()
            .unwrap();
        let deadline = Instant::now() + Duration::from_secs(10);
        while child.try_wait().unwrap().is_none() {
            if Instant::now() >= deadline {
                child.kill().unwrap();
                let output = child.wait_with_output().unwrap();
                panic!(
                    "child {role} timed out\nstdout:\n{}\nstderr:\n{}",
                    String::from_utf8_lossy(&output.stdout),
                    String::from_utf8_lossy(&output.stderr)
                );
            }
            thread::sleep(Duration::from_millis(10));
        }
        let output = child.wait_with_output().unwrap();
        assert!(
            output.status.success(),
            "child {role} failed with {}\nstdout:\n{}\nstderr:\n{}",
            output.status,
            String::from_utf8_lossy(&output.stdout),
            String::from_utf8_lossy(&output.stderr)
        );
    };

    run_child("emit", &request_path);
    let encoded = fs::read_to_string(&request_path).unwrap();
    assert!(encoded.len() < 65_536);
    let tampered = encoded.replacen(PROFILE, CHANGED_PROFILE, 1);
    assert_ne!(encoded, tampered);
    fs::write(&tampered_path, tampered).unwrap();

    run_child("receive-matching", &request_path);
    run_child("receive-renamed", &request_path);
    run_child("receive-tampered-profile", &tampered_path);

    fs::remove_file(request_path).unwrap();
    fs::remove_file(tampered_path).unwrap();
    fs::remove_dir(directory).unwrap();
}

// This is public only inside the ephemeral research integration-test crate.
// It is not a stable library surface or a promoted receiver API.
pub fn receive_pinned_serialized_leaf_request(case: &str, request_path: &Path) {
    const PROFILE: &str = "adva.research.native-input-binding-open-line-leaf-request.v0";
    const CHANGED_PROFILE: &str = "adva.research.native-input-binding-open-line-leaf-request.v1";

    let module = if case == "renamed-module" {
        "native-binding-process-renamed"
    } else {
        "native-binding-process"
    };
    let body = "(frontier (use static) (use dynamic))";
    let leaf = ExpectedExternalLeaf {
        source: "s-KX-L".into(),
        occurrence: "occ-KX-L".into(),
        target_source: "t-KX-L".into(),
        target_occurrence: "tocc-KX-L".into(),
    };
    let (source, residual) = fixtures_in(module, body, Rational::ONE);
    let certificate = propose(&source, &residual, Rational::ONE);
    let expected = request(&source, &residual, Rational::ONE);
    let original = fs::read_to_string(request_path).unwrap();
    let encoded = if case == "changed-profile" {
        let changed = original.replacen(PROFILE, CHANGED_PROFILE, 1);
        assert_ne!(original, changed);
        changed
    } else {
        original
    };
    let outcome = receive_serialized_leaf_request(
        &source,
        &residual,
        &certificate,
        &expected,
        &leaf,
        &encoded,
        65_536,
        512,
    );

    match case {
        "matching" => assert_eq!(outcome, Outcome::Certified(Box::new(certificate))),
        "renamed-module" => assert_eq!(
            outcome,
            Outcome::Refused("serialized source or residual snapshot mismatch")
        ),
        "changed-profile" => assert_eq!(
            outcome,
            Outcome::Refused("serialized request profile mismatch")
        ),
        _ => panic!("unexpected consumer case: {case}"),
    }
}

#[test]
fn missing_or_forged_accounting_is_refused() {
    let value = Rational::new(7, 3).unwrap();
    let (source, residual) = fixtures(BODY, value);
    let original = propose(&source, &residual, value);
    let expected = request(&source, &residual, value);
    let mut mutations = Vec::new();
    let mut changed = original.clone();
    changed.event_map.pop();
    mutations.push(changed);
    let mut changed = original.clone();
    changed.event_map.swap(0, 1);
    mutations.push(changed);
    let mut changed = original.clone();
    changed.forgotten_static_occurrences.pop();
    mutations.push(changed);
    let mut changed = original.clone();
    changed.forgotten_static_history.pop();
    mutations.push(changed);
    let mut changed = original.clone();
    changed.occurrence_map.pop();
    mutations.push(changed);
    let mut changed = original.clone();
    changed.static_value = Rational::ONE;
    mutations.push(changed);
    let mut changed = original.clone();
    changed.occurrence_map[1].1 = None;
    mutations.push(changed);
    let mut changed = original.clone();
    changed.occurrence_map[1].1.as_mut().unwrap().context = source.result.function.clone();
    mutations.push(changed);
    let mut changed = original.clone();
    changed.occurrence_map[4].1.as_mut().unwrap().path = OccurrencePath::root();
    mutations.push(changed);
    for changed in mutations {
        assert!(matches!(
            receive(&source, &residual, &changed, &expected, 512),
            Outcome::Refused(_)
        ));
    }
}

#[test]
fn changed_body_with_the_same_local_ids_cannot_repin_the_callers_source() {
    let value = Rational::ONE;
    let (source, residual) = fixtures(BODY, value);
    let expected = request(&source, &residual, value);
    let changed_body = BODY.replace("(add (copy (use dynamic)))", "(mul (copy (use dynamic)))");
    let (changed_source, changed_residual) = fixtures(&changed_body, value);
    assert_eq!(source.result.function, changed_source.result.function);
    assert_eq!(source.result.occurrences, changed_source.result.occurrences);
    let repinned = propose(&changed_source, &changed_residual, value);
    assert!(matches!(
        receive(
            &changed_source,
            &changed_residual,
            &repinned,
            &expected,
            512
        ),
        Outcome::Refused(_)
    ));
    let changed_request_context = request(&source, &residual, value);
    let mut forged = propose(&source, &residual, value);
    forged.residual_snapshot.function = source.result.function.clone();
    assert!(matches!(
        receive(&source, &residual, &forged, &changed_request_context, 512),
        Outcome::Refused(_)
    ));
}

#[test]
fn ordered_outputs_and_graft_maps_are_checked_again() {
    let value = Rational::ONE;
    let (source, residual) = fixtures(BODY, value);
    let expected = request(&source, &residual, value);
    let mut changed = residual.clone();
    changed.result.outputs.swap(0, 1);
    let repinned = propose(&source, &changed, value);
    assert!(matches!(
        receive(&source, &changed, &repinned, &expected, 512),
        Outcome::Refused(_)
    ));
    let mut changed = residual.clone();
    changed.graft_trace.result.frames[1].holes.swap(0, 1);
    assert!(matches!(
        receive(
            &source,
            &changed,
            &propose(&source, &residual, value),
            &expected,
            512
        ),
        Outcome::Refused(_)
    ));
}

#[test]
fn literal_version_and_repinned_static_data_do_not_change_the_question() {
    let value = Rational::new(7, 3).unwrap();
    let (source, residual) = fixtures(BODY, value);
    let expected = request(&source, &residual, value);
    let mut historical_literal = residual.clone();
    let binding_id = historical_literal.result.nodes[0].id;
    historical_literal.result.nodes[0].operation = OperationRef::constant(value);
    for event in &mut historical_literal.result.history.prefix {
        if let HistoryEvent::Operation { node, operation } = event {
            if *node == binding_id {
                *operation = OperationRef::constant(value);
            }
        }
    }
    assert!(validate_diagram(historical_literal.result.clone()).is_ok());
    let repinned = propose(&source, &historical_literal, value);
    assert!(matches!(
        receive(&source, &historical_literal, &repinned, &expected, 512),
        Outcome::Refused(_)
    ));
    let (_, changed_literal) = fixtures(BODY, Rational::ONE);
    let repinned = propose(&source, &changed_literal, Rational::ONE);
    assert!(matches!(
        receive(&source, &changed_literal, &repinned, &expected, 512),
        Outcome::Refused(_)
    ));
}

#[test]
fn deletion_of_hidden_discard_or_copy_is_not_a_specialization_certificate() {
    let value = Rational::ONE;
    let (source, residual) = fixtures(BODY, value);
    let expected = request(&source, &residual, value);
    for changed_body in [
        BODY.replace(" (discard 1)", ""),
        BODY.replace("(add (copy (use dynamic)))", "(neg (use dynamic))"),
    ] {
        let (_, changed_residual) = fixtures(&changed_body, value);
        let repinned = propose(&source, &changed_residual, value);
        assert!(matches!(
            receive(&source, &changed_residual, &repinned, &expected, 512),
            Outcome::Refused(_)
        ));
    }
}

#[test]
fn a_valid_graph_outside_the_frozen_size_profile_is_unknown() {
    let mut dynamic = "(use dynamic)".to_owned();
    for _ in 0..17 {
        dynamic = format!("(id {dynamic})");
    }
    let body = format!("(frontier (use static) {dynamic})");
    let (source, residual) = fixtures(&body, Rational::ONE);
    assert_eq!(source.result.nodes.len(), 17);
    assert_eq!(residual.result.nodes.len(), 18);
    let certificate = propose(&source, &residual, Rational::ONE);
    assert_eq!(
        receive(
            &source,
            &residual,
            &certificate,
            &request(&source, &residual, Rational::ONE),
            512
        ),
        Outcome::Unknown("outside the fixed finite structural profile")
    );
}

#[test]
fn exhaustion_produces_no_certificate_or_automatic_refuelling() {
    let (source, residual) = fixtures(BODY, Rational::ONE);
    let certificate = propose(&source, &residual, Rational::ONE);
    let expected = request(&source, &residual, Rational::ONE);
    for work in [0, 1, 40] {
        assert!(matches!(
            receive(&source, &residual, &certificate, &expected, work),
            Outcome::Unknown(_)
        ));
    }
}
