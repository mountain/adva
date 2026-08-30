use adva_ir::{CutConsumer, NodeId};
use adva_lisp::{
    advance_causal_cut, analyze_causal_cut, compile_function, link_modules, parse_module,
};

fn shared_sum() -> adva_ir::SharedProgramDiagram {
    let module = parse_module(
        "(module process (export shared-sum) \
         (def shared-sum (fn ((x Real)) Real (add (copy (use x))))))",
    )
    .unwrap();
    let linked = link_modules(vec![module]).unwrap();
    compile_function(&linked, "process", "shared-sum")
        .unwrap()
        .result
}

#[test]
fn causal_cuts_are_derived_from_the_checked_operation_dag() {
    let diagram = shared_sum();

    let initial = analyze_causal_cut(&diagram, &[]).unwrap();
    assert!(initial.certificate.certified());
    assert!(initial.result.completed.is_empty());
    assert_eq!(initial.result.frontier.len(), 1);
    assert_eq!(
        initial.result.frontier[0].consumer,
        CutConsumer::Node {
            node: NodeId(0),
            input_index: 0
        }
    );

    let branched = analyze_causal_cut(&diagram, &[NodeId(0)]).unwrap();
    assert!(branched.certificate.certified());
    assert_eq!(branched.result.frontier.len(), 2);
    let left = &branched.result.frontier[0].wire.lineage[0];
    let right = &branched.result.frontier[1].wire.lineage[0];
    assert_ne!(left, right);
    assert_eq!(
        branched.result.frontier[0].sources,
        branched.result.frontier[1].sources
    );
    let partition = diagram.source_partition();
    let source_members = partition.values().next().unwrap();
    assert!(source_members.contains(left));
    assert!(source_members.contains(right));

    let final_cut = analyze_causal_cut(&diagram, &[NodeId(0), NodeId(1)]).unwrap();
    assert_eq!(final_cut.result.frontier.len(), 1);
    assert_eq!(
        final_cut.result.frontier[0].consumer,
        CutConsumer::Output { index: 0 }
    );
}

#[test]
fn one_causal_step_records_frontier_replacement_without_evaluation() {
    let diagram = shared_sum();
    let step = advance_causal_cut(&diagram, &[], NodeId(0)).unwrap();
    assert!(step.certificate.certified());
    assert_eq!(step.result.consumed.len(), 1);
    assert_eq!(step.result.produced.len(), 2);
    assert_eq!(step.result.before.frontier.len(), 1);
    assert_eq!(step.result.after.frontier.len(), 2);
}

#[test]
fn a_cut_cannot_contain_an_event_without_its_causal_past() {
    let error = analyze_causal_cut(&shared_sum(), &[NodeId(1)]).unwrap_err();
    assert!(error.to_string().contains("without predecessors"));
}
