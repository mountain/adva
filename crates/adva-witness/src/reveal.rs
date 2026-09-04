use crate::{
    AdvaDocumentV0, ArtifactKeyV0, FrameIdV0, FrameRelationCellV0, FrameRelationErrorV0,
    RelationFillingV0, RelationProfileV0,
};
use serde::{Deserialize, Serialize};
use std::collections::BTreeSet;
use std::fs;
use std::path::{Path, PathBuf};
use thiserror::Error;

/// Schema identifier for the first bounded `M6` reveal witness.
pub const REVEAL_WITNESS_SCHEMA_V0: &str = "adva.m6-reveal-witness.research";

/// Research artifact version. This is not `adva.ir` version one.
pub const REVEAL_WITNESS_VERSION_V0: u32 = 0;

const REQUIRED_M6_OCCURRENCES: usize = 6;
const OPEN_FILLER_KEY: &str = "experiment:first:m6-semantic-filler-required";

/// The three observer coordinates used by the first naming experiment.
#[derive(Clone, Copy, Debug, Eq, Ord, PartialEq, PartialOrd, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum ObserverDomainV0 {
    Time,
    Space,
    Construction,
}

/// One provisional human name for one directed cross-domain transport.
///
/// The name resolves an entry point only. It is not a semantic identity and
/// never replaces the document-local frame coordinate.
#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct DomainTransportNameV0 {
    pub name: String,
    pub from: ObserverDomainV0,
    pub to: ObserverDomainV0,
}

/// Two directed three-edge cycles used to calibrate the six off-diagonal
/// transports between time, space, and construction.
#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct M6NamingPlanV0 {
    pub forward: [DomainTransportNameV0; 3],
    pub conjugate: [DomainTransportNameV0; 3],
}

impl M6NamingPlanV0 {
    /// The first explicitly injected naming proposal.
    ///
    /// These names are an experimental observer vocabulary, not additions to
    /// the stable language or claims that the transports already have the
    /// proposed semantics.
    #[must_use]
    pub fn first_calibration() -> Self {
        Self {
            forward: [
                transport_name("run", ObserverDomainV0::Construction, ObserverDomainV0::Time),
                transport_name("reveal", ObserverDomainV0::Time, ObserverDomainV0::Space),
                transport_name("name", ObserverDomainV0::Space, ObserverDomainV0::Construction),
            ],
            conjugate: [
                transport_name(
                    "instantiate",
                    ObserverDomainV0::Construction,
                    ObserverDomainV0::Space,
                ),
                transport_name("resume", ObserverDomainV0::Space, ObserverDomainV0::Time),
                transport_name(
                    "compile",
                    ObserverDomainV0::Time,
                    ObserverDomainV0::Construction,
                ),
            ],
        }
    }

    fn check(&self) -> Result<(), RevealErrorV0> {
        let names = self
            .forward
            .iter()
            .chain(self.conjugate.iter())
            .collect::<Vec<_>>();
        if names.iter().any(|transport| transport.name.is_empty()) {
            return Err(RevealErrorV0::InvalidNamingPlan(
                "transport names must be nonempty",
            ));
        }
        if names
            .iter()
            .map(|transport| transport.name.as_str())
            .collect::<BTreeSet<_>>()
            .len()
            != REQUIRED_M6_OCCURRENCES
        {
            return Err(RevealErrorV0::InvalidNamingPlan(
                "the six transport names must be distinct",
            ));
        }
        let pairs = names
            .iter()
            .map(|transport| (transport.from, transport.to))
            .collect::<BTreeSet<_>>();
        if pairs.len() != REQUIRED_M6_OCCURRENCES
            || pairs.iter().any(|(from, to)| from == to)
        {
            return Err(RevealErrorV0::InvalidNamingPlan(
                "the plan must cover all six off-diagonal directed domain pairs",
            ));
        }
        check_cycle(&self.forward)?;
        check_cycle(&self.conjugate)?;
        Ok(())
    }
}

/// One injected name after resolution to its authoritative frame coordinate.
#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct ResolvedDomainTransportV0 {
    pub name: String,
    pub frame: FrameIdV0,
    pub from: ObserverDomainV0,
    pub to: ObserverDomainV0,
}

/// Why the first bounded reveal still exposes an open question.
#[derive(Clone, Copy, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum RevealQuestionKindV0 {
    FuelBoundary,
    RelationFiller,
}

/// One explicitly retained question rather than a fabricated result.
#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct RevealQuestionV0 {
    pub kind: RevealQuestionKindV0,
    pub detail: String,
    pub residual: Option<ArtifactKeyV0>,
}

/// Whether this finite observer reached the complete six-frame boundary.
#[derive(Clone, Copy, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum RevealRunStateV0 {
    Completed,
    Suspended,
}

/// The first self-describing result emitted by running `reveal.adva`.
///
/// Completion means that all six named frame occurrences were inspected. The
/// embedded relation remains open until a separate semantic filler is supplied.
#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct RevealWitnessV0 {
    pub schema: String,
    pub version: u32,
    pub source_document_digest: String,
    pub fuel_requested: u64,
    pub fuel_used: u64,
    pub state: RevealRunStateV0,
    pub forward: [ResolvedDomainTransportV0; 3],
    pub conjugate: [ResolvedDomainTransportV0; 3],
    pub observed: Vec<String>,
    pub remaining: Vec<String>,
    pub questions: Vec<RevealQuestionV0>,
    pub relation: Option<FrameRelationCellV0>,
}

/// Receipt for one completed atomic reveal-witness save.
#[derive(Clone, Debug, Eq, PartialEq)]
pub struct RevealSaveReceiptV0 {
    pub path: PathBuf,
    pub witness_digest: String,
    pub bytes_written: u64,
}

impl RevealWitnessV0 {
    /// Decode and structurally recheck one reveal witness.
    ///
    /// This does not replay the source document or fill the open relation.
    ///
    /// # Errors
    ///
    /// Rejects malformed JSON or inconsistent finite-run bookkeeping.
    pub fn from_json(source: &str) -> Result<Self, RevealErrorV0> {
        let witness: Self = serde_json::from_str(source)
            .map_err(|error| RevealErrorV0::Json(error.to_string()))?;
        witness.check()?;
        Ok(witness)
    }

    /// Encode one structurally checked witness deterministically.
    ///
    /// # Errors
    ///
    /// Rejects inconsistent bookkeeping or serialization failure.
    pub fn to_json(&self) -> Result<String, RevealErrorV0> {
        self.check()?;
        serde_json::to_string_pretty(self).map_err(|error| RevealErrorV0::Json(error.to_string()))
    }

    /// Recheck the self-contained portion of a reveal witness.
    ///
    /// # Errors
    ///
    /// Rejects the wrong schema, malformed naming cycles, inconsistent fuel
    /// accounting, or a relation that no longer agrees with the named frames.
    pub fn check(&self) -> Result<(), RevealErrorV0> {
        if self.schema != REVEAL_WITNESS_SCHEMA_V0 || self.version != REVEAL_WITNESS_VERSION_V0 {
            return Err(RevealErrorV0::InvalidWitness(
                "unsupported reveal witness schema or version",
            ));
        }
        if !self.source_document_digest.starts_with("blake3:")
            || self.source_document_digest.len() != "blake3:".len() + 64
        {
            return Err(RevealErrorV0::InvalidWitness(
                "the source document digest must be a BLAKE3 coordinate",
            ));
        }
        let plan = naming_plan_from_resolved(&self.forward, &self.conjugate);
        plan.check()?;
        let schedule = self
            .forward
            .iter()
            .chain(self.conjugate.iter())
            .collect::<Vec<_>>();
        if schedule
            .iter()
            .map(|transport| transport.frame)
            .collect::<BTreeSet<_>>()
            .len()
            != REQUIRED_M6_OCCURRENCES
        {
            return Err(RevealErrorV0::InvalidWitness(
                "the six names must resolve to six distinct frame coordinates",
            ));
        }
        let used = usize::try_from(self.fuel_used).map_err(|_| {
            RevealErrorV0::InvalidWitness("fuel used does not fit the current platform")
        })?;
        if self.fuel_used > self.fuel_requested
            || used > REQUIRED_M6_OCCURRENCES
            || self.observed
                != schedule[..used]
                    .iter()
                    .map(|transport| transport.name.clone())
                    .collect::<Vec<_>>()
            || self.remaining
                != schedule[used..]
                    .iter()
                    .map(|transport| transport.name.clone())
                    .collect::<Vec<_>>()
        {
            return Err(RevealErrorV0::InvalidWitness(
                "finite schedule bookkeeping is inconsistent",
            ));
        }
        match self.state {
            RevealRunStateV0::Completed => self.check_completed(&schedule),
            RevealRunStateV0::Suspended => self.check_suspended(),
        }
    }

    fn check_completed(
        &self,
        schedule: &[&ResolvedDomainTransportV0],
    ) -> Result<(), RevealErrorV0> {
        if self.fuel_used != REQUIRED_M6_OCCURRENCES as u64 || !self.remaining.is_empty() {
            return Err(RevealErrorV0::InvalidWitness(
                "a completed reveal must observe all six frame occurrences",
            ));
        }
        let relation = self.relation.as_ref().ok_or(RevealErrorV0::InvalidWitness(
            "a completed reveal must retain its relation cell",
        ))?;
        if relation.document_digest != self.source_document_digest {
            return Err(RevealErrorV0::InvalidWitness(
                "the relation and reveal witness use different document digests",
            ));
        }
        let named_frames = schedule
            .iter()
            .map(|transport| transport.frame)
            .collect::<Vec<_>>();
        let relation_frames = relation
            .left
            .steps
            .iter()
            .chain(relation.right.steps.iter())
            .map(|step| step.frame)
            .collect::<Vec<_>>();
        let expected_residual = ArtifactKeyV0::cache_label(OPEN_FILLER_KEY)
            .expect("the static reveal residual is nonempty");
        if named_frames != relation_frames
            || relation.relation.profile != RelationProfileV0::braid_m6()
            || relation.relation.check().is_err()
            || relation.relation.filling
                != (RelationFillingV0::Open {
                    residual: expected_residual.clone(),
                })
        {
            return Err(RevealErrorV0::InvalidWitness(
                "the retained relation does not match the named M6 boundary",
            ));
        }
        if self.questions
            != vec![RevealQuestionV0 {
                kind: RevealQuestionKindV0::RelationFiller,
                detail: "the M6 boundary is formed, but its semantic filler has not been established"
                    .to_owned(),
                residual: Some(expected_residual),
            }]
        {
            return Err(RevealErrorV0::InvalidWitness(
                "a completed first reveal must retain the semantic filler question",
            ));
        }
        Ok(())
    }

    fn check_suspended(&self) -> Result<(), RevealErrorV0> {
        if self.fuel_used >= REQUIRED_M6_OCCURRENCES as u64
            || self.relation.is_some()
            || self.questions.len() != 1
            || self.questions[0].kind != RevealQuestionKindV0::FuelBoundary
            || self.questions[0].residual.is_some()
        {
            return Err(RevealErrorV0::InvalidWitness(
                "a suspended reveal must retain only its fuel-boundary question",
            ));
        }
        Ok(())
    }
}

/// Run one finite named `M6` reveal over a validated neutral document.
///
/// The six names are presentation labels only. The relation checker consumes
/// resolved frame IDs, exact handoffs, common endpoints, and frame mechanisms.
///
/// # Errors
///
/// Rejects an invalid naming plan, document, entry-point reference, or `M6`
/// formation.
pub fn run_m6_reveal_v0(
    document: &AdvaDocumentV0,
    plan: M6NamingPlanV0,
    fuel: u64,
) -> Result<RevealWitnessV0, RevealErrorV0> {
    plan.check()?;
    let source_document_digest = document
        .validated_digest()
        .map_err(|error| RevealErrorV0::InvalidDocument(error.to_string()))?;
    let forward = resolve_cycle(document, &plan.forward)?;
    let conjugate = resolve_cycle(document, &plan.conjugate)?;
    let schedule = forward
        .iter()
        .chain(conjugate.iter())
        .collect::<Vec<_>>();
    if schedule
        .iter()
        .map(|transport| transport.frame)
        .collect::<BTreeSet<_>>()
        .len()
        != REQUIRED_M6_OCCURRENCES
    {
        return Err(RevealErrorV0::InvalidNamingPlan(
            "the six names must resolve to six distinct frame coordinates",
        ));
    }
    let fuel_used = fuel.min(REQUIRED_M6_OCCURRENCES as u64);
    let used = usize::try_from(fuel_used).expect("fuel is bounded by six");
    let observed = schedule[..used]
        .iter()
        .map(|transport| transport.name.clone())
        .collect::<Vec<_>>();
    let remaining = schedule[used..]
        .iter()
        .map(|transport| transport.name.clone())
        .collect::<Vec<_>>();

    let (state, questions, relation) = if used < REQUIRED_M6_OCCURRENCES {
        (
            RevealRunStateV0::Suspended,
            vec![RevealQuestionV0 {
                kind: RevealQuestionKindV0::FuelBoundary,
                detail: format!(
                    "finite observer stopped after {used} of {REQUIRED_M6_OCCURRENCES} named occurrences"
                ),
                residual: None,
            }],
            None,
        )
    } else {
        let residual = ArtifactKeyV0::cache_label(OPEN_FILLER_KEY)
            .expect("the static reveal residual is nonempty");
        let forward_frames = forward.map(|transport| transport.frame);
        let conjugate_frames = conjugate.map(|transport| transport.frame);
        let relation = FrameRelationCellV0::derive(
            document,
            RelationProfileV0::braid_m6(),
            &forward_frames,
            &conjugate_frames,
            RelationFillingV0::Open {
                residual: residual.clone(),
            },
        )?;
        (
            RevealRunStateV0::Completed,
            vec![RevealQuestionV0 {
                kind: RevealQuestionKindV0::RelationFiller,
                detail: "the M6 boundary is formed, but its semantic filler has not been established"
                    .to_owned(),
                residual: Some(residual),
            }],
            Some(relation),
        )
    };
    let witness = RevealWitnessV0 {
        schema: REVEAL_WITNESS_SCHEMA_V0.to_owned(),
        version: REVEAL_WITNESS_VERSION_V0,
        source_document_digest,
        fuel_requested: fuel,
        fuel_used,
        state,
        forward,
        conjugate,
        observed,
        remaining,
        questions,
        relation,
    };
    witness.check()?;
    Ok(witness)
}

/// Atomically persist one checked reveal witness with the common `.adva`
/// suffix.
///
/// # Errors
///
/// Rejects an invalid witness, a non-`.adva` path, or an I/O failure.
pub fn save_reveal_witness_v0(
    path: impl AsRef<Path>,
    witness: &RevealWitnessV0,
) -> Result<RevealSaveReceiptV0, RevealErrorV0> {
    let path = path.as_ref();
    crate::persistence::require_adva_extension(path)
        .map_err(|error| RevealErrorV0::Persistence(error.to_string()))?;
    let encoded = format!("{}\n", witness.to_json()?);
    crate::persistence::write_atomically(path, encoded.as_bytes())
        .map_err(|error| RevealErrorV0::Persistence(error.to_string()))?;
    Ok(RevealSaveReceiptV0 {
        path: path.to_path_buf(),
        witness_digest: format!("blake3:{}", blake3::hash(encoded.as_bytes()).to_hex()),
        bytes_written: u64::try_from(encoded.len()).unwrap_or(u64::MAX),
    })
}

/// Load and structurally recheck one persisted reveal witness.
///
/// # Errors
///
/// Rejects a non-`.adva` path, unreadable content, malformed JSON, or
/// inconsistent witness bookkeeping.
pub fn load_reveal_witness_v0(
    path: impl AsRef<Path>,
) -> Result<RevealWitnessV0, RevealErrorV0> {
    let path = path.as_ref();
    crate::persistence::require_adva_extension(path)
        .map_err(|error| RevealErrorV0::Persistence(error.to_string()))?;
    let source = fs::read_to_string(path).map_err(|error| RevealErrorV0::Io {
        path: path.to_path_buf(),
        detail: error.to_string(),
    })?;
    RevealWitnessV0::from_json(&source)
}

fn transport_name(
    name: &str,
    from: ObserverDomainV0,
    to: ObserverDomainV0,
) -> DomainTransportNameV0 {
    DomainTransportNameV0 {
        name: name.to_owned(),
        from,
        to,
    }
}

fn check_cycle(cycle: &[DomainTransportNameV0; 3]) -> Result<(), RevealErrorV0> {
    if cycle[0].to != cycle[1].from
        || cycle[1].to != cycle[2].from
        || cycle[2].to != cycle[0].from
    {
        return Err(RevealErrorV0::InvalidNamingPlan(
            "each three-name side must form a directed cycle",
        ));
    }
    Ok(())
}

fn resolve_cycle(
    document: &AdvaDocumentV0,
    cycle: &[DomainTransportNameV0; 3],
) -> Result<[ResolvedDomainTransportV0; 3], RevealErrorV0> {
    let resolved = cycle
        .iter()
        .map(|named| {
            let entrypoint = document
                .entrypoints
                .iter()
                .find(|entrypoint| entrypoint.name == named.name)
                .ok_or_else(|| RevealErrorV0::UnknownEntryPoint(named.name.clone()))?;
            Ok(ResolvedDomainTransportV0 {
                name: named.name.clone(),
                frame: entrypoint.frame,
                from: named.from,
                to: named.to,
            })
        })
        .collect::<Result<Vec<_>, RevealErrorV0>>()?;
    resolved
        .try_into()
        .map_err(|_| RevealErrorV0::InvalidNamingPlan("each M6 side must contain three names"))
}

fn naming_plan_from_resolved(
    forward: &[ResolvedDomainTransportV0; 3],
    conjugate: &[ResolvedDomainTransportV0; 3],
) -> M6NamingPlanV0 {
    M6NamingPlanV0 {
        forward: forward.clone().map(|transport| DomainTransportNameV0 {
            name: transport.name,
            from: transport.from,
            to: transport.to,
        }),
        conjugate: conjugate.clone().map(|transport| DomainTransportNameV0 {
            name: transport.name,
            from: transport.from,
            to: transport.to,
        }),
    }
}

#[derive(Clone, Debug, Eq, Error, PartialEq)]
pub enum RevealErrorV0 {
    #[error("invalid M6 naming plan: {0}")]
    InvalidNamingPlan(&'static str),
    #[error("invalid neutral Adva document: {0}")]
    InvalidDocument(String),
    #[error("the naming plan references unknown entry point {0:?}")]
    UnknownEntryPoint(String),
    #[error("invalid reveal witness: {0}")]
    InvalidWitness(&'static str),
    #[error("reveal witness JSON error: {0}")]
    Json(String),
    #[error("reveal witness persistence error: {0}")]
    Persistence(String),
    #[error("I/O error at {path:?}: {detail}")]
    Io { path: PathBuf, detail: String },
    #[error(transparent)]
    Relation(#[from] FrameRelationErrorV0),
}
