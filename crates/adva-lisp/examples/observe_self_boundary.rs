//! Fixed native capability audit. No new operation or self-interpreter is installed.

use adva_ir::CompilationArtifact;
use adva_lisp::{compile_function, evaluate, link_modules, observe_history, parse_module};
use serde_json::{Value, json};
use std::collections::BTreeMap;
use std::error::Error;
use std::fs::OpenOptions;
use std::io::Write;
use std::path::{Path, PathBuf};
use std::time::Instant;

type AuditResult<T> = Result<T, Box<dyn Error>>;
type Costs = BTreeMap<String, f64>;

const WORDS: &str = include_str!("../../../programs/self-boundary/words.lisp");
const CODE: &str = "(module code-gap (export f) (def f (fn ((x Code)) Real (id (use x)))))";
const QUOTE: &str = "(module quote-gap (export f) (def f (fn ((x Real)) Real (quote (use x)))))";
const CASE: &str = "(module case-gap (export f) (def f (fn ((x Real)) Real (case (use x)))))";
const RECURSION: &str =
    "(module recursive-gap (export f) (def f (fn ((x Real)) Real (call f (use x)))))";
const IDENTITY: &str = "(module history-test (export f) (def f (fn ((x Real)) Real (id (use x)))))";
const DOUBLE_NEGATION: &str =
    "(module history-test (export f) (def f (fn ((x Real)) Real (neg (neg (use x))))))";

const MAX_SOURCE_BYTES: usize = 2048;
const MAX_COMPILED_NODES: usize = 64;
const MAX_ARTIFACT_BYTES: usize = 131_072;

fn measure<T>(costs: &mut Costs, phase: &str, action: impl FnOnce() -> T) -> T {
    let started = Instant::now();
    let result = action();
    *costs.entry(phase.to_owned()).or_default() += started.elapsed().as_secs_f64();
    result
}

fn require(condition: bool, message: &str) -> AuditResult<()> {
    if condition {
        Ok(())
    } else {
        Err(message.to_owned().into())
    }
}

fn compile_source(
    source: &str,
    module: &str,
    function: &str,
    costs: &mut Costs,
    nodes: &mut usize,
) -> AuditResult<CompilationArtifact> {
    let parsed = measure(costs, "parse", || parse_module(source))?;
    let linked = measure(costs, "link", || link_modules(vec![parsed]))?;
    let compiled = measure(costs, "compile", || {
        compile_function(&linked, module, function)
    })?;
    *nodes = nodes
        .checked_add(compiled.result.nodes.len())
        .ok_or("node count overflow")?;
    require(
        *nodes <= MAX_COMPILED_NODES,
        "compiled node budget exceeded",
    )?;
    require(
        compiled.certificate.certified(),
        "compilation not certified",
    )?;
    require(
        compiled.graft_trace.certificate.certified(),
        "graft trace not certified",
    )?;
    Ok(compiled)
}

fn parse_refusal(
    label: &str,
    source: &str,
    expected: &str,
    costs: &mut Costs,
) -> AuditResult<Value> {
    let error = match measure(costs, "parse", || parse_module(source)) {
        Ok(_) => return Err(format!("{label} unexpectedly parsed").into()),
        Err(error) => error.to_string(),
    };
    require(error.contains(expected), "unexpected parse refusal")?;
    Ok(json!({
        "case": label,
        "source": source,
        "refusal_phase": "parse",
        "error": error,
        "checked_expected_fragment": expected
    }))
}

fn output_path() -> AuditResult<Option<PathBuf>> {
    let mut args = std::env::args_os().skip(1);
    let Some(flag) = args.next() else {
        return Ok(None);
    };
    require(
        flag == "--output",
        "usage: observe_self_boundary [--output PATH]",
    )?;
    let path = PathBuf::from(args.next().ok_or("missing --output path")?);
    require(args.next().is_none(), "unexpected extra argument")?;
    require(
        path.file_name().and_then(|name| name.to_str()) == Some("self-boundary.json"),
        "output basename must be self-boundary.json",
    )?;
    Ok(Some(path))
}

fn write_new(path: &Path, bytes: &[u8]) -> AuditResult<()> {
    require(
        bytes.len() <= MAX_ARTIFACT_BYTES,
        "artifact byte budget exceeded",
    )?;
    let mut file = OpenOptions::new().write(true).create_new(true).open(path)?;
    file.write_all(bytes)?;
    file.sync_all()?;
    Ok(())
}

fn audit() -> AuditResult<Value> {
    let sources = [
        WORDS,
        CODE,
        QUOTE,
        CASE,
        RECURSION,
        IDENTITY,
        DOUBLE_NEGATION,
    ];
    for source in sources {
        require(
            source.len() <= MAX_SOURCE_BYTES,
            "source byte budget exceeded",
        )?;
    }
    let mut costs = Costs::new();
    let mut compiled_nodes = 0;
    let words = compile_source(
        WORDS,
        "self-boundary",
        "learn",
        &mut costs,
        &mut compiled_nodes,
    )?;
    let inputs = BTreeMap::from([("x".to_owned(), 2.0)]);
    let first = measure(&mut costs, "evaluate", || evaluate(&words.result, &inputs))?;
    require(first.values == vec![2.0], "composition failed at x=2")?;
    let reuse_inputs = BTreeMap::from([("x".to_owned(), 3.0)]);
    let reuse = measure(&mut costs, "reuse_evaluate", || {
        evaluate(&words.result, &reuse_inputs)
    })?;
    require(reuse.values == vec![3.0], "composition failed at x=3")?;
    let words_history = measure(&mut costs, "observe", || observe_history(&words.result));

    let mut refusals = vec![
        parse_refusal("code-input", CODE, "unknown type \"Code\"", &mut costs)?,
        parse_refusal("quote", QUOTE, "unknown operation \"quote\"", &mut costs)?,
        parse_refusal("case", CASE, "unknown operation \"case\"", &mut costs)?,
    ];
    let parsed = measure(&mut costs, "parse", || parse_module(RECURSION))?;
    let linked = measure(&mut costs, "link", || link_modules(vec![parsed]))?;
    let recursive_error = match measure(&mut costs, "compile", || {
        compile_function(&linked, "recursive-gap", "f")
    }) {
        Ok(_) => return Err("recursive call unexpectedly compiled".into()),
        Err(error) => error.to_string(),
    };
    require(
        recursive_error.contains("recursive call"),
        "unexpected recursive refusal",
    )?;
    refusals.push(json!({
        "case": "recursive-call",
        "source": RECURSION,
        "refusal_phase": "compile",
        "parse_and_link": "accepted",
        "error": recursive_error,
        "checked_expected_fragment": "recursive call"
    }));

    let identity = compile_source(
        IDENTITY,
        "history-test",
        "f",
        &mut costs,
        &mut compiled_nodes,
    )?;
    let double_negation = compile_source(
        DOUBLE_NEGATION,
        "history-test",
        "f",
        &mut costs,
        &mut compiled_nodes,
    )?;
    let id_value = measure(&mut costs, "evaluate", || {
        evaluate(&identity.result, &inputs)
    })?;
    let neg_value = measure(&mut costs, "evaluate", || {
        evaluate(&double_negation.result, &inputs)
    })?;
    require(id_value.values == vec![2.0], "identity value mismatch")?;
    require(
        id_value.values == neg_value.values,
        "value comparison failed",
    )?;
    require(
        identity.result.function == double_negation.result.function
            && identity.result.signature == double_negation.result.signature,
        "counterexample changed the named input boundary",
    )?;
    let id_history = measure(&mut costs, "observe", || observe_history(&identity.result));
    let neg_history = measure(&mut costs, "observe", || {
        observe_history(&double_negation.result)
    });
    require(id_history != neg_history, "expected distinct histories")?;

    let mut payload = measure(&mut costs, "evidence_construction", || {
        json!({
            "schema": "adva.research.self-boundary",
            "version": 0,
            "source_base": "57c1d04bcfe51b82f6e559a61ca02e668f630b5a",
            "status": "finite-capability-audit-passed",
            "self_interpreter_status": "Unknown",
            "budget": {
                "fixed_case_groups": 6,
                "fixed_source_texts": 7,
                "max_source_bytes_each": MAX_SOURCE_BYTES,
                "max_compiled_nodes_aggregate": MAX_COMPILED_NODES,
                "max_artifact_bytes": MAX_ARTIFACT_BYTES,
                "search_candidates": 0,
                "automatic_restarts": 0,
                "wall_timeout_and_memory": "external supervisor required"
            },
            "actual": {
                "source_bytes": sources.map(str::len),
                "successful_compilations": 3,
                "rejected_compilations": 1,
                "rejected_parses": 3,
                "compiled_nodes_aggregate": compiled_nodes,
                "evaluations": 4,
                "history_observations": 3,
                "peak_memory_bytes": null
            },
            "named_composition": {
                "source": WORDS,
                "function": words.result.function,
                "compile_certificate": words.certificate,
                "graft_certificate": words.graft_trace.certificate,
                "compiled_nodes": words.result.nodes.len(),
                "history_event_count": words.result.history.prefix.len(),
                "history": words_history,
                "input": inputs,
                "evaluation": first,
                "reuse_input": reuse_inputs,
                "reuse_evaluation": reuse,
                "reuse_recompilation": false
            },
            "refusals": refusals,
            "forget_counterexample": {
                "same_module_function_and_input_boundary": true,
                "same_observed_value": true,
                "same_history": false,
                "identity": {
                    "source": IDENTITY,
                    "evaluation": id_value,
                    "compile_certificate": identity.certificate,
                    "history_event_count": identity.result.history.prefix.len(),
                    "history": id_history
                },
                "double_negation": {
                    "source": DOUBLE_NEGATION,
                    "evaluation": neg_value,
                    "compile_certificate": double_negation.certificate,
                    "history_event_count": double_negation.result.history.prefix.len(),
                    "history": neg_history
                },
                "conclusion": "Value alone does not determine retained program history."
            },
            "role_distinctions": {
                "learn": "Fixture function name for finite composition; no learning update.",
                "observe_in_fixture": "Value identity function named by the author.",
                "observe_history": "Existing native Rust history observation API.",
                "self": "Finite directed roundtrip; does not interpret its own code.",
                "free_and_Universe": "No new interpretation established by this audit."
            },
            "limitations": [
                "Only seven frozen sources and two composition inputs were checked.",
                "Real uses f64; these binary-exact cases are not exact-arithmetic proofs.",
                "No native polynomial, multiplicative-residual, or M6 certificate is made.",
                "No Code value, quote, case, recursion, or interpreter builtin is added.",
                "Compiler and checker continue to run in Rust outside the fixture.",
                "No source identity is authorized by scalar equality or a name.",
                "No historical inverse follows from the value-level roundtrip.",
                "No file named adva.adva or recursive extension is generated.",
                "A refusal here is not a proof that every encoding is impossible."
            ]
        })
    });
    payload["phase_seconds"] = json!(costs);
    Ok(payload)
}

fn main() -> AuditResult<()> {
    let output = output_path()?;
    let started = Instant::now();
    let payload = audit()?;
    let audit_seconds = started.elapsed().as_secs_f64();
    let serialization_start = Instant::now();
    let bytes = serde_json::to_vec_pretty(&payload)?;
    let serialization_seconds = serialization_start.elapsed().as_secs_f64();
    require(
        bytes.len() <= MAX_ARTIFACT_BYTES,
        "artifact byte budget exceeded",
    )?;
    if let Some(path) = output {
        let write_start = Instant::now();
        write_new(&path, &bytes)?;
        eprintln!(
            "output_write_seconds={}",
            write_start.elapsed().as_secs_f64()
        );
    }
    println!("SELF_BOUNDARY_EVIDENCE_BEGIN");
    println!("{}", std::str::from_utf8(&bytes)?);
    println!("SELF_BOUNDARY_EVIDENCE_END");
    eprintln!("audit_seconds={audit_seconds}");
    eprintln!("serialization_seconds={serialization_seconds}");
    eprintln!("serialized_artifact_bytes={}", bytes.len());
    Ok(())
}
