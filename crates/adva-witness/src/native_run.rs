//! Bounded research command envelope over the existing PSC0 Rust compiler.
//!
//! This module introduces no stable operation and makes no exact-arithmetic
//! claim: `Real` is the existing IEEE-754 `f64` scalar realization.

use adva_ir::{CompilationArtifact, EvaluationResult, ProgramTerm, ValueType};
use adva_lisp::{compile_function, evaluate, link_modules, parse_module};
use serde::{Deserialize, Serialize};
use std::collections::BTreeMap;
use std::time::Instant;

pub const NATIVE_RUN_PROGRAM_SCHEMA_V0: &str = "adva.run.program.research";
pub const NATIVE_RUN_REPORT_SCHEMA_V0: &str = "adva.run.report.research";
pub const NATIVE_RUN_MAX_ENVELOPE_BYTES: usize = 16_384;
pub const NATIVE_RUN_MAX_SOURCE_BYTES: usize = 4_096;
pub const NATIVE_RUN_MAX_TERMS: usize = 16;
pub const NATIVE_RUN_MAX_COPIES: usize = 4;
pub const NATIVE_RUN_MAX_DEPTH: usize = 32;
pub const NATIVE_RUN_MAX_INPUTS: usize = 8;

#[derive(Clone, Debug, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct NativeRunProgramV0 {
    pub schema: String,
    pub version: u32,
    pub source: String,
    pub module: String,
    pub entry: String,
    pub inputs: BTreeMap<String, f64>,
    pub fuel: usize,
}

#[derive(Clone, Debug, Default, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct NativeRunActualV0 {
    pub envelope_bytes: usize,
    pub source_bytes: usize,
    pub lexical_max_depth: usize,
    pub ast_terms: usize,
    pub copy_operations: usize,
    pub reserved_fuel: usize,
    pub remaining_fuel: Option<usize>,
    pub compiled_nodes: usize,
    pub occurrences: usize,
    pub history_events: usize,
    pub evaluated_nodes: usize,
    pub peak_memory_bytes: Option<usize>,
}

#[derive(Clone, Debug, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct NativeRunReportV0 {
    pub schema: String,
    pub version: u32,
    /// `Completed` is execution of this envelope, not closure of a theorem.
    pub state: String,
    pub error: Option<String>,
    pub error_phase: Option<String>,
    pub arithmetic: String,
    pub fuel_unit: String,
    /// Exact bounded envelope bytes as UTF-8, for replay rather than identity.
    pub program_json: Option<String>,
    pub program: Option<NativeRunProgramV0>,
    pub compilation: Option<CompilationArtifact>,
    pub evaluation: Option<EvaluationResult>,
    pub actual: NativeRunActualV0,
    pub phase_seconds: BTreeMap<String, f64>,
}

impl NativeRunReportV0 {
    fn new(bytes: usize) -> Self {
        Self {
            schema: NATIVE_RUN_REPORT_SCHEMA_V0.to_owned(),
            version: 0,
            state: "Rejected".to_owned(),
            error: None,
            error_phase: None,
            arithmetic:
                "PSC0 builtin scalar realization: IEEE-754 f64; not exact rational arithmetic"
                    .to_owned(),
            fuel_unit: "AST terms admitted before lowering; distinct from time and evaluated nodes"
                .to_owned(),
            program_json: None,
            program: None,
            compilation: None,
            evaluation: None,
            actual: NativeRunActualV0 {
                envelope_bytes: bytes,
                ..NativeRunActualV0::default()
            },
            phase_seconds: BTreeMap::new(),
        }
    }

    fn reject(&mut self, phase: &str, error: impl ToString) {
        self.error_phase = Some(phase.to_owned());
        self.error = Some(error.to_string());
    }
}

/// Execute one finite, single-definition envelope using existing Rust APIs.
///
/// The envelope is not a native neutral-carrier persistence document. All
/// refusals retain a report; an oversized envelope is not copied into it.
/// Output serialization and file I/O belong to the command layer.
/// Supplied inputs and final outputs must be finite. This does not establish
/// that every intermediate scalar or hidden differential is finite, nor does
/// the existing evaluation certificate become an exact-arithmetic proof.
pub fn run_native_program_v0(source_json: &str) -> NativeRunReportV0 {
    let started = Instant::now();
    let mut report = NativeRunReportV0::new(source_json.len());
    if source_json.len() > NATIVE_RUN_MAX_ENVELOPE_BYTES {
        report.reject("envelope_preflight", "envelope exceeds 16384 bytes");
    } else {
        report.program_json = Some(source_json.to_owned());
        let parsed = timed(&mut report.phase_seconds, "envelope_parse", || {
            serde_json::from_str::<NativeRunProgramV0>(source_json)
        });
        match parsed {
            Err(error) => report.reject("envelope_parse", error),
            Ok(program) => {
                report.program = Some(program.clone());
                if let Err((phase, error)) = execute(&program, &mut report) {
                    report.reject(phase, error);
                } else {
                    report.state = "Completed".to_owned();
                }
            }
        }
    }
    report.phase_seconds.insert(
        "total_before_serialization".to_owned(),
        started.elapsed().as_secs_f64(),
    );
    report
}

fn timed<T>(times: &mut BTreeMap<String, f64>, name: &str, action: impl FnOnce() -> T) -> T {
    let started = Instant::now();
    let result = action();
    times.insert(name.to_owned(), started.elapsed().as_secs_f64());
    result
}

type RunFailure = (&'static str, String);

fn execute(program: &NativeRunProgramV0, report: &mut NativeRunReportV0) -> Result<(), RunFailure> {
    timed(&mut report.phase_seconds, "source_preflight", || {
        preflight_source(program, &mut report.actual)
    })
    .map_err(|error| ("source_preflight", error))?;
    let parsed = timed(&mut report.phase_seconds, "lisp_parse", || {
        parse_module(&program.source)
    })
    .map_err(|error| ("lisp_parse", error.to_string()))?;
    timed(&mut report.phase_seconds, "term_preflight", || {
        let module = &parsed.module;
        if module.name.0 != program.module {
            return Err("module name does not match the envelope".to_owned());
        }
        if !module.imports.is_empty() || module.definitions.len() != 1 {
            return Err("profile requires one definition and no imports".to_owned());
        }
        let definition = &module.definitions[0];
        if definition.name.0 != program.entry
            || !module.exports.iter().any(|name| name.0 == program.entry)
        {
            return Err("entry must be the sole definition and explicitly exported".to_owned());
        }
        if definition.signature.inputs.len() > NATIVE_RUN_MAX_INPUTS
            || definition
                .signature
                .inputs
                .iter()
                .any(|port| port.value_type != ValueType::Real)
            || definition
                .signature
                .outputs
                .iter()
                .any(|value_type| *value_type != ValueType::Real)
        {
            return Err(
                "profile permits at most eight Real inputs and only Real output ports".to_owned(),
            );
        }
        count_terms(&definition.body, &mut report.actual)?;
        if report.actual.ast_terms > program.fuel {
            return Err("insufficient AST admission fuel; compilation was not started".to_owned());
        }
        report.actual.reserved_fuel = report.actual.ast_terms;
        report.actual.remaining_fuel = Some(program.fuel - report.actual.ast_terms);
        Ok(())
    })
    .map_err(|error| ("term_preflight", error))?;
    let linked = timed(&mut report.phase_seconds, "link", || {
        link_modules(vec![parsed])
    })
    .map_err(|error| ("link", error.to_string()))?;
    let compilation = timed(&mut report.phase_seconds, "compile", || {
        compile_function(&linked, &program.module, &program.entry)
    })
    .map_err(|error| ("compile", error.to_string()))?;
    if !compilation.certificate.certified() || !compilation.graft_trace.certificate.certified() {
        return Err((
            "compile",
            "compiler did not return checked certificates".to_owned(),
        ));
    }
    report.actual.compiled_nodes = compilation.result.nodes.len();
    report.actual.occurrences = compilation.result.occurrences.len();
    report.actual.history_events = compilation.result.history.prefix.len();
    let evaluation = timed(&mut report.phase_seconds, "evaluate", || {
        evaluate(&compilation.result, &program.inputs)
    });
    report.compilation = Some(compilation);
    let evaluation = evaluation.map_err(|error| ("evaluate", error.to_string()))?;
    report.actual.evaluated_nodes = evaluation.certificate.executed_nodes.len();
    if evaluation.values.iter().any(|value| !value.is_finite()) {
        return Err((
            "evaluate",
            "nonfinite output cannot be stored as a successful scalar result".to_owned(),
        ));
    }
    report.evaluation = Some(evaluation);
    Ok(())
}

fn preflight_source(
    program: &NativeRunProgramV0,
    actual: &mut NativeRunActualV0,
) -> Result<(), String> {
    if program.schema != NATIVE_RUN_PROGRAM_SCHEMA_V0 || program.version != 0 {
        return Err("unsupported native run schema or version".to_owned());
    }
    if !(1..=NATIVE_RUN_MAX_TERMS).contains(&program.fuel) {
        return Err("fuel must be an integer in 1..=16".to_owned());
    }
    actual.source_bytes = program.source.len();
    if program.source.len() > NATIVE_RUN_MAX_SOURCE_BYTES || !program.source.is_ascii() {
        return Err("source must be ASCII and at most 4096 bytes".to_owned());
    }
    if program.inputs.len() > NATIVE_RUN_MAX_INPUTS
        || program.inputs.values().any(|value| !value.is_finite())
    {
        return Err("inputs must contain at most eight finite scalar values".to_owned());
    }
    let mut depth = 0usize;
    let mut comment = false;
    for byte in program.source.bytes() {
        if comment {
            if byte == b'\n' {
                comment = false;
            }
            continue;
        }
        match byte {
            b';' => comment = true,
            b'(' => {
                depth += 1;
                actual.lexical_max_depth = actual.lexical_max_depth.max(depth);
                if depth > NATIVE_RUN_MAX_DEPTH {
                    return Err("source nesting exceeds 32 before parsing".to_owned());
                }
            }
            b')' => {
                depth = depth
                    .checked_sub(1)
                    .ok_or("unmatched closing parenthesis")?;
            }
            _ => {}
        }
    }
    if depth != 0 {
        return Err("unclosed source parentheses".to_owned());
    }
    Ok(())
}

fn count_terms(term: &ProgramTerm, actual: &mut NativeRunActualV0) -> Result<(), String> {
    actual.ast_terms += 1;
    if actual.ast_terms > NATIVE_RUN_MAX_TERMS {
        return Err("AST term budget exceeds 16 before compilation".to_owned());
    }
    let children = match term {
        ProgramTerm::Use { .. } | ProgramTerm::Constant { .. } => return Ok(()),
        ProgramTerm::Call { .. } => {
            return Err("Call is outside this first bounded run profile".to_owned());
        }
        ProgramTerm::Frontier { terms } => terms,
        ProgramTerm::Apply {
            operation,
            arguments,
        } => {
            // This caps an existing structural operation; it does not define it.
            if operation.name == "copy" {
                actual.copy_operations += 1;
                if actual.copy_operations > NATIVE_RUN_MAX_COPIES {
                    return Err("copy budget exceeds four before compilation".to_owned());
                }
            }
            arguments
        }
    };
    for child in children {
        count_terms(child, actual)?;
    }
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;
    use adva_lisp::import_diagram_json;
    use serde_json::json;

    const ARITHMETIC: &str = "(module arithmetic (export compute) (def compute (fn ((x Real) (y Real) (z Real)) Real (add (use x) (mul (use y) (use z))))))";

    fn program(source: &str, inputs: serde_json::Value) -> String {
        json!({
            "schema": NATIVE_RUN_PROGRAM_SCHEMA_V0,
            "version": 0,
            "source": source,
            "module": "arithmetic",
            "entry": "compute",
            "inputs": inputs,
            "fuel": 16
        })
        .to_string()
    }

    fn unary(body: &str) -> String {
        format!("(module arithmetic (export compute) (def compute (fn ((x Real)) Real {body})))")
    }

    #[test]
    fn native_run_computes_and_reuses_a_checked_diagram() {
        let input = program(ARITHMETIC, json!({"x": 2, "y": 3, "z": 4}));
        let report = run_native_program_v0(&input);
        assert_eq!(report.state, "Completed", "{:?}", report.error);
        assert_eq!(report.evaluation.as_ref().unwrap().values, vec![14.0]);
        assert_eq!(report.actual.ast_terms, 5);
        assert_eq!(report.program_json.as_deref(), Some(input.as_str()));
        let compilation = report.compilation.as_ref().unwrap();
        let encoded = serde_json::to_string(&compilation.result).unwrap();
        let checked = import_diagram_json(&encoded).unwrap();
        assert!(checked.certificate.certified());
        assert_eq!(checked.result.history, compilation.result.history);
        let mut tampered: serde_json::Value = serde_json::from_str(&encoded).unwrap();
        tampered["history"]["prefix"] = json!([]);
        assert!(import_diagram_json(&tampered.to_string()).is_err());
        let reuse = BTreeMap::from([
            ("x".to_owned(), 5.0),
            ("y".to_owned(), 2.0),
            ("z".to_owned(), 3.0),
        ]);
        assert_eq!(
            evaluate(&checked.result, &reuse).unwrap().values,
            vec![11.0]
        );
        let replay = run_native_program_v0(&input);
        assert_eq!(replay.compilation, report.compilation);
        assert_eq!(replay.evaluation, report.evaluation);
        let serialized = serde_json::to_string(&report).unwrap();
        let decoded: NativeRunReportV0 = serde_json::from_str(&serialized).unwrap();
        assert_eq!(decoded.compilation, report.compilation);
    }

    #[test]
    fn native_run_rejects_linearity_and_wrong_input_names() {
        for (source, inputs, phase) in [
            (unary("(add (use x) (use x))"), json!({"x": 2}), "compile"),
            (unary("(id (use x))"), json!({"y": 2}), "evaluate"),
        ] {
            let report = run_native_program_v0(&program(&source, inputs));
            assert_eq!(report.state, "Rejected");
            assert_eq!(report.error_phase.as_deref(), Some(phase));
            assert!(report.evaluation.is_none());
        }
    }

    #[test]
    fn native_run_refuses_call_and_copy_expansion_before_compile() {
        let call = unary("(call compute (use x))");
        let mut copies = "(use x)".to_owned();
        for _ in 0..5 {
            copies = format!("(add (copy {copies}))");
        }
        for source in [call, unary(&copies)] {
            let report = run_native_program_v0(&program(&source, json!({"x": 2})));
            assert_eq!(report.state, "Rejected");
            assert_eq!(report.error_phase.as_deref(), Some("term_preflight"));
            assert!(!report.phase_seconds.contains_key("compile"));
        }
    }

    #[test]
    fn native_run_checks_fuel_and_depth_before_compilation() {
        let mut envelope: serde_json::Value =
            serde_json::from_str(&program(ARITHMETIC, json!({"x": 2, "y": 3, "z": 4}))).unwrap();
        envelope["fuel"] = json!(4);
        let report = run_native_program_v0(&envelope.to_string());
        assert_eq!(report.error_phase.as_deref(), Some("term_preflight"));
        assert_eq!(report.actual.reserved_fuel, 0);
        assert!(report.compilation.is_none());
        let deep = format!("{}{}", "(".repeat(33), ")".repeat(33));
        let report = run_native_program_v0(&program(&deep, json!({})));
        assert_eq!(report.error_phase.as_deref(), Some("source_preflight"));
        assert!(!report.phase_seconds.contains_key("lisp_parse"));
    }

    #[test]
    fn native_input_and_report_preserve_k28_binary64_values() {
        let source = "(module arithmetic (export compute) (def compute (fn ((x Real) (y Real)) Real (mul (use x) (use y)))))";
        let input = program(
            source,
            json!({
                "x": 1.0 + 2.0_f64.powi(-28),
                "y": 1.0 - 2.0_f64.powi(-28),
            }),
        );
        let report = run_native_program_v0(&input);
        assert_eq!(report.state, "Completed");
        let expected = (1.0 - 2.0_f64.powi(-28)).to_bits();
        assert_eq!(
            report.program.as_ref().unwrap().inputs["y"].to_bits(),
            expected
        );
        assert_eq!(report.evaluation.as_ref().unwrap().values, vec![1.0]);
        let encoded = serde_json::to_string(&report).unwrap();
        let decoded: NativeRunReportV0 = serde_json::from_str(&encoded).unwrap();
        assert_eq!(decoded.program.unwrap().inputs["y"].to_bits(), expected);
        assert_eq!(decoded.evaluation.unwrap().values, vec![1.0]);
    }

    #[test]
    fn native_run_refuses_nonfinite_outputs_and_log_domain_failures() {
        for (body, x) in [("(exp (use x))", 1000.0), ("(log (use x))", 0.0)] {
            let report = run_native_program_v0(&program(&unary(body), json!({"x": x})));
            assert_eq!(report.state, "Rejected");
            assert_eq!(report.error_phase.as_deref(), Some("evaluate"));
            assert!(report.compilation.is_some());
            assert!(report.evaluation.is_none());
            assert!(serde_json::to_string(&report).is_ok());
        }
    }

    #[test]
    fn native_run_refuses_unsupported_envelopes_and_nonreal_boundaries() {
        for input in [
            "{}".to_owned(),
            "{".to_owned(),
            " ".repeat(NATIVE_RUN_MAX_ENVELOPE_BYTES + 1),
        ] {
            assert_eq!(run_native_program_v0(&input).state, "Rejected");
        }
        let mut envelope: serde_json::Value =
            serde_json::from_str(&program(&unary("(use x)"), json!({"x": 2}))).unwrap();
        envelope["unexpected"] = json!(true);
        assert_eq!(
            run_native_program_v0(&envelope.to_string())
                .error_phase
                .as_deref(),
            Some("envelope_parse")
        );
        envelope.as_object_mut().unwrap().remove("unexpected");
        envelope["version"] = json!(1);
        assert_eq!(
            run_native_program_v0(&envelope.to_string())
                .error_phase
                .as_deref(),
            Some("source_preflight")
        );
        envelope["version"] = json!(0);
        envelope["source"] = json!(";".repeat(NATIVE_RUN_MAX_SOURCE_BYTES + 1));
        assert_eq!(
            run_native_program_v0(&envelope.to_string())
                .error_phase
                .as_deref(),
            Some("source_preflight")
        );
        envelope["source"] = json!(
            "(module arithmetic (export compute) (def compute (fn ((x Bool)) Bool (use x))))"
        );
        assert_eq!(
            run_native_program_v0(&envelope.to_string())
                .error_phase
                .as_deref(),
            Some("term_preflight")
        );
    }

    #[test]
    fn native_run_preserves_histories_even_when_values_agree() {
        let identity = run_native_program_v0(&program(&unary("(id (use x))"), json!({"x": 2})));
        let reverse =
            run_native_program_v0(&program(&unary("(neg (neg (use x)))"), json!({"x": 2})));
        assert_eq!(identity.state, "Completed");
        assert_eq!(reverse.state, "Completed");
        assert_eq!(
            identity.evaluation.unwrap().values,
            reverse.evaluation.unwrap().values
        );
        assert_ne!(
            identity.compilation.unwrap().result.history,
            reverse.compilation.unwrap().result.history
        );
    }
}
