use adva_lisp::{compile_function, evaluate, link_modules, parse_module};
use std::collections::BTreeMap;

#[test]
fn frontier_preserves_order_without_creating_source_sharing() {
    let module = parse_module(
        "(module boundaries
           (export reverse)
           (def reverse
             (fn ((x Real) (y Real)) (outputs Real Real)
               (frontier (use y) (use x)))))",
    )
    .unwrap();
    let linked = link_modules(vec![module]).unwrap();
    let diagram = compile_function(&linked, "boundaries", "reverse")
        .unwrap()
        .result;
    let result = evaluate(
        &diagram,
        &BTreeMap::from([("x".to_owned(), 2.0), ("y".to_owned(), 3.0)]),
    )
    .unwrap();

    assert_eq!(result.values, vec![3.0, 2.0]);
    assert_eq!(diagram.source_partition().len(), 2);
    assert!(diagram.nodes.is_empty());
}

#[test]
fn frontier_is_the_only_pre_release_boundary_spelling() {
    let module = parse_module(
        "(module boundaries
           (export pair)
           (def pair
             (fn ((x Real) (y Real)) (outputs Real Real)
               (frontier (use x) (use y)))))",
    )
    .unwrap();
    let json = module.to_json().unwrap();
    assert!(json.contains("\"kind\": \"frontier\""));
    assert!(!json.contains("tensor"));

    let error = parse_module(
        "(module legacy
           (export pair)
           (def pair
             (fn ((x Real) (y Real)) (outputs Real Real)
               (tensor (use x) (use y)))))",
    )
    .unwrap_err();
    assert!(error.to_string().contains("unknown operation \"tensor\""));
}

#[test]
fn frontier_does_not_authorize_implicit_aliasing() {
    let module = parse_module(
        "(module bad
           (export duplicate)
           (def duplicate
             (fn ((x Real)) (outputs Real Real)
               (frontier (use x) (use x)))))",
    )
    .unwrap();
    let linked = link_modules(vec![module]).unwrap();
    let error = compile_function(&linked, "bad", "duplicate").unwrap_err();
    assert!(error.to_string().contains("use explicit copy"));
}
