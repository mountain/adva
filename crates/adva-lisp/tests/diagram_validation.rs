use adva_ir::{
    DirectedRewrite, HistoryEvent, NormalizationStep, SharedProgramDiagram, SourceId, WireProducer,
};
use adva_lisp::{
    compile_function, evaluate, import_diagram_json, link_modules, parse_module, validate_diagram,
};
use std::collections::BTreeMap;

fn compile(source: &str, module: &str, function: &str) -> SharedProgramDiagram {
    let linked = link_modules(vec![parse_module(source).unwrap()]).unwrap();
    compile_function(&linked, module, function).unwrap().result
}

fn pair_diagram() -> SharedProgramDiagram {
    compile(
        "(module pair
           (export values)
           (def values
             (fn ((x Real) (y Real)) (outputs Real Real)
               (frontier (use x) (use y)))))",
        "pair",
        "values",
    )
}

fn shared_diagram() -> SharedProgramDiagram {
    compile(
        "(module sharing
           (export double)
           (def double
             (fn ((x Real)) Real
               (add (copy (use x))))))",
        "sharing",
        "double",
    )
}

#[test]
fn compiled_and_round_tripped_diagrams_receive_the_same_checked_certificate() {
    let diagram = shared_diagram();
    let direct = validate_diagram(diagram.clone()).unwrap();
    let imported = import_diagram_json(&diagram.to_json().unwrap()).unwrap();

    assert!(direct.certificate.certified());
    assert_eq!(direct.certificate, imported.certificate);
    assert_eq!(direct.result, imported.result);
    assert_eq!(
        imported.certificate.source_partition_snapshot,
        diagram.source_partition()
    );
}

#[test]
fn semantic_import_rejects_implicit_aliasing_even_when_json_decodes() {
    let mut diagram = pair_diagram();
    diagram.outputs[1] = diagram.outputs[0].clone();
    let json = diagram.to_json().unwrap();

    SharedProgramDiagram::from_json(&json).unwrap();
    let error = import_diagram_json(&json).unwrap_err();
    assert!(error.to_string().contains("consumed exactly once"));
}

#[test]
fn evaluator_cannot_bypass_diagram_integrity_check() {
    let mut diagram = pair_diagram();
    diagram.outputs[1] = diagram.outputs[0].clone();

    let error = evaluate(
        &diagram,
        &BTreeMap::from([("x".to_owned(), 1.0), ("y".to_owned(), 1.0)]),
    )
    .unwrap_err();
    assert!(error.to_string().contains("consumed exactly once"));
}

#[test]
fn copy_history_cannot_change_source_or_occurrence_path() {
    let mut source_tampered = shared_diagram();
    let child = source_tampered
        .history
        .prefix
        .iter()
        .find_map(|event| match event {
            HistoryEvent::Copy { children, .. } => Some(children[0].clone()),
            _ => None,
        })
        .unwrap();
    source_tampered
        .occurrences
        .iter_mut()
        .find(|occurrence| occurrence.id == child)
        .unwrap()
        .source = SourceId::explicit("source:forged");
    let error = validate_diagram(source_tampered).unwrap_err();
    assert!(error.to_string().contains("does not preserve source"));

    let mut path_tampered = shared_diagram();
    let child = path_tampered
        .history
        .prefix
        .iter()
        .find_map(|event| match event {
            HistoryEvent::Copy { children, .. } => Some(children[0].clone()),
            _ => None,
        })
        .unwrap();
    path_tampered.history.occurrence_paths.remove(&child);
    let error = validate_diagram(path_tampered).unwrap_err();
    assert!(error.to_string().contains("occurrence_paths"));
}

#[test]
fn wires_must_reference_preceding_canonical_producers() {
    let mut diagram = shared_diagram();
    let node = diagram.nodes[0].id;
    diagram.nodes[0].inputs[0].producer = WireProducer::Node { node };
    diagram.nodes[0].inputs[0].output_index = 0;

    let error = validate_diagram(diagram).unwrap_err();
    assert!(error.to_string().contains("non-topological"));
}

#[test]
fn unchecked_rewrite_traces_fail_closed() {
    let mut diagram = shared_diagram();
    diagram.history.rewrite_trace.push(NormalizationStep {
        rewrite: DirectedRewrite {
            name: "unchecked".to_owned(),
            source_boundary: diagram.signature.clone(),
            target_boundary: diagram.signature.clone(),
        },
        before_node_count: 2,
        after_node_count: 1,
    });

    let error = validate_diagram(diagram).unwrap_err();
    assert!(error.to_string().contains("rewrite_trace"));
}
