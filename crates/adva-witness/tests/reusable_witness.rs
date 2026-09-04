use adva_ir::DiagramValidationArtifact;
use adva_lisp::{compile_function, link_modules, parse_module, validate_diagram};
use adva_witness::{
    ArtifactKeyV0, BoundaryChargeV0, BoundaryCoordinateV0, BoundaryTermV0, CellTemplateV0,
    ExactExprV0, HoleBindingV0, HoleSpecV0, RelationWordV0, RoleV0, SeedErrorV0, SeedRegistryV0,
    SeedRuleV0, TemplateIdV0, TermGlyphV0, TypeWordV0, ValueWordV0, WitnessErrorV0, WitnessProofV0,
    WitnessStoreV0, validate_dependency_graph_v0,
};
use num_bigint::BigInt;
use std::collections::BTreeMap;

fn expression() -> ExactExprV0 {
    ExactExprV0::sum(
        ExactExprV0::variable("x"),
        ExactExprV0::product(ExactExprV0::variable("y"), ExactExprV0::variable("z")),
    )
}

fn holes() -> [HoleSpecV0; 3] {
    [
        HoleSpecV0 {
            index: 0,
            role: RoleV0::Construction,
            variable: "x".to_owned(),
        },
        HoleSpecV0 {
            index: 1,
            role: RoleV0::Space,
            variable: "y".to_owned(),
        },
        HoleSpecV0 {
            index: 2,
            role: RoleV0::Time,
            variable: "z".to_owned(),
        },
    ]
}

fn checked_diagram(module_name: &str) -> DiagramValidationArtifact {
    let source = format!(
        "(module {module_name}
           (export pass)
           (def pass
             (fn ((x Real) (y Real) (z Real)) (outputs Real Real Real)
               (frontier (use x) (use y) (use z)))))"
    );
    let module = parse_module(&source).unwrap();
    let linked = link_modules(vec![module]).unwrap();
    let compiled = compile_function(&linked, module_name, "pass").unwrap();
    validate_diagram(compiled.result).unwrap()
}

fn checked_shared_diagram(module_name: &str) -> DiagramValidationArtifact {
    let source = format!(
        "(module {module_name}
           (export pass)
           (def pass
             (fn ((x Real) (z Real)) (outputs Real Real Real)
               (frontier (copy (use x)) (use z)))))"
    );
    let module = parse_module(&source).unwrap();
    let linked = link_modules(vec![module]).unwrap();
    let compiled = compile_function(&linked, module_name, "pass").unwrap();
    validate_diagram(compiled.result).unwrap()
}

fn bindings(diagram: &DiagramValidationArtifact) -> [HoleBindingV0; 3] {
    assert_eq!(diagram.result.outputs.len(), 3);
    let binding = |index: usize, role: RoleV0| {
        let lineage = &diagram.result.outputs[index].lineage;
        assert_eq!(lineage.len(), 1);
        let occurrence = diagram
            .result
            .occurrences
            .iter()
            .find(|occurrence| occurrence.id == lineage[0])
            .unwrap();
        HoleBindingV0 {
            hole_index: u8::try_from(index).unwrap(),
            role,
            source: occurrence.source.clone(),
            occurrence: occurrence.id.clone(),
            path: occurrence.path.clone(),
        }
    };
    [
        binding(0, RoleV0::Construction),
        binding(1, RoleV0::Space),
        binding(2, RoleV0::Time),
    ]
}

fn insert_seed_children(store: &mut WitnessStoreV0) -> [ArtifactKeyV0; 3] {
    [
        store
            .insert(WitnessProofV0::Seed {
                term: TermGlyphV0::Construction,
            })
            .unwrap(),
        store
            .insert(WitnessProofV0::Seed {
                term: TermGlyphV0::Space,
            })
            .unwrap(),
        store
            .insert(WitnessProofV0::Seed {
                term: TermGlyphV0::Time,
            })
            .unwrap(),
    ]
}

fn insert_closed_body(store: &mut WitnessStoreV0, expr: ExactExprV0) -> ArtifactKeyV0 {
    let transition = store
        .insert(WitnessProofV0::ArithmeticTransition {
            actual_boundary: BoundaryChargeV0::zero(),
            declared_boundary: BoundaryChargeV0::zero(),
            before: expr.clone(),
            after: expr,
        })
        .unwrap();
    store
        .insert(WitnessProofV0::Seal { body: transition })
        .unwrap()
}

#[test]
fn corrected_six_seed_registry_is_balanced() {
    let registry = SeedRegistryV0::canonical();
    assert_eq!(registry.verify_all().unwrap().len(), 6);
    let surfaces = registry
        .rules()
        .iter()
        .map(|rule| {
            (
                rule.term.surface(),
                rule.type_word.surface(),
                rule.value_word.surface(),
            )
        })
        .collect::<Vec<_>>();
    assert_eq!(
        surfaces,
        vec![
            ("{}", "[] > ()".to_owned(), "() < []".to_owned()),
            ("[]", "() > {}".to_owned(), "{} < ()".to_owned()),
            ("()", "{} > []".to_owned(), "[] < {}".to_owned()),
            ("|", "|||".to_owned(), "1".to_owned()),
            (">", "<|>".to_owned(), "+".to_owned()),
            ("<", ">|<".to_owned(), "*".to_owned()),
        ]
    );

    let unit = registry.rule(TermGlyphV0::Unit).unwrap();
    assert!(matches!(
        &unit.value_word,
        ValueWordV0::Unit { support } if support == &[0, 1, 2]
    ));
}

#[test]
fn original_typo_and_erased_unit_multiplicity_are_rejected() {
    use RoleV0::{Construction as K, Space as X, Time as T};
    let typo = SeedRuleV0 {
        term: TermGlyphV0::Construction,
        type_word: TypeWordV0::Relation {
            word: RelationWordV0::greater(X, K),
        },
        value_word: ValueWordV0::Relation {
            word: RelationWordV0::less(T, X),
        },
    };
    assert!(matches!(
        typo.verify(),
        Err(SeedErrorV0::UnbalancedRule { .. })
    ));

    let collapsed_unit = SeedRuleV0 {
        term: TermGlyphV0::Unit,
        type_word: TypeWordV0::UnitTriplet,
        value_word: ValueWordV0::Unit { support: vec![1] },
    };
    assert!(matches!(
        collapsed_unit.verify(),
        Err(SeedErrorV0::UnbalancedRule { .. })
    ));
}

#[test]
fn exact_polynomial_normalization_proves_distributivity_ratio_one() {
    let x = ExactExprV0::variable("x");
    let y = ExactExprV0::variable("y");
    let z = ExactExprV0::variable("z");
    let factored = ExactExprV0::product(x.clone(), ExactExprV0::sum(y.clone(), z.clone()));
    let expanded = ExactExprV0::sum(
        ExactExprV0::product(x.clone(), y),
        ExactExprV0::product(x, z),
    );
    assert_eq!(factored.normalize().unwrap(), expanded.normalize().unwrap());
}

#[test]
fn template_artifact_is_reused_but_instances_and_occurrences_are_fresh() {
    let mut store = WitnessStoreV0::new();
    let children = insert_seed_children(&mut store);
    let body = insert_closed_body(&mut store, expression());
    let template = CellTemplateV0::new(
        TemplateIdV0::new("triadic-fma@0").unwrap(),
        holes(),
        expression(),
        body,
    )
    .unwrap()
    .form(&store)
    .unwrap();

    let first_diagram = checked_diagram("first_witness_use");
    let second_diagram = checked_diagram("second_witness_use");

    let first = template
        .instantiate(
            &mut store,
            &first_diagram,
            bindings(&first_diagram),
            children.clone(),
        )
        .unwrap();
    let second = template
        .instantiate(
            &mut store,
            &second_diagram,
            bindings(&second_diagram),
            children,
        )
        .unwrap();

    assert_eq!(first.artifact, second.artifact);
    assert_ne!(first.id, second.id);
    assert_ne!(first.program, second.program);
    assert_ne!(first.bindings, second.bindings);
    assert_eq!(store.len(), 6);

    let first_result = first
        .execute(&store, [BigInt::from(2), BigInt::from(3), BigInt::from(4)])
        .unwrap();
    let second_result = second
        .execute(&store, [BigInt::from(5), BigInt::from(2), BigInt::from(3)])
        .unwrap();
    assert_eq!(first_result.value, BigInt::from(14));
    assert_eq!(second_result.value, BigInt::from(11));
    assert_ne!(first_result.instance, second_result.instance);
}

#[test]
fn one_occurrence_cannot_fill_two_holes_implicitly() {
    let mut store = WitnessStoreV0::new();
    let children = insert_seed_children(&mut store);
    let body = insert_closed_body(&mut store, expression());
    let template = CellTemplateV0::new(
        TemplateIdV0::new("no-alias@0").unwrap(),
        holes(),
        expression(),
        body,
    )
    .unwrap()
    .form(&store)
    .unwrap();
    let diagram = checked_diagram("alias_witness_use");
    let mut invalid = bindings(&diagram);
    invalid[1].occurrence = invalid[0].occurrence.clone();
    assert!(matches!(
        template.instantiate(&mut store, &diagram, invalid, children),
        Err(WitnessErrorV0::ImplicitOccurrenceAlias(_))
    ));
}

#[test]
fn explicit_copy_may_bind_distinct_occurrences_of_one_source() {
    let mut store = WitnessStoreV0::new();
    let children = insert_seed_children(&mut store);
    let body = insert_closed_body(&mut store, expression());
    let template = CellTemplateV0::new(
        TemplateIdV0::new("explicit-share@0").unwrap(),
        holes(),
        expression(),
        body,
    )
    .unwrap()
    .form(&store)
    .unwrap();
    let diagram = checked_shared_diagram("explicit_share_witness_use");
    let bindings = bindings(&diagram);
    assert_eq!(bindings[0].source, bindings[1].source);
    assert_ne!(bindings[0].occurrence, bindings[1].occurrence);
    assert_ne!(bindings[0].path, bindings[1].path);
    template
        .instantiate(&mut store, &diagram, bindings, children)
        .unwrap();
}

#[test]
fn intermediate_zero_faults_even_when_the_outer_result_would_be_nonzero() {
    let result = ExactExprV0::sum(
        ExactExprV0::sum(ExactExprV0::variable("x"), ExactExprV0::variable("y")),
        ExactExprV0::variable("z"),
    );
    let mut store = WitnessStoreV0::new();
    let children = insert_seed_children(&mut store);
    let body = insert_closed_body(&mut store, result.clone());
    let diagram = checked_diagram("zero_witness_use");
    let instance = CellTemplateV0::new(
        TemplateIdV0::new("zero-guard@0").unwrap(),
        holes(),
        result,
        body,
    )
    .unwrap()
    .form(&store)
    .unwrap()
    .instantiate(&mut store, &diagram, bindings(&diagram), children)
    .unwrap();

    let error = instance
        .execute(&store, [BigInt::from(1), BigInt::from(-1), BigInt::from(2)])
        .unwrap_err();
    assert!(matches!(
        error,
        WitnessErrorV0::Arithmetic(adva_witness::ArithmeticErrorV0::ZeroFault { .. })
    ));
}

#[test]
fn nonunit_transport_cannot_execute_or_be_sealed() {
    let mut store = WitnessStoreV0::new();
    let children = insert_seed_children(&mut store);
    let transition = store
        .insert(WitnessProofV0::ArithmeticTransition {
            actual_boundary: BoundaryChargeV0::zero(),
            declared_boundary: BoundaryChargeV0::zero(),
            before: ExactExprV0::variable("x"),
            after: ExactExprV0::sum(ExactExprV0::variable("x"), ExactExprV0::constant(1)),
        })
        .unwrap();
    assert!(matches!(
        store.insert(WitnessProofV0::Seal {
            body: transition.clone()
        }),
        Err(WitnessErrorV0::UnclosedMultiplicativeResidual { .. })
    ));

    let diagram = checked_diagram("nonunit_witness_use");
    let instance = CellTemplateV0::new(
        TemplateIdV0::new("nonunit@0").unwrap(),
        holes(),
        expression(),
        transition,
    )
    .unwrap()
    .form(&store)
    .unwrap()
    .instantiate(&mut store, &diagram, bindings(&diagram), children)
    .unwrap();
    assert!(matches!(
        instance.execute(&store, [BigInt::from(1), BigInt::from(2), BigInt::from(3)]),
        Err(WitnessErrorV0::UnclosedMultiplicativeResidual { .. })
    ));
}

#[test]
fn nonzero_relative_boundary_cannot_form_or_enter_composition() {
    let mut store = WitnessStoreV0::new();
    let actual = BoundaryChargeV0::from_terms([BoundaryTermV0::new(
        BoundaryCoordinateV0::Role {
            role: RoleV0::Construction,
        },
        1,
    )])
    .unwrap();
    let unformed = store
        .insert(WitnessProofV0::ArithmeticTransition {
            actual_boundary: actual,
            declared_boundary: BoundaryChargeV0::zero(),
            before: expression(),
            after: expression(),
        })
        .unwrap();
    assert!(matches!(
        CellTemplateV0::new(
            TemplateIdV0::new("unformed@0").unwrap(),
            holes(),
            expression(),
            unformed.clone(),
        )
        .unwrap()
        .form(&store),
        Err(WitnessErrorV0::UnformedDependency(_))
    ));

    let seed = store
        .insert(WitnessProofV0::Seed {
            term: TermGlyphV0::Unit,
        })
        .unwrap();
    assert!(matches!(
        store.insert(WitnessProofV0::Compose {
            left: unformed,
            connector: seed.clone(),
            right: seed,
        }),
        Err(WitnessErrorV0::UnformedDependency(_))
    ));
}

#[test]
fn dependency_cycles_are_rejected_before_evaluation() {
    let a = ArtifactKeyV0::cache_label("a").unwrap();
    let b = ArtifactKeyV0::cache_label("b").unwrap();
    let graph = BTreeMap::from([
        (a.clone(), WitnessProofV0::Seal { body: b.clone() }),
        (b, WitnessProofV0::Seal { body: a }),
    ]);
    assert!(matches!(
        validate_dependency_graph_v0(&graph),
        Err(WitnessErrorV0::CyclicDependency(_))
    ));
}

#[test]
fn template_result_must_be_linear_in_its_three_declared_holes() {
    let result = ExactExprV0::sum(
        ExactExprV0::variable("x"),
        ExactExprV0::sum(ExactExprV0::variable("x"), ExactExprV0::variable("z")),
    );
    assert!(matches!(
        CellTemplateV0::new(
            TemplateIdV0::new("nonlinear@0").unwrap(),
            holes(),
            result,
            ArtifactKeyV0::cache_label("unused-body").unwrap(),
        ),
        Err(WitnessErrorV0::NonlinearTemplateVariable(variable)) if variable == "x"
    ));
}
