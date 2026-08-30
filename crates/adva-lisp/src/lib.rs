//! Modular, typed Lisp kernel for Adva.

mod compile;
mod eval;
mod module;
mod operation;
mod parser;
mod process;
mod validate;

pub use compile::compile_function;
pub use eval::{evaluate, evaluate_with_differential, observe_history, observe_source_partition};
pub use module::{LinkedModules, link_modules};
pub use operation::{
    BUILTIN_NAMESPACE, BUILTIN_VERSION, LineageRule, OperationSpec, builtin_operation_specs,
    resolve_operation,
};
pub use parser::parse_module;
pub use process::{advance_causal_cut, analyze_causal_cut};
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
