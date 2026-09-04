use crate::{
    AdvaDocumentV0, ArtifactKeyV0, CarrierIdV0, FrameIdV0, FrameInputV0, InputLabelV0, MechanismV0,
};
use adva_ir::CheckStatus;
use serde::{Deserialize, Serialize};
use std::collections::BTreeSet;
use thiserror::Error;

/// The two bounded rank-two relation cells currently admitted by the
/// research companion.
///
/// A kind names a relation between two raw paths. It is not a declaration
/// that the paths are definitionally or semantically equal.
#[derive(Clone, Copy, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum RelationKindV0 {
    Interchange,
    Braid,
}

/// The finite boundary retained by one relation cell.
#[derive(Clone, Copy, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum RelationBoundaryShapeV0 {
    Q4,
    M6,
}

impl RelationBoundaryShapeV0 {
    #[must_use]
    pub const fn occurrence_count(self) -> u8 {
        match self {
            Self::Q4 => 4,
            Self::M6 => 6,
        }
    }
}

/// The non-group process presentation retained before inverse relations are
/// introduced.
#[derive(Clone, Copy, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum ProcessLiftV0 {
    TraceMonoid,
    PositiveBraidMonoid,
}

/// A finite Coxeter quotient used only as a checked state-space view.
///
/// This is neither the raw history algebra nor the full geometric symmetry
/// group of the displayed polygon.
#[derive(Clone, Copy, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum CoxeterShadowV0 {
    KleinFour,
    SymmetricThree,
}

/// One coherent relation profile across boundary, process, and finite-shadow
/// readings.
#[derive(Clone, Copy, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct RelationProfileV0 {
    pub kind: RelationKindV0,
    pub boundary: RelationBoundaryShapeV0,
    pub process_lift: ProcessLiftV0,
    pub coxeter_shadow: CoxeterShadowV0,
}

impl RelationProfileV0 {
    #[must_use]
    pub const fn interchange_q4() -> Self {
        Self {
            kind: RelationKindV0::Interchange,
            boundary: RelationBoundaryShapeV0::Q4,
            process_lift: ProcessLiftV0::TraceMonoid,
            coxeter_shadow: CoxeterShadowV0::KleinFour,
        }
    }

    #[must_use]
    pub const fn braid_m6() -> Self {
        Self {
            kind: RelationKindV0::Braid,
            boundary: RelationBoundaryShapeV0::M6,
            process_lift: ProcessLiftV0::PositiveBraidMonoid,
            coxeter_shadow: CoxeterShadowV0::SymmetricThree,
        }
    }

    fn check(self) -> Result<(), RelationFormationErrorV0> {
        let expected = match self.kind {
            RelationKindV0::Interchange => Self::interchange_q4(),
            RelationKindV0::Braid => Self::braid_m6(),
        };
        if self == expected {
            Ok(())
        } else {
            Err(RelationFormationErrorV0::IncoherentProfile {
                actual: self,
                expected,
            })
        }
    }
}

/// One caller-named generator in a raw relation path.
///
/// The label is a research coordinate only. It does not allocate an Adva IR
/// operation, source, occurrence, or group element.
#[derive(Clone, Debug, Eq, Ord, PartialEq, PartialOrd, Serialize, Deserialize)]
#[serde(transparent)]
pub struct RelationGeneratorV0(String);

impl RelationGeneratorV0 {
    /// Construct a nonempty generator label.
    ///
    /// # Errors
    ///
    /// Rejects the empty string.
    pub fn new(value: impl Into<String>) -> Result<Self, RelationFormationErrorV0> {
        let value = value.into();
        if value.is_empty() {
            return Err(RelationFormationErrorV0::EmptyGenerator);
        }
        Ok(Self(value))
    }

    #[must_use]
    pub fn as_str(&self) -> &str {
        &self.0
    }

    fn check(&self) -> Result<(), RelationFormationErrorV0> {
        if self.0.is_empty() {
            Err(RelationFormationErrorV0::EmptyGenerator)
        } else {
            Ok(())
        }
    }
}

/// One nonempty raw path. Path order remains authoritative after a relation
/// cell is formed.
#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct RelationPathV0 {
    steps: Vec<RelationGeneratorV0>,
}

impl RelationPathV0 {
    /// Construct and check one finite raw path.
    ///
    /// # Errors
    ///
    /// Rejects an empty path or an empty generator label.
    pub fn new(
        steps: impl IntoIterator<Item = RelationGeneratorV0>,
    ) -> Result<Self, RelationFormationErrorV0> {
        let path = Self {
            steps: steps.into_iter().collect(),
        };
        path.check()?;
        Ok(path)
    }

    #[must_use]
    pub fn steps(&self) -> &[RelationGeneratorV0] {
        &self.steps
    }

    fn check(&self) -> Result<(), RelationFormationErrorV0> {
        if self.steps.is_empty() {
            return Err(RelationFormationErrorV0::EmptyPath);
        }
        self.steps.iter().try_for_each(RelationGeneratorV0::check)
    }
}

/// Which explicitly witnessed orientation may be read as a transport.
#[derive(Clone, Copy, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum RelationOrientationV0 {
    LeftToRight,
    RightToLeft,
}

/// Whether the boundary remains open or cites one explicit directional
/// filler.
///
/// A witness key is only a cache reference. Formation does not replay it or
/// prove semantic equality. A reverse transport always requires an explicit
/// reverse-oriented filler.
#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(tag = "state", rename_all = "snake_case")]
pub enum RelationFillingV0 {
    Open {
        residual: ArtifactKeyV0,
    },
    Filled {
        orientation: RelationOrientationV0,
        witness: ArtifactKeyV0,
        retained_residual: Option<ArtifactKeyV0>,
    },
}

/// One proof-relevant relation boundary over two still-distinct raw paths.
#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct RelationCellV0 {
    pub profile: RelationProfileV0,
    pub left: RelationPathV0,
    pub right: RelationPathV0,
    pub filling: RelationFillingV0,
}

impl RelationCellV0 {
    /// Construct and check one bounded relation cell.
    ///
    /// # Errors
    ///
    /// Rejects an incoherent profile, malformed relation words, identical raw
    /// histories, or empty witness/residual references.
    pub fn new(
        profile: RelationProfileV0,
        left: RelationPathV0,
        right: RelationPathV0,
        filling: RelationFillingV0,
    ) -> Result<Self, RelationFormationErrorV0> {
        let cell = Self {
            profile,
            left,
            right,
            filling,
        };
        cell.check()?;
        Ok(cell)
    }

    /// Recheck formation and return its narrow audit record.
    ///
    /// This certificate checks syntax and explicit references only. It does
    /// not check that the named filler is a valid program transformation.
    ///
    /// # Errors
    ///
    /// Rejects every malformed invariant accepted by deserialization or
    /// direct struct construction.
    pub fn check(&self) -> Result<RelationFormationCertificateV0, RelationFormationErrorV0> {
        self.profile.check()?;
        self.left.check()?;
        self.right.check()?;
        if self.left == self.right {
            return Err(RelationFormationErrorV0::IdenticalRawPaths);
        }
        match self.profile.kind {
            RelationKindV0::Interchange => check_interchange(&self.left, &self.right)?,
            RelationKindV0::Braid => check_braid(&self.left, &self.right)?,
        }
        check_filling(&self.filling)?;
        Ok(RelationFormationCertificateV0 {
            profile: self.profile,
            boundary_occurrences: self.profile.boundary.occurrence_count(),
            coherent_profile: CheckStatus::Checked,
            canonical_relation_word: CheckStatus::Checked,
            distinct_raw_paths: CheckStatus::Checked,
            explicit_filling_state: CheckStatus::Checked,
        })
    }

    /// Read the explicitly oriented filler as a transport record.
    ///
    /// # Errors
    ///
    /// Open boundaries cannot transport. This method never manufactures the
    /// reverse orientation and never interprets transport as conjugacy.
    pub fn transport(&self) -> Result<RelationTransportV0, RelationFormationErrorV0> {
        let formation = self.check()?;
        let RelationFillingV0::Filled {
            orientation,
            witness,
            retained_residual,
        } = &self.filling
        else {
            return Err(RelationFormationErrorV0::OpenBoundaryCannotTransport);
        };
        let (from, to) = match orientation {
            RelationOrientationV0::LeftToRight => (self.left.clone(), self.right.clone()),
            RelationOrientationV0::RightToLeft => (self.right.clone(), self.left.clone()),
        };
        Ok(RelationTransportV0 {
            formation,
            orientation: *orientation,
            from,
            to,
            witness: witness.clone(),
            retained_residual: retained_residual.clone(),
        })
    }
}

/// Narrow formation audit for one `Q4` or `M6` relation cell.
#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct RelationFormationCertificateV0 {
    pub profile: RelationProfileV0,
    pub boundary_occurrences: u8,
    pub coherent_profile: CheckStatus,
    pub canonical_relation_word: CheckStatus,
    pub distinct_raw_paths: CheckStatus,
    pub explicit_filling_state: CheckStatus,
}

/// One directional transport record derived from an explicitly filled cell.
///
/// This is not inverse execution, program equality, or a general conjugacy
/// certificate.
#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct RelationTransportV0 {
    pub formation: RelationFormationCertificateV0,
    pub orientation: RelationOrientationV0,
    pub from: RelationPathV0,
    pub to: RelationPathV0,
    pub witness: ArtifactKeyV0,
    pub retained_residual: Option<ArtifactKeyV0>,
}

/// One complete recorded three-port output boundary.
///
/// The labels retain their output reading. A later frame may read the same
/// three carrier coordinates under a separately derived input permutation.
#[derive(Clone, Copy, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct RecordedFrameOutputV0 {
    pub history: CarrierIdV0,
    pub result: CarrierIdV0,
    pub evidence: CarrierIdV0,
}

impl RecordedFrameOutputV0 {
    const fn references(self) -> [CarrierIdV0; 3] {
        [self.history, self.result, self.evidence]
    }
}

/// The explicit permutation by which one recorded output is read as the next
/// frame's input.
#[derive(Clone, Copy, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct FrameHandoffRouteV0 {
    pub history_to: InputLabelV0,
    pub result_to: InputLabelV0,
    pub evidence_to: InputLabelV0,
}

/// One full three-carrier handoff between adjacent document-local frame
/// occurrences.
#[derive(Clone, Copy, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct FrameHandoffV0 {
    pub from: FrameIdV0,
    pub to: FrameIdV0,
    pub route: FrameHandoffRouteV0,
}

/// One document-local transition occurrence retained in a relation path.
///
/// `FrameIdV0` is a storage coordinate, not an `adva_ir::OccurrenceId`. The
/// relation generator is derived from the frame mechanism rather than from a
/// caller-supplied label.
#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct FrameRelationStepV0 {
    pub frame: FrameIdV0,
    pub mechanism: MechanismV0,
    pub input: FrameInputV0,
    pub output: RecordedFrameOutputV0,
}

/// One finite path through recorded transition frames in one validated
/// neutral `.adva` document.
#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct FrameRelationPathV0 {
    pub steps: Vec<FrameRelationStepV0>,
    pub handoffs: Vec<FrameHandoffV0>,
    pub start: FrameInputV0,
    pub end: RecordedFrameOutputV0,
    pub mechanism_path: RelationPathV0,
}

impl FrameRelationPathV0 {
    /// Derive one path from explicit document-local frame occurrences.
    ///
    /// Every frame must have a complete recorded output, every adjacent pair
    /// must reuse exactly the preceding three output carriers, and no frame
    /// occurrence may be repeated. The input permutation is derived and
    /// retained rather than guessed by a CLI default.
    ///
    /// # Errors
    ///
    /// Rejects an invalid document, an empty or repeated frame path, an
    /// unknown or ready frame, or a non-bijective adjacent handoff.
    pub fn derive(
        document: &AdvaDocumentV0,
        frames: &[FrameIdV0],
    ) -> Result<Self, FrameRelationErrorV0> {
        document
            .validated_digest()
            .map_err(|error| FrameRelationErrorV0::InvalidDocument(error.to_string()))?;
        derive_frame_path(document, frames)
    }
}

/// A `Q4` or `M6` relation whose path words and endpoints are derived from one
/// validated neutral document.
#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct FrameRelationCellV0 {
    pub document_digest: String,
    pub left: FrameRelationPathV0,
    pub right: FrameRelationPathV0,
    pub relation: RelationCellV0,
    pub certificate: FrameRelationCertificateV0,
}

impl FrameRelationCellV0 {
    /// Derive a bounded relation cell from two explicit frame paths.
    ///
    /// Both paths must start at the same labelled input boundary and finish at
    /// the same labelled recorded-output boundary. Relation words come only
    /// from `compute/verify/learn` mechanism labels. Method carriers remain
    /// ordinary inputs and are never reinterpreted as edge generators.
    ///
    /// # Errors
    ///
    /// Rejects every path error, unequal endpoints, or a mechanism word that
    /// does not form the requested `Q4` or `M6` profile.
    pub fn derive(
        document: &AdvaDocumentV0,
        profile: RelationProfileV0,
        left_frames: &[FrameIdV0],
        right_frames: &[FrameIdV0],
        filling: RelationFillingV0,
    ) -> Result<Self, FrameRelationErrorV0> {
        let document_digest = document
            .validated_digest()
            .map_err(|error| FrameRelationErrorV0::InvalidDocument(error.to_string()))?;
        let left = derive_frame_path(document, left_frames)?;
        let right = derive_frame_path(document, right_frames)?;
        if left.start != right.start {
            return Err(FrameRelationErrorV0::DifferentStartBoundary);
        }
        if left.end != right.end {
            return Err(FrameRelationErrorV0::DifferentEndBoundary);
        }
        let relation = RelationCellV0::new(
            profile,
            left.mechanism_path.clone(),
            right.mechanism_path.clone(),
            filling,
        )?;
        let formation = relation.check()?;
        Ok(Self {
            document_digest: document_digest.clone(),
            left,
            right,
            relation,
            certificate: FrameRelationCertificateV0 {
                document_digest,
                document_graph: CheckStatus::Checked,
                frame_occurrences: CheckStatus::Checked,
                complete_handoffs: CheckStatus::Checked,
                common_endpoints: CheckStatus::Checked,
                relation_formation: formation,
            },
        })
    }
}

/// Narrow audit record for a relation derived from stored transition frames.
#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct FrameRelationCertificateV0 {
    pub document_digest: String,
    pub document_graph: CheckStatus,
    pub frame_occurrences: CheckStatus,
    pub complete_handoffs: CheckStatus,
    pub common_endpoints: CheckStatus,
    pub relation_formation: RelationFormationCertificateV0,
}

fn derive_frame_path(
    document: &AdvaDocumentV0,
    frames: &[FrameIdV0],
) -> Result<FrameRelationPathV0, FrameRelationErrorV0> {
    if frames.is_empty() {
        return Err(FrameRelationErrorV0::EmptyFramePath);
    }
    let mut seen = BTreeSet::new();
    let mut steps = Vec::with_capacity(frames.len());
    for frame_id in frames {
        if !seen.insert(*frame_id) {
            return Err(FrameRelationErrorV0::RepeatedFrame(*frame_id));
        }
        let frame = document
            .frames
            .iter()
            .find(|frame| frame.id == *frame_id)
            .ok_or(FrameRelationErrorV0::UnknownFrame(*frame_id))?;
        let (Some(history), Some(result), Some(evidence)) = (
            frame.output.history,
            frame.output.result,
            frame.output.evidence,
        ) else {
            return Err(FrameRelationErrorV0::UnrecordedFrame(*frame_id));
        };
        steps.push(FrameRelationStepV0 {
            frame: *frame_id,
            mechanism: frame.mechanism.mechanism(),
            input: frame.input,
            output: RecordedFrameOutputV0 {
                history,
                result,
                evidence,
            },
        });
    }

    let handoffs = steps
        .windows(2)
        .map(|pair| derive_handoff(&pair[0], &pair[1]))
        .collect::<Result<Vec<_>, _>>()?;
    let mechanism_path = RelationPathV0::new(steps.iter().map(|step| {
        RelationGeneratorV0::new(step.mechanism.as_str())
            .expect("mechanism surface labels are nonempty")
    }))?;
    let start = steps.first().expect("nonempty path checked above").input;
    let end = steps.last().expect("nonempty path checked above").output;
    Ok(FrameRelationPathV0 {
        steps,
        handoffs,
        start,
        end,
        mechanism_path,
    })
}

fn derive_handoff(
    from: &FrameRelationStepV0,
    to: &FrameRelationStepV0,
) -> Result<FrameHandoffV0, FrameRelationErrorV0> {
    let input = [
        (to.input.subject, InputLabelV0::Subject),
        (to.input.method, InputLabelV0::Method),
        (to.input.object, InputLabelV0::Object),
    ];
    let outputs = from.output.references();
    let mut route = Vec::with_capacity(3);
    for output in outputs {
        let Some((_, label)) = input.iter().find(|(carrier, _)| *carrier == output) else {
            return Err(FrameRelationErrorV0::IncompleteHandoff {
                from: from.frame,
                to: to.frame,
            });
        };
        route.push(*label);
    }
    let [history_to, result_to, evidence_to] = route.as_slice() else {
        unreachable!("three output carriers always produce three routes")
    };
    if route.iter().copied().collect::<BTreeSet<_>>().len() != 3 {
        return Err(FrameRelationErrorV0::IncompleteHandoff {
            from: from.frame,
            to: to.frame,
        });
    }
    Ok(FrameHandoffV0 {
        from: from.frame,
        to: to.frame,
        route: FrameHandoffRouteV0 {
            history_to: *history_to,
            result_to: *result_to,
            evidence_to: *evidence_to,
        },
    })
}

fn check_interchange(
    left: &RelationPathV0,
    right: &RelationPathV0,
) -> Result<(), RelationFormationErrorV0> {
    let [a, b] = left.steps() else {
        return Err(RelationFormationErrorV0::InvalidInterchangeWord);
    };
    let [right_b, right_a] = right.steps() else {
        return Err(RelationFormationErrorV0::InvalidInterchangeWord);
    };
    if a == b || right_b != b || right_a != a {
        return Err(RelationFormationErrorV0::InvalidInterchangeWord);
    }
    Ok(())
}

fn check_braid(
    left: &RelationPathV0,
    right: &RelationPathV0,
) -> Result<(), RelationFormationErrorV0> {
    let [a, b, a_again] = left.steps() else {
        return Err(RelationFormationErrorV0::InvalidBraidWord);
    };
    let [right_b, right_a, right_b_again] = right.steps() else {
        return Err(RelationFormationErrorV0::InvalidBraidWord);
    };
    if a != a_again || a == b || right_b != b || right_a != a || right_b_again != b {
        return Err(RelationFormationErrorV0::InvalidBraidWord);
    }
    Ok(())
}

fn check_filling(filling: &RelationFillingV0) -> Result<(), RelationFormationErrorV0> {
    match filling {
        RelationFillingV0::Open { residual } => {
            ensure_reference(residual, RelationFormationErrorV0::EmptyResidualReference)
        }
        RelationFillingV0::Filled {
            witness,
            retained_residual,
            ..
        } => {
            ensure_reference(witness, RelationFormationErrorV0::EmptyWitnessReference)?;
            if let Some(residual) = retained_residual {
                ensure_reference(residual, RelationFormationErrorV0::EmptyResidualReference)?;
            }
            Ok(())
        }
    }
}

fn ensure_reference(
    reference: &ArtifactKeyV0,
    error: RelationFormationErrorV0,
) -> Result<(), RelationFormationErrorV0> {
    if reference.as_str().is_empty() {
        Err(error)
    } else {
        Ok(())
    }
}

#[derive(Clone, Debug, Eq, Error, PartialEq)]
pub enum RelationFormationErrorV0 {
    #[error("a relation generator label cannot be empty")]
    EmptyGenerator,
    #[error("a relation path cannot be empty")]
    EmptyPath,
    #[error("relation profile is incoherent: expected {expected:?}, got {actual:?}")]
    IncoherentProfile {
        actual: RelationProfileV0,
        expected: RelationProfileV0,
    },
    #[error("a relation cell must retain two distinct raw paths")]
    IdenticalRawPaths,
    #[error("an interchange cell requires distinct words ab and ba")]
    InvalidInterchangeWord,
    #[error("a braid cell requires distinct words aba and bab")]
    InvalidBraidWord,
    #[error("an open relation needs a nonempty residual reference")]
    EmptyResidualReference,
    #[error("a filled relation needs a nonempty witness reference")]
    EmptyWitnessReference,
    #[error("an open relation boundary cannot be read as transport")]
    OpenBoundaryCannotTransport,
}

#[derive(Clone, Debug, Eq, Error, PartialEq)]
pub enum FrameRelationErrorV0 {
    #[error("invalid neutral Adva document: {0}")]
    InvalidDocument(String),
    #[error("a frame relation path cannot be empty")]
    EmptyFramePath,
    #[error("frame {0:?} is not present in the validated document")]
    UnknownFrame(FrameIdV0),
    #[error("frame {0:?} occurs more than once in one finite path")]
    RepeatedFrame(FrameIdV0),
    #[error("frame {0:?} has no complete recorded output boundary")]
    UnrecordedFrame(FrameIdV0),
    #[error("frame {from:?} does not hand off all three outputs to frame {to:?}")]
    IncompleteHandoff { from: FrameIdV0, to: FrameIdV0 },
    #[error("relation paths do not have the same labelled input boundary")]
    DifferentStartBoundary,
    #[error("relation paths do not have the same labelled recorded-output boundary")]
    DifferentEndBoundary,
    #[error(transparent)]
    Relation(#[from] RelationFormationErrorV0),
}
