use crate::{NodeId, SourceId, WireRef};
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
