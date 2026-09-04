use adva_witness::{
    ADVA_FILE_SUFFIX_V0, ArtifactKeyV0, DischargeV0, FillAssignmentV0, FillPlanV0,
    FrontierSiteV0, InputLabelV0, MechanismAdmissionV0, MechanismFormV0, MechanismInputV0,
    MechanismOutputV0, MechanismSyntaxErrorV0, MechanismV0, NeutralCarrierV0, OpenFrontierV0,
    OutputLabelV0, RoleV0, VerificationStatusV0,
};

fn key(name: &str) -> ArtifactKeyV0 {
    ArtifactKeyV0::cache_label(format!("test:{name}")).unwrap()
}

fn site(role: RoleV0, hole: u8, occurrence: u32) -> FrontierSiteV0 {
    FrontierSiteV0::new(role, hole, occurrence)
}

fn frontier(sites: impl IntoIterator<Item = FrontierSiteV0>) -> OpenFrontierV0 {
    OpenFrontierV0::from_sites(sites).unwrap()
}

fn carrier(name: &str, frontier: OpenFrontierV0) -> NeutralCarrierV0 {
    NeutralCarrierV0 {
        structure: key(name),
        frontier,
    }
}

fn input(
    subject: OpenFrontierV0,
    method: OpenFrontierV0,
    object: OpenFrontierV0,
) -> MechanismInputV0 {
    MechanismInputV0 {
        subject: carrier("subject", subject),
        method: carrier("method", method),
        object: carrier("object", object),
    }
}

#[test]
fn nine_words_are_three_input_nouns_three_edge_verbs_and_three_output_nouns() {
    assert_eq!(ADVA_FILE_SUFFIX_V0, "adva");
    assert_eq!(
        InputLabelV0::ALL,
        [
            InputLabelV0::Subject,
            InputLabelV0::Method,
            InputLabelV0::Object,
        ]
    );
    assert_eq!(
        MechanismV0::ALL,
        [
            MechanismV0::Compute,
            MechanismV0::Verify,
            MechanismV0::Learn,
        ]
    );
    assert_eq!(
        OutputLabelV0::ALL,
        [
            OutputLabelV0::History,
            OutputLabelV0::Result,
            OutputLabelV0::Evidence,
        ]
    );

    let encoded = serde_json::to_string(&carrier("neutral", OpenFrontierV0::closed())).unwrap();
    assert!(!encoded.contains("program"));
    assert!(!encoded.contains("proof"));
    assert!(!encoded.contains("model"));
}

#[test]
fn frontier_coordinates_are_canonical_and_cannot_change_role_by_aliasing() {
    let first = site(RoleV0::Time, 1, 0);
    let second = site(RoleV0::Space, 0, 1);
    let canonical = frontier([first.clone(), second.clone()]);
    let reversed = frontier([second, first]);
    assert_eq!(canonical, reversed);

    let duplicate = OpenFrontierV0::from_sites([
        site(RoleV0::Construction, 2, 7),
        site(RoleV0::Space, 2, 7),
    ]);
    assert_eq!(
        duplicate,
        Err(MechanismSyntaxErrorV0::DuplicateFrontierCoordinate {
            hole: 2,
            occurrence: 7,
        })
    );
}

#[test]
fn computation_requires_closed_subject_and_object_but_retains_method_interface() {
    let method_site = site(RoleV0::Construction, 0, 0);
    let form = MechanismFormV0::Compute {
        input: input(
            OpenFrontierV0::closed(),
            frontier([method_site.clone()]),
            OpenFrontierV0::closed(),
        ),
    };
    assert_eq!(form.mechanism(), MechanismV0::Compute);
    assert_eq!(
        form.check().unwrap(),
        MechanismAdmissionV0::Compute {
            method_frontier: frontier([method_site]),
        }
    );

    let open_subject = frontier([site(RoleV0::Space, 1, 0)]);
    let subject_error = MechanismFormV0::Compute {
        input: input(
            open_subject.clone(),
            OpenFrontierV0::closed(),
            OpenFrontierV0::closed(),
        ),
    };
    assert_eq!(
        subject_error.check(),
        Err(MechanismSyntaxErrorV0::OpenComputeSubject(open_subject))
    );

    let open_object = frontier([site(RoleV0::Time, 2, 0)]);
    let object_error = MechanismFormV0::Compute {
        input: input(
            OpenFrontierV0::closed(),
            OpenFrontierV0::closed(),
            open_object.clone(),
        ),
    };
    assert_eq!(
        object_error.check(),
        Err(MechanismSyntaxErrorV0::OpenComputeObject(open_object))
    );
}

#[test]
fn verification_accepts_an_exact_open_context_as_conditional() {
    let assumption = site(RoleV0::Construction, 0, 4);
    let open = frontier([assumption]);
    let form = MechanismFormV0::Verify {
        input: input(
            open.clone(),
            OpenFrontierV0::closed(),
            OpenFrontierV0::closed(),
        ),
        declared_subject: open.clone(),
        discharges: Vec::new(),
    };
    assert_eq!(form.mechanism(), MechanismV0::Verify);
    assert_eq!(
        form.check().unwrap(),
        MechanismAdmissionV0::Verify {
            status: VerificationStatusV0::Conditional,
            remaining_subject: open,
        }
    );
}

#[test]
fn verification_requires_explicit_discharge_for_a_declared_but_absent_site() {
    let premise = site(RoleV0::Space, 1, 9);
    let declared = frontier([premise.clone()]);
    let missing = MechanismFormV0::Verify {
        input: input(
            OpenFrontierV0::closed(),
            OpenFrontierV0::closed(),
            OpenFrontierV0::closed(),
        ),
        declared_subject: declared.clone(),
        discharges: Vec::new(),
    };
    assert_eq!(
        missing.check(),
        Err(MechanismSyntaxErrorV0::UnaccountedDeclaredSites(vec![
            premise.clone()
        ]))
    );

    let discharged = MechanismFormV0::Verify {
        input: input(
            OpenFrontierV0::closed(),
            OpenFrontierV0::closed(),
            OpenFrontierV0::closed(),
        ),
        declared_subject: declared,
        discharges: vec![DischargeV0 {
            site: premise,
            witness: key("discharge-witness"),
        }],
    };
    assert_eq!(
        discharged.check().unwrap(),
        MechanismAdmissionV0::Verify {
            status: VerificationStatusV0::Closed,
            remaining_subject: OpenFrontierV0::closed(),
        }
    );
}

#[test]
fn verification_rejects_an_undeclared_or_simultaneously_discharged_open_site() {
    let open_site = site(RoleV0::Time, 2, 5);
    let open = frontier([open_site.clone()]);
    let undeclared = MechanismFormV0::Verify {
        input: input(
            open.clone(),
            OpenFrontierV0::closed(),
            OpenFrontierV0::closed(),
        ),
        declared_subject: OpenFrontierV0::closed(),
        discharges: Vec::new(),
    };
    assert_eq!(
        undeclared.check(),
        Err(MechanismSyntaxErrorV0::UndeclaredVerificationSites(vec![
            open_site.clone()
        ]))
    );

    let double_account = MechanismFormV0::Verify {
        input: input(
            open.clone(),
            OpenFrontierV0::closed(),
            OpenFrontierV0::closed(),
        ),
        declared_subject: open,
        discharges: vec![DischargeV0 {
            site: open_site.clone(),
            witness: key("impossible-discharge"),
        }],
    };
    assert_eq!(
        double_account.check(),
        Err(MechanismSyntaxErrorV0::DischargedOpenSite(open_site))
    );
}

#[test]
fn learning_returns_a_partial_fill_plan_and_retains_new_subholes() {
    let target = site(RoleV0::Construction, 0, 0);
    let untouched = site(RoleV0::Space, 1, 0);
    let subhole = site(RoleV0::Time, 2, 8);
    let subject = frontier([target.clone(), untouched.clone()]);
    let form = MechanismFormV0::Learn {
        input: input(
            subject,
            OpenFrontierV0::closed(),
            OpenFrontierV0::closed(),
        ),
        plan: FillPlanV0 {
            assignments: vec![FillAssignmentV0 {
                target: target.clone(),
                replacement: carrier("candidate", frontier([subhole.clone()])),
                evidence: Some(key("candidate-evidence")),
            }],
        },
    };
    assert_eq!(form.mechanism(), MechanismV0::Learn);
    assert_eq!(
        form.check().unwrap(),
        MechanismAdmissionV0::Learn {
            filled_subject: frontier([target]),
            remaining_subject: frontier([untouched, subhole]),
        }
    );
}

#[test]
fn learning_requires_an_open_subject_and_an_actual_target() {
    let closed = MechanismFormV0::Learn {
        input: input(
            OpenFrontierV0::closed(),
            OpenFrontierV0::closed(),
            OpenFrontierV0::closed(),
        ),
        plan: FillPlanV0 {
            assignments: Vec::new(),
        },
    };
    assert_eq!(
        closed.check(),
        Err(MechanismSyntaxErrorV0::ClosedLearningSubject)
    );

    let actual = site(RoleV0::Construction, 0, 1);
    let unknown = site(RoleV0::Construction, 0, 2);
    let form = MechanismFormV0::Learn {
        input: input(
            frontier([actual]),
            OpenFrontierV0::closed(),
            OpenFrontierV0::closed(),
        ),
        plan: FillPlanV0 {
            assignments: vec![FillAssignmentV0 {
                target: unknown.clone(),
                replacement: carrier("candidate", OpenFrontierV0::closed()),
                evidence: None,
            }],
        },
    };
    assert_eq!(
        form.check(),
        Err(MechanismSyntaxErrorV0::UnknownLearningTarget(unknown))
    );
}

#[test]
fn learning_rejects_implicit_contraction_and_frontier_collision() {
    let target = site(RoleV0::Construction, 0, 0);
    let repeated = FillAssignmentV0 {
        target: target.clone(),
        replacement: carrier("candidate-a", OpenFrontierV0::closed()),
        evidence: None,
    };
    let duplicate_target = MechanismFormV0::Learn {
        input: input(
            frontier([target.clone()]),
            OpenFrontierV0::closed(),
            OpenFrontierV0::closed(),
        ),
        plan: FillPlanV0 {
            assignments: vec![
                repeated.clone(),
                FillAssignmentV0 {
                    replacement: carrier("candidate-b", OpenFrontierV0::closed()),
                    ..repeated
                },
            ],
        },
    };
    assert_eq!(
        duplicate_target.check(),
        Err(MechanismSyntaxErrorV0::RepeatedLearningTarget(
            target.clone()
        ))
    );

    let untouched = site(RoleV0::Space, 1, 0);
    let colliding = site(RoleV0::Time, untouched.hole, untouched.occurrence);
    let collision = MechanismFormV0::Learn {
        input: input(
            frontier([target.clone(), untouched]),
            OpenFrontierV0::closed(),
            OpenFrontierV0::closed(),
        ),
        plan: FillPlanV0 {
            assignments: vec![FillAssignmentV0 {
                target,
                replacement: carrier("candidate", frontier([colliding.clone()])),
                evidence: None,
            }],
        },
    };
    assert_eq!(
        collision.check(),
        Err(MechanismSyntaxErrorV0::ReplacementFrontierCollision(
            colliding
        ))
    );
}

#[test]
fn mechanism_forms_round_trip_without_promoting_contextual_carrier_kinds() {
    let form = MechanismFormV0::Compute {
        input: input(
            OpenFrontierV0::closed(),
            frontier([site(RoleV0::Construction, 0, 0)]),
            OpenFrontierV0::closed(),
        ),
    };
    let encoded = serde_json::to_string_pretty(&form).unwrap();
    let decoded: MechanismFormV0 = serde_json::from_str(&encoded).unwrap();
    assert_eq!(decoded, form);
    assert!(encoded.contains("\"mechanism\": \"compute\""));
    assert!(!encoded.contains("carrier_kind"));
}

#[test]
fn output_persistence_uses_three_labels_without_changing_carrier_kind() {
    let output = MechanismOutputV0 {
        history: carrier("history", OpenFrontierV0::closed()),
        result: carrier("result", OpenFrontierV0::closed()),
        evidence: carrier("evidence", OpenFrontierV0::closed()),
    };
    let encoded = serde_json::to_string(&output).unwrap();
    assert!(encoded.contains("\"history\""));
    assert!(encoded.contains("\"result\""));
    assert!(encoded.contains("\"evidence\""));
    assert!(!encoded.contains("program"));
    assert!(!encoded.contains("proof"));
    assert!(!encoded.contains("model"));
}
