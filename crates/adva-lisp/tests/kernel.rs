use adva_ir::{HistoryEvent, Observation, SharedProgramDiagram};
use adva_lisp::{
    compile_function, evaluate, evaluate_with_differential, link_modules, observe_history,
    observe_source_partition, parse_module,
};
use std::collections::BTreeMap;

const ARITHMETIC: &str = r#"
(module arithmetic
  (export shared-double scale-double square)
  (def shared-double
    (fn ((x Real)) Real
      (add (copy (use x)))))
  (def scale-double
    (fn ((x Real)) Real
      (scale 2 (use x))))
  (def square
    (fn ((x Real)) Real
      (mul (copy (use x))))))
"#;

const CLIENT: &str = r#"
(module client
  (import arithmetic shared-double)
  (export quadruple)
  (def quadruple
    (fn ((x Real)) Real
      (call arithmetic/shared-double
        (call arithmetic/shared-double (use x))))))
"#;

fn workspace() -> adva_lisp::LinkedModules {
    link_modules(vec![
        parse_module(ARITHMETIC).unwrap(),
        parse_module(CLIENT).unwrap(),
    ])
    .unwrap()
}

#[test]
fn k1_copy_has_distinct_occurrences_with_one_explicit_source() {
    let artifact = compile_function(&workspace(), "arithmetic", "shared-double").unwrap();
    assert!(artifact.certificate.certified());
    let partition = artifact.result.source_partition();
    assert_eq!(partition.len(), 1);

    let copy = artifact
        .result
        .history
        .prefix
        .iter()
        .find_map(|event| match event {
            HistoryEvent::Copy { children, .. } => Some(children),
            _ => None,
        })
        .unwrap();
    assert_eq!(copy.len(), 2);
    assert_ne!(copy[0], copy[1]);
    let occurrences = &artifact.result.occurrences;
    let left = occurrences.iter().find(|item| item.id == copy[0]).unwrap();
    let right = occurrences.iter().find(|item| item.id == copy[1]).unwrap();
    assert_eq!(left.source, right.source);
    assert_ne!(left.path, right.path);
}

#[test]
fn independent_equal_inputs_never_merge_sources() {
    let module = parse_module(
        "(module independent (export sum) (def sum (fn ((x Real) (y Real)) Real (add (use x) (use y)))))",
    )
    .unwrap();
    let linked = link_modules(vec![module]).unwrap();
    let artifact = compile_function(&linked, "independent", "sum").unwrap();
    let result = evaluate(
        &artifact.result,
        &BTreeMap::from([("x".to_owned(), 7.0), ("y".to_owned(), 7.0)]),
    )
    .unwrap();
    assert_eq!(result.values, vec![14.0]);
    assert_eq!(artifact.result.source_partition().len(), 2);
}

#[test]
fn k2_value_observation_does_not_collapse_source_or_history_observation() {
    let linked = workspace();
    let shared = compile_function(&linked, "arithmetic", "shared-double")
        .unwrap()
        .result;
    let scale = compile_function(&linked, "arithmetic", "scale-double")
        .unwrap()
        .result;
    let inputs = BTreeMap::from([("x".to_owned(), 5.0)]);
    assert_eq!(evaluate(&shared, &inputs).unwrap().values, vec![10.0]);
    assert_eq!(evaluate(&scale, &inputs).unwrap().values, vec![10.0]);
    assert_ne!(shared, scale);
    assert_ne!(
        observe_source_partition(&shared),
        observe_source_partition(&scale)
    );
    assert_ne!(observe_history(&shared), observe_history(&scale));
}

#[test]
fn module_calls_are_typed_and_remain_in_history() {
    let artifact = compile_function(&workspace(), "client", "quadruple").unwrap();
    let result = evaluate(&artifact.result, &BTreeMap::from([("x".to_owned(), 3.0)])).unwrap();
    assert_eq!(result.values, vec![12.0]);
    let call_count = artifact
        .result
        .history
        .prefix
        .iter()
        .filter(|event| matches!(event, HistoryEvent::Call { .. }))
        .count();
    assert_eq!(call_count, 2);
}

#[test]
fn calculus_uses_the_same_checked_operation_graph() {
    let square = compile_function(&workspace(), "arithmetic", "square")
        .unwrap()
        .result;
    let result =
        evaluate_with_differential(&square, &BTreeMap::from([("x".to_owned(), 3.0)])).unwrap();
    assert_eq!(result.values, vec![9.0]);
    assert_eq!(result.jacobian[0]["x"], 6.0);
    assert!(
        result
            .certificate
            .operation_rules
            .contains(&"copy".to_owned())
    );
    assert!(
        result
            .certificate
            .operation_rules
            .contains(&"mul".to_owned())
    );
}

#[test]
fn serialization_round_trip_preserves_paths_partition_and_boundary() {
    let diagram = compile_function(&workspace(), "arithmetic", "shared-double")
        .unwrap()
        .result;
    let encoded = diagram.to_json().unwrap();
    let decoded = SharedProgramDiagram::from_json(&encoded).unwrap();
    assert_eq!(decoded.signature, diagram.signature);
    assert_eq!(
        decoded.history.occurrence_paths,
        diagram.history.occurrence_paths
    );
    assert_eq!(decoded.source_partition(), diagram.source_partition());
    assert_eq!(decoded, diagram);
}

#[test]
fn serialization_rejects_an_unknown_diagram_version() {
    let diagram = compile_function(&workspace(), "arithmetic", "shared-double")
        .unwrap()
        .result;
    let mut document = serde_json::to_value(&diagram).unwrap();
    document["version"] = serde_json::json!(2);
    let error = SharedProgramDiagram::from_json(&serde_json::to_string(&document).unwrap())
        .unwrap_err();
    assert!(error.to_string().contains("unsupported IR schema"));
}

#[test]
fn host_allocation_addresses_do_not_change_semantics() {
    let first_workspace = workspace();
    let second_workspace = workspace();
    let first = Box::new(
        compile_function(&first_workspace, "arithmetic", "shared-double")
            .unwrap()
            .result,
    );
    let second = Box::new(
        compile_function(&second_workspace, "arithmetic", "shared-double")
            .unwrap()
            .result,
    );
    assert_ne!(
        std::ptr::from_ref(first.as_ref()),
        std::ptr::from_ref(second.as_ref())
    );
    assert_eq!(first.to_json().unwrap(), second.to_json().unwrap());
}

#[test]
fn implicit_aliasing_is_rejected() {
    let module =
        parse_module("(module bad (export f) (def f (fn ((x Real)) Real (add (use x) (use x)))))")
            .unwrap();
    let linked = link_modules(vec![module]).unwrap();
    let error = compile_function(&linked, "bad", "f").unwrap_err();
    assert!(error.to_string().contains("explicit copy"));
}

#[test]
fn observations_are_typed_variants_not_authority_to_rewrite() {
    let diagram = compile_function(&workspace(), "arithmetic", "shared-double")
        .unwrap()
        .result;
    assert!(matches!(
        observe_source_partition(&diagram),
        Observation::SourcePartition { .. }
    ));
    assert!(matches!(
        observe_history(&diagram),
        Observation::History { .. }
    ));
}
