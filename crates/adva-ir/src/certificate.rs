use crate::{
    CausalCut, CausalStep, CertificateId, FunctionSignature, GraftFrameId, GraftTrace, NodeId,
    ProgramSlice, SharedProgramDiagram,
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
    pub graft_trace: GraftTraceArtifact,
}

/// Certificate for a compiler-emitted finite nested substitution trace.
#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct GraftTraceCertificate {
    pub id: CertificateId,
    pub scope: String,
    pub diagram_integrity: CheckStatus,
    pub deterministic_frame_ids: CheckStatus,
    pub parent_child_nesting: CheckStatus,
    pub ordered_hole_bindings: CheckStatus,
    pub argument_body_regions: CheckStatus,
    pub boundary_maps: CheckStatus,
    pub call_history_links: CheckStatus,
    pub frame_ids: Vec<GraftFrameId>,
}

impl GraftTraceCertificate {
    pub fn certified(&self) -> bool {
        [
            self.diagram_integrity,
            self.deterministic_frame_ids,
            self.parent_child_nesting,
            self.ordered_hole_bindings,
            self.argument_body_regions,
            self.boundary_maps,
            self.call_history_links,
        ]
        .into_iter()
        .all(|status| status == CheckStatus::Checked)
    }
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct GraftTraceArtifact {
    pub result: GraftTrace,
    pub certificate: GraftTraceCertificate,
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

/// Certificate for an exact finite interval between two causal cuts.
#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct ProgramSliceCertificate {
    pub id: CertificateId,
    pub scope: String,
    pub diagram_integrity: CheckStatus,
    pub lower_past: CheckStatus,
    pub upper_past: CheckStatus,
    pub past_inclusion: CheckStatus,
    pub event_difference: CheckStatus,
    pub boundary_partition: CheckStatus,
    pub internal_events: CheckStatus,
    pub original_id_preservation: CheckStatus,
    pub lineage_preservation: CheckStatus,
    /// `None` means that no compiler graft trace was supplied.
    pub graft_frame_consistency: Option<CheckStatus>,
    pub lower_completed: Vec<NodeId>,
    pub upper_completed: Vec<NodeId>,
    pub event_ids: Vec<NodeId>,
}

impl ProgramSliceCertificate {
    pub fn certified(&self) -> bool {
        [
            self.diagram_integrity,
            self.lower_past,
            self.upper_past,
            self.past_inclusion,
            self.event_difference,
            self.boundary_partition,
            self.internal_events,
            self.original_id_preservation,
            self.lineage_preservation,
        ]
        .into_iter()
        .all(|status| status == CheckStatus::Checked)
            && self
                .graft_frame_consistency
                .is_none_or(|status| status == CheckStatus::Checked)
    }
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct ProgramSliceArtifact {
    pub result: ProgramSlice,
    pub certificate: ProgramSliceCertificate,
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
