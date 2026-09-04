use crate::{
    ArithmeticErrorV0, BoundaryChargeV0, BoundaryErrorV0, ExactExprV0, MultiplicativeResidualV0,
    RoleV0, SeedErrorV0, SeedRegistryV0, TermGlyphV0, WITNESS_SCHEMA_V0, WITNESS_VERSION_V0,
};
use adva_ir::{
    CertificateId, CompilationArtifact, DiagramValidationArtifact, GraftFrameId, GraftFrameKind,
    GraftScopePath, OccurrenceId, OccurrencePath, QualifiedName, SourceId,
};
use num_bigint::BigInt;
use serde::{Deserialize, Serialize};
use std::collections::{BTreeMap, BTreeSet};
use std::fmt::{self, Display};
use thiserror::Error;

/// Content address for cache lookup only. It is never a source or occurrence
/// identity.
#[derive(Clone, Debug, Eq, Ord, PartialEq, PartialOrd, Serialize, Deserialize)]
#[serde(transparent)]
pub struct ArtifactKeyV0(String);

impl ArtifactKeyV0 {
    /// Construct a nonsemantic graph label, primarily for importing or
    /// validating an artifact graph.
    ///
    /// # Errors
    ///
    /// Returns [`WitnessErrorV0::EmptyArtifactKey`] for an empty label.
    pub fn cache_label(value: impl Into<String>) -> Result<Self, WitnessErrorV0> {
        let value = value.into();
        if value.is_empty() {
            return Err(WitnessErrorV0::EmptyArtifactKey);
        }
        Ok(Self(value))
    }

    #[must_use]
    pub fn as_str(&self) -> &str {
        &self.0
    }

    fn digest(proof: &WitnessProofV0) -> Result<Self, WitnessErrorV0> {
        let canonical = serde_json::to_vec(proof)?;
        Ok(Self(format!(
            "blake3:{}",
            blake3::hash(&canonical).to_hex()
        )))
    }
}

impl Display for ArtifactKeyV0 {
    fn fmt(&self, formatter: &mut fmt::Formatter<'_>) -> fmt::Result {
        formatter.write_str(&self.0)
    }
}

/// One node in the finite witness proof DAG.
#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(tag = "kind", rename_all = "snake_case")]
pub enum WitnessProofV0 {
    Seed {
        term: TermGlyphV0,
    },
    ArithmeticTransition {
        actual_boundary: BoundaryChargeV0,
        declared_boundary: BoundaryChargeV0,
        before: ExactExprV0,
        after: ExactExprV0,
    },
    Instantiate {
        template: ArtifactKeyV0,
        children: [ArtifactKeyV0; 3],
    },
    Compose {
        left: ArtifactKeyV0,
        connector: ArtifactKeyV0,
        right: ArtifactKeyV0,
    },
    Seal {
        body: ArtifactKeyV0,
    },
}

impl WitnessProofV0 {
    #[must_use]
    pub fn dependencies(&self) -> Vec<&ArtifactKeyV0> {
        match self {
            Self::Seed { .. } | Self::ArithmeticTransition { .. } => Vec::new(),
            Self::Instantiate { template, children } => {
                std::iter::once(template).chain(children.iter()).collect()
            }
            Self::Compose {
                left,
                connector,
                right,
            } => vec![left, connector, right],
            Self::Seal { body } => vec![body],
        }
    }
}

/// Exact reusable summary derived from a proof node and its dependencies.
#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct WitnessSummaryV0 {
    pub additive_residual: BoundaryChargeV0,
    pub multiplicative_residual: MultiplicativeResidualV0,
    pub nonzero_obligations: Vec<ExactExprV0>,
}

impl WitnessSummaryV0 {
    #[must_use]
    pub fn is_formed(&self) -> bool {
        self.additive_residual.is_zero()
    }

    #[must_use]
    pub fn is_multiplicatively_closed(&self) -> bool {
        self.multiplicative_residual.is_one()
    }
}

/// Stored proof node plus the exact summary independently derived at insert.
#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct WitnessArtifactV0 {
    pub schema: String,
    pub version: u32,
    pub key: ArtifactKeyV0,
    pub proof: WitnessProofV0,
    pub summary: WitnessSummaryV0,
}

/// In-memory content-addressed proof store. Semantic IDs never come from this
/// store.
#[derive(Clone, Debug, Default)]
pub struct WitnessStoreV0 {
    artifacts: BTreeMap<ArtifactKeyV0, WitnessArtifactV0>,
    next_instance_ordinal: u64,
}

impl WitnessStoreV0 {
    #[must_use]
    pub fn new() -> Self {
        Self::default()
    }

    /// Insert and verify one proof node. Existing identical content is reused.
    ///
    /// # Errors
    ///
    /// Rejects missing dependencies, invalid seed ledgers, invalid arithmetic,
    /// locally unformed components, and invalid seals.
    pub fn insert(&mut self, proof: WitnessProofV0) -> Result<ArtifactKeyV0, WitnessErrorV0> {
        for dependency in proof.dependencies() {
            if !self.artifacts.contains_key(dependency) {
                return Err(WitnessErrorV0::MissingDependency(dependency.clone()));
            }
        }

        let key = ArtifactKeyV0::digest(&proof)?;
        if proof
            .dependencies()
            .into_iter()
            .any(|dependency| dependency == &key)
        {
            return Err(WitnessErrorV0::CyclicDependency(key));
        }
        if let Some(existing) = self.artifacts.get(&key) {
            if existing.proof == proof {
                return Ok(key);
            }
            return Err(WitnessErrorV0::ArtifactHashCollision(key));
        }

        let summary = self.derive_summary(&proof)?;
        self.artifacts.insert(
            key.clone(),
            WitnessArtifactV0 {
                schema: WITNESS_SCHEMA_V0.to_owned(),
                version: WITNESS_VERSION_V0,
                key: key.clone(),
                proof,
                summary,
            },
        );
        Ok(key)
    }

    #[must_use]
    pub fn artifact(&self, key: &ArtifactKeyV0) -> Option<&WitnessArtifactV0> {
        self.artifacts.get(key)
    }

    #[must_use]
    pub fn len(&self) -> usize {
        self.artifacts.len()
    }

    #[must_use]
    pub fn is_empty(&self) -> bool {
        self.artifacts.is_empty()
    }

    fn summary(&self, key: &ArtifactKeyV0) -> Result<WitnessSummaryV0, WitnessErrorV0> {
        self.artifacts
            .get(key)
            .map(|artifact| artifact.summary.clone())
            .ok_or_else(|| WitnessErrorV0::MissingDependency(key.clone()))
    }

    fn require_formed(&self, key: &ArtifactKeyV0) -> Result<WitnessSummaryV0, WitnessErrorV0> {
        let summary = self.summary(key)?;
        if !summary.is_formed() {
            return Err(WitnessErrorV0::UnformedDependency(key.clone()));
        }
        Ok(summary)
    }

    fn derive_summary(&self, proof: &WitnessProofV0) -> Result<WitnessSummaryV0, WitnessErrorV0> {
        match proof {
            WitnessProofV0::Seed { term } => {
                let registry = SeedRegistryV0::canonical();
                let rule = registry
                    .rule(*term)
                    .ok_or(WitnessErrorV0::UnknownSeed(*term))?;
                let verification = rule.verify()?;
                Ok(WitnessSummaryV0 {
                    additive_residual: verification.additive_residual,
                    multiplicative_residual: MultiplicativeResidualV0::identity(),
                    nonzero_obligations: Vec::new(),
                })
            }
            WitnessProofV0::ArithmeticTransition {
                actual_boundary,
                declared_boundary,
                before,
                after,
            } => Ok(WitnessSummaryV0 {
                additive_residual: actual_boundary.checked_sub(declared_boundary)?,
                multiplicative_residual: MultiplicativeResidualV0::from_transition(before, after)?,
                nonzero_obligations: vec![before.clone(), after.clone()],
            }),
            WitnessProofV0::Instantiate { template, children } => {
                let mut parts = Vec::with_capacity(4);
                parts.push(self.require_formed(template)?);
                for child in children {
                    parts.push(self.require_formed(child)?);
                }
                combine_summaries(parts)
            }
            WitnessProofV0::Compose {
                left,
                connector,
                right,
            } => combine_summaries([
                self.require_formed(left)?,
                self.require_formed(connector)?,
                self.require_formed(right)?,
            ]),
            WitnessProofV0::Seal { body } => {
                let summary = self.require_formed(body)?;
                if !summary.is_multiplicatively_closed() {
                    return Err(WitnessErrorV0::UnclosedMultiplicativeResidual {
                        key: body.clone(),
                        residual: summary.multiplicative_residual,
                    });
                }
                Ok(summary)
            }
        }
    }

    fn allocate_instance_id(
        &mut self,
        template: &TemplateIdV0,
    ) -> Result<InstanceIdV0, WitnessErrorV0> {
        let ordinal = self.next_instance_ordinal;
        self.next_instance_ordinal = self
            .next_instance_ordinal
            .checked_add(1)
            .ok_or(WitnessErrorV0::InstanceOrdinalOverflow)?;
        Ok(InstanceIdV0 {
            template: template.clone(),
            ordinal,
        })
    }
}

fn combine_summaries(
    summaries: impl IntoIterator<Item = WitnessSummaryV0>,
) -> Result<WitnessSummaryV0, WitnessErrorV0> {
    let mut additive_residual = BoundaryChargeV0::zero();
    let mut multiplicative_residual = MultiplicativeResidualV0::identity();
    let mut nonzero_obligations = Vec::new();
    for summary in summaries {
        additive_residual = additive_residual.checked_add(&summary.additive_residual)?;
        multiplicative_residual =
            multiplicative_residual.checked_multiply(&summary.multiplicative_residual)?;
        nonzero_obligations.extend(summary.nonzero_obligations);
    }
    Ok(WitnessSummaryV0 {
        additive_residual,
        multiplicative_residual,
        nonzero_obligations,
    })
}

/// Validate that an externally supplied proof graph is finite, closed under
/// dependencies, and acyclic. This check does not trust graph keys as semantic
/// identities.
///
/// # Errors
///
/// Returns a missing-dependency or cyclic-dependency error.
pub fn validate_dependency_graph_v0(
    graph: &BTreeMap<ArtifactKeyV0, WitnessProofV0>,
) -> Result<(), WitnessErrorV0> {
    fn visit(
        key: &ArtifactKeyV0,
        graph: &BTreeMap<ArtifactKeyV0, WitnessProofV0>,
        states: &mut BTreeMap<ArtifactKeyV0, u8>,
    ) -> Result<(), WitnessErrorV0> {
        match states.get(key).copied() {
            Some(1) => return Err(WitnessErrorV0::CyclicDependency(key.clone())),
            Some(2) => return Ok(()),
            _ => {}
        }
        let proof = graph
            .get(key)
            .ok_or_else(|| WitnessErrorV0::MissingDependency(key.clone()))?;
        states.insert(key.clone(), 1);
        for dependency in proof.dependencies() {
            if !graph.contains_key(dependency) {
                return Err(WitnessErrorV0::MissingDependency(dependency.clone()));
            }
            visit(dependency, graph, states)?;
        }
        states.insert(key.clone(), 2);
        Ok(())
    }

    let mut states = BTreeMap::new();
    for key in graph.keys() {
        visit(key, graph, &mut states)?;
    }
    Ok(())
}

#[derive(Clone, Debug, Eq, Ord, PartialEq, PartialOrd, Serialize, Deserialize)]
#[serde(transparent)]
pub struct TemplateIdV0(String);

impl TemplateIdV0 {
    /// Construct a named, versioned template identifier.
    ///
    /// # Errors
    ///
    /// Returns [`WitnessErrorV0::EmptyTemplateId`] for an empty identifier.
    pub fn new(value: impl Into<String>) -> Result<Self, WitnessErrorV0> {
        let value = value.into();
        if value.is_empty() {
            return Err(WitnessErrorV0::EmptyTemplateId);
        }
        Ok(Self(value))
    }

    #[must_use]
    pub fn as_str(&self) -> &str {
        &self.0
    }
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct HoleSpecV0 {
    pub index: u8,
    pub role: RoleV0,
    pub variable: String,
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct CellTemplateV0 {
    pub id: TemplateIdV0,
    pub holes: [HoleSpecV0; 3],
    pub result: ExactExprV0,
    pub body: ArtifactKeyV0,
}

impl CellTemplateV0 {
    /// Construct one linear triadic template.
    ///
    /// # Errors
    ///
    /// Rejects noncanonical hole order, repeated roles or variables, empty
    /// variables, and result expressions that do not use every hole exactly
    /// once.
    pub fn new(
        id: TemplateIdV0,
        holes: [HoleSpecV0; 3],
        result: ExactExprV0,
        body: ArtifactKeyV0,
    ) -> Result<Self, WitnessErrorV0> {
        let mut roles = BTreeSet::new();
        let mut variables = BTreeSet::new();
        for (expected, hole) in holes.iter().enumerate() {
            if usize::from(hole.index) != expected {
                return Err(WitnessErrorV0::InvalidHoleOrder);
            }
            if hole.variable.is_empty() {
                return Err(WitnessErrorV0::EmptyHoleVariable);
            }
            if !roles.insert(hole.role) {
                return Err(WitnessErrorV0::RepeatedHoleRole(hole.role));
            }
            if !variables.insert(hole.variable.clone()) {
                return Err(WitnessErrorV0::RepeatedHoleVariable(hole.variable.clone()));
            }
        }
        result.normalize()?;
        let occurrences = result.variable_occurrences();
        for variable in &variables {
            if occurrences.get(variable).copied() != Some(1) {
                return Err(WitnessErrorV0::NonlinearTemplateVariable(variable.clone()));
            }
        }
        if occurrences
            .keys()
            .any(|variable| !variables.contains(variable))
        {
            return Err(WitnessErrorV0::UndeclaredTemplateVariable);
        }
        Ok(Self {
            id,
            holes,
            result,
            body,
        })
    }

    /// Check the additive formation residual and enter the formed type state.
    ///
    /// # Errors
    ///
    /// Rejects an unknown or additively unbalanced body artifact.
    pub fn form(self, store: &WitnessStoreV0) -> Result<FormedCellV0, WitnessErrorV0> {
        let summary = store.summary(&self.body)?;
        if !summary.is_formed() {
            return Err(WitnessErrorV0::UnformedDependency(self.body.clone()));
        }
        Ok(FormedCellV0 {
            template: self,
            formation: summary.additive_residual,
        })
    }
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct FormedCellV0 {
    pub template: CellTemplateV0,
    pub formation: BoundaryChargeV0,
}

impl FormedCellV0 {
    /// Instantiate a formed template with fresh instance identity and explicit
    /// Rust-owned source/occurrence bindings.
    ///
    /// # Errors
    ///
    /// Rejects binding mismatch, implicit occurrence aliasing, unformed child
    /// witnesses, or instance-counter overflow.
    pub fn instantiate(
        &self,
        store: &mut WitnessStoreV0,
        checked_diagram: &DiagramValidationArtifact,
        bindings: [HoleBindingV0; 3],
        children: [ArtifactKeyV0; 3],
    ) -> Result<CellInstanceV0, WitnessErrorV0> {
        if !checked_diagram.certificate.certified() {
            return Err(WitnessErrorV0::UncertifiedBindingContext);
        }
        checked_diagram
            .result
            .validate_version()
            .map_err(|error| WitnessErrorV0::InvalidBindingContext(error.to_string()))?;
        self.validate_binding_interface(&bindings)?;
        for binding in &bindings {
            let existing = checked_diagram
                .result
                .occurrences
                .iter()
                .find(|occurrence| occurrence.id == binding.occurrence);
            if !matches!(
                existing,
                Some(occurrence)
                    if occurrence.source == binding.source && occurrence.path == binding.path
            ) {
                return Err(WitnessErrorV0::BindingNotInCheckedDiagram {
                    occurrence: binding.occurrence.clone(),
                });
            }
        }
        self.finish_instantiation(
            store,
            checked_diagram.result.function.clone(),
            bindings,
            children,
            BindingOriginV0::CheckedDiagram {
                certificate: checked_diagram.certificate.id.clone(),
            },
        )
    }

    /// Derive all three source/occurrence/path bindings from one certified
    /// compiler graft frame.
    ///
    /// This is intentionally stricter than accepting three caller-built
    /// [`HoleBindingV0`] records. Every frame entry wire must carry exactly one
    /// occurrence in V0; empty or merged lineage is reported as ambiguous.
    ///
    /// # Errors
    ///
    /// Rejects uncertified or internally unlinked compilation artifacts,
    /// missing/non-triadic frames, non-singleton entry lineage, implicit
    /// occurrence aliasing, unformed children, or instance-counter overflow.
    pub fn instantiate_from_graft(
        &self,
        store: &mut WitnessStoreV0,
        compilation: &CompilationArtifact,
        frame_id: &GraftFrameId,
        children: [ArtifactKeyV0; 3],
    ) -> Result<CellInstanceV0, WitnessErrorV0> {
        if !compilation.certificate.certified()
            || !compilation.graft_trace.certificate.certified()
        {
            return Err(WitnessErrorV0::UncertifiedGraftContext);
        }
        compilation
            .result
            .validate_version()
            .map_err(|error| WitnessErrorV0::InvalidGraftContext(error.to_string()))?;
        if compilation.certificate.boundary != compilation.result.signature {
            return Err(WitnessErrorV0::InvalidGraftContext(
                "compilation certificate boundary differs from the diagram".to_owned(),
            ));
        }

        let trace = &compilation.graft_trace.result;
        let frame_ids = trace
            .frames
            .iter()
            .map(|frame| frame.id.clone())
            .collect::<Vec<_>>();
        if frame_ids != compilation.graft_trace.certificate.frame_ids
            || frame_ids.iter().collect::<BTreeSet<_>>().len() != frame_ids.len()
        {
            return Err(WitnessErrorV0::InvalidGraftContext(
                "graft certificate frame ledger differs from the trace".to_owned(),
            ));
        }
        let root = trace
            .frames
            .iter()
            .find(|frame| frame.id == trace.root)
            .ok_or_else(|| {
                WitnessErrorV0::InvalidGraftContext("graft root frame is missing".to_owned())
            })?;
        let expected_nodes = compilation
            .result
            .nodes
            .iter()
            .map(|node| node.id)
            .collect::<Vec<_>>();
        if root.kind != GraftFrameKind::Root
            || root.parent.is_some()
            || root.caller != compilation.result.function
            || root.callee != compilation.result.function
            || root.boundary != compilation.result.signature
            || root.body_region != expected_nodes
            || root.exit_wires != compilation.result.outputs
        {
            return Err(WitnessErrorV0::InvalidGraftContext(
                "graft root does not link to the compiled diagram".to_owned(),
            ));
        }

        let frame = trace
            .frames
            .iter()
            .find(|frame| &frame.id == frame_id)
            .ok_or_else(|| WitnessErrorV0::UnknownGraftFrame(frame_id.clone()))?;
        if frame.holes.len() != 3
            || frame.entry_wires.len() != 3
            || frame.boundary.domain().ports().len() != 3
        {
            return Err(WitnessErrorV0::NonTriadicGraftFrame {
                frame: frame.id.clone(),
                holes: frame.holes.len(),
            });
        }

        let diagram_wires = compilation
            .result
            .nodes
            .iter()
            .flat_map(|node| node.inputs.iter())
            .chain(compilation.result.outputs.iter())
            .collect::<Vec<_>>();
        let mut derived = Vec::with_capacity(3);
        for (position, ((hole, entry_wire), boundary_hole)) in frame
            .holes
            .iter()
            .zip(frame.entry_wires.iter())
            .zip(frame.boundary.domain().ports())
            .enumerate()
        {
            if usize::try_from(hole.hole_index).ok() != Some(position)
                || &hole.hole != boundary_hole
                || &hole.entry_wire != entry_wire
                || !diagram_wires.contains(&entry_wire)
            {
                return Err(WitnessErrorV0::InvalidGraftContext(format!(
                    "graft frame {} has an invalid hole at position {position}",
                    frame.id
                )));
            }
            if entry_wire.lineage.len() != 1 {
                return Err(WitnessErrorV0::NonSingletonGraftLineage {
                    frame: frame.id.clone(),
                    hole: u8::try_from(position).expect("three-hole position fits in u8"),
                    occurrences: entry_wire.lineage.len(),
                });
            }
            let occurrence_id = &entry_wire.lineage[0];
            let occurrence = compilation
                .result
                .occurrences
                .iter()
                .find(|occurrence| &occurrence.id == occurrence_id)
                .ok_or_else(|| WitnessErrorV0::BindingNotInCheckedDiagram {
                    occurrence: occurrence_id.clone(),
                })?;
            let template_hole = &self.template.holes[position];
            derived.push(HoleBindingV0 {
                hole_index: template_hole.index,
                role: template_hole.role,
                source: occurrence.source.clone(),
                occurrence: occurrence.id.clone(),
                path: occurrence.path.clone(),
            });
        }
        let bindings: [HoleBindingV0; 3] = derived.try_into().map_err(|_| {
            WitnessErrorV0::InvalidGraftContext(
                "three derived graft bindings could not form an array".to_owned(),
            )
        })?;
        self.validate_binding_interface(&bindings)?;
        self.finish_instantiation(
            store,
            compilation.result.function.clone(),
            bindings,
            children,
            BindingOriginV0::GraftFrame {
                compilation_certificate: compilation.certificate.id.clone(),
                graft_certificate: compilation.graft_trace.certificate.id.clone(),
                frame: frame.id.clone(),
                scope_path: frame.scope_path.clone(),
                caller: frame.caller.clone(),
                callee: frame.callee.clone(),
            },
        )
    }

    fn validate_binding_interface(
        &self,
        bindings: &[HoleBindingV0; 3],
    ) -> Result<(), WitnessErrorV0> {
        let mut occurrences = BTreeSet::new();
        for (position, (hole, binding)) in
            self.template.holes.iter().zip(bindings.iter()).enumerate()
        {
            if usize::from(binding.hole_index) != position
                || binding.hole_index != hole.index
                || binding.role != hole.role
            {
                return Err(WitnessErrorV0::BindingMismatch { hole: hole.index });
            }
            if !occurrences.insert(binding.occurrence.clone()) {
                return Err(WitnessErrorV0::ImplicitOccurrenceAlias(
                    binding.occurrence.clone(),
                ));
            }
        }
        Ok(())
    }

    fn finish_instantiation(
        &self,
        store: &mut WitnessStoreV0,
        program: QualifiedName,
        bindings: [HoleBindingV0; 3],
        children: [ArtifactKeyV0; 3],
        binding_origin: BindingOriginV0,
    ) -> Result<CellInstanceV0, WitnessErrorV0> {
        let artifact = store.insert(WitnessProofV0::Instantiate {
            template: self.template.body.clone(),
            children,
        })?;
        let id = store.allocate_instance_id(&self.template.id)?;
        Ok(CellInstanceV0 {
            id,
            template_id: self.template.id.clone(),
            program,
            holes: self.template.holes.clone(),
            bindings,
            binding_origin,
            result: self.template.result.clone(),
            artifact,
        })
    }
}

/// Existing semantic occurrence bound to one template hole. This record never
/// allocates a source or occurrence.
#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct HoleBindingV0 {
    pub hole_index: u8,
    pub role: RoleV0,
    pub source: SourceId,
    pub occurrence: OccurrenceId,
    pub path: OccurrencePath,
}

/// Auditable origin of an instance's already-existing occurrence bindings.
/// Certificate identifiers are retained as provenance, never as program or
/// occurrence identities.
#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(tag = "kind", rename_all = "snake_case")]
pub enum BindingOriginV0 {
    CheckedDiagram {
        certificate: CertificateId,
    },
    GraftFrame {
        compilation_certificate: CertificateId,
        graft_certificate: CertificateId,
        frame: GraftFrameId,
        scope_path: GraftScopePath,
        caller: QualifiedName,
        callee: QualifiedName,
    },
}

#[derive(Clone, Debug, Eq, Ord, PartialEq, PartialOrd, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct InstanceIdV0 {
    pub template: TemplateIdV0,
    pub ordinal: u64,
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct CellInstanceV0 {
    pub id: InstanceIdV0,
    pub template_id: TemplateIdV0,
    pub program: QualifiedName,
    pub holes: [HoleSpecV0; 3],
    pub bindings: [HoleBindingV0; 3],
    pub binding_origin: BindingOriginV0,
    pub result: ExactExprV0,
    pub artifact: ArtifactKeyV0,
}

impl CellInstanceV0 {
    /// Execute one instance with exact hole values.
    ///
    /// The program result is returned separately from the multiplicative
    /// transport residual. The latter must normalize to one; the result need
    /// not be one. Zero at any retained guard or result node is a fault.
    ///
    /// # Errors
    ///
    /// Rejects an unknown/unformed artifact, a non-unit multiplicative
    /// residual, an incomplete environment, or an intermediate zero.
    pub fn execute(
        &self,
        store: &WitnessStoreV0,
        values: [BigInt; 3],
    ) -> Result<ExecutedCellV0, WitnessErrorV0> {
        let summary = store.require_formed(&self.artifact)?;
        if !summary.is_multiplicatively_closed() {
            return Err(WitnessErrorV0::UnclosedMultiplicativeResidual {
                key: self.artifact.clone(),
                residual: summary.multiplicative_residual,
            });
        }
        let environment = self
            .holes
            .iter()
            .zip(values)
            .map(|(hole, value)| (hole.variable.clone(), value))
            .collect::<BTreeMap<_, _>>();
        for obligation in &summary.nonzero_obligations {
            obligation.evaluate_guarded(&environment)?;
        }
        let value = self.result.evaluate_guarded(&environment)?;
        Ok(ExecutedCellV0 {
            instance: self.id.clone(),
            artifact: self.artifact.clone(),
            value,
        })
    }
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct ExecutedCellV0 {
    pub instance: InstanceIdV0,
    pub artifact: ArtifactKeyV0,
    pub value: BigInt,
}

#[derive(Debug, Error)]
pub enum WitnessErrorV0 {
    #[error(transparent)]
    Arithmetic(#[from] ArithmeticErrorV0),
    #[error(transparent)]
    Boundary(#[from] BoundaryErrorV0),
    #[error(transparent)]
    Seed(#[from] SeedErrorV0),
    #[error("witness artifact JSON error: {0}")]
    Json(#[from] serde_json::Error),
    #[error("artifact cache key must not be empty")]
    EmptyArtifactKey,
    #[error("template identifier must not be empty")]
    EmptyTemplateId,
    #[error("template hole variable must not be empty")]
    EmptyHoleVariable,
    #[error("template holes must be ordered exactly 0, 1, 2")]
    InvalidHoleOrder,
    #[error("template repeats role {0:?}")]
    RepeatedHoleRole(RoleV0),
    #[error("template repeats variable {0:?}")]
    RepeatedHoleVariable(String),
    #[error("template variable {0:?} must occur exactly once")]
    NonlinearTemplateVariable(String),
    #[error("template result mentions a variable not declared by its holes")]
    UndeclaredTemplateVariable,
    #[error("missing witness dependency {0}")]
    MissingDependency(ArtifactKeyV0),
    #[error("cyclic witness dependency at {0}")]
    CyclicDependency(ArtifactKeyV0),
    #[error("artifact digest collision at {0}")]
    ArtifactHashCollision(ArtifactKeyV0),
    #[error("unknown canonical seed {0:?}")]
    UnknownSeed(TermGlyphV0),
    #[error("witness dependency {0} has a nonzero additive residual")]
    UnformedDependency(ArtifactKeyV0),
    #[error("artifact {key} has a non-unit multiplicative residual {residual:?}")]
    UnclosedMultiplicativeResidual {
        key: ArtifactKeyV0,
        residual: MultiplicativeResidualV0,
    },
    #[error("hole {hole} binding does not match its template interface")]
    BindingMismatch { hole: u8 },
    #[error("the occurrence-binding context is not a certified diagram")]
    UncertifiedBindingContext,
    #[error("invalid occurrence-binding context: {0}")]
    InvalidBindingContext(String),
    #[error("the graft-binding context is not a certified compilation")]
    UncertifiedGraftContext,
    #[error("invalid graft-binding context: {0}")]
    InvalidGraftContext(String),
    #[error("graft frame {0} is not present in the certified trace")]
    UnknownGraftFrame(GraftFrameId),
    #[error("graft frame {frame} has {holes} holes; exactly three are required")]
    NonTriadicGraftFrame { frame: GraftFrameId, holes: usize },
    #[error(
        "graft frame {frame} hole {hole} has {occurrences} lineage occurrences; exactly one is required"
    )]
    NonSingletonGraftLineage {
        frame: GraftFrameId,
        hole: u8,
        occurrences: usize,
    },
    #[error(
        "occurrence {occurrence} is not present with the declared source and path in the checked diagram"
    )]
    BindingNotInCheckedDiagram { occurrence: OccurrenceId },
    #[error("occurrence {0} was implicitly bound to more than one hole")]
    ImplicitOccurrenceAlias(OccurrenceId),
    #[error("instance ordinal overflow")]
    InstanceOrdinalOverflow,
}
