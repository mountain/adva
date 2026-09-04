use adva_ir::CheckStatus;
use adva_witness::{
    ArtifactKeyV0, CoxeterShadowV0, ProcessLiftV0, RelationBoundaryShapeV0, RelationCellV0,
    RelationFillingV0, RelationFormationErrorV0, RelationGeneratorV0, RelationKindV0,
    RelationOrientationV0, RelationPathV0, RelationProfileV0,
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
