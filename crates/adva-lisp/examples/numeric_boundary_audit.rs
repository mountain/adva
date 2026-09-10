//! Diagnostic driver: retain actual Rust bit patterns without changing semantics.
use adva_ir::Rational;
use adva_lisp::{compile_function, evaluate, evaluate_with_differential, link_modules, parse_module};
use std::collections::BTreeMap;

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let mut gradients = Vec::new();
    for (exponent, scale) in [(1010, 10), (1013, 10), (1014, 10), (1020, 10), (1010, 20)] {
        let denominator = 1_i64 << scale;
        let source = format!(
            "(module audit (export f) (def f (fn ((x Real)) Real (log (scale 1/{denominator} (use x))))))"
        );
        let linked = link_modules(vec![parse_module(&source)?])?;
        let artifact = compile_function(&linked, "audit", "f")?;
        let x = f64::from_bits(((1023 - exponent) as u64) << 52);
        let result = evaluate_with_differential(&artifact.result, &BTreeMap::from([("x".to_owned(), x)]))?;
        let gradient = result.jacobian[0]["x"];
        let expected = f64::from_bits(((1023 + exponent) as u64) << 52);
        gradients.push(serde_json::json!({
            "x_exponent": exponent, "scale_exponent": scale, "source": source,
            "input_bits": format!("{:016x}", x.to_bits()),
            "gradient_bits": format!("{:016x}", gradient.to_bits()),
            "expected_bits": format!("{:016x}", expected.to_bits()),
            "finite_value": result.values[0].is_finite(),
            "finite_gradient": gradient.is_finite(),
            "matches_expected": gradient.to_bits() == expected.to_bits(),
            "certificate": result.certificate
        }));
    }
    let mut rational = Vec::new();
    for (n, d) in [(9_007_199_254_740_992, 9_007_199_254_740_993),
                   (9_007_199_254_740_993, 9_007_199_254_740_994), (1, 1024)] {
        let value = Rational::new(n, d)?.as_f64();
        rational.push(serde_json::json!({"numerator": n, "denominator": d,
                                        "bits": format!("{:016x}", value.to_bits())}));
    }
    let linked = link_modules(vec![parse_module(
        "(module audit (export f) (def f (fn ((x Real)) Real (log (use x)))))"
    )?])?;
    let artifact = compile_function(&linked, "audit", "f")?;
    let mut inputs = Vec::new();
    for (name, x) in [("finite", 1.0), ("nan", f64::NAN), ("infinity", f64::INFINITY)] {
        match evaluate(&artifact.result, &BTreeMap::from([("x".to_owned(), x)])) {
            Ok(result) => inputs.push(serde_json::json!({"case": name, "status": "Ok",
                "bits": format!("{:016x}", result.values[0].to_bits()),
                "finite": result.values[0].is_finite(), "certificate": result.certificate})),
            Err(error) => inputs.push(serde_json::json!({"case": name, "status": "Err", "error": error.to_string()})),
        }
    }
    println!("{}", serde_json::to_string_pretty(&serde_json::json!({
        "schema": "adva.native-numeric-boundary-diagnostic.v0",
        "log_gradients": gradients, "rational_conversion": rational, "input_boundary": inputs,
        "scope": "Diagnostic only; no exact-identity or finite-gradient admission from structural certificates"
    }))?);
    Ok(())
}
