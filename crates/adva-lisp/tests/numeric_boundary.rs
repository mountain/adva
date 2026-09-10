//! Versioned numerical regressions; exact powers of two are independent oracles.
use adva_ir::{Observation, ProgramTerm, Rational, SharedProgramDiagram};
use adva_lisp::{
    compile_function, evaluate, evaluate_finite, evaluate_with_differential,
    evaluate_with_finite_differential, import_diagram_json, link_modules, parse_module,
};
use std::collections::BTreeMap;

fn diagram(exponent: u32, legacy: bool) -> SharedProgramDiagram {
    let denominator = 1_i64 << exponent;
    let source = format!(
        "(module audit (export f) (def f (fn ((x Real)) Real (log (scale 1/{denominator} (use x))))))"
    );
    let mut module = parse_module(&source).unwrap();
    if let ProgramTerm::Apply { operation, .. } = &mut module.module.definitions[0].body {
        assert_eq!(operation.name, "log");
        assert_eq!(operation.version, 2);
        if legacy {
            // Explicit legacy term selection precedes compilation. Do not edit
            // a compiled graph independently of its recorded operation history.
            operation.version = 1;
        }
    } else {
        panic!("expected a log application");
    }
    let linked = link_modules(vec![module]).unwrap();
    compile_function(&linked, "audit", "f").unwrap().result
}

#[test]
fn log_v2_handles_subnormal_compositions_and_an_independent_scale() {
    for (exponent, scale) in [
        (1010_u64, 10),
        (1013, 10),
        (1014, 10),
        (1020, 10),
        (1010, 20),
    ] {
        let graph = diagram(scale, false);
        let x = f64::from_bits((1023 - exponent) << 52);
        let expected = f64::from_bits((1023 + exponent) << 52);
        let result =
            evaluate_with_differential(&graph, &BTreeMap::from([("x".to_owned(), x)])).unwrap();
        assert_eq!(result.jacobian[0]["x"].to_bits(), expected.to_bits());
        assert!(result.values[0].is_finite());
        assert!(
            result
                .certificate
                .operation_rules
                .contains(&"adva.builtin:log@2".to_owned())
        );
    }
}

#[test]
fn stored_log_versions_replay_without_reinterpretation() {
    let inputs = BTreeMap::from([("x".to_owned(), f64::from_bits(3_u64 << 52))]);
    for legacy in [true, false] {
        let graph = diagram(10, legacy);
        let encoded = graph.to_json().unwrap();
        let restored = import_diagram_json(&encoded).unwrap().result;
        assert_eq!(graph, restored);
        let before = evaluate_with_differential(&graph, &inputs).unwrap();
        let after = evaluate_with_differential(&restored, &inputs).unwrap();
        assert_eq!(
            before.jacobian[0]["x"].to_bits(),
            after.jacobian[0]["x"].to_bits()
        );
        assert_eq!(before.certificate, after.certificate);
        assert_eq!(after.jacobian[0]["x"].is_infinite(), legacy);
        let version = if legacy { 1 } else { 2 };
        assert!(
            after
                .certificate
                .operation_rules
                .contains(&format!("adva.builtin:log@{version}"))
        );
    }
}

#[test]
fn ordinary_log_gradient_agrees_between_versions() {
    for legacy in [true, false] {
        let graph = diagram(0, legacy);
        let result =
            evaluate_with_differential(&graph, &BTreeMap::from([("x".to_owned(), 2.0)])).unwrap();
        assert_eq!(result.jacobian[0]["x"], 0.5);
    }
}

fn compile_body(body: &str, signature: &str) -> SharedProgramDiagram {
    let source = format!("(module audit (export f) (def f (fn {signature} Real {body})))");
    let linked = link_modules(vec![parse_module(&source).unwrap()]).unwrap();
    compile_function(&linked, "audit", "f").unwrap().result
}

#[test]
fn literals_select_constant_v2_and_stored_terms_keep_legacy_rounding() {
    let mut parsed = parse_module(
        "(module audit (export f) (def f (fn () Real 9007199254740995/9007199254740994)))",
    )
    .unwrap();
    for legacy in [false, true] {
        if legacy {
            parsed.module.definitions[0].body = ProgramTerm::Constant {
                value: Rational::new(9_007_199_254_740_995, 9_007_199_254_740_994).unwrap(),
            };
        }
        let linked = link_modules(vec![parsed.clone()]).unwrap();
        let graph = compile_function(&linked, "audit", "f").unwrap().result;
        let restored = import_diagram_json(&graph.to_json().unwrap())
            .unwrap()
            .result;
        let expected_version = if legacy { 1 } else { 2 };
        assert_eq!(restored.nodes[0].operation.version, expected_version);
        assert_eq!(
            evaluate(&restored, &BTreeMap::new()).unwrap().values[0].to_bits(),
            1.0_f64.to_bits() + u64::from(legacy)
        );
        assert!(
            evaluate_with_differential(&restored, &BTreeMap::new())
                .unwrap()
                .certificate
                .operation_rules
                .contains(&format!("adva.builtin:constant@{expected_version}"))
        );
    }
}

#[test]
fn finite_boundary_refuses_special_inputs_values_and_derivatives() {
    for body in ["(use x)", "(log (use x))"] {
        let graph = compile_body(body, "((x Real))");
        for value in [f64::NAN, f64::INFINITY, f64::NEG_INFINITY] {
            let input = BTreeMap::from([("x".to_owned(), value)]);
            assert!(evaluate_finite(&graph, &input).is_err());
            assert!(evaluate_with_finite_differential(&graph, &input).is_err());
        }
    }
    let overflow = compile_body("(exp (use x))", "((x Real))");
    let inputs = BTreeMap::from([("x".to_owned(), 1000.0)]);
    assert!(evaluate_finite(&overflow, &inputs).is_err());
    assert!(evaluate_with_finite_differential(&overflow, &inputs).is_err());
    let log = compile_body("(log (use x))", "((x Real))");
    let inputs = BTreeMap::from([("x".to_owned(), f64::from_bits(1))]);
    // Finite values remain usable when only the unrequested derivative overflows.
    assert!(evaluate_finite(&log, &inputs).unwrap().values[0].is_finite());
    assert!(evaluate_with_finite_differential(&log, &inputs).is_err());
    // Historical rule replay remains available through the explicit raw API.
    assert!(evaluate_with_differential(&log, &inputs).unwrap().jacobian[0]["x"].is_infinite());
}

#[test]
fn nonfinite_results_cannot_turn_into_json_null() {
    let identity = compile_body("(use x)", "((x Real))");
    for value in [f64::NAN, f64::INFINITY, f64::NEG_INFINITY] {
        let inputs = BTreeMap::from([("x".to_owned(), value)]);
        let raw = evaluate(&identity, &inputs).unwrap();
        assert!(serde_json::to_string(&raw).is_err());
        assert!(
            serde_json::to_value(Observation::Value {
                values: vec![value]
            })
            .is_err()
        );
        assert!(
            serde_json::to_value(evaluate_with_differential(&identity, &inputs).unwrap()).is_err()
        );
    }
    let log = compile_body("(log (use x))", "((x Real))");
    let inputs = BTreeMap::from([("x".to_owned(), f64::from_bits(1))]);
    assert!(serde_json::to_value(evaluate_with_differential(&log, &inputs).unwrap()).is_err());
    let finite = evaluate_finite(&log, &inputs).unwrap();
    let json = serde_json::to_string(&finite).unwrap();
    assert_eq!(
        serde_json::from_str::<adva_ir::EvaluationResult>(&json).unwrap(),
        finite
    );
}
