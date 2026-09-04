//! Research companion for reusable six-word witnesses.
//!
//! This crate does not extend `adva.ir` version 1 and does not allocate
//! [`adva_ir::SourceId`] or [`adva_ir::OccurrenceId`]. It checks a bounded,
//! exact witness language whose artifacts may be cached independently from
//! the fresh program instances that cite them.

mod arithmetic;
mod boundary;
mod mechanism;
mod persistence;
mod relation;
mod seed;
mod witness;

pub use arithmetic::*;
pub use boundary::*;
pub use mechanism::*;
pub use persistence::*;
pub use relation::*;
pub use seed::*;
pub use witness::*;

/// Schema identifier for serialized research artifacts.
pub const WITNESS_SCHEMA_V0: &str = "adva.witness.research";

/// Experimental schema version. Version zero is not part of `adva.ir`.
pub const WITNESS_VERSION_V0: u32 = 0;
