//! Bit-pattern diagnostics for both log versions, conversions and input boundaries.
use adva_ir::{ProgramTerm, Rational, SharedProgramDiagram};
use adva_lisp::{
    compile_function, evaluate, evaluate_finite, evaluate_with_differential, link_modules,
    parse_module,
};
use std::collections::BTreeMap;

fn log_diagram(
    scale: u32,
    version: u32,
) -> Result<SharedProgramDiagram, Box<dyn std::error::Error>> {
    let denominator = 1_i64 << scale;
    let source = format!(
        "(module audit (export f) (def f (fn ((x Real)) Real (log (scale 1/{denominator} (use x))))))"
    );
    let mut module = parse_module(&source)?;
    let ProgramTerm::Apply { operation, .. } = &mut module.module.definitions[0].body else {
        return Err("expected outer log application".into());
    };
    operation.version = version;
    let linked = link_modules(vec![module])?;
    Ok(compile_function(&linked, "audit", "f")?.result)
}

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let mut gradients = Vec::new();
    for (exponent, scale) in [
        (1010_u64, 10),
        (1013, 10),
        (1014, 10),
        (1020, 10),
        (1010, 20),
    ] {
        for version in [1, 2] {
            let diagram = log_diagram(scale, version)?;
            let x = f64::from_bits((1023 - exponent) << 52);
            let inputs = BTreeMap::from([("x".to_owned(), x)]);
            let result = evaluate_with_differential(&diagram, &inputs)?;
            let gradient = result.jacobian[0]["x"];
            let expected = f64::from_bits((1023 + exponent) << 52);
            gradients.push(serde_json::json!({
                "log_version": version, "x_exponent": exponent, "scale_exponent": scale,
                "input_bits": format!("{:016x}", x.to_bits()),
                "gradient_bits": format!("{:016x}", gradient.to_bits()),
                "expected_bits": format!("{:016x}", expected.to_bits()),
                "finite_value": result.values[0].is_finite(),
                "finite_gradient": gradient.is_finite(),
                "matches_expected": gradient.to_bits() == expected.to_bits(),
                "certificate": result.certificate
            }));
        }
    }
    let mut rational = Vec::new();
    for (n, d) in [
        (9_007_199_254_740_995, 9_007_199_254_740_994),
        (9_007_199_254_740_992, 9_007_199_254_740_993),
        (9_007_199_254_740_993, 9_007_199_254_740_994),
        (1, 1024),
    ] {
        let value = Rational::new(n, d)?.as_f64();
        rational.push(serde_json::json!({
            "numerator": n, "denominator": d, "bits": format!("{:016x}", value.to_bits()),
            "legacy_bits": format!("{:016x}", (n as f64 / d as f64).to_bits())
        }));
    }
    let mut inputs = Vec::new();
    for version in [1, 2] {
        let diagram = log_diagram(0, version)?;
        for (name, x) in [
            ("finite", 1.0),
            ("nan", f64::NAN),
            ("infinity", f64::INFINITY),
        ] {
            match evaluate(&diagram, &BTreeMap::from([("x".to_owned(), x)])) {
                Ok(result) => inputs.push(serde_json::json!({
                    "case": name, "log_version": version, "status": "Ok",
                    "bits": format!("{:016x}", result.values[0].to_bits()),
                    "finite": result.values[0].is_finite(), "certificate": result.certificate
                })),
                Err(error) => inputs.push(serde_json::json!({
                    "case": name, "log_version": version, "status": "Err",
                    "error": error.to_string()
                })),
            }
        }
    }
    let mut finite_inputs = Vec::new();
    let diagram = log_diagram(0, 2)?;
    for (name, x) in [
        ("finite", 1.0),
        ("nan", f64::NAN),
        ("infinity", f64::INFINITY),
    ] {
        let result = evaluate_finite(&diagram, &BTreeMap::from([("x".to_owned(), x)]));
        finite_inputs.push(serde_json::json!({
            "case": name, "accepted": result.is_ok(), "error": result.err().map(|e| e.to_string())
        }));
    }
    let decoded: f64 = serde_json::from_str("0.9999999962747097")?;
    let expected = 1.0 - 2.0_f64.powi(-28);
    let report = serde_json::json!({
        "schema": "adva.native-numeric-boundary-diagnostic.v2",
        "log_gradients": gradients, "rational_conversion": rational, "input_boundary": inputs,
        "finite_input_boundary": finite_inputs,
        "json_k28": {"decoded_bits": format!("{:016x}", decoded.to_bits()),
            "expected_bits": format!("{:016x}", expected.to_bits()),
            "matches": decoded.to_bits() == expected.to_bits()},
        "scope": "No exact-identity or finite-gradient guarantee from structural certificates"
    });
    println!("{}", serde_json::to_string_pretty(&report)?);
    Ok(())
}
