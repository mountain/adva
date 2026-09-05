//! Scoped positive and negative witnesses about the existing trace projections.

use crate::{
    ConstructiveTraceCodeV0, FrameRelationPathV0, SpatialTraceCodeV0, TemporalTraceCodeV0,
    TraceArithmeticCalibrationV0, TraceArithmeticErrorV0,
};
use serde::{Deserialize, Serialize};
use thiserror::Error;

pub const TRACE_PROJECTION_SCHEMA_V0: &str = "adva.trace-projection-witness-pair.research";
pub const TRACE_PROJECTION_METHOD_V0: &str = "serial-counts-and-construction-obstruction:v0";

/// A checked count factorization for one nonempty complete three-port path.
/// This retains the path; it does not certify execution or elapsed time.
#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct TemporalCountWitnessV0 {
    pub path: FrameRelationPathV0,
    pub trace_digest: String,
    pub construction_step_count: u32,
    pub derived_time: TemporalTraceCodeV0,
}

impl TemporalCountWitnessV0 {
    pub fn check(&self) -> Result<(), TraceProjectionErrorV0> {
        if self != &derive_temporal_count_witness_v0(&self.path)? {
            return Err(TraceProjectionErrorV0::InvalidWitness(
                "temporal witness disagrees with the checked path and count rule",
            ));
        }
        Ok(())
    }
}

/// Two equal (time, space) inputs with unequal full construction outputs.
/// Its paths and document coordinate are retained in the enclosing calibration.
#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct ConstructionRecoveryObstructionV0 {
    pub left_trace_digest: String,
    pub right_trace_digest: String,
    pub shared_time: TemporalTraceCodeV0,
    pub shared_space: SpatialTraceCodeV0,
    pub left_construction: ConstructiveTraceCodeV0,
    pub right_construction: ConstructiveTraceCodeV0,
}

/// An additive research artifact; the embedded five M6 questions stay open.
/// A successful check certifies the two stated projection results only.
#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct TraceProjectionWitnessPairV0 {
    pub schema: String,
    pub version: u32,
    pub method: String,
    pub source_calibration_digest: String,
    pub source_calibration: TraceArithmeticCalibrationV0,
    pub temporal_witnesses: [TemporalCountWitnessV0; 2],
    pub construction_obstruction: ConstructionRecoveryObstructionV0,
}

impl TraceProjectionWitnessPairV0 {
    pub fn from_json(source: &str) -> Result<Self, TraceProjectionErrorV0> {
        let witness: Self = serde_json::from_str(source)?;
        witness.check()?;
        Ok(witness)
    }

    pub fn to_json(&self) -> Result<String, TraceProjectionErrorV0> {
        self.check()?;
        Ok(serde_json::to_string_pretty(self)?)
    }

    /// Recheck raw paths, every derived field, method, scope, and source binding.
    pub fn check(&self) -> Result<(), TraceProjectionErrorV0> {
        if self != &derive_trace_projection_witness_pair_v0(&self.source_calibration)? {
            return Err(TraceProjectionErrorV0::InvalidWitness(
                "projection witness pair disagrees with its checked source or frozen method",
            ));
        }
        Ok(())
    }
}

/// Evaluate the count rule in its representable domain without allocating a path.
/// Rejects n = 0 and 3(n - 1) overflow. This alone does not validate a path.
pub fn temporal_counts_from_length_v0(
    step_count: u32,
) -> Result<TemporalTraceCodeV0, TraceProjectionErrorV0> {
    let causal_handoffs = step_count
        .checked_sub(1)
        .ok_or(TraceProjectionErrorV0::InvalidLength)?;
    let transferred_ports = causal_handoffs
        .checked_mul(3)
        .ok_or(TraceProjectionErrorV0::InvalidLength)?;
    Ok(TemporalTraceCodeV0 {
        frame_occurrences: step_count,
        causal_handoffs,
        transferred_ports,
    })
}

/// Reuse the authoritative research path validator before applying the rule.
/// The inputs are recorded document-local paths, not executed program histories.
pub fn derive_temporal_count_witness_v0(
    path: &FrameRelationPathV0,
) -> Result<TemporalCountWitnessV0, TraceProjectionErrorV0> {
    let code = crate::trace_arithmetic::encode_path(path)?;
    let derived_time = temporal_counts_from_length_v0(code.construction.step_count)?;
    if derived_time != code.time {
        return Err(TraceProjectionErrorV0::InvalidWitness(
            "the path time projection does not factor through its construction length",
        ));
    }
    Ok(TemporalCountWitnessV0 {
        path: path.clone(),
        trace_digest: code.trace_digest,
        construction_step_count: code.construction.step_count,
        derived_time,
    })
}

/// Derive a positive count witness on each side and one finite recovery obstruction.
/// The exact source calibration and both ordered histories remain embedded.
pub fn derive_trace_projection_witness_pair_v0(
    calibration: &TraceArithmeticCalibrationV0,
) -> Result<TraceProjectionWitnessPairV0, TraceProjectionErrorV0> {
    calibration.check()?;
    let left = &calibration.left;
    let right = &calibration.right;
    if left.time != right.time || left.space != right.space {
        return Err(TraceProjectionErrorV0::InvalidWitness(
            "a recovery obstruction requires equal time and space inputs",
        ));
    }
    if left.construction == right.construction {
        return Err(TraceProjectionErrorV0::InvalidWitness(
            "a recovery obstruction requires unequal construction outputs",
        ));
    }
    let source_bytes = format!("{}\n", calibration.to_json()?);
    Ok(TraceProjectionWitnessPairV0 {
        schema: TRACE_PROJECTION_SCHEMA_V0.to_owned(),
        version: 0,
        method: TRACE_PROJECTION_METHOD_V0.to_owned(),
        source_calibration_digest: format!(
            "blake3:{}",
            blake3::hash(source_bytes.as_bytes()).to_hex()
        ),
        source_calibration: calibration.clone(),
        temporal_witnesses: [
            derive_temporal_count_witness_v0(&calibration.relation.left)?,
            derive_temporal_count_witness_v0(&calibration.relation.right)?,
        ],
        construction_obstruction: ConstructionRecoveryObstructionV0 {
            left_trace_digest: left.trace_digest.clone(),
            right_trace_digest: right.trace_digest.clone(),
            shared_time: left.time,
            shared_space: left.space,
            left_construction: left.construction.clone(),
            right_construction: right.construction.clone(),
        },
    })
}

#[derive(Debug, Error)]
pub enum TraceProjectionErrorV0 {
    #[error("count rule requires n >= 1 and 3(n - 1) representable as u32")]
    InvalidLength,
    #[error("invalid trace projection witness: {0}")]
    InvalidWitness(&'static str),
    #[error(transparent)]
    Source(#[from] TraceArithmeticErrorV0),
    #[error(transparent)]
    Json(#[from] serde_json::Error),
}
