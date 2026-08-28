use crate::{
    CellId, FunctionSignature, ModuleName, NodeId, OccurrenceId, OccurrencePath, OperationRef,
    QualifiedName, SourceId, ValueType,
};
use serde::{Deserialize, Serialize};
use std::collections::BTreeMap;

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(tag = "kind", rename_all = "snake_case")]
pub enum WireProducer {
    Input { index: u32 },
    Node { node: NodeId },
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct WireRef {
    pub producer: WireProducer,
    pub output_index: u32,
    pub value_type: ValueType,
    pub lineage: Vec<OccurrenceId>,
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct OperationNode {
    pub id: NodeId,
    pub operation: OperationRef,
    pub inputs: Vec<WireRef>,
    pub output_types: Vec<ValueType>,
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct Occurrence {
    pub id: OccurrenceId,
    pub source: SourceId,
    pub path: OccurrencePath,
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(tag = "kind", rename_all = "snake_case")]
pub enum HistoryEvent {
    Source {
        source: SourceId,
        occurrence: OccurrenceId,
    },
    Copy {
        node: NodeId,
        parent: OccurrenceId,
        children: Vec<OccurrenceId>,
    },
    Operation {
        node: NodeId,
        operation: OperationRef,
    },
    Call {
        function: QualifiedName,
    },
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct DirectedRewrite {
    pub name: String,
    pub source_boundary: FunctionSignature,
    pub target_boundary: FunctionSignature,
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct NormalizationStep {
    pub rewrite: DirectedRewrite,
    pub before_node_count: u32,
    pub after_node_count: u32,
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct EquationCell {
    pub id: CellId,
    pub name: String,
    pub source_boundary: FunctionSignature,
    pub target_boundary: FunctionSignature,
    pub inverse: CellId,
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct CoherenceCell {
    pub id: CellId,
    pub name: String,
    pub source_path: Vec<CellId>,
    pub target_path: Vec<CellId>,
    pub inverse: CellId,
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct History {
    pub prefix: Vec<HistoryEvent>,
    pub occurrence_paths: BTreeMap<OccurrenceId, OccurrencePath>,
    pub rewrite_trace: Vec<NormalizationStep>,
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct SharedProgramDiagram {
    pub schema: String,
    pub version: u32,
    pub module: ModuleName,
    pub function: QualifiedName,
    pub signature: FunctionSignature,
    pub nodes: Vec<OperationNode>,
    pub outputs: Vec<WireRef>,
    pub occurrences: Vec<Occurrence>,
    pub history: History,
}

impl SharedProgramDiagram {
    pub fn source_partition(&self) -> BTreeMap<SourceId, Vec<OccurrenceId>> {
        let mut partition: BTreeMap<SourceId, Vec<OccurrenceId>> = BTreeMap::new();
        for occurrence in &self.occurrences {
            partition
                .entry(occurrence.source.clone())
                .or_default()
                .push(occurrence.id.clone());
        }
        partition
    }

    pub fn to_json(&self) -> Result<String, serde_json::Error> {
        serde_json::to_string_pretty(self)
    }

    pub fn from_json(source: &str) -> Result<Self, serde_json::Error> {
        serde_json::from_str(source)
    }
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct ProjectiveDevelopment {
    pub history: History,
    pub observer_name: String,
    pub projective_coordinates: Vec<Vec<String>>,
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum ObservationPolicy {
    Value,
    SourcePartition,
    History,
}

#[derive(Clone, Debug, PartialEq, Serialize, Deserialize)]
#[serde(tag = "kind", rename_all = "snake_case")]
pub enum Observation {
    Value {
        values: Vec<f64>,
    },
    SourcePartition {
        partition: BTreeMap<SourceId, Vec<OccurrenceId>>,
    },
    History {
        history: History,
    },
}
