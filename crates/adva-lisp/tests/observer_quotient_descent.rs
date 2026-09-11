//! Does an observer-relative reading descend across one checked causal step?
//!
//! Research 0168's dynamical bridge was corrected by
//! `docs/research/triadic-period-bridge-correction.md`, which makes the
//! quotient criterion executable: for a finite total map `F` on `S` and a
//! surjection `q: S -> Y`, a map `g` with `q F = g q` exists exactly when
//! `q(s) = q(t)` implies `q(F(s)) = q(F(t))`.
//!
//! This file does two independent things with that criterion.
//!
//! 1. It re-implements the criterion and reproduces the four fixture tables
//!    the correction note publishes, in a different language. That is a
//!    cross-implementation check of the published criterion.
//! 2. It instantiates the criterion on a real checked
//!    `TriadicObserverTransitionV0`, where the observation is the
//!    observer-relative role label read from declared input-source fibres and
//!    the step is the checked lineage relation. Nothing here is an Adva
//!    identity; the states are indices into checked incidences.

use adva_ir::{TriadicDomainV0, TriadicObserverPolicyV0};
use adva_lisp::{
    analyze_triadic_observer_transition_v0, compile_function, link_modules, parse_module,
};
use std::collections::BTreeSet;

const OBSERVER_MODULE: &str = r#"
(module observer
  (export triadic-flow)

  (def triadic-flow
    (fn ((temporal Real) (spatial Real) (construction Real))
        (outputs Real Real Real)
      (frontier
        (discard 1)
        (add (copy (use temporal)))
        (id (use spatial))
        (id (use construction)))))
)
"#;

fn compile(name: &str) -> adva_ir::CompilationArtifact {
    let module = parse_module(OBSERVER_MODULE).unwrap();
    let linked = link_modules(vec![module]).unwrap();
    compile_function(&linked, "observer", name).unwrap()
}

fn triadic_policy() -> TriadicObserverPolicyV0 {
    TriadicObserverPolicyV0 {
        input_domains: vec![
            TriadicDomainV0::Time,
            TriadicDomainV0::Space,
            TriadicDomainV0::Construction,
        ],
    }
}

// ---------------------------------------------------------------- the criterion

/// The descent condition for a total map `f` and an observation `q`.
///
/// Returns the descended map, one entry per observation label, when it exists,
/// and otherwise the first conflicting pair of states. Both are exact finite
/// computations over indices; no numeric tolerance is involved.
fn descend_total(f: &[usize], q: &[usize]) -> Result<Vec<usize>, (usize, usize)> {
    assert_eq!(f.len(), q.len(), "f and q must share a domain");
    let labels = q.iter().copied().max().map_or(0, |m| m + 1);
    let mut g: Vec<Option<usize>> = vec![None; labels];
    for s in 0..q.len() {
        for t in 0..q.len() {
            if q[s] != q[t] {
                continue;
            }
            if q[f[s]] != q[f[t]] {
                return Err((s, t));
            }
        }
    }
    for s in 0..q.len() {
        g[q[s]] = Some(q[f[s]]);
    }
    let g = g
        .into_iter()
        .map(|entry| entry.expect("every observation label is realised by some state"))
        .collect::<Vec<_>>();
    // The commuting equation is rechecked on every state, not inferred from
    // the pairwise test.
    for s in 0..q.len() {
        assert_eq!(g[q[s]], q[f[s]], "commuting equation fails at state {s}");
    }
    Ok(g)
}

/// The descent condition when the step is a relation rather than a total map,
/// as a checked lineage relation is once copy branches. Each state carries the
/// set of observations of its images, and the condition is that equal
/// observations have equal image-observation sets.
fn descend_relation(
    images: &[BTreeSet<usize>],
    q: &[usize],
) -> Result<Vec<BTreeSet<usize>>, (usize, usize)> {
    let labels = q.iter().copied().max().map_or(0, |m| m + 1);
    for s in 0..q.len() {
        for t in 0..q.len() {
            if q[s] == q[t] && images[s] != images[t] {
                return Err((s, t));
            }
        }
    }
    let mut g: Vec<BTreeSet<usize>> = vec![BTreeSet::new(); labels];
    for s in 0..q.len() {
        assert!(
            g[q[s]].is_empty() || g[q[s]] == images[s],
            "descended map is not well defined at label {}",
            q[s]
        );
        g[q[s]] = images[s].clone();
    }
    Ok(g)
}

// ------------------------------------------- 1. their four published fixtures

#[test]
fn the_published_quotient_fixtures_reproduce_in_rust() {
    // Failed descent: states 0 and 1 both observe 0, then observe 0 and 1.
    let failed = descend_total(&[0, 2, 2, 3], &[0, 0, 1, 1]);
    assert_eq!(failed, Err((0, 1)));

    // Non-injective quotient: g = [1, 1], only least period one occurs.
    assert_eq!(descend_total(&[2, 3, 2, 3], &[0, 0, 1, 1]), Ok(vec![1, 1]));

    // Two-cycle quotient: g = [1, 0], least period two.
    assert_eq!(descend_total(&[2, 3, 0, 1], &[0, 0, 1, 1]), Ok(vec![1, 0]));

    // Finite three-cycle quotient: g = [1, 2, 0], least period three but not a
    // real-interval witness.
    assert_eq!(
        descend_total(&[2, 3, 4, 5, 0, 1], &[0, 0, 1, 1, 2, 2]),
        Ok(vec![1, 2, 0])
    );
}

#[test]
fn a_surjection_is_not_enough_and_the_failing_pair_is_retained() {
    // The criterion is about the pair of maps, not about q being many-to-one:
    // the failing fixture above is a surjection and still does not descend.
    let err = descend_total(&[0, 2, 2, 3], &[0, 0, 1, 1]).unwrap_err();
    assert_eq!(err, (0, 1));
    // A constant observation descends for any step, so the check is not vacuous
    // in the other direction either.
    assert_eq!(descend_total(&[0, 2, 2, 3], &[0, 0, 0, 0]), Ok(vec![0]));
}

// ------------------------------- 2. instantiation on a checked Adva transition

#[test]
fn the_observer_role_label_descends_across_one_checked_causal_step() {
    let artifact = compile("triadic-flow");
    let all = artifact
        .result
        .nodes
        .iter()
        .map(|node| node.id)
        .collect::<Vec<_>>();
    let transition =
        analyze_triadic_observer_transition_v0(&artifact.result, &triadic_policy(), &[], &all)
            .unwrap();
    let result = &transition.result;
    assert!(transition.certificate.certified());

    // The observation: the three-way role label of each lower incidence. The
    // checked transition already assigns exactly one domain per incidence, so
    // this is a read of checked data and not a new labelling.
    let lower_domains = result
        .lower
        .incidences
        .iter()
        .map(|incidence| match incidence.domain {
            TriadicDomainV0::Time => 0usize,
            TriadicDomainV0::Space => 1usize,
            TriadicDomainV0::Construction => 2usize,
        })
        .collect::<Vec<_>>();
    assert_eq!(lower_domains.len(), 3);
    assert_eq!(
        lower_domains.iter().copied().collect::<BTreeSet<_>>(),
        BTreeSet::from([0, 1, 2]),
        "the fixture is expected to carry one incidence per role"
    );

    // The step: the checked lineage relation, read as the image set of each
    // lower incidence. It is a relation, because copy branches.
    let mut images = vec![BTreeSet::new(); result.lower.incidences.len()];
    for link in &result.lineage_links {
        let upper = result.upper.incidences[link.upper_incidence_index as usize].domain;
        let label = match upper {
            TriadicDomainV0::Time => 0usize,
            TriadicDomainV0::Space => 1usize,
            TriadicDomainV0::Construction => 2usize,
        };
        images[link.lower_incidence_index as usize].insert(label);
    }

    // Reachable domain and residual partition it exactly: a lower incidence is
    // either carried by at least one link or it is not, and the unchecked part
    // is retained rather than dropped.
    let reachable = images.iter().filter(|image| !image.is_empty()).count();
    let unreachable = images.len() - reachable;
    // Recorded exactly, because the partition identity below holds for any
    // fixture and would be a vacuous assertion on its own. Every lower
    // incidence of this fixture is carried across the step, so this fixture
    // does NOT exercise an unchecked lower incidence, and the role each
    // incidence carries is carried to itself.
    assert_eq!(
        images,
        vec![
            BTreeSet::from([0]),
            BTreeSet::from([1]),
            BTreeSet::from([2])
        ]
    );
    assert_eq!((reachable, unreachable), (3, 0));
    assert_eq!(reachable + unreachable, result.lower.incidences.len());

    // Descent on the reachable part. Because a role label is a function of the
    // input-source fibre and the checked lineage relation preserves source, the
    // label must descend, and it must descend to itself.
    let reachable_indices = (0..images.len())
        .filter(|index| !images[*index].is_empty())
        .collect::<Vec<_>>();
    let images_reachable = reachable_indices
        .iter()
        .map(|index| images[*index].clone())
        .collect::<Vec<_>>();
    let labels_reachable = reachable_indices
        .iter()
        .map(|index| lower_domains[*index])
        .collect::<Vec<_>>();
    let g = descend_relation(&images_reachable, &labels_reachable)
        .expect("the role label is source-determined and must descend");
    for (position, index) in reachable_indices.iter().enumerate() {
        assert_eq!(
            g[labels_reachable[position]],
            BTreeSet::from([lower_domains[*index]]),
            "a role label must descend to itself"
        );
    }
}

#[test]
fn the_cut_reading_does_not_descend_because_copy_changes_its_size() {
    let artifact = compile("triadic-flow");
    let all = artifact
        .result
        .nodes
        .iter()
        .map(|node| node.id)
        .collect::<Vec<_>>();
    let transition =
        analyze_triadic_observer_transition_v0(&artifact.result, &triadic_policy(), &[], &all)
            .unwrap();
    let result = &transition.result;

    // The per-incidence role label descends. The reading of the whole cut does
    // not, and the reason is not subtle: copy introduces an incidence, so the
    // two cuts have different sizes and no map between their incidence-index
    // readings can be bijective.
    assert_eq!(result.lower.incidences.len(), 3);
    assert_eq!(result.upper.incidences.len(), 4);

    // The branch that makes this true is a checked copy, not a recount.
    let branching = {
        let mut counts = vec![0usize; result.lower.incidences.len()];
        for link in &result.lineage_links {
            counts[link.lower_incidence_index as usize] += 1;
        }
        counts
    };
    assert!(
        branching.iter().any(|count| *count > 1),
        "the fixture is expected to contain a branching step"
    );
    assert_eq!(branching.iter().sum::<usize>(), result.lineage_links.len());

    // Every hidden incidence stays hidden and every visible one stays visible
    // within its own chart: the opposite-pair readings are retained per chart
    // and are not merged across charts.
    for view in &result.lower.opposite_pair_views {
        assert_eq!(
            view.visible_incidence_indices.len() + view.hidden_own_incidence_indices.len(),
            result.lower.incidences.len()
        );
    }
    // The residual field is retained on both sides. It is empty for this
    // fixture, so this test does not exercise a non-empty source-free residual;
    // the fixture that does is covered by the sibling test
    // `triadic_transition_retains_source_free_wires_outside_all_three_views`.
    assert!(result.lower.source_free_wire_indices.is_empty());
    assert!(result.upper.source_free_wire_indices.is_empty());
    assert_eq!(result.lower.cut.frontier.len(), 3);
    assert_eq!(result.upper.cut.frontier.len(), 3);
}
