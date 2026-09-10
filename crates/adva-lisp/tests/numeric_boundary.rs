//! Versioned numerical regressions; exact powers of two are independent oracles.
use adva_ir::{ProgramTerm, SharedProgramDiagram};
use adva_lisp::{
    compile_function, evaluate_with_differential, import_diagram_json, link_modules, parse_module,
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
    for (exponent, scale) in [(1010_u64, 10), (1013, 10), (1014, 10), (1020, 10), (1010, 20)] {
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
