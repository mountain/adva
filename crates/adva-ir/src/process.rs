use crate::{GraftFrameId, HistoryEvent, NodeId, Occurrence, OperationNode, SourceId, WireRef};
use serde::{Deserialize, Serialize};

/// The unique consumer of a checked linear wire at a causal cut.
#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(tag = "kind", rename_all = "snake_case")]
pub enum CutConsumer {
    Node { node: NodeId, input_index: u32 },
    Output { index: u32 },
}

/// One checked wire crossing from a completed causal past to its future.
#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct CutWire {
    pub wire: WireRef,
    pub sources: Vec<SourceId>,
    pub consumer: CutConsumer,
}

/// A downward-closed set of operation events and its open frontier.
#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct CausalCut {
    pub completed: Vec<NodeId>,
    pub frontier: Vec<CutWire>,
}

/// One enabled operation crossing a causal cut.
#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct CausalStep {
    pub event: NodeId,
    pub before: CausalCut,
    pub after: CausalCut,
    pub consumed: Vec<CutWire>,
    pub produced: Vec<CutWire>,
}

/// The events from one syntactic argument that lie in a causal interval.
#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct GraftArgumentIntersection {
    pub argument_index: u32,
    pub events: Vec<NodeId>,
}

/// An explicit link from a program slice to one compiler graft frame.
#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct GraftFrameIntersection {
    pub frame: GraftFrameId,
    pub argument_events: Vec<GraftArgumentIntersection>,
    pub body_events: Vec<NodeId>,
    pub call_history_index: Option<u32>,
}

/// An identity-preserving view of one checked program between nested cuts.
#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct ProgramSlice {
    pub lower: CausalCut,
    pub upper: CausalCut,
    pub events: Vec<OperationNode>,
    pub lower_boundary: Vec<CutWire>,
    pub upper_boundary: Vec<CutWire>,
    pub through_wires: Vec<CutWire>,
    pub internal_events: Vec<NodeId>,
    pub occurrences: Vec<Occurrence>,
    /// Copy and operation history whose node lies in this interval.
    pub event_history: Vec<HistoryEvent>,
    /// Present only when analysis was given a validated compiler graft trace.
    pub graft_intersections: Option<Vec<GraftFrameIntersection>>,
}
