use crate::{CertificateId, FunctionSignature, SharedProgramDiagram};
use serde::{Deserialize, Serialize};
use std::collections::BTreeMap;

#[derive(Clone, Copy, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum CheckStatus {
    Checked,
    Unchecked,
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct CompilationCertificate {
    pub id: CertificateId,
    pub scope: String,
    pub boundary: FunctionSignature,
    pub module_links: CheckStatus,
    pub linear_use: CheckStatus,
    pub types: CheckStatus,
    pub call_history: CheckStatus,
}

impl CompilationCertificate {
    pub fn certified(&self) -> bool {
        [
            self.module_links,
            self.linear_use,
            self.types,
            self.call_history,
        ]
        .into_iter()
        .all(|status| status == CheckStatus::Checked)
    }
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct CompilationArtifact {
    pub result: SharedProgramDiagram,
    pub certificate: CompilationCertificate,
}

#[derive(Clone, Debug, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct EvaluationCertificate {
    pub id: CertificateId,
    pub scope: String,
    pub executed_nodes: Vec<u32>,
    pub input_types_checked: bool,
    pub operation_rules_checked: bool,
}

#[derive(Clone, Debug, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct EvaluationResult {
    pub values: Vec<f64>,
    pub certificate: EvaluationCertificate,
}

#[derive(Clone, Debug, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct DifferentiationCertificate {
    pub id: CertificateId,
    pub scope: String,
    pub method: String,
    pub operation_rules: Vec<String>,
    pub input_types_checked: bool,
}

#[derive(Clone, Debug, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct DifferentialResult {
    pub values: Vec<f64>,
    pub jacobian: Vec<BTreeMap<String, f64>>,
    pub certificate: DifferentiationCertificate,
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(tag = "decision", rename_all = "snake_case")]
pub enum Decision<Yes, No> {
    Yes { certificate: Yes },
    No { countercertificate: No },
    Unknown { reason: String },
}
