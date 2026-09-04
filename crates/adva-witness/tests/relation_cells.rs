use adva_ir::CheckStatus;
use adva_witness::{
    AdvaDocumentV0, ArtifactKeyV0, CarrierIdV0, CoxeterShadowV0, EntryPointV0,
    FrameHandoffRouteV0, FrameIdV0, FrameInputV0, FrameMechanismV0, FrameOutputV0,
    FrameRelationCellV0, FrameRelationErrorV0, FrameRelationPathV0, InputLabelV0, MechanismV0,
    NeutralCarrierV0, OpenFrontierV0, ProcessLiftV0, RelationBoundaryShapeV0, RelationCellV0,
    RelationFillingV0, RelationFormationErrorV0, RelationGeneratorV0, RelationKindV0,
    RelationOrientationV0, RelationPathV0, RelationProfileV0, StoredCarrierV0,
    TransitionFrameV0,
};

fn key(name: &str) -> ArtifactKeyV0 {
    ArtifactKeyV0::cache_label(format!("test:{name}")).unwrap()
}

fn generator(name: &str) -> RelationGeneratorV0 {
    RelationGeneratorV0::new(name).unwrap()
}

fn path(names: &[&str]) -> RelationPathV0 {
    RelationPathV0::new(names.iter().copied().map(generator)).unwrap()
}

fn stored_carrier(id: u32) -> StoredCarrierV0 {
    StoredCarrierV0::new(
        CarrierIdV0::new(id),
        NeutralCarrierV0 {
            structure: key(&format!("carrier-{id}")),
            frontier: OpenFrontierV0::closed(),
        },
    )
}

fn input(ids: [u32; 3]) -> FrameInputV0 {
    FrameInputV0::new(
        CarrierIdV0::new(ids[0]),
        CarrierIdV0::new(ids[1]),
        CarrierIdV0::new(ids[2]),
    )
}

fn output(ids: [u32; 3]) -> FrameOutputV0 {
    FrameOutputV0::recorded(
        CarrierIdV0::new(ids[0]),
        CarrierIdV0::new(ids[1]),
        CarrierIdV0::new(ids[2]),
    )
}

fn mechanism(mechanism: MechanismV0) -> FrameMechanismV0 {
    match mechanism {
        MechanismV0::Compute => FrameMechanismV0::Compute,
        MechanismV0::Verify => FrameMechanismV0::Verify {
            declared_subject: OpenFrontierV0::closed(),
            discharges: Vec::new(),
        },
        MechanismV0::Learn => panic!("closed test carriers do not admit learning"),
    }
}

fn frame(
    id: u32,
    input_ids: [u32; 3],
    frame_mechanism: MechanismV0,
    output_ids: [u32; 3],
) -> TransitionFrameV0 {
    TransitionFrameV0 {
        id: FrameIdV0::new(id),
        input: input(input_ids),
        mechanism: mechanism(frame_mechanism),
        output: output(output_ids),
    }
}

fn document_with_frames(carrier_count: u32, frames: Vec<TransitionFrameV0>) -> AdvaDocumentV0 {
    AdvaDocumentV0::new(
        (0..carrier_count).map(stored_carrier).collect(),
        frames,
        vec![EntryPointV0 {
            name: "start".to_owned(),
            frame: FrameIdV0::new(0),
        }],
    )
    .unwrap()
}

fn q4_document() -> AdvaDocumentV0 {
    document_with_frames(
        12,
        vec![
            frame(0, [0, 1, 2], MechanismV0::Compute, [3, 4, 5]),
            frame(1, [4, 5, 3], MechanismV0::Verify, [9, 10, 11]),
            frame(2, [0, 1, 2], MechanismV0::Verify, [6, 7, 8]),
            frame(3, [6, 7, 8], MechanismV0::Compute, [9, 10, 11]),
        ],
    )
}

fn m6_document() -> AdvaDocumentV0 {
    document_with_frames(
        18,
        vec![
            frame(0, [0, 1, 2], MechanismV0::Compute, [3, 4, 5]),
            frame(1, [3, 4, 5], MechanismV0::Verify, [6, 7, 8]),
            frame(2, [6, 7, 8], MechanismV0::Compute, [15, 16, 17]),
            frame(3, [0, 1, 2], MechanismV0::Verify, [9, 10, 11]),
            frame(4, [9, 10, 11], MechanismV0::Compute, [12, 13, 14]),
            frame(5, [12, 13, 14], MechanismV0::Verify, [15, 16, 17]),
        ],
    )
}

#[test]
fn q4_and_m6_have_distinct_checked_process_profiles() {
    let q4 = RelationProfileV0::interchange_q4();
    assert_eq!(q4.kind, RelationKindV0::Interchange);
    assert_eq!(q4.boundary, RelationBoundaryShapeV0::Q4);
    assert_eq!(q4.process_lift, ProcessLiftV0::TraceMonoid);
    assert_eq!(q4.coxeter_shadow, CoxeterShadowV0::KleinFour);
    assert_eq!(q4.boundary.occurrence_count(), 4);

    let m6 = RelationProfileV0::braid_m6();
    assert_eq!(m6.kind, RelationKindV0::Braid);
    assert_eq!(m6.boundary, RelationBoundaryShapeV0::M6);
    assert_eq!(m6.process_lift, ProcessLiftV0::PositiveBraidMonoid);
    assert_eq!(m6.coxeter_shadow, CoxeterShadowV0::SymmetricThree);
    assert_eq!(m6.boundary.occurrence_count(), 6);
}

#[test]
fn q4_forms_ab_ba_without_erasing_either_history() {
    let left = path(&["a", "b"]);
    let right = path(&["b", "a"]);
    let cell = RelationCellV0::new(
        RelationProfileV0::interchange_q4(),
        left.clone(),
        right.clone(),
        RelationFillingV0::Filled {
            orientation: RelationOrientationV0::LeftToRight,
            witness: key("independence-witness"),
            retained_residual: Some(key("scope-residual")),
        },
    )
    .unwrap();

    let formation = cell.check().unwrap();
    assert_eq!(formation.boundary_occurrences, 4);
    assert_eq!(formation.coherent_profile, CheckStatus::Checked);
    assert_eq!(formation.canonical_relation_word, CheckStatus::Checked);
    assert_eq!(formation.distinct_raw_paths, CheckStatus::Checked);
    assert_eq!(cell.left, left);
    assert_eq!(cell.right, right);

    let transport = cell.transport().unwrap();
    assert_eq!(transport.orientation, RelationOrientationV0::LeftToRight);
    assert_eq!(transport.from, cell.left);
    assert_eq!(transport.to, cell.right);
    assert_eq!(
        transport.retained_residual.unwrap().as_str(),
        "test:scope-residual"
    );
}

#[test]
fn m6_forms_aba_bab_with_an_independent_profile() {
    let cell = RelationCellV0::new(
        RelationProfileV0::braid_m6(),
        path(&["sigma-1", "sigma-2", "sigma-1"]),
        path(&["sigma-2", "sigma-1", "sigma-2"]),
        RelationFillingV0::Filled {
            orientation: RelationOrientationV0::RightToLeft,
            witness: key("braid-witness"),
            retained_residual: None,
        },
    )
    .unwrap();

    let formation = cell.check().unwrap();
    assert_eq!(formation.profile, RelationProfileV0::braid_m6());
    assert_eq!(formation.boundary_occurrences, 6);

    let transport = cell.transport().unwrap();
    assert_eq!(transport.orientation, RelationOrientationV0::RightToLeft);
    assert_eq!(transport.from, cell.right);
    assert_eq!(transport.to, cell.left);
    assert_eq!(transport.witness.as_str(), "test:braid-witness");
}

#[test]
fn an_open_boundary_retains_a_residual_and_cannot_transport() {
    let cell = RelationCellV0::new(
        RelationProfileV0::interchange_q4(),
        path(&["a", "b"]),
        path(&["b", "a"]),
        RelationFillingV0::Open {
            residual: key("unresolved-interaction"),
        },
    )
    .unwrap();

    assert!(cell.check().is_ok());
    assert_eq!(
        cell.transport(),
        Err(RelationFormationErrorV0::OpenBoundaryCannotTransport)
    );
}

#[test]
fn a_group_shadow_cannot_be_silently_moved_between_q4_and_m6() {
    let incoherent = RelationProfileV0 {
        kind: RelationKindV0::Interchange,
        boundary: RelationBoundaryShapeV0::Q4,
        process_lift: ProcessLiftV0::PositiveBraidMonoid,
        coxeter_shadow: CoxeterShadowV0::SymmetricThree,
    };
    let cell = RelationCellV0 {
        profile: incoherent,
        left: path(&["a", "b"]),
        right: path(&["b", "a"]),
        filling: RelationFillingV0::Open {
            residual: key("profile-mismatch"),
        },
    };

    assert_eq!(
        cell.check(),
        Err(RelationFormationErrorV0::IncoherentProfile {
            actual: incoherent,
            expected: RelationProfileV0::interchange_q4(),
        })
    );
}

#[test]
fn malformed_relation_words_are_rejected_without_quotienting_history() {
    assert_eq!(
        RelationCellV0::new(
            RelationProfileV0::interchange_q4(),
            path(&["a", "b"]),
            path(&["a", "b"]),
            RelationFillingV0::Open {
                residual: key("same-history"),
            },
        ),
        Err(RelationFormationErrorV0::IdenticalRawPaths)
    );

    assert_eq!(
        RelationCellV0::new(
            RelationProfileV0::interchange_q4(),
            path(&["a", "b"]),
            path(&["b", "c"]),
            RelationFillingV0::Open {
                residual: key("not-an-interchange"),
            },
        ),
        Err(RelationFormationErrorV0::InvalidInterchangeWord)
    );

    assert_eq!(
        RelationCellV0::new(
            RelationProfileV0::braid_m6(),
            path(&["a", "b", "a"]),
            path(&["b", "a", "c"]),
            RelationFillingV0::Open {
                residual: key("not-a-braid"),
            },
        ),
        Err(RelationFormationErrorV0::InvalidBraidWord)
    );
}

#[test]
fn serialized_profiles_are_rechecked_after_decoding() {
    let cell = RelationCellV0::new(
        RelationProfileV0::interchange_q4(),
        path(&["a", "b"]),
        path(&["b", "a"]),
        RelationFillingV0::Open {
            residual: key("serialized-residual"),
        },
    )
    .unwrap();
    let mut encoded = serde_json::to_value(cell).unwrap();
    encoded["profile"]["coxeter_shadow"] = serde_json::json!("symmetric_three");
    let decoded: RelationCellV0 = serde_json::from_value(encoded).unwrap();

    assert!(matches!(
        decoded.check(),
        Err(RelationFormationErrorV0::IncoherentProfile { .. })
    ));
}

#[test]
fn empty_generator_labels_are_rejected_at_the_constructor() {
    assert_eq!(
        RelationGeneratorV0::new(""),
        Err(RelationFormationErrorV0::EmptyGenerator)
    );
}

#[test]
fn q4_is_derived_from_frame_mechanisms_and_explicit_three_port_handoffs() {
    let document = q4_document();
    let cell = FrameRelationCellV0::derive(
        &document,
        RelationProfileV0::interchange_q4(),
        &[FrameIdV0::new(0), FrameIdV0::new(1)],
        &[FrameIdV0::new(2), FrameIdV0::new(3)],
        RelationFillingV0::Open {
            residual: key("frame-q4-residual"),
        },
    )
    .unwrap();

    assert_eq!(
        cell.left
            .mechanism_path
            .steps()
            .iter()
            .map(RelationGeneratorV0::as_str)
            .collect::<Vec<_>>(),
        vec!["compute", "verify"]
    );
    assert_eq!(
        cell.right
            .mechanism_path
            .steps()
            .iter()
            .map(RelationGeneratorV0::as_str)
            .collect::<Vec<_>>(),
        vec!["verify", "compute"]
    );
    assert_eq!(
        cell.left.handoffs[0].route,
        FrameHandoffRouteV0 {
            history_to: InputLabelV0::Object,
            result_to: InputLabelV0::Subject,
            evidence_to: InputLabelV0::Method,
        }
    );
    assert_eq!(cell.left.start, cell.right.start);
    assert_eq!(cell.left.end, cell.right.end);
    assert_eq!(cell.certificate.document_graph, CheckStatus::Checked);
    assert_eq!(cell.certificate.complete_handoffs, CheckStatus::Checked);
    assert_eq!(cell.certificate.common_endpoints, CheckStatus::Checked);
    assert_eq!(cell.document_digest, cell.certificate.document_digest);
}

#[test]
fn m6_is_derived_from_six_distinct_frame_occurrences() {
    let document = m6_document();
    let cell = FrameRelationCellV0::derive(
        &document,
        RelationProfileV0::braid_m6(),
        &[
            FrameIdV0::new(0),
            FrameIdV0::new(1),
            FrameIdV0::new(2),
        ],
        &[
            FrameIdV0::new(3),
            FrameIdV0::new(4),
            FrameIdV0::new(5),
        ],
        RelationFillingV0::Filled {
            orientation: RelationOrientationV0::LeftToRight,
            witness: key("frame-m6-witness"),
            retained_residual: Some(key("frame-m6-residual")),
        },
    )
    .unwrap();

    assert_eq!(cell.left.steps.len(), 3);
    assert_eq!(cell.right.steps.len(), 3);
    assert_eq!(cell.left.handoffs.len(), 2);
    assert_eq!(cell.right.handoffs.len(), 2);
    assert_eq!(cell.relation.profile, RelationProfileV0::braid_m6());
    assert_eq!(
        cell.relation.transport().unwrap().retained_residual,
        Some(key("frame-m6-residual"))
    );
}

#[test]
fn frame_paths_reject_reuse_ready_outputs_and_broken_handoffs() {
    let document = q4_document();
    assert!(matches!(
        FrameRelationPathV0::derive(
            &document,
            &[FrameIdV0::new(0), FrameIdV0::new(0)]
        ),
        Err(FrameRelationErrorV0::RepeatedFrame(FrameIdV0(0)))
    ));

    let mut ready = q4_document();
    ready.frames[1].output = FrameOutputV0::ready();
    assert!(matches!(
        FrameRelationPathV0::derive(&ready, &[FrameIdV0::new(0), FrameIdV0::new(1)]),
        Err(FrameRelationErrorV0::UnrecordedFrame(FrameIdV0(1)))
    ));

    let mut broken = q4_document();
    broken.frames[1].input.subject = CarrierIdV0::new(6);
    assert!(matches!(
        FrameRelationPathV0::derive(&broken, &[FrameIdV0::new(0), FrameIdV0::new(1)]),
        Err(FrameRelationErrorV0::IncompleteHandoff {
            from: FrameIdV0(0),
            to: FrameIdV0(1),
        })
    ));
}

#[test]
fn frame_paths_reject_empty_unknown_and_invalid_documents() {
    let document = q4_document();
    assert_eq!(
        FrameRelationPathV0::derive(&document, &[]),
        Err(FrameRelationErrorV0::EmptyFramePath)
    );
    assert_eq!(
        FrameRelationPathV0::derive(&document, &[FrameIdV0::new(99)]),
        Err(FrameRelationErrorV0::UnknownFrame(FrameIdV0(99)))
    );

    let mut invalid = q4_document();
    invalid.carriers.swap(0, 1);
    assert!(matches!(
        FrameRelationPathV0::derive(&invalid, &[FrameIdV0::new(0)]),
        Err(FrameRelationErrorV0::InvalidDocument(_))
    ));
}

#[test]
fn relation_paths_require_exact_common_labelled_endpoints() {
    let mut different_start = q4_document();
    different_start.frames[2].input.subject = CarrierIdV0::new(11);
    assert_eq!(
        FrameRelationCellV0::derive(
            &different_start,
            RelationProfileV0::interchange_q4(),
            &[FrameIdV0::new(0), FrameIdV0::new(1)],
            &[FrameIdV0::new(2), FrameIdV0::new(3)],
            RelationFillingV0::Open {
                residual: key("start-mismatch"),
            },
        ),
        Err(FrameRelationErrorV0::DifferentStartBoundary)
    );

    let mut document = q4_document();
    document.frames[3].output.result = Some(CarrierIdV0::new(8));
    assert_eq!(
        FrameRelationCellV0::derive(
            &document,
            RelationProfileV0::interchange_q4(),
            &[FrameIdV0::new(0), FrameIdV0::new(1)],
            &[FrameIdV0::new(2), FrameIdV0::new(3)],
            RelationFillingV0::Open {
                residual: key("endpoint-mismatch"),
            },
        ),
        Err(FrameRelationErrorV0::DifferentEndBoundary)
    );
}
