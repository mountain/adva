//! Immutable, language-independent ontology for Adva.

mod certificate;
mod diagram;
mod ids;
mod term;

pub use certificate::*;
pub use diagram::*;
pub use ids::*;
pub use term::*;

use serde::{Deserialize, Serialize};
use thiserror::Error;

pub const IR_SCHEMA: &str = "adva.ir";
pub const IR_VERSION: u32 = 1;

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct ModuleIr {
    pub schema: String,
    pub version: u32,
    pub module: ModuleDefinition,
}

impl ModuleIr {
    pub fn new(module: ModuleDefinition) -> Self {
        Self {
            schema: IR_SCHEMA.to_owned(),
            version: IR_VERSION,
            module,
        }
    }

    pub fn validate_version(&self) -> Result<(), IrError> {
        if self.schema != IR_SCHEMA || self.version != IR_VERSION {
            return Err(IrError::UnsupportedSchema {
                schema: self.schema.clone(),
                version: self.version,
            });
        }
        Ok(())
    }

    pub fn to_json(&self) -> Result<String, IrError> {
        Ok(serde_json::to_string_pretty(self)?)
    }

    pub fn from_json(source: &str) -> Result<Self, IrError> {
        let ir: Self = serde_json::from_str(source)?;
        ir.validate_version()?;
        Ok(ir)
    }
}

#[derive(Debug, Error)]
pub enum IrError {
    #[error("unsupported IR schema {schema:?} version {version}")]
    UnsupportedSchema { schema: String, version: u32 },
    #[error("invalid rational denominator 0")]
    ZeroDenominator,
    #[error("JSON IR error: {0}")]
    Json(#[from] serde_json::Error),
}
