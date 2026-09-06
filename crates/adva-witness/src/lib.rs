//! Research companion for reusable six-word witnesses.
//!
//! This crate does not extend `adva.ir` version 1 and does not allocate
//! [`adva_ir::SourceId`] or [`adva_ir::OccurrenceId`]. It checks a bounded,
//! exact witness language whose artifacts may be cached independently from
//! the fresh program instances that cite them.

mod arithmetic;
mod boundary;
mod closure_transport;
mod hypothesis_formation;
mod inquiry;
mod magic_square;
mod mechanism;
mod native_run;
mod persistence;
mod problem_value;
mod relation;
mod reveal;
mod seed;
mod trace_arithmetic;
mod trace_projection;
mod verification;
mod witness;

pub use arithmetic::*;
pub use boundary::*;
pub use closure_transport::*;
pub use hypothesis_formation::*;
pub use inquiry::*;
pub use magic_square::*;
pub use mechanism::*;
pub use native_run::*;
pub use persistence::*;
pub use problem_value::*;
pub use relation::*;
pub use reveal::*;
pub use seed::*;
pub use trace_arithmetic::*;
pub use trace_projection::*;
pub use verification::*;
pub use witness::*;

/// Schema identifier for serialized research artifacts.
pub const WITNESS_SCHEMA_V0: &str = "adva.witness.research";

/// Experimental schema version. Version zero is not part of `adva.ir`.
pub const WITNESS_VERSION_V0: u32 = 0;
