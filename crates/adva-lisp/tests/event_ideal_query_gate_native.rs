//! Event-ideal instantiation of the proposed quotient-query gate.
//!
//! This research test keeps a certified schedule word beside one canonical
//! `ProgramSlice`.  Projecting a schedule receipt to its final completed event
//! ideal forgets route order.  A proposition may descend only when it is
//! constant on the complete fibre of legal schedules with that ideal.

use adva_ir::NodeId;
use adva_lisp::{
    advance_causal_cut, analyze_program_slice, compile_function, link_modules, parse_module,
};
use std::collections::BTreeSet;

const MODULE: &str = r#"
(module native-event-ideal-gate
  (export independent-diamond independent-three)

  (def independent-diamond
    (fn ((left Real) (right Real)) Real
      (add
        (frontier
          (neg (use left))
          (id (use right))))))

  (def independent-three
    (fn ((temporal Real) (spatial Real) (construction Real))
        (outputs Real Real Real Real Real)
      (frontier
        (copy (use temporal))
        (copy (use spatial))
        (id (use construction)))))
)
"#;

#[derive(Clone, Debug, Eq, PartialEq)]
struct ScheduleReceipt {
    word: Vec<NodeId>,
    cut_path: Vec<Vec<NodeId>>,
    final_ideal: Vec<NodeId>,
}

#[derive(Clone, Debug, Eq, PartialEq)]
enum QueryGate<L> {
    Descends(BTreeSet<L>),
    NonSaturated { left: usize, right: usize },
}

fn compile(name: &str) -> adva_ir::CompilationArtifact {
    let module = parse_module(MODULE).unwrap();
    let linked = link_modules(vec![module]).unwrap();
    compile_function(&linked, "native-event-ideal-gate", name).unwrap()
}

fn receive_schedule(artifact: &adva_ir::CompilationArtifact, word: &[NodeId]) -> ScheduleReceipt {
    let mut completed = Vec::new();
    let mut cut_path = vec![completed.clone()];
    for event in word {
        let step = advance_causal_cut(&artifact.result, &completed, *event).unwrap();
        assert!(step.certificate.certified());
        assert_eq!(step.result.before.completed, completed);
        completed = step.result.after.completed;
        cut_path.push(completed.clone());
    }

    let all = artifact
        .result
        .nodes
        .iter()
        .map(|node| node.id)
        .collect::<Vec<_>>();
    assert_eq!(completed, all);

    ScheduleReceipt {
        word: word.to_vec(),
        cut_path,
        final_ideal: completed,
    }
}

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
    assert_eq!(pullback, *selected);
    (QueryGate::Descends(labels), work)
}

fn check_fibre(
    artifact: &adva_ir::CompilationArtifact,
    words: &[Vec<NodeId>],
    expected_work: (usize, usize),
) {
    let all = artifact
        .result
        .nodes
        .iter()
        .map(|node| node.id)
        .collect::<Vec<_>>();
    let slice = analyze_program_slice(&artifact.result, &[], &all).unwrap();
    assert!(slice.certificate.certified());

    let receipts = words
        .iter()
        .map(|word| receive_schedule(artifact, word))
        .collect::<Vec<_>>();
    assert!(receipts.windows(2).all(|pair| pair[0].word != pair[1].word));
    assert!(
        receipts
            .windows(2)
            .any(|pair| pair[0].cut_path != pair[1].cut_path)
    );
    assert!(
        receipts
            .iter()
            .all(|receipt| receipt.final_ideal == slice.result.upper.completed)
    );

    let quotient = receipts
        .iter()
        .map(|receipt| receipt.final_ideal.clone())
        .collect::<Vec<_>>();
    let whole_fibre = (0..receipts.len()).collect::<BTreeSet<_>>();
    let (positive, positive_work) = gate_query(&quotient, &whole_fibre);
    assert_eq!(positive, QueryGate::Descends(BTreeSet::from([all.clone()])));

    let first_event = words[0][0];
    let first_sensitive = receipts
        .iter()
        .enumerate()
        .filter_map(|(index, receipt)| (receipt.word[0] == first_event).then_some(index))
        .collect::<BTreeSet<_>>();
    assert!(!first_sensitive.is_empty());
    assert_ne!(first_sensitive.len(), receipts.len());
    let (negative, negative_work) = gate_query(&quotient, &first_sensitive);
    let (left, right) = match negative {
        QueryGate::NonSaturated { left, right } => (left, right),
        QueryGate::Descends(_) => panic!("a first-event query must not descend by final ideal"),
    };
    assert_eq!(receipts[left].final_ideal, receipts[right].final_ideal);
    assert_ne!(
        first_sensitive.contains(&left),
        first_sensitive.contains(&right)
    );
    assert_ne!(receipts[left].word, receipts[right].word);
    assert_ne!(receipts[left].cut_path, receipts[right].cut_path);
    assert_eq!((positive_work, negative_work), expected_work);
}

#[test]
fn diamond_final_ideal_accepts_the_whole_fibre_and_rejects_route_order() {
    let artifact = compile("independent-diamond");
    let nodes = artifact
        .result
        .nodes
        .iter()
        .map(|node| node.id)
        .collect::<Vec<_>>();
    assert_eq!(nodes.len(), 3);

    let words = vec![
        vec![nodes[0], nodes[1], nodes[2]],
        vec![nodes[1], nodes[0], nodes[2]],
    ];
    check_fibre(&artifact, &words, (6, 4));
}

#[test]
fn three_independent_events_reuse_the_gate_on_all_six_schedules() {
    let artifact = compile("independent-three");
    let nodes = artifact
        .result
        .nodes
        .iter()
        .map(|node| node.id)
        .collect::<Vec<_>>();
    assert_eq!(nodes.len(), 3);

    let words = vec![
        vec![nodes[0], nodes[1], nodes[2]],
        vec![nodes[0], nodes[2], nodes[1]],
        vec![nodes[1], nodes[0], nodes[2]],
        vec![nodes[1], nodes[2], nodes[0]],
        vec![nodes[2], nodes[0], nodes[1]],
        vec![nodes[2], nodes[1], nodes[0]],
    ];
    check_fibre(&artifact, &words, (42, 36));
}
