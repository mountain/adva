use adva_witness::{
    AdvaDocumentV0, CharacteristicStateV0, ConstructiveTraceCodeV0, M6NamingPlanV0, MechanismV0,
    ProjectionAlignmentV0, TraceArithmeticErrorV0, TraceArithmeticQuestionKindV0,
    TruthFiberStateV0, calibrate_trace_arithmetic_v0, load_reveal_witness_v0,
    load_trace_arithmetic_v0, run_m6_reveal_v0, save_trace_arithmetic_v0,
};
use std::path::PathBuf;
use std::sync::atomic::{AtomicU64, Ordering};

static TEST_ORDINAL: AtomicU64 = AtomicU64::new(0);

fn first_program() -> AdvaDocumentV0 {
    let path =
        PathBuf::from(env!("CARGO_MANIFEST_DIR")).join("../../programs/bootstrap-0/reveal.adva");
    AdvaDocumentV0::from_json(&std::fs::read_to_string(path).unwrap()).unwrap()
}

fn first_witness() -> adva_witness::RevealWitnessV0 {
    let path = PathBuf::from(env!("CARGO_MANIFEST_DIR"))
        .join("../../programs/bootstrap-0/first-reveal-witness.adva");
    load_reveal_witness_v0(path).unwrap()
}

fn temporary_calibration_path() -> PathBuf {
    let ordinal = TEST_ORDINAL.fetch_add(1, Ordering::Relaxed);
    let directory = std::env::temp_dir().join(format!(
        "adva-trace-arithmetic-{}-{ordinal}",
        std::process::id()
    ));
    std::fs::create_dir_all(&directory).unwrap();
    directory.join("calibration.adva")
}

#[test]
fn first_reveal_has_matched_time_and_space_but_divergent_construction() {
    let calibration = calibrate_trace_arithmetic_v0(&first_witness()).unwrap();

    assert_eq!(calibration.alignment.time, ProjectionAlignmentV0::Matched);
    assert_eq!(calibration.alignment.space, ProjectionAlignmentV0::Matched);
    assert_eq!(
        calibration.alignment.construction,
        ProjectionAlignmentV0::Diverged
    );
    assert!(calibration.additive_residual.time.is_zero());
    assert!(calibration.additive_residual.space.is_zero());
    assert_eq!(calibration.additive_residual.construction.compute, 1);
    assert_eq!(calibration.additive_residual.construction.verify, -1);
    assert_eq!(calibration.additive_residual.construction.learn, 0);
    assert_eq!(calibration.additive_residual.construction.step_count, 0);
    assert_eq!(calibration.additive_residual.construction.alternations, 0);
    assert!(!calibration.additive_residual.construction.is_zero());
    assert_ne!(
        calibration.left.trace_digest,
        calibration.right.trace_digest
    );
    calibration.check().unwrap();
}

#[test]
fn naive_commutative_m6_holonomy_does_not_normalize_to_one() {
    let calibration = calibrate_trace_arithmetic_v0(&first_witness()).unwrap();

    assert!(!calibration.commutative_holonomy.right_over_left.is_one());
    assert!(calibration.commutative_holonomy.witness.is_none());
    assert_eq!(calibration.truth_fiber.state, TruthFiberStateV0::Open);
    assert!(calibration.truth_fiber.shared_truth_coordinate.is_none());
    assert_eq!(calibration.questions.len(), 5);
    assert_eq!(
        calibration.questions[0].kind,
        TraceArithmeticQuestionKindV0::TimeCharacteristic
    );
    assert_eq!(
        calibration.questions[4].kind,
        TraceArithmeticQuestionKindV0::CommonTruthCoordinate
    );
    assert!(
        calibration
            .characteristic_constraints
            .iter()
            .all(|constraint| constraint.state == CharacteristicStateV0::Open
                && constraint.witness.is_none())
    );
}

#[test]
fn an_arithmetic_projection_collision_does_not_identify_ordered_traces() {
    let left = ConstructiveTraceCodeV0::from_mechanisms([
        MechanismV0::Compute,
        MechanismV0::Verify,
        MechanismV0::Compute,
        MechanismV0::Verify,
    ])
    .unwrap();
    let right = ConstructiveTraceCodeV0::from_mechanisms([
        MechanismV0::Verify,
        MechanismV0::Compute,
        MechanismV0::Verify,
        MechanismV0::Compute,
    ])
    .unwrap();

    assert_eq!(left.incidence, right.incidence);
    assert_eq!(left.step_count, right.step_count);
    assert_eq!(left.alternations, right.alternations);
    assert_ne!(left.ordered_word, right.ordered_word);
    assert_ne!(left, right);
}

#[test]
fn calibration_rejects_suspension_and_tampered_derived_fields() {
    let suspended =
        run_m6_reveal_v0(&first_program(), M6NamingPlanV0::first_calibration(), 4).unwrap();
    assert!(matches!(
        calibrate_trace_arithmetic_v0(&suspended),
        Err(TraceArithmeticErrorV0::InvalidSourceWitness(_))
    ));

    let mut calibration = calibrate_trace_arithmetic_v0(&first_witness()).unwrap();
    calibration.alignment.time = ProjectionAlignmentV0::Diverged;
    assert!(calibration.check().is_err());

    let mut calibration = calibrate_trace_arithmetic_v0(&first_witness()).unwrap();
    calibration.left.trace_digest = format!("blake3:{}", "0".repeat(64));
    assert!(calibration.check().is_err());
}

#[test]
fn calibration_round_trips_as_a_checked_adva_file() {
    let calibration = calibrate_trace_arithmetic_v0(&first_witness()).unwrap();
    let path = temporary_calibration_path();
    let receipt = save_trace_arithmetic_v0(&path, &calibration).unwrap();
    let loaded = load_trace_arithmetic_v0(&path).unwrap();

    assert_eq!(loaded, calibration);
    assert!(receipt.calibration_digest.starts_with("blake3:"));
    assert!(receipt.bytes_written > 0);

    std::fs::remove_file(&path).unwrap();
    std::fs::remove_dir(path.parent().unwrap()).unwrap();
}
