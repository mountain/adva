//! Project-original finite experiment by Codex (OpenAI), Unknown v0.3.
//! Research-local enumeration and receiving, not a stable learning API.
use adva_ir::{CompilationArtifact, HistoryEvent, TriadicDomainV0, TriadicObserverPolicyV0};
use adva_lisp::{
    analyze_triadic_observer_transition_v0, compile_function, link_modules, parse_module,
    validate_diagram,
};
use serde_json::{Value, json};
use std::collections::BTreeMap;

const FAMILY_SIZE: u8 = 16;

// The caller fixes this grammar, not the proposal. key = 2 * copy_mask + pad.
// Each of three branches uses exactly one input; padding is one extra id on a.
fn source(key: u8) -> String {
    assert!(key < FAMILY_SIZE);
    let mask = key / 2;
    let branches = ["a", "b", "c"]
        .iter()
        .enumerate()
        .map(|(i, name)| {
            let input = format!("(use {name})");
            let inner = if i == 0 && key % 2 == 1 {
                format!("(id {input})")
            } else {
                input
            };
            let op = if mask & (1 << i) == 0 { "id" } else { "copy" };
            format!("({op} {inner})")
        })
        .collect::<Vec<_>>()
        .join(" ");
    let outputs = vec!["Real"; 3 + mask.count_ones() as usize].join(" ");
    // Names deliberately identical across candidates: names cannot reveal key.
    format!(
        "(module finite-world (export world) (def world (fn ((a Real) (b Real) (c Real)) (outputs {outputs}) (frontier {branches}))))"
    )
}

fn compile(key: u8) -> CompilationArtifact {
    let module = parse_module(&source(key)).unwrap();
    let linked = link_modules(vec![module]).unwrap();
    let artifact = compile_function(&linked, "finite-world", "world").unwrap();
    assert!(artifact.certificate.certified());
    assert!(artifact.graft_trace.certificate.certified());
    artifact
}

#[derive(Clone, Debug)]
struct Proposal {
    key: u8, // enumeration coordinate, never a semantic identity
    artifact: CompilationArtifact,
}

fn propose() -> Vec<Proposal> {
    (0..FAMILY_SIZE)
        .map(|key| Proposal {
            key,
            artifact: compile(key),
        })
        .collect()
}

#[derive(Debug, PartialEq)]
enum Received {
    Complete {
        survivors: Vec<u8>,
        minima: Vec<u8>,
        work: usize,
    },
    UnknownCoverage,
    UnknownBudget {
        next_key: u8,
        work: usize,
        checked_survivors: Vec<u8>,
    },
    InvalidEvidence,
    InvalidQuestion,
}

// All features below are derived afresh in Rust from the checked slice.
// They are research readouts of the native carrier, not stable ObservationPolicy.
fn features(artifact: &CompilationArtifact) -> (Vec<usize>, Value) {
    let diagram = &artifact.result;
    assert!(
        validate_diagram(diagram.clone())
            .unwrap()
            .certificate
            .certified()
    );
    let all = diagram.nodes.iter().map(|node| node.id).collect::<Vec<_>>();
    let policy = TriadicObserverPolicyV0 {
        input_domains: vec![
            TriadicDomainV0::Time,
            TriadicDomainV0::Space,
            TriadicDomainV0::Construction,
        ],
    };
    let transition = analyze_triadic_observer_transition_v0(diagram, &policy, &[], &all).unwrap();
    assert!(transition.certificate.certified());
    let result = &transition.result;
    assert_eq!(result.lower.incidences.len(), 3);
    assert!(result.upper.source_free_wire_indices.is_empty());
    let mut counts = vec![result.upper.incidences.len()];
    for root in &result.lower.incidences {
        counts.push(
            result
                .upper
                .incidences
                .iter()
                .filter(|upper| {
                    assert!(result.slice.occurrences.contains(&upper.occurrence));
                    upper.occurrence.source == root.occurrence.source
                })
                .count(),
        );
    }
    let copy_count = result
        .slice
        .event_history
        .iter()
        .filter(|e| matches!(e, HistoryEvent::Copy { .. }))
        .count();
    assert_eq!(counts[0], 3 + copy_count);
    counts.push(result.slice.events.len());
    (counts, json!(transition))
}

// Trusted typed receiving entry, not an arbitrary untrusted JSON endpoint.
// Size of proposal vector and native artifacts is bounded before kernel calls.
// One unit per canonical compilation, one per validation+slice feature bundle;
// internal kernel instructions, allocations and comparisons are not unit costs.
fn receive(
    proposal: &[Proposal],
    reveal: &[usize],
    observed: &[usize],
    allowance: usize,
) -> Received {
    if reveal.iter().any(|&i| i > 4)
        || reveal.windows(2).any(|w| w[0] >= w[1])
        || reveal.len() != observed.len()
    {
        return Received::InvalidQuestion;
    }
    if proposal.len() != usize::from(FAMILY_SIZE)
        || proposal
            .iter()
            .enumerate()
            .any(|(i, p)| usize::from(p.key) != i)
    {
        return Received::UnknownCoverage;
    }
    let mut work = 0;
    let mut survivors = Vec::new();
    let mut costs = BTreeMap::new();
    for p in proposal {
        if allowance.saturating_sub(work) < 2 {
            return Received::UnknownBudget {
                next_key: p.key,
                work,
                checked_survivors: survivors,
            };
        }
        let d = &p.artifact.result;
        if d.nodes.len() > 4
            || d.occurrences.len() > 9
            || d.history.prefix.len() > 16
            || d.outputs.len() > 6
        {
            return Received::InvalidEvidence;
        }
        work += 1;
        let expected = compile(p.key);
        // Complete native artifact agreement binds body, order, IDs and history;
        // trusting a certificate boolean or a proposal-supplied feature is insufficient.
        if p.artifact != expected {
            return Received::InvalidEvidence;
        }
        work += 1;
        let (readout, _) = features(&expected);
        if reveal.iter().zip(observed).all(|(&i, &v)| readout[i] == v) {
            survivors.push(p.key);
            costs.insert(p.key, d.nodes.len());
        }
    }
    let minimum = costs.values().min().copied();
    let minima = survivors
        .iter()
        .copied()
        .filter(|key| costs.get(key).copied() == minimum)
        .collect();
    Received::Complete {
        survivors,
        minima,
        work,
    }
}

fn partition(proposals: &[Proposal], reveal: &[usize]) -> BTreeMap<Vec<usize>, Vec<u8>> {
    let mut classes: BTreeMap<Vec<usize>, Vec<u8>> = BTreeMap::new();
    for p in proposals {
        let (f, _) = features(&p.artifact);
        classes
            .entry(reveal.iter().map(|&i| f[i]).collect())
            .or_default()
            .push(p.key);
    }
    classes
}

// Independent finite combinatorial oracle. It does not allocate native IDs.
fn oracle_partition(reveal: &[usize]) -> BTreeMap<Vec<usize>, Vec<u8>> {
    let mut classes: BTreeMap<Vec<usize>, Vec<u8>> = BTreeMap::new();
    for a in 0..=1u8 {
        for b in 0..=1u8 {
            for c in 0..=1u8 {
                for pad in 0..=1u8 {
                    let key = 2 * (a + 2 * b + 4 * c) + pad;
                    let f = [
                        3 + usize::from(a + b + c),
                        1 + usize::from(a),
                        1 + usize::from(b),
                        1 + usize::from(c),
                        3 + usize::from(pad),
                    ];
                    classes
                        .entry(reveal.iter().map(|&i| f[i]).collect())
                        .or_default()
                        .push(key);
                }
            }
        }
    }
    for class in classes.values_mut() {
        class.sort();
    }
    classes
}

#[test]
fn complete_world_search_and_exact_partitions() {
    let proposals = propose();
    for i in 0..proposals.len() {
        for j in 0..i {
            assert_ne!(proposals[i].artifact.result, proposals[j].artifact.result);
        }
    }
    for reveal in [
        vec![0],
        vec![0, 1],
        vec![0, 1, 2],
        vec![0, 1, 2, 3],
        vec![0, 1, 2, 4],
    ] {
        let actual = partition(&proposals, &reveal);
        assert_eq!(actual, oracle_partition(&reveal));
        for (observed, expected) in actual {
            let result = receive(&proposals, &reveal, &observed, 32);
            let Received::Complete {
                survivors,
                minima,
                work,
            } = result
            else {
                panic!("complete family required")
            };
            assert_eq!(survivors, expected);
            assert_eq!(work, 32);
            assert_eq!(
                minima,
                survivors
                    .iter()
                    .copied()
                    .filter(|k| survivors.len() == 1 || k % 2 == 0)
                    .collect::<Vec<_>>()
            );
        }
    }
}

#[test]
fn refinement_retains_ambiguity_and_minimality_is_not_recovery() {
    let proposals = propose();
    assert_eq!(features(&proposals[5].artifact).0, vec![4, 1, 2, 1, 4]);
    assert_eq!(
        receive(&proposals, &[0], &[4], 32),
        Received::Complete {
            survivors: vec![2, 3, 4, 5, 8, 9],
            minima: vec![2, 4, 8],
            work: 32
        }
    );
    assert_eq!(
        receive(&proposals, &[0, 1], &[4, 1], 32),
        Received::Complete {
            survivors: vec![4, 5, 8, 9],
            minima: vec![4, 8],
            work: 32
        }
    );
    assert_eq!(
        receive(&proposals, &[0, 1, 2], &[4, 1, 2], 32),
        Received::Complete {
            survivors: vec![4, 5],
            minima: vec![4],
            work: 32
        }
    );
    assert_eq!(
        receive(&proposals, &[0, 1, 2, 4], &[4, 1, 2, 4], 32),
        Received::Complete {
            survivors: vec![5],
            minima: vec![5],
            work: 32
        }
    );
    // Candidate 5 is the hidden world. Candidate 4 is strictly smaller but has
    // a different complete checked history. Even revealing c cannot separate them.
    assert_eq!(
        features(&proposals[4].artifact).0[..4],
        features(&proposals[5].artifact).0[..4]
    );
    assert_ne!(
        proposals[4].artifact.result.history,
        proposals[5].artifact.result.history
    );
    assert_eq!(
        partition(&proposals, &[0, 1, 2, 3])
            .values()
            .map(Vec::len)
            .collect::<Vec<_>>(),
        vec![2; 8]
    );
}

#[test]
fn missing_duplicate_and_substituted_worlds_do_not_receive() {
    let mut proposals = propose();
    let omitted = proposals.remove(5);
    assert_eq!(
        receive(&proposals, &[0], &[4], 32),
        Received::UnknownCoverage
    );
    proposals.insert(5, omitted);
    proposals[5] = proposals[4].clone();
    assert_eq!(
        receive(&proposals, &[0], &[4], 32),
        Received::UnknownCoverage
    );
    // Same key and same function/source names cannot hide a changed body.
    proposals[5].key = 5;
    assert_eq!(
        receive(&proposals, &[0], &[4], 32),
        Received::InvalidEvidence
    );
}

#[test]
fn identity_path_and_history_mutations_are_refused() {
    let original = propose();
    let mut altered = original.clone();
    altered[5].artifact.result.history.prefix.pop();
    assert_eq!(receive(&altered, &[0], &[4], 32), Received::InvalidEvidence);
    let mut altered = original.clone();
    altered[5].artifact.result.occurrences[0].path.0.push(9);
    assert_eq!(receive(&altered, &[0], &[4], 32), Received::InvalidEvidence);
    let mut altered = original.clone();
    altered[5].artifact.graft_trace.result = original[4].artifact.graft_trace.result.clone();
    assert_eq!(receive(&altered, &[0], &[4], 32), Received::InvalidEvidence);
}

#[test]
fn budget_empty_fibre_and_invalid_questions_remain_distinct() {
    let proposals = propose();
    assert_eq!(
        receive(&proposals, &[0], &[4], 0),
        Received::UnknownBudget {
            next_key: 0,
            work: 0,
            checked_survivors: vec![]
        }
    );
    assert_eq!(
        receive(&proposals, &[0], &[4], 31),
        Received::UnknownBudget {
            next_key: 15,
            work: 30,
            checked_survivors: vec![2, 3, 4, 5, 8, 9]
        }
    );
    assert_eq!(
        receive(&proposals, &[0], &[7], 32),
        Received::Complete {
            survivors: vec![],
            minima: vec![],
            work: 32
        }
    );
    assert_eq!(
        receive(&proposals, &[0, 0], &[4, 4], 32),
        Received::InvalidQuestion
    );
    assert_eq!(
        receive(&proposals, &[5], &[1], 32),
        Received::InvalidQuestion
    );
    assert_eq!(
        receive(&proposals, &[0], &[], 32),
        Received::InvalidQuestion
    );
}

#[test]
fn emit_replayable_native_evidence() {
    let proposals = propose();
    let candidates = proposals.iter().map(|p| {
        let (f, transition) = features(&p.artifact);
        json!({"key":p.key,"source":source(p.key),"compilation":p.artifact,"transition":transition,"features":f,"node_cost":p.artifact.result.nodes.len()})
    }).collect::<Vec<_>>();
    let partitions = [vec![0],vec![0,1],vec![0,1,2],vec![0,1,2,3],vec![0,1,2,4]].iter().map(|q| {
        json!({"reveal":q,"classes":partition(&proposals,q).into_iter().map(|(observation,keys)|json!({"observation":observation,"keys":keys})).collect::<Vec<_>>()})
    }).collect::<Vec<_>>();
    let evidence = json!({"schema":"adva.finite-world-identification.research","version":0,"family_size":16,"hidden_world":5,"candidates":candidates,"partitions":partitions,"target_results":[format!("{:?}",receive(&proposals,&[0],&[4],32)),format!("{:?}",receive(&proposals,&[0,1],&[4,1],32)),format!("{:?}",receive(&proposals,&[0,1,2],&[4,1,2],32)),format!("{:?}",receive(&proposals,&[0,1,2,4],&[4,1,2,4],32))],"residual":"full source multiplicities leave identity padding ambiguous; no residual specialization executed"});
    println!("WORLD_EVIDENCE={evidence}");
}
