//! Native source-fibre instantiation of the proposed quotient-query gate.
//!
//! This is a research test, not a stable API. Rust compiles and validates two
//! programs, constructs their complete `ProgramSlice` values, and reads exact
//! source and occurrence identities from the checked upper cuts. A proposition
//! may descend through the source quotient only when it is constant on every
//! source fibre.

use adva_ir::{
    HistoryEvent, SourceId, TriadicCutIncidenceV0, TriadicDomainV0, TriadicObserverPolicyV0,
};
use adva_lisp::{
    analyze_triadic_observer_transition_v0, compile_function, link_modules, parse_module,
};
use std::collections::{BTreeMap, BTreeSet};

const MODULE: &str = r#"
(module native-source-fibre-gate
  (export one-copy two-copy)

  (def one-copy
    (fn ((temporal Real) (spatial Real) (construction Real))
        (outputs Real Real Real Real)
      (frontier
        (copy (use temporal))
        (id (use spatial))
        (id (use construction)))))

  (def two-copy
    (fn ((temporal Real) (spatial Real) (construction Real))
        (outputs Real Real Real Real Real)
      (frontier
        (copy (use temporal))
        (copy (use spatial))
        (id (use construction)))))
)
"#;

#[derive(Clone, Debug, Eq, PartialEq)]
enum QueryGate<L> {
    Descends(BTreeSet<L>),
    NonSaturated { left: usize, right: usize },
}

/// Check one proposition on a finite carrier against an explicit quotient.
///
/// Work is counted as ordered fibre comparisons, plus one full pullback pass
/// when the proposition descends. The full pair scan is retained even after a
/// first obstruction so the declared finite cost does not depend on witness
/// order.
fn gate_query<L: Clone + Ord>(quotient: &[L], selected: &BTreeSet<usize>) -> (QueryGate<L>, usize) {
    assert!(selected.iter().all(|index| *index < quotient.len()));

    let mut first_obstruction = None;
    let mut work = 0usize;
    for left in 0..quotient.len() {
        for right in 0..quotient.len() {
            work += 1;
            if first_obstruction.is_none()
                && quotient[left] == quotient[right]
                && selected.contains(&left) != selected.contains(&right)
            {
                first_obstruction = Some((left, right));
            }
        }
    }

    if let Some((left, right)) = first_obstruction {
        return (QueryGate::NonSaturated { left, right }, work);
    }

    let labels = selected
        .iter()
        .map(|index| quotient[*index].clone())
        .collect::<BTreeSet<_>>();
    let pullback = quotient
        .iter()
        .enumerate()
        .filter_map(|(index, label)| labels.contains(label).then_some(index))
        .collect::<BTreeSet<_>>();
    work += quotient.len();
    assert_eq!(
        pullback, *selected,
        "a descended query must pull back to the original proposition"
    );
    (QueryGate::Descends(labels), work)
}

fn compile(name: &str) -> adva_ir::CompilationArtifact {
    let module = parse_module(MODULE).unwrap();
    let linked = link_modules(vec![module]).unwrap();
    compile_function(&linked, "native-source-fibre-gate", name).unwrap()
}

fn policy() -> TriadicObserverPolicyV0 {
    TriadicObserverPolicyV0 {
        input_domains: vec![
            TriadicDomainV0::Time,
            TriadicDomainV0::Space,
            TriadicDomainV0::Construction,
        ],
    }
}

fn source_fibres(incidences: &[TriadicCutIncidenceV0]) -> BTreeMap<SourceId, Vec<usize>> {
    let mut fibres = BTreeMap::new();
    for (index, incidence) in incidences.iter().enumerate() {
        fibres
            .entry(incidence.occurrence.source.clone())
            .or_insert_with(Vec::new)
            .push(index);
    }
    fibres
}

fn check_fibre(incidences: &[TriadicCutIncidenceV0], indices: &[usize]) -> (usize, usize) {
    assert_eq!(indices.len(), 2, "the declared fixture uses copy siblings");

    let quotient = incidences
        .iter()
        .map(|incidence| incidence.occurrence.source.clone())
        .collect::<Vec<_>>();
    let selected_fibre = indices.iter().copied().collect::<BTreeSet<_>>();
    let source = incidences[indices[0]].occurrence.source.clone();

    let (positive, positive_work) = gate_query(&quotient, &selected_fibre);
    assert_eq!(
        positive,
        QueryGate::Descends(BTreeSet::from([source.clone()]))
    );

    let selected_occurrence = BTreeSet::from([indices[0]]);
    let (negative, negative_work) = gate_query(&quotient, &selected_occurrence);
    let (left, right) = match negative {
        QueryGate::NonSaturated { left, right } => (left, right),
        QueryGate::Descends(_) => panic!("one copied occurrence must not descend by source"),
    };
    assert_eq!(quotient[left], quotient[right]);
    assert_ne!(
        selected_occurrence.contains(&left),
        selected_occurrence.contains(&right)
    );
    assert_ne!(
        incidences[left].occurrence.id,
        incidences[right].occurrence.id
    );
    assert_ne!(
        incidences[left].occurrence.path,
        incidences[right].occurrence.path
    );

    (positive_work, negative_work)
}

#[test]
fn one_copy_accepts_the_source_fibre_and_rejects_one_sibling() {
    let artifact = compile("one-copy");
    let all = artifact
        .result
        .nodes
        .iter()
        .map(|node| node.id)
        .collect::<Vec<_>>();
    let transition =
        analyze_triadic_observer_transition_v0(&artifact.result, &policy(), &[], &all).unwrap();
    assert!(transition.certificate.certified());

    let result = &transition.result;
    assert_eq!(result.upper.incidences.len(), 4);
    assert!(result.upper.source_free_wire_indices.is_empty());
    assert!(
        result
            .upper
            .incidences
            .iter()
            .all(|incidence| result.slice.occurrences.contains(&incidence.occurrence))
    );
    assert_eq!(
        result
            .slice
            .event_history
            .iter()
            .filter(|event| matches!(event, HistoryEvent::Copy { .. }))
            .count(),
        1
    );

    let fibres = source_fibres(&result.upper.incidences);
    let duplicated = fibres
        .values()
        .filter(|indices| indices.len() == 2)
        .collect::<Vec<_>>();
    assert_eq!(duplicated.len(), 1);
    assert_eq!(
        fibres.values().map(Vec::len).collect::<Vec<_>>(),
        vec![2, 1, 1]
    );

    let (positive_work, negative_work) = check_fibre(&result.upper.incidences, duplicated[0]);
    assert_eq!((positive_work, negative_work), (20, 16));
    assert_eq!(positive_work + negative_work, 36);
}

#[test]
fn two_copy_reuses_the_gate_on_two_independent_source_fibres() {
    let artifact = compile("two-copy");
    let all = artifact
        .result
        .nodes
        .iter()
        .map(|node| node.id)
        .collect::<Vec<_>>();
    let transition =
        analyze_triadic_observer_transition_v0(&artifact.result, &policy(), &[], &all).unwrap();
    assert!(transition.certificate.certified());

    let result = &transition.result;
    assert_eq!(result.upper.incidences.len(), 5);
    assert!(result.upper.source_free_wire_indices.is_empty());
    assert!(
        result
            .upper
            .incidences
            .iter()
            .all(|incidence| result.slice.occurrences.contains(&incidence.occurrence))
    );
    assert_eq!(
        result
            .slice
            .event_history
            .iter()
            .filter(|event| matches!(event, HistoryEvent::Copy { .. }))
            .count(),
        2
    );

    let fibres = source_fibres(&result.upper.incidences);
    let duplicated = fibres
        .values()
        .filter(|indices| indices.len() == 2)
        .collect::<Vec<_>>();
    assert_eq!(duplicated.len(), 2);
    let mut multiplicities = fibres.values().map(Vec::len).collect::<Vec<_>>();
    multiplicities.sort_unstable();
    assert_eq!(multiplicities, vec![1, 2, 2]);

    let mut work = 0usize;
    for indices in duplicated {
        let (positive_work, negative_work) = check_fibre(&result.upper.incidences, indices);
        assert_eq!((positive_work, negative_work), (30, 25));
        work += positive_work + negative_work;
    }
    assert_eq!(work, 110);
}
