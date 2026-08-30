use crate::{
    FunctionSignature, GraftFrameId, NodeId, QualifiedName, TypedPort, WireRef,
};
use serde::{Deserialize, Serialize};

/// One deterministic descent step locating a call frame in grafted syntax.
#[derive(Clone, Debug, Eq, Hash, Ord, PartialEq, PartialOrd, Serialize, Deserialize)]
#[serde(tag = "kind", rename_all = "snake_case")]
pub enum GraftPathStep {
    RootBody,
    ApplyArgument { index: u32 },
    FrontierTerm { index: u32 },
    CallArgument { index: u32 },
    CalleeBody,
}

/// A stable compilation path, independent of host addresses or AST sharing.
#[derive(
    Clone, Debug, Default, Eq, Hash, Ord, PartialEq, PartialOrd, Serialize, Deserialize,
)]
#[serde(transparent)]
pub struct GraftScopePath(Vec<GraftPathStep>);

impl GraftScopePath {
    pub fn new(steps: Vec<GraftPathStep>) -> Self {
        Self(steps)
    }

    pub fn steps(&self) -> &[GraftPathStep] {
        &self.0
    }

    #[must_use]
    pub fn child(&self, step: GraftPathStep) -> Self {
        let mut steps = self.0.clone();
        steps.push(step);
        Self(steps)
    }
}

/// Whether a frame is the compiled root or one finite call substitution.
#[derive(Clone, Copy, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum GraftFrameKind {
    Root,
    Call,
}

/// The region of the parent frame in which a nested call was encountered.
#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(tag = "kind", rename_all = "snake_case")]
pub enum GraftRegionRole {
    Root,
    RootBody,
    Argument { index: u32 },
    CalleeBody,
}

/// Every operation emitted while lowering one syntactic call argument.
#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct GraftArgumentRegion {
    pub argument_index: u32,
    pub nodes: Vec<NodeId>,
    pub outputs: Vec<WireRef>,
}

/// The exact output of an argument program grafted into one ordered hole.
#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct GraftHoleBinding {
    pub hole_index: u32,
    pub hole: TypedPort,
    /// Root holes are program inputs and therefore have no call argument.
    pub argument_index: Option<u32>,
    pub argument_output_index: u32,
    pub entry_wire: WireRef,
}

/// One identity-preserving finite substitution frame emitted by the compiler.
#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct GraftFrame {
    pub id: GraftFrameId,
    pub scope_path: GraftScopePath,
    pub kind: GraftFrameKind,
    pub parent: Option<GraftFrameId>,
    pub children: Vec<GraftFrameId>,
    pub region_in_parent: GraftRegionRole,
    pub caller: QualifiedName,
    pub callee: QualifiedName,
    pub boundary: FunctionSignature,
    pub arguments: Vec<GraftArgumentRegion>,
    pub holes: Vec<GraftHoleBinding>,
    pub body_region: Vec<NodeId>,
    pub entry_wires: Vec<WireRef>,
    pub exit_wires: Vec<WireRef>,
    pub call_history_index: Option<u32>,
}

/// Rooted companion trace for the nested substitutions of one compilation.
#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct GraftTrace {
    pub root: GraftFrameId,
    pub frames: Vec<GraftFrame>,
}
