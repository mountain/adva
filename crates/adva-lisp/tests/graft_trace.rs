use adva_ir::{GraftFrame, GraftFrameKind, GraftRegionRole, NodeId};
use adva_lisp::{compile_function, link_modules, parse_module};

const NESTED_TWO_HOLE: &str = r#"
(module graft-trace
  (export root hidden-argument)

  (def neg-one
    (fn ((x Real)) Real
      (neg (use x))))

  (def id-one
    (fn ((x Real)) Real
      (id (use x))))

  (def add-two
    (fn ((left Real) (right Real)) Real
      (add
        (frontier
          (use left)
          (use right)))))

  (def pair
    (fn ((left Real) (right Real)) Real
      (call add-two
        (use left)
        (use right))))

  (def root
    (fn ((x Real) (y Real)) Real
      (call pair
        (frontier
          (call neg-one (use x))
          (call id-one (use y))))))

  (def hidden-argument
    (fn ((x Real) (y Real)) Real
      (call pair
        (discard 1)
        (frontier
          (use x)
          (use y)))))
)
"#;

fn compile(name: &str) -> adva_ir::CompilationArtifact {
    let module = parse_module(NESTED_TWO_HOLE).unwrap();
    let linked = link_modules(vec![module]).unwrap();
    compile_function(&linked, "graft-trace", name).unwrap()
}

fn call_frame<'a>(
    trace: &'a adva_ir::GraftTrace,
    callee: &str,
) -> &'a GraftFrame {
    trace
        .frames
        .iter()
        .find(|frame| {
            frame.kind == GraftFrameKind::Call
                && frame.callee.function.as_str() == callee
        })
        .unwrap()
}

#[test]
fn compiler_emits_deterministic_nested_two_hole_graft_frames() {
    let first = compile("root");
    let second = compile("root");
    assert!(first.graft_trace.certificate.certified());
    assert_eq!(first.graft_trace, second.graft_trace);

    let trace = &first.graft_trace.result;
    assert_eq!(trace.frames.len(), 5);
    let root = &trace.frames[0];
    assert_eq!(root.kind, GraftFrameKind::Root);
    assert_eq!(root.id, trace.root);
    assert_eq!(root.body_region, vec![NodeId(0), NodeId(1), NodeId(2)]);

    let pair = call_frame(trace, "pair");
    let neg = call_frame(trace, "neg-one");
    let identity = call_frame(trace, "id-one");
    let add = call_frame(trace, "add-two");

    assert_eq!(pair.parent.as_ref(), Some(&root.id));
    assert_eq!(pair.children, vec![neg.id.clone(), identity.id.clone(), add.id.clone()]);
    assert_eq!(pair.arguments.len(), 1);
    assert_eq!(pair.arguments[0].nodes, vec![NodeId(0), NodeId(1)]);
    assert_eq!(pair.arguments[0].outputs.len(), 2);
    assert_eq!(pair.body_region, vec![NodeId(2)]);
    assert_eq!(pair.holes.len(), 2);
    assert_eq!(pair.holes[0].argument_index, Some(0));
    assert_eq!(pair.holes[0].argument_output_index, 0);
    assert_eq!(pair.holes[1].argument_index, Some(0));
    assert_eq!(pair.holes[1].argument_output_index, 1);
    assert_eq!(pair.entry_wires[0], pair.holes[0].entry_wire);
    assert_eq!(pair.entry_wires[1], pair.holes[1].entry_wire);

    assert_eq!(neg.parent.as_ref(), Some(&pair.id));
    assert_eq!(identity.parent.as_ref(), Some(&pair.id));
    assert_eq!(add.parent.as_ref(), Some(&pair.id));
    assert_eq!(
        neg.region_in_parent,
        GraftRegionRole::Argument { index: 0 }
    );
    assert_eq!(
        identity.region_in_parent,
        GraftRegionRole::Argument { index: 0 }
    );
    assert_eq!(add.region_in_parent, GraftRegionRole::CalleeBody);
    assert_eq!(neg.caller.function.as_str(), "root");
    assert_eq!(identity.caller.function.as_str(), "root");
    assert_eq!(add.caller.function.as_str(), "pair");

    let call_history = first
        .result
        .history
        .prefix
        .iter()
        .enumerate()
        .filter_map(|(index, event)| {
            matches!(event, adva_ir::HistoryEvent::Call { .. }).then_some(index as u32)
        })
        .collect::<Vec<_>>();
    let linked_history = trace
        .frames
        .iter()
        .filter_map(|frame| frame.call_history_index)
        .collect::<Vec<_>>();
    assert_eq!(linked_history.len(), call_history.len());
    assert_eq!(
        linked_history.iter().copied().collect::<std::collections::BTreeSet<_>>(),
        call_history.iter().copied().collect()
    );
}

#[test]
fn argument_regions_retain_events_that_bind_no_hole() {
    let artifact = compile("hidden-argument");
    let pair = call_frame(&artifact.graft_trace.result, "pair");

    assert_eq!(pair.arguments.len(), 2);
    assert_eq!(pair.arguments[0].nodes, vec![NodeId(0), NodeId(1)]);
    assert!(pair.arguments[0].outputs.is_empty());
    assert!(pair.arguments[1].nodes.is_empty());
    assert_eq!(pair.arguments[1].outputs.len(), 2);
    assert_eq!(pair.holes[0].argument_index, Some(1));
    assert_eq!(pair.holes[0].argument_output_index, 0);
    assert_eq!(pair.holes[1].argument_index, Some(1));
    assert_eq!(pair.holes[1].argument_output_index, 1);

    let names = pair.arguments[0]
        .nodes
        .iter()
        .map(|id| {
            artifact
                .result
                .nodes
                .iter()
                .find(|node| node.id == *id)
                .unwrap()
                .operation
                .name
                .as_str()
        })
        .collect::<Vec<_>>();
    assert_eq!(names, vec!["constant", "discard"]);
    assert!(artifact.graft_trace.certificate.certified());
}
