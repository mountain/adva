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

/// One observer role in the bounded three-domain transition calibration.
///
/// These labels belong to an explicit observation policy. They do not change
/// the type or identity of any program wire, source, or occurrence.
#[derive(Clone, Copy, Debug, Eq, Hash, Ord, PartialEq, PartialOrd, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum TriadicDomainV0 {
    Construction,
    Space,
    Time,
}

/// Assign the three input-source fibres to observer roles by input position.
#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct TriadicObserverPolicyV0 {
    pub input_domains: Vec<TriadicDomainV0>,
}

/// One occurrence-level incidence at a checked causal cut.
///
/// The two indices point back into the unchanged `CausalCut`: first to its
/// frontier wire and then to one exact occurrence in that wire's lineage.
#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct TriadicCutIncidenceV0 {
    pub cut_wire_index: u32,
    pub lineage_index: u32,
    pub occurrence: Occurrence,
    pub domain: TriadicDomainV0,
}

/// The opposite-pair reading available to one of the three observer roles.
#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct TriadicOppositePairCutV0 {
    pub observer: TriadicDomainV0,
    pub visible_incidence_indices: Vec<u32>,
    pub hidden_own_incidence_indices: Vec<u32>,
}

/// A triadic occurrence reading of one exact causal cut.
#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct TriadicCutObservationV0 {
    pub cut: CausalCut,
    pub incidences: Vec<TriadicCutIncidenceV0>,
    /// Cut wires with empty source lineage are retained here, visible to none
    /// of the three source-relative opposite-pair charts.
    pub source_free_wire_indices: Vec<u32>,
    pub opposite_pair_views: Vec<TriadicOppositePairCutV0>,
}

/// One exact ancestry link between lower and upper cut incidences.
///
/// A link exists when source identity is unchanged and the lower occurrence
/// path is a prefix of the upper path. Copy extends paths; ordinary operations
/// preserve them; discard leaves no upper descendant.
#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct TriadicLineageLinkV0 {
    pub lower_incidence_index: u32,
    pub upper_incidence_index: u32,
}

/// The lineage links visible from one opposite-pair chart.
#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct TriadicOppositePairTransitionV0 {
    pub observer: TriadicDomainV0,
    pub visible_lineage_link_indices: Vec<u32>,
}

/// A certificate-ready triadic observer view of one exact `ProgramSlice`.
///
/// The embedded slice is the complete checked residual. The three views are
/// overlapping projections of its source incidences, not three duplicated
/// programs and not an active program transformation.
#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct TriadicObserverTransitionV0 {
    pub policy: TriadicObserverPolicyV0,
    pub slice: ProgramSlice,
    pub lower: TriadicCutObservationV0,
    pub upper: TriadicCutObservationV0,
    pub lineage_links: Vec<TriadicLineageLinkV0>,
    pub opposite_pair_transitions: Vec<TriadicOppositePairTransitionV0>,
}
