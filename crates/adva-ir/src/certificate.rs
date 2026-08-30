use crate::{
    CausalCut, CausalStep, CertificateId, FunctionSignature, NodeId, SharedProgramDiagram,
};
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
    pub diagram_integrity: CheckStatus,
}

impl CompilationCertificate {
    pub fn certified(&self) -> bool {
        [
            self.module_links,
            self.linear_use,
            self.types,
            self.call_history,
            self.diagram_integrity,
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

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct DiagramValidationCertificate {
    pub id: CertificateId,
    pub scope: String,
    pub boundary: FunctionSignature,
    pub schema: CheckStatus,
    pub identifiers: CheckStatus,
    pub graph: CheckStatus,
    pub operation_boundaries: CheckStatus,
    pub linear_use: CheckStatus,
    pub occurrence_paths: CheckStatus,
    pub source_partition: CheckStatus,
    pub history: CheckStatus,
    pub rewrite_trace: CheckStatus,
    pub node_ids: Vec<crate::NodeId>,
    pub source_partition_snapshot: BTreeMap<crate::SourceId, Vec<crate::OccurrenceId>>,
    pub history_event_count: u32,
}

impl DiagramValidationCertificate {
    pub fn certified(&self) -> bool {
        [
            self.schema,
            self.identifiers,
            self.graph,
            self.operation_boundaries,
            self.linear_use,
            self.occurrence_paths,
            self.source_partition,
            self.history,
            self.rewrite_trace,
        ]
        .into_iter()
        .all(|status| status == CheckStatus::Checked)
    }
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct DiagramValidationArtifact {
    pub result: SharedProgramDiagram,
    pub certificate: DiagramValidationCertificate,
}

/// Certificate for deriving one open frontier from a checked program DAG.
#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct CausalCutCertificate {
    pub id: CertificateId,
    pub scope: String,
    pub diagram_integrity: CheckStatus,
    pub completed_past: CheckStatus,
    pub crossing_frontier: CheckStatus,
    pub lineage_preservation: CheckStatus,
    pub completed_nodes: Vec<NodeId>,
}

impl CausalCutCertificate {
    pub fn certified(&self) -> bool {
        [
            self.diagram_integrity,
            self.completed_past,
            self.crossing_frontier,
            self.lineage_preservation,
        ]
        .into_iter()
        .all(|status| status == CheckStatus::Checked)
    }
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct CausalCutArtifact {
    pub result: CausalCut,
    pub certificate: CausalCutCertificate,
}

/// Certificate for one enabled event replacing wires across a causal cut.
#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct CausalStepCertificate {
    pub id: CertificateId,
    pub scope: String,
    pub diagram_integrity: CheckStatus,
    pub event_enabled: CheckStatus,
    pub frontier_replacement: CheckStatus,
    pub event: NodeId,
}

impl CausalStepCertificate {
    pub fn certified(&self) -> bool {
        [
            self.diagram_integrity,
            self.event_enabled,
            self.frontier_replacement,
        ]
        .into_iter()
        .all(|status| status == CheckStatus::Checked)
    }
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct CausalStepArtifact {
    pub result: CausalStep,
    pub certificate: CausalStepCertificate,
}

#[derive(Clone, Debug, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct EvaluationCertificate {
    pub id: CertificateId,
    pub scope: String,
    pub executed_nodes: Vec<u32>,
    pub input_types_checked: bool,
    pub diagram_integrity: CheckStatus,
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
    pub diagram_integrity: CheckStatus,
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
