use crate::{
    ArithmeticErrorV0, ArtifactKeyV0, CarrierIdV0, ExactExprV0, FrameHandoffRouteV0, FrameInputV0,
    FrameRelationCellV0, FrameRelationPathV0, InputLabelV0, MechanismV0, MultiplicativeResidualV0,
    ObserverDomainV0, PolynomialV0, RecordedFrameOutputV0, RelationFillingV0, RelationProfileV0,
    RevealErrorV0, RevealRunStateV0, RevealWitnessV0,
};
use adva_ir::CheckStatus;
use serde::{Deserialize, Serialize};
use std::collections::BTreeSet;
use std::fs;
use std::path::{Path, PathBuf};
use thiserror::Error;

/// Schema identifier for the first three-sided trace-arithmetic calibration.
pub const TRACE_ARITHMETIC_SCHEMA_V0: &str = "adva.trace-arithmetic-calibration.research";

/// Research artifact version. This is not `adva.ir` version one.
pub const TRACE_ARITHMETIC_VERSION_V0: u32 = 0;

const TIME_CHARACTERISTIC_KEY: &str = "experiment:first:m6-time-characteristic-required";
const SPACE_CHARACTERISTIC_KEY: &str = "experiment:first:m6-space-characteristic-required";
const CONSTRUCTION_CHARACTERISTIC_KEY: &str =
    "experiment:first:m6-construction-characteristic-required";
const HOLONOMY_KEY: &str = "experiment:first:m6-multiplicative-holonomy-required";
const COMMON_TRUTH_KEY: &str = "experiment:first:m6-common-truth-coordinate-required";

/// A finite count projection of one stored trace onto its time coordinate.
#[derive(Clone, Copy, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct TemporalTraceCodeV0 {
    pub frame_occurrences: u32,
    pub causal_handoffs: u32,
    pub transferred_ports: u32,
}

/// Exact labelled endpoints of one stored trace.
#[derive(Clone, Copy, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct SpatialTraceCodeV0 {
    pub start: FrameInputV0,
    pub end: RecordedFrameOutputV0,
}

/// Commutative mechanism multiplicities. This deliberately forgets order.
#[derive(Clone, Copy, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct MechanismIncidenceV0 {
    pub compute: u32,
    pub verify: u32,
    pub learn: u32,
}

/// Construction-side projection with its exact ordered word retained beside
/// the lossy arithmetic incidence.
#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct ConstructiveTraceCodeV0 {
    pub incidence: MechanismIncidenceV0,
    pub step_count: u32,
    pub alternations: u32,
    pub ordered_word: Vec<MechanismV0>,
}

impl ConstructiveTraceCodeV0 {
    /// Project one nonempty mechanism word without treating the projection as
    /// a trace identity.
    ///
    /// # Errors
    ///
    /// Rejects an empty or platform-unrepresentable word.
    pub fn from_mechanisms(
        mechanisms: impl IntoIterator<Item = MechanismV0>,
    ) -> Result<Self, TraceArithmeticErrorV0> {
        let ordered_word = mechanisms.into_iter().collect::<Vec<_>>();
        if ordered_word.is_empty() {
            return Err(TraceArithmeticErrorV0::InvalidCalibration(
                "a constructive trace word must be nonempty",
            ));
        }
        let step_count = u32::try_from(ordered_word.len()).map_err(|_| {
            TraceArithmeticErrorV0::InvalidCalibration(
                "the constructive trace word exceeds the bounded u32 representation",
            )
        })?;
        let alternations = u32::try_from(
            ordered_word
                .windows(2)
                .filter(|pair| pair[0] != pair[1])
                .count(),
        )
        .map_err(|_| {
            TraceArithmeticErrorV0::InvalidCalibration(
                "the alternation count exceeds the bounded u32 representation",
            )
        })?;
        let mut incidence = MechanismIncidenceV0 {
            compute: 0,
            verify: 0,
            learn: 0,
        };
        for mechanism in &ordered_word {
            let coordinate = match mechanism {
                MechanismV0::Compute => &mut incidence.compute,
                MechanismV0::Verify => &mut incidence.verify,
                MechanismV0::Learn => &mut incidence.learn,
            };
            *coordinate =
                coordinate
                    .checked_add(1)
                    .ok_or(TraceArithmeticErrorV0::InvalidCalibration(
                        "a mechanism incidence exceeds the bounded u32 representation",
                    ))?;
        }
        Ok(Self {
            incidence,
            step_count,
            alternations,
            ordered_word,
        })
    }
}

/// Three projections of one exact frame path.
#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct TraceArithmeticCodeV0 {
    pub trace_digest: String,
    pub time: TemporalTraceCodeV0,
    pub space: SpatialTraceCodeV0,
    pub construction: ConstructiveTraceCodeV0,
    pub commutative_weight: PolynomialV0,
}

/// Signed time-coordinate difference, always read as `left - right`.
#[derive(Clone, Copy, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct TemporalResidualV0 {
    pub frame_occurrences: i64,
    pub causal_handoffs: i64,
    pub transferred_ports: i64,
}

impl TemporalResidualV0 {
    #[must_use]
    pub const fn is_zero(self) -> bool {
        self.frame_occurrences == 0 && self.causal_handoffs == 0 && self.transferred_ports == 0
    }
}

/// Signed labelled-boundary difference, always read as `left - right`.
#[derive(Clone, Copy, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct SpatialResidualV0 {
    pub start: [i64; 3],
    pub end: [i64; 3],
}

impl SpatialResidualV0 {
    #[must_use]
    pub fn is_zero(self) -> bool {
        self.start
            .into_iter()
            .chain(self.end)
            .all(|value| value == 0)
    }
}

/// Signed construction-coordinate difference, always read as `left - right`.
#[derive(Clone, Copy, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct ConstructiveResidualV0 {
    pub compute: i64,
    pub verify: i64,
    pub learn: i64,
    pub step_count: i64,
    pub alternations: i64,
}

impl ConstructiveResidualV0 {
    #[must_use]
    pub const fn is_zero(self) -> bool {
        self.compute == 0
            && self.verify == 0
            && self.learn == 0
            && self.step_count == 0
            && self.alternations == 0
    }
}

/// Typed additive residuals. Coordinates from different sides never cancel
/// one another through a scalar sum.
#[derive(Clone, Copy, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct ThreeSideAdditiveResidualV0 {
    pub time: TemporalResidualV0,
    pub space: SpatialResidualV0,
    pub construction: ConstructiveResidualV0,
}

/// Observable equality state of one path-to-side projection.
#[derive(Clone, Copy, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum ProjectionAlignmentV0 {
    Matched,
    Diverged,
}

/// The three independent path-to-side alignment results.
#[derive(Clone, Copy, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct ThreeSideAlignmentV0 {
    pub time: ProjectionAlignmentV0,
    pub space: ProjectionAlignmentV0,
    pub construction: ProjectionAlignmentV0,
}

/// Whether a cross-side characteristic map has an explicit witness.
#[derive(Clone, Copy, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum CharacteristicStateV0 {
    Witnessed,
    Open,
}

/// One requested equation of the form `target = chi(opposite sides)`.
#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct OppositeSideCharacteristicV0 {
    pub target: ObserverDomainV0,
    pub derived_from: [ObserverDomainV0; 2],
    pub state: CharacteristicStateV0,
    pub witness: Option<ArtifactKeyV0>,
}

/// The naive commutative product shadow of the two raw words.
///
/// It is a diagnostic only: it forgets path order and does not descend to a
/// braid quotient unless a separate witness establishes the needed relation.
#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct CommutativeHolonomyV0 {
    pub right_over_left: MultiplicativeResidualV0,
    pub state: MultiplicativeHolonomyStateV0,
    pub witness: Option<ArtifactKeyV0>,
}

/// Exact state of the commutative multiplicative diagnostic.
#[derive(Clone, Copy, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum MultiplicativeHolonomyStateV0 {
    Identity,
    NonIdentity,
}

/// Whether both readings have been placed in one explicitly witnessed truth
/// fiber. Matching projections alone cannot close this state.
#[derive(Clone, Copy, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum TruthFiberStateV0 {
    Witnessed,
    Open,
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct TruthFiberV0 {
    pub state: TruthFiberStateV0,
    pub shared_truth_coordinate: Option<ArtifactKeyV0>,
}

/// One independently addressable question exposed by the calibration.
#[derive(Clone, Copy, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum TraceArithmeticQuestionKindV0 {
    TimeCharacteristic,
    SpaceCharacteristic,
    ConstructionCharacteristic,
    MultiplicativeHolonomy,
    CommonTruthCoordinate,
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct TraceArithmeticQuestionV0 {
    pub kind: TraceArithmeticQuestionKindV0,
    pub detail: String,
    pub residual: ArtifactKeyV0,
}

/// A self-checking arithmetic reading of the two exact paths retained by one
/// completed reveal witness.
#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct TraceArithmeticCalibrationV0 {
    pub schema: String,
    pub version: u32,
    pub source_witness_digest: String,
    pub source_document_digest: String,
    pub relation: FrameRelationCellV0,
    pub left: TraceArithmeticCodeV0,
    pub right: TraceArithmeticCodeV0,
    pub additive_residual: ThreeSideAdditiveResidualV0,
    pub alignment: ThreeSideAlignmentV0,
    pub characteristic_constraints: [OppositeSideCharacteristicV0; 3],
    pub commutative_holonomy: CommutativeHolonomyV0,
    pub truth_fiber: TruthFiberV0,
    pub questions: Vec<TraceArithmeticQuestionV0>,
}

/// Receipt for one completed atomic calibration save.
#[derive(Clone, Debug, Eq, PartialEq)]
pub struct TraceArithmeticSaveReceiptV0 {
    pub path: PathBuf,
    pub calibration_digest: String,
    pub bytes_written: u64,
}

impl TraceArithmeticCalibrationV0 {
    /// Decode and structurally recheck one calibration artifact.
    ///
    /// # Errors
    ///
    /// Rejects malformed JSON or any derived field that disagrees with the
    /// retained raw relation paths.
    pub fn from_json(source: &str) -> Result<Self, TraceArithmeticErrorV0> {
        let calibration: Self = serde_json::from_str(source)
            .map_err(|error| TraceArithmeticErrorV0::Json(error.to_string()))?;
        calibration.check()?;
        Ok(calibration)
    }

    /// Encode one structurally checked calibration deterministically.
    ///
    /// # Errors
    ///
    /// Rejects inconsistent derived data or serialization failure.
    pub fn to_json(&self) -> Result<String, TraceArithmeticErrorV0> {
        self.check()?;
        serde_json::to_string_pretty(self)
            .map_err(|error| TraceArithmeticErrorV0::Json(error.to_string()))
    }

    /// Recompute every arithmetic field from the retained exact relation.
    ///
    /// This check does not replay mechanism execution, construct a cross-side
    /// characteristic map, or authenticate a shared truth coordinate.
    ///
    /// # Errors
    ///
    /// Rejects an unsupported schema, malformed source coordinate, invalid
    /// relation trace, or a stale/tampered derived field.
    pub fn check(&self) -> Result<(), TraceArithmeticErrorV0> {
        if self.schema != TRACE_ARITHMETIC_SCHEMA_V0 || self.version != TRACE_ARITHMETIC_VERSION_V0
        {
            return Err(TraceArithmeticErrorV0::InvalidCalibration(
                "unsupported trace-arithmetic schema or version",
            ));
        }
        check_digest(&self.source_witness_digest)?;
        check_digest(&self.source_document_digest)?;
        check_relation(&self.relation, &self.source_document_digest)?;

        let left = encode_path(&self.relation.left)?;
        let right = encode_path(&self.relation.right)?;
        if self.left != left || self.right != right {
            return Err(TraceArithmeticErrorV0::InvalidCalibration(
                "a trace code does not match its retained raw path",
            ));
        }
        let additive_residual = additive_residual(&left, &right);
        if self.additive_residual != additive_residual {
            return Err(TraceArithmeticErrorV0::InvalidCalibration(
                "the three-sided additive residual is stale or malformed",
            ));
        }
        let alignment = alignment(&additive_residual);
        if self.alignment != alignment {
            return Err(TraceArithmeticErrorV0::InvalidCalibration(
                "the three-sided alignment does not match its typed residual",
            ));
        }
        if self.characteristic_constraints != open_characteristic_constraints() {
            return Err(TraceArithmeticErrorV0::InvalidCalibration(
                "version zero has no witnessed cross-side characteristic maps",
            ));
        }
        let commutative_holonomy = holonomy(&left, &right);
        if self.commutative_holonomy != commutative_holonomy {
            return Err(TraceArithmeticErrorV0::InvalidCalibration(
                "the commutative holonomy does not match the path weights",
            ));
        }
        if self.truth_fiber
            != (TruthFiberV0 {
                state: TruthFiberStateV0::Open,
                shared_truth_coordinate: None,
            })
        {
            return Err(TraceArithmeticErrorV0::InvalidCalibration(
                "projection matches cannot manufacture a shared truth coordinate",
            ));
        }
        if self.questions != open_questions() {
            return Err(TraceArithmeticErrorV0::InvalidCalibration(
                "the open arithmetic questions are stale or malformed",
            ));
        }
        Ok(())
    }
}

/// Derive the first three-sided trace-arithmetic calibration from a completed
/// persisted reveal witness.
///
/// # Errors
///
/// Rejects a suspended/malformed reveal witness or arithmetic failure.
pub fn calibrate_trace_arithmetic_v0(
    witness: &RevealWitnessV0,
) -> Result<TraceArithmeticCalibrationV0, TraceArithmeticErrorV0> {
    witness.check()?;
    if witness.state != RevealRunStateV0::Completed {
        return Err(TraceArithmeticErrorV0::InvalidSourceWitness(
            "trace arithmetic requires a completed reveal witness",
        ));
    }
    let relation = witness
        .relation
        .clone()
        .ok_or(TraceArithmeticErrorV0::InvalidSourceWitness(
            "a completed reveal witness must retain its relation",
        ))?;
    let left = encode_path(&relation.left)?;
    let right = encode_path(&relation.right)?;
    let additive_residual = additive_residual(&left, &right);
    let alignment = alignment(&additive_residual);
    let commutative_holonomy = holonomy(&left, &right);
    let calibration = TraceArithmeticCalibrationV0 {
        schema: TRACE_ARITHMETIC_SCHEMA_V0.to_owned(),
        version: TRACE_ARITHMETIC_VERSION_V0,
        source_witness_digest: reveal_digest(witness)?,
        source_document_digest: witness.source_document_digest.clone(),
        relation,
        left,
        right,
        additive_residual,
        alignment,
        characteristic_constraints: open_characteristic_constraints(),
        commutative_holonomy,
        truth_fiber: TruthFiberV0 {
            state: TruthFiberStateV0::Open,
            shared_truth_coordinate: None,
        },
        questions: open_questions(),
    };
    calibration.check()?;
    Ok(calibration)
}

/// Atomically persist one checked calibration with the common `.adva`
/// suffix.
///
/// # Errors
///
/// Rejects an invalid calibration, a non-`.adva` path, or an I/O failure.
pub fn save_trace_arithmetic_v0(
    path: impl AsRef<Path>,
    calibration: &TraceArithmeticCalibrationV0,
) -> Result<TraceArithmeticSaveReceiptV0, TraceArithmeticErrorV0> {
    let path = path.as_ref();
    crate::persistence::require_adva_extension(path)
        .map_err(|error| TraceArithmeticErrorV0::Persistence(error.to_string()))?;
    let encoded = format!("{}\n", calibration.to_json()?);
    crate::persistence::write_atomically(path, encoded.as_bytes())
        .map_err(|error| TraceArithmeticErrorV0::Persistence(error.to_string()))?;
    Ok(TraceArithmeticSaveReceiptV0 {
        path: path.to_path_buf(),
        calibration_digest: format!("blake3:{}", blake3::hash(encoded.as_bytes()).to_hex()),
        bytes_written: u64::try_from(encoded.len()).unwrap_or(u64::MAX),
    })
}

/// Load and structurally recheck one persisted calibration.
///
/// # Errors
///
/// Rejects a non-`.adva` path, unreadable content, malformed JSON, or a
/// calibration whose derived fields no longer match its retained paths.
pub fn load_trace_arithmetic_v0(
    path: impl AsRef<Path>,
) -> Result<TraceArithmeticCalibrationV0, TraceArithmeticErrorV0> {
    let path = path.as_ref();
    crate::persistence::require_adva_extension(path)
        .map_err(|error| TraceArithmeticErrorV0::Persistence(error.to_string()))?;
    let source = fs::read_to_string(path).map_err(|error| TraceArithmeticErrorV0::Io {
        path: path.to_path_buf(),
        detail: error.to_string(),
    })?;
    TraceArithmeticCalibrationV0::from_json(&source)
}

fn encode_path(
    path: &FrameRelationPathV0,
) -> Result<TraceArithmeticCodeV0, TraceArithmeticErrorV0> {
    check_path(path)?;
    let frame_occurrences = u32::try_from(path.steps.len()).map_err(|_| {
        TraceArithmeticErrorV0::InvalidCalibration(
            "the frame count exceeds the bounded u32 representation",
        )
    })?;
    let causal_handoffs = u32::try_from(path.handoffs.len()).map_err(|_| {
        TraceArithmeticErrorV0::InvalidCalibration(
            "the handoff count exceeds the bounded u32 representation",
        )
    })?;
    let transferred_ports =
        causal_handoffs
            .checked_mul(3)
            .ok_or(TraceArithmeticErrorV0::InvalidCalibration(
                "the transferred-port count exceeds the bounded u32 representation",
            ))?;
    let construction =
        ConstructiveTraceCodeV0::from_mechanisms(path.steps.iter().map(|step| step.mechanism))?;
    let expression = mechanism_expression(&construction.ordered_word);
    let canonical = serde_json::to_vec(path)
        .map_err(|error| TraceArithmeticErrorV0::Json(error.to_string()))?;
    Ok(TraceArithmeticCodeV0 {
        trace_digest: format!("blake3:{}", blake3::hash(&canonical).to_hex()),
        time: TemporalTraceCodeV0 {
            frame_occurrences,
            causal_handoffs,
            transferred_ports,
        },
        space: SpatialTraceCodeV0 {
            start: path.start,
            end: path.end,
        },
        construction,
        commutative_weight: expression.normalize()?,
    })
}

fn check_relation(
    relation: &FrameRelationCellV0,
    document_digest: &str,
) -> Result<(), TraceArithmeticErrorV0> {
    if relation.document_digest != document_digest
        || relation.certificate.document_digest != document_digest
        || relation.relation.profile != RelationProfileV0::braid_m6()
        || !matches!(&relation.relation.filling, RelationFillingV0::Open { .. })
        || relation.left.start != relation.right.start
        || relation.left.end != relation.right.end
        || relation.left.mechanism_path != relation.relation.left
        || relation.right.mechanism_path != relation.relation.right
    {
        return Err(TraceArithmeticErrorV0::InvalidCalibration(
            "the retained relation is not one open M6 cell with common endpoints",
        ));
    }
    check_path(&relation.left)?;
    check_path(&relation.right)?;
    let formation = relation
        .relation
        .check()
        .map_err(|_| TraceArithmeticErrorV0::InvalidCalibration("invalid M6 relation word"))?;
    if relation.certificate.document_graph != CheckStatus::Checked
        || relation.certificate.frame_occurrences != CheckStatus::Checked
        || relation.certificate.complete_handoffs != CheckStatus::Checked
        || relation.certificate.common_endpoints != CheckStatus::Checked
        || relation.certificate.relation_formation != formation
    {
        return Err(TraceArithmeticErrorV0::InvalidCalibration(
            "the retained frame-relation certificate is malformed",
        ));
    }
    if relation
        .left
        .steps
        .iter()
        .chain(&relation.right.steps)
        .map(|step| step.frame)
        .collect::<BTreeSet<_>>()
        .len()
        != 6
    {
        return Err(TraceArithmeticErrorV0::InvalidCalibration(
            "the first M6 calibration requires six distinct frame coordinates",
        ));
    }
    Ok(())
}

fn check_path(path: &FrameRelationPathV0) -> Result<(), TraceArithmeticErrorV0> {
    let Some(first) = path.steps.first() else {
        return Err(TraceArithmeticErrorV0::InvalidCalibration(
            "a retained trace path must be nonempty",
        ));
    };
    let last = path.steps.last().expect("a first step exists");
    if path.start != first.input
        || path.end != last.output
        || path.handoffs.len().checked_add(1) != Some(path.steps.len())
        || path.mechanism_path.steps().len() != path.steps.len()
        || path
            .mechanism_path
            .steps()
            .iter()
            .zip(&path.steps)
            .any(|(generator, step)| generator.as_str() != step.mechanism.as_str())
        || path
            .steps
            .iter()
            .map(|step| step.frame)
            .collect::<BTreeSet<_>>()
            .len()
            != path.steps.len()
    {
        return Err(TraceArithmeticErrorV0::InvalidCalibration(
            "a retained trace path has inconsistent exact structure",
        ));
    }
    for (handoff, pair) in path.handoffs.iter().zip(path.steps.windows(2)) {
        let expected_route = handoff_route(pair[0].output, pair[1].input).ok_or(
            TraceArithmeticErrorV0::InvalidCalibration(
                "a retained trace path has an incomplete three-port handoff",
            ),
        )?;
        if handoff.from != pair[0].frame
            || handoff.to != pair[1].frame
            || handoff.route != expected_route
        {
            return Err(TraceArithmeticErrorV0::InvalidCalibration(
                "a retained trace path has a stale handoff route",
            ));
        }
    }
    Ok(())
}

fn handoff_route(
    output: RecordedFrameOutputV0,
    input: FrameInputV0,
) -> Option<FrameHandoffRouteV0> {
    let inputs = [
        (input.subject, InputLabelV0::Subject),
        (input.method, InputLabelV0::Method),
        (input.object, InputLabelV0::Object),
    ];
    let outputs = [output.history, output.result, output.evidence];
    let route = outputs
        .into_iter()
        .map(|carrier| {
            inputs
                .iter()
                .find_map(|(candidate, label)| (*candidate == carrier).then_some(*label))
        })
        .collect::<Option<Vec<_>>>()?;
    let [history_to, result_to, evidence_to] = route.as_slice() else {
        return None;
    };
    if route.iter().copied().collect::<BTreeSet<_>>().len() != 3 {
        return None;
    }
    Some(FrameHandoffRouteV0 {
        history_to: *history_to,
        result_to: *result_to,
        evidence_to: *evidence_to,
    })
}

fn additive_residual(
    left: &TraceArithmeticCodeV0,
    right: &TraceArithmeticCodeV0,
) -> ThreeSideAdditiveResidualV0 {
    ThreeSideAdditiveResidualV0 {
        time: TemporalResidualV0 {
            frame_occurrences: delta(left.time.frame_occurrences, right.time.frame_occurrences),
            causal_handoffs: delta(left.time.causal_handoffs, right.time.causal_handoffs),
            transferred_ports: delta(left.time.transferred_ports, right.time.transferred_ports),
        },
        space: SpatialResidualV0 {
            start: carrier_deltas(input_ids(left.space.start), input_ids(right.space.start)),
            end: carrier_deltas(output_ids(left.space.end), output_ids(right.space.end)),
        },
        construction: ConstructiveResidualV0 {
            compute: delta(
                left.construction.incidence.compute,
                right.construction.incidence.compute,
            ),
            verify: delta(
                left.construction.incidence.verify,
                right.construction.incidence.verify,
            ),
            learn: delta(
                left.construction.incidence.learn,
                right.construction.incidence.learn,
            ),
            step_count: delta(left.construction.step_count, right.construction.step_count),
            alternations: delta(
                left.construction.alternations,
                right.construction.alternations,
            ),
        },
    }
}

fn alignment(residual: &ThreeSideAdditiveResidualV0) -> ThreeSideAlignmentV0 {
    ThreeSideAlignmentV0 {
        time: projection_alignment(residual.time.is_zero()),
        space: projection_alignment(residual.space.is_zero()),
        construction: projection_alignment(residual.construction.is_zero()),
    }
}

const fn projection_alignment(is_zero: bool) -> ProjectionAlignmentV0 {
    if is_zero {
        ProjectionAlignmentV0::Matched
    } else {
        ProjectionAlignmentV0::Diverged
    }
}

fn holonomy(left: &TraceArithmeticCodeV0, right: &TraceArithmeticCodeV0) -> CommutativeHolonomyV0 {
    let right_over_left = MultiplicativeResidualV0 {
        numerator: right.commutative_weight.clone(),
        denominator: left.commutative_weight.clone(),
    };
    CommutativeHolonomyV0 {
        state: if right_over_left.is_one() {
            MultiplicativeHolonomyStateV0::Identity
        } else {
            MultiplicativeHolonomyStateV0::NonIdentity
        },
        right_over_left,
        witness: None,
    }
}

fn mechanism_expression(word: &[MechanismV0]) -> ExactExprV0 {
    word.iter()
        .fold(ExactExprV0::constant(1), |expression, mechanism| {
            ExactExprV0::product(
                expression,
                ExactExprV0::variable(format!("mechanism.{}", mechanism.as_str())),
            )
        })
}

fn open_characteristic_constraints() -> [OppositeSideCharacteristicV0; 3] {
    [
        OppositeSideCharacteristicV0 {
            target: ObserverDomainV0::Time,
            derived_from: [ObserverDomainV0::Space, ObserverDomainV0::Construction],
            state: CharacteristicStateV0::Open,
            witness: None,
        },
        OppositeSideCharacteristicV0 {
            target: ObserverDomainV0::Space,
            derived_from: [ObserverDomainV0::Construction, ObserverDomainV0::Time],
            state: CharacteristicStateV0::Open,
            witness: None,
        },
        OppositeSideCharacteristicV0 {
            target: ObserverDomainV0::Construction,
            derived_from: [ObserverDomainV0::Time, ObserverDomainV0::Space],
            state: CharacteristicStateV0::Open,
            witness: None,
        },
    ]
}

fn open_questions() -> Vec<TraceArithmeticQuestionV0> {
    vec![
        question(
            TraceArithmeticQuestionKindV0::TimeCharacteristic,
            "no witness yet derives the time characteristic from space and construction",
            TIME_CHARACTERISTIC_KEY,
        ),
        question(
            TraceArithmeticQuestionKindV0::SpaceCharacteristic,
            "no witness yet derives the space characteristic from construction and time",
            SPACE_CHARACTERISTIC_KEY,
        ),
        question(
            TraceArithmeticQuestionKindV0::ConstructionCharacteristic,
            "the construction projections diverge and no time-space characteristic witness closes them",
            CONSTRUCTION_CHARACTERISTIC_KEY,
        ),
        question(
            TraceArithmeticQuestionKindV0::MultiplicativeHolonomy,
            "the commutative mechanism-weight shadow has not normalized to one",
            HOLONOMY_KEY,
        ),
        question(
            TraceArithmeticQuestionKindV0::CommonTruthCoordinate,
            "matching projections do not identify a shared externally witnessed truth coordinate",
            COMMON_TRUTH_KEY,
        ),
    ]
}

fn question(
    kind: TraceArithmeticQuestionKindV0,
    detail: &str,
    key: &str,
) -> TraceArithmeticQuestionV0 {
    TraceArithmeticQuestionV0 {
        kind,
        detail: detail.to_owned(),
        residual: ArtifactKeyV0::cache_label(key).expect("static residual keys are nonempty"),
    }
}

fn reveal_digest(witness: &RevealWitnessV0) -> Result<String, TraceArithmeticErrorV0> {
    let encoded = format!("{}\n", witness.to_json()?);
    Ok(format!(
        "blake3:{}",
        blake3::hash(encoded.as_bytes()).to_hex()
    ))
}

fn check_digest(digest: &str) -> Result<(), TraceArithmeticErrorV0> {
    let Some(hex) = digest.strip_prefix("blake3:") else {
        return Err(TraceArithmeticErrorV0::InvalidCalibration(
            "a source digest must be a BLAKE3 coordinate",
        ));
    };
    if hex.len() != 64 || !hex.bytes().all(|byte| byte.is_ascii_hexdigit()) {
        return Err(TraceArithmeticErrorV0::InvalidCalibration(
            "a source digest must be a BLAKE3 coordinate",
        ));
    }
    Ok(())
}

const fn input_ids(input: FrameInputV0) -> [CarrierIdV0; 3] {
    [input.subject, input.method, input.object]
}

const fn output_ids(output: RecordedFrameOutputV0) -> [CarrierIdV0; 3] {
    [output.history, output.result, output.evidence]
}

fn carrier_deltas(left: [CarrierIdV0; 3], right: [CarrierIdV0; 3]) -> [i64; 3] {
    std::array::from_fn(|index| i64::from(left[index].0) - i64::from(right[index].0))
}

fn delta(left: u32, right: u32) -> i64 {
    i64::from(left) - i64::from(right)
}

#[derive(Clone, Debug, Eq, Error, PartialEq)]
pub enum TraceArithmeticErrorV0 {
    #[error("invalid source reveal witness: {0}")]
    InvalidSourceWitness(&'static str),
    #[error("invalid trace-arithmetic calibration: {0}")]
    InvalidCalibration(&'static str),
    #[error("trace-arithmetic JSON error: {0}")]
    Json(String),
    #[error("trace-arithmetic persistence error: {0}")]
    Persistence(String),
    #[error("I/O error at {path:?}: {detail}")]
    Io { path: PathBuf, detail: String },
    #[error(transparent)]
    Arithmetic(#[from] ArithmeticErrorV0),
    #[error(transparent)]
    Reveal(#[from] RevealErrorV0),
}
