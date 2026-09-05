use adva_witness::{
    AdvaDocumentV0, CharacteristicStateV0, FrameIdV0, FrameRelationPathV0, M6NamingPlanV0,
    TemporalTraceCodeV0, TraceProjectionErrorV0, TraceProjectionWitnessPairV0,
    calibrate_trace_arithmetic_v0, derive_temporal_count_witness_v0,
    derive_trace_projection_witness_pair_v0, load_trace_arithmetic_v0, run_m6_reveal_v0,
    temporal_counts_from_length_v0,
};
use std::path::PathBuf;

fn program_path(name: &str) -> PathBuf {
    PathBuf::from(env!("CARGO_MANIFEST_DIR"))
        .join("../../programs/bootstrap-0")
        .join(name)
}

fn first_pair() -> TraceProjectionWitnessPairV0 {
    let source = load_trace_arithmetic_v0(program_path("first-trace-arithmetic.adva")).unwrap();
    derive_trace_projection_witness_pair_v0(&source).unwrap()
}

#[test]
fn pair_certifies_counts_and_refutes_recovery_without_closing_the_source() {
    let pair = first_pair();
    let negative = &pair.construction_obstruction;
    assert_eq!(
        negative.shared_time,
        TemporalTraceCodeV0 {
            frame_occurrences: 3,
            causal_handoffs: 2,
            transferred_ports: 6,
        }
    );
    assert_eq!(negative.left_construction.incidence.compute, 2);
    assert_eq!(negative.right_construction.incidence.compute, 1);
    assert_ne!(negative.left_construction, negative.right_construction);
    assert_ne!(negative.left_trace_digest, negative.right_trace_digest);
    assert_eq!(pair.source_calibration.questions.len(), 5);
    assert!(
        pair.source_calibration
            .characteristic_constraints
            .iter()
            .all(|entry| entry.state == CharacteristicStateV0::Open && entry.witness.is_none())
    );
    assert_eq!(
        pair.source_calibration_digest,
        "blake3:09be4633b0cbef2e9d8a29f2e6b7b2ea1a1bf7e3f715655d411b42f18af3d407"
    );
    for positive in &pair.temporal_witnesses {
        positive.check().unwrap();
    }
    pair.check().unwrap();
}

#[test]
fn count_rule_reuses_checked_one_two_and_three_frame_paths() {
    let source = std::fs::read_to_string(program_path("reveal.adva")).unwrap();
    let document = AdvaDocumentV0::from_json(&source).unwrap();
    let frames = [FrameIdV0::new(0), FrameIdV0::new(1), FrameIdV0::new(2)];
    for (length, expected) in [(1, (1, 0, 0)), (2, (2, 1, 3)), (3, (3, 2, 6))] {
        let path = FrameRelationPathV0::derive(&document, &frames[..length]).unwrap();
        let witness = derive_temporal_count_witness_v0(&path).unwrap();
        let time = witness.derived_time;
        assert_eq!(
            (
                time.frame_occurrences,
                time.causal_handoffs,
                time.transferred_ports
            ),
            expected
        );
        assert_eq!(witness.path, path);
        witness.check().unwrap();
    }
}

#[test]
fn count_rule_checks_zero_and_the_exact_u32_port_boundary_without_allocation() {
    let last_length = u32::MAX / 3 + 1;
    let last = temporal_counts_from_length_v0(last_length).unwrap();
    assert_eq!(last.transferred_ports, u32::MAX);
    for length in [0, last_length + 1, u32::MAX] {
        assert!(matches!(
            temporal_counts_from_length_v0(length),
            Err(TraceProjectionErrorV0::InvalidLength)
        ));
    }
}

#[test]
fn pair_reuses_a_fresh_checked_document_with_exchanged_mechanisms() {
    let source = std::fs::read_to_string(program_path("reveal.adva")).unwrap();
    let mut candidate: serde_json::Value = serde_json::from_str(&source).unwrap();
    for frame in candidate["frames"].as_array_mut().unwrap() {
        frame["mechanism"] = if frame["mechanism"]["kind"] == "compute" {
            serde_json::json!({
                "kind": "verify", "declared_subject": {"sites": []}, "discharges": []
            })
        } else {
            serde_json::json!({"kind": "compute"})
        };
    }
    let document = AdvaDocumentV0::from_json(&candidate.to_string()).unwrap();
    let reveal = run_m6_reveal_v0(&document, M6NamingPlanV0::first_calibration(), 6).unwrap();
    let calibration = calibrate_trace_arithmetic_v0(&reveal).unwrap();
    let reused = derive_trace_projection_witness_pair_v0(&calibration).unwrap();
    let first = first_pair();
    assert_ne!(
        reused.source_calibration_digest,
        first.source_calibration_digest
    );
    assert_eq!(
        reused.construction_obstruction.left_construction,
        first.construction_obstruction.right_construction
    );
    reused.check().unwrap();
}

#[test]
fn temporal_checker_rejects_missing_handoffs_and_forged_counts() {
    let original = first_pair().temporal_witnesses[0].clone();
    let mut path = original.path.clone();
    path.handoffs.pop();
    assert!(derive_temporal_count_witness_v0(&path).is_err());
    let mut path = original.path.clone();
    path.steps[1].frame = path.steps[0].frame;
    assert!(derive_temporal_count_witness_v0(&path).is_err());
    let mut witness = original;
    witness.derived_time.transferred_ports = 5;
    assert!(witness.check().is_err());
}

#[test]
fn pair_checker_rejects_forged_negative_evidence_method_and_source_binding() {
    let original = first_pair();
    let mut changed = original.clone();
    changed.construction_obstruction.right_construction =
        changed.construction_obstruction.left_construction.clone();
    assert!(changed.check().is_err());
    let mut changed = original.clone();
    changed.construction_obstruction.shared_space.start.subject =
        adva_witness::CarrierIdV0::new(99);
    assert!(changed.check().is_err());
    let mut changed = original.clone();
    changed.construction_obstruction.shared_time.frame_occurrences = 4;
    assert!(changed.check().is_err());
    let mut changed = original.clone();
    changed.source_calibration_digest = format!("blake3:{}", "0".repeat(64));
    assert!(changed.check().is_err());
    let mut changed = original.clone();
    changed.method.push_str(":changed");
    assert!(changed.check().is_err());
    let mut changed = original;
    changed.source_calibration.left.construction.incidence.compute = 99;
    assert!(changed.check().is_err());
}

#[test]
fn pair_round_trip_rechecks_schema_and_every_derived_field() {
    let pair = first_pair();
    let json = pair.to_json().unwrap();
    assert_eq!(TraceProjectionWitnessPairV0::from_json(&json).unwrap(), pair);
    let mut candidate: serde_json::Value = serde_json::from_str(&json).unwrap();
    candidate["version"] = serde_json::json!(1);
    assert!(TraceProjectionWitnessPairV0::from_json(&candidate.to_string()).is_err());
    candidate["version"] = serde_json::json!(0);
    candidate["unexpected"] = serde_json::json!(true);
    assert!(TraceProjectionWitnessPairV0::from_json(&candidate.to_string()).is_err());
}
