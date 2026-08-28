use adva_ir::{OperationRef, ProgramTerm, Rational, ValueType};
use adva_lisp::{
    LineageRule, builtin_operation_specs, compile_function, evaluate, evaluate_with_differential,
    link_modules, parse_module, resolve_operation,
};
use std::collections::{BTreeMap, BTreeSet};

fn operation_module(name: &str) -> String {
    let (inputs, outputs, body) = match name {
        "id" => ("((x Real))", "Real", "(id (use x))"),
        "copy" => ("((x Real))", "(outputs Real Real)", "(copy (use x))"),
        "discard" => ("((x Real))", "(outputs)", "(discard (use x))"),
        "swap" => (
            "((x Real) (y Real))",
            "(outputs Real Real)",
            "(swap (use x) (use y))",
        ),
        "add" => ("((x Real) (y Real))", "Real", "(add (use x) (use y))"),
        "mul" => ("((x Real) (y Real))", "Real", "(mul (use x) (use y))"),
        "scale" => ("((x Real) (y Real))", "Real", "(scale (use x) (use y))"),
        "neg" => ("((x Real))", "Real", "(neg (use x))"),
        "sin" => ("((x Real))", "Real", "(sin (use x))"),
        "cos" => ("((x Real))", "Real", "(cos (use x))"),
        "exp" => ("((x Real))", "Real", "(exp (use x))"),
        "log" => ("((x Real))", "Real", "(log (use x))"),
        other => panic!("missing registry test fixture for {other}"),
    };
    format!("(module registry (export f) (def f (fn {inputs} {outputs} {body})))")
}

#[test]
fn every_surface_operation_uses_one_registered_semantic_declaration() {
    let expected = BTreeSet::from([
        "add", "copy", "cos", "discard", "exp", "id", "log", "mul", "neg", "scale", "sin", "swap",
    ]);
    let registered = builtin_operation_specs()
        .iter()
        .filter(|spec| spec.surface_form)
        .map(|spec| spec.name)
        .collect::<BTreeSet<_>>();
    assert_eq!(registered, expected);

    for name in registered {
        let linked = link_modules(vec![parse_module(&operation_module(name)).unwrap()]).unwrap();
        let artifact = compile_function(&linked, "registry", "f").unwrap();
        let inputs = artifact
            .result
            .signature
            .inputs
            .iter()
            .map(|port| {
                let value = if port.name == "x" { 2.0 } else { 3.0 };
                (port.name.clone(), value)
            })
            .collect::<BTreeMap<_, _>>();
        evaluate(&artifact.result, &inputs).unwrap();
        evaluate_with_differential(&artifact.result, &inputs).unwrap();
    }
}

#[test]
fn constants_are_registered_but_not_surface_operation_forms() {
    let linked = link_modules(vec![
        parse_module("(module constants (export two) (def two (fn () Real 2)))").unwrap(),
    ])
    .unwrap();
    let artifact = compile_function(&linked, "constants", "two").unwrap();
    assert_eq!(
        evaluate(&artifact.result, &BTreeMap::new()).unwrap().values,
        vec![2.0]
    );

    let constant = OperationRef::constant(Rational::integer(2));
    let spec = resolve_operation(&constant).unwrap();
    assert_eq!(spec.name, "constant");
    assert!(!spec.surface_form);
    assert_eq!(spec.parameters, &["value"]);
}

#[test]
fn registry_rejects_unregistered_parameters_during_lowering() {
    let mut module =
        parse_module("(module malformed (export f) (def f (fn ((x Real)) Real (neg (use x)))))")
            .unwrap();
    let ProgramTerm::Apply { operation, .. } = &mut module.module.definitions[0].body else {
        panic!("fixture must parse as an operation application");
    };
    operation
        .parameters
        .insert("accidental".to_owned(), Rational::ONE);

    let linked = link_modules(vec![module]).unwrap();
    let error = compile_function(&linked, "malformed", "f").unwrap_err();
    assert!(error.to_string().contains("expects parameters"));
}

#[test]
fn evaluator_rechecks_registered_cell_boundaries() {
    let linked = link_modules(vec![
        parse_module("(module malformed (export f) (def f (fn ((x Real)) Real (neg (use x)))))")
            .unwrap(),
    ])
    .unwrap();
    let mut diagram = compile_function(&linked, "malformed", "f").unwrap().result;
    diagram.nodes[0].output_types[0] = ValueType::Bool;

    let error = evaluate(&diagram, &BTreeMap::from([("x".to_owned(), 2.0)])).unwrap_err();
    assert!(error.to_string().contains("declares outputs"));
}

#[test]
fn structural_lineage_rules_are_explicit_registry_data() {
    let rules = builtin_operation_specs()
        .iter()
        .map(|spec| (spec.name, spec.lineage_rule))
        .collect::<BTreeMap<_, _>>();
    assert_eq!(rules["copy"], LineageRule::Copy);
    assert_eq!(rules["discard"], LineageRule::Discard);
    assert_eq!(rules["swap"], LineageRule::Swap);
    assert_eq!(rules["add"], LineageRule::MergeInputs);
}
