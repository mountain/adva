//! Modular, typed Lisp kernel for Adva.

mod compile;
mod eval;
mod module;
mod parser;

pub use compile::compile_function;
pub use eval::{evaluate, evaluate_with_differential, observe_history, observe_source_partition};
pub use module::{LinkedModules, link_modules};
pub use parser::parse_module;

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
    #[error("evaluation error: {0}")]
    Evaluation(String),
    #[error("IR error: {0}")]
    Ir(#[from] adva_ir::IrError),
    #[error("serialization error: {0}")]
    Serialization(#[from] serde_json::Error),
}

