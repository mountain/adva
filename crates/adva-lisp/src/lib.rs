//! Modular, typed Lisp kernel for Adva.

mod compile;
mod eval;
mod module;
mod operation;
mod parser;
mod process;
mod validate;

pub use compile::compile_function;
pub use eval::{
    evaluate, evaluate_finite, evaluate_with_differential, evaluate_with_finite_differential,
    observe_history, observe_source_partition,
};
pub use module::{LinkedModules, link_modules};
pub use operation::{
    BUILTIN_NAMESPACE, BUILTIN_VERSION, LineageRule, OperationSpec, builtin_operation_specs,
    resolve_operation,
};
pub use parser::parse_module;
pub use process::{
    advance_causal_cut, analyze_causal_cut, analyze_program_slice,
    analyze_program_slice_with_graft, analyze_triadic_observer_transition_v0,
    analyze_triadic_observer_transition_with_graft_v0, compose_program_slices,
    compose_program_slices_with_graft, compose_triadic_observer_transitions_v0,
    compose_triadic_observer_transitions_with_graft_v0,
};
pub use validate::{import_diagram_json, validate_diagram};

use thiserror::Error;

#[derive(Debug, Error)]
pub enum LispError {
    #[error("syntax error: {0}")]
    Syntax(String),
    #[error("module error: {0}")]
    Module(String),
    #[error("type error: {0}")]
    Type(String),
    #[error("linearity error: {0}")]
    Linearity(String),
    #[error("diagram validation error: {0}")]
    Validation(String),
    #[error("evaluation error: {0}")]
    Evaluation(String),
    #[error("IR error: {0}")]
    Ir(#[from] adva_ir::IrError),
    #[error("serialization error: {0}")]
    Serialization(#[from] serde_json::Error),
}
