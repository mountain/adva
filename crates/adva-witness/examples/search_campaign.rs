//! Research 0153. Frozen arithmetic verifier blocks; bounded policy-only changes.
use adva_witness::*;
use num_bigint::BigInt;
use serde::{Deserialize, Serialize};
use serde_json::{Value, json};
use std::collections::BTreeMap;
use std::path::Path;

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
enum Expr {
    X,
    Two,
    Add(Box<Self>, Box<Self>),
    Mul(Box<Self>, Box<Self>),
}

impl Expr {
    fn add(a: Self, b: Self) -> Self {
        Self::Add(Box::new(a), Box::new(b))
    }
    fn mul(a: Self, b: Self) -> Self {
        Self::Mul(Box::new(a), Box::new(b))
    }
    fn exact(&self) -> ExactExprV0 {
        match self {
            Self::X => ExactExprV0::variable("x"),
            Self::Two => ExactExprV0::constant(2),
            Self::Add(a, b) => ExactExprV0::sum(a.exact(), b.exact()),
            Self::Mul(a, b) => ExactExprV0::product(a.exact(), b.exact()),
        }
    }
    fn shape(&self) -> (usize, usize) {
        match self {
            Self::X | Self::Two => (1, 1),
            Self::Add(a, b) | Self::Mul(a, b) => {
                let (an, ad) = a.shape();
                let (bn, bd) = b.shape();
                (1 + an + bn, 1 + ad.max(bd))
            }
        }
    }
    fn bounded(&self) -> bool {
        let (nodes, depth) = self.shape();
        nodes <= 127 && depth <= 16
    }
    fn lean(&self) -> String {
        match self {
            Self::X => "x".into(),
            Self::Two => "(2 : Int)".into(),
            Self::Add(a, b) => format!("({} + {})", a.lean(), b.lean()),
            Self::Mul(a, b) => format!("({} * {})", a.lean(), b.lean()),
        }
    }
    fn mm(&self) -> String {
        match self {
            Self::X => "A".into(),
            Self::Two => "2".into(),
            Self::Add(a, b) => format!("( {} + {} )", a.mm(), b.mm()),
            Self::Mul(a, b) => format!("( {} x. {} )", a.mm(), b.mm()),
        }
    }
    fn class_proof(&self) -> String {
        match self {
            Self::X => "cA".into(),
            Self::Two => "c2".into(),
            Self::Add(a, b) | Self::Mul(a, b) => format!(
                "{} {} {} co",
                a.class_proof(),
                b.class_proof(),
                if matches!(self, Self::Add(..)) {
                    "caddc"
                } else {
                    "cmul"
                }
            ),
        }
    }
    fn closure(&self) -> String {
        match self {
            Self::X => format!("{PHI} id"),
            Self::Two => format!("{PHI} 2cnd"),
            Self::Add(a, b) | Self::Mul(a, b) => format!(
                "{PHI} {} {} {} {} {}",
                a.class_proof(),
                b.class_proof(),
                a.closure(),
                b.closure(),
                if matches!(self, Self::Add(..)) {
                    "addcld"
                } else {
                    "mulcld"
                }
            ),
        }
    }
}

const PHI: &str = "cA cc wcel"; // Syntax proof of the explicit A e. CC guard.

#[derive(Clone, Debug, Eq, PartialEq, Serialize)]
struct Move {
    path: Vec<usize>, // Arithmetic syntax positions, never SourceId/OccurrenceId.
    expand: bool,
}

#[derive(Clone)]
struct Rewritten {
    after: Expr,
    lean: String,
    mm: String,
}

fn rewrite(before: &Expr, path: &[usize], expand: bool) -> Result<Rewritten, String> {
    if path.is_empty() {
        let t = match (before, expand) {
            (Expr::Mul(a, b), true) if **a == Expr::Two => b.as_ref(),
            (Expr::Add(a, b), false) if a == b => a.as_ref(),
            _ => return Err("not an instance of the loaded doubling law".into()),
        };
        let doubled = Expr::mul(Expr::Two, t.clone());
        let added = Expr::add(t.clone(), t.clone());
        let forward_mm = format!("{PHI} {} {} 2timesd", t.class_proof(), t.closure());
        return Ok(if expand {
            Rewritten {
                after: added,
                lean: format!("(Int.two_mul {})", t.lean()),
                mm: forward_mm,
            }
        } else {
            Rewritten {
                after: doubled.clone(),
                lean: format!("(Int.two_mul {}).symm", t.lean()),
                mm: format!(
                    "{PHI} {} {} {forward_mm} eqcomd",
                    doubled.class_proof(),
                    added.class_proof()
                ),
            }
        });
    }
    let (a, b, plus) = match before {
        Expr::Add(a, b) => (a.as_ref(), b.as_ref(), true),
        Expr::Mul(a, b) => (a.as_ref(), b.as_ref(), false),
        _ => return Err("rewrite position passes through a leaf".into()),
    };
    let (child, other) = match path[0] {
        0 => (a, b),
        1 => (b, a),
        _ => return Err("rewrite position must be zero or one".into()),
    };
    let sub = rewrite(child, &path[1..], expand)?;
    let op = if plus { "+" } else { "*" };
    let body = if path[0] == 0 {
        format!("(z {op} {})", other.lean())
    } else {
        format!("({} {op} z)", other.lean())
    };
    let (left, right) = if path[0] == 0 {
        (sub.after.clone(), other.clone())
    } else {
        (other.clone(), sub.after.clone())
    };
    Ok(Rewritten {
        after: if plus {
            Expr::add(left, right)
        } else {
            Expr::mul(left, right)
        },
        lean: format!("(congrArg (fun (z : Int) => {body}) ({}))", sub.lean),
        mm: format!(
            "{PHI} {} {} {} {} {} {}",
            child.class_proof(),
            sub.after.class_proof(),
            other.class_proof(),
            if plus { "caddc" } else { "cmul" },
            sub.mm,
            if path[0] == 0 { "oveq1d" } else { "oveq2d" }
        ),
    })
}

fn residual(a: &Expr, b: &Expr) -> usize {
    if a == b {
        return 0;
    }
    match (a, b) {
        (Expr::Add(a, b), Expr::Add(c, d)) | (Expr::Mul(a, b), Expr::Mul(c, d)) => {
            residual(a, c) + residual(b, d)
        }
        _ => a.shape().0 + b.shape().0,
    }
}

fn moves(expr: &Expr, path: &mut Vec<usize>, out: &mut Vec<Move>) {
    match expr {
        Expr::Mul(a, _) if **a == Expr::Two => out.push(Move {
            path: path.clone(),
            expand: true,
        }),
        Expr::Add(a, b) if a == b => out.push(Move {
            path: path.clone(),
            expand: false,
        }),
        _ => {}
    }
    if let Expr::Add(a, b) | Expr::Mul(a, b) = expr {
        for (index, child) in [a, b].into_iter().enumerate() {
            path.push(index);
            moves(child, path, out);
            path.pop();
        }
    }
}

fn witness(before: &Expr, after: &Expr) -> Result<Value, String> {
    if !before.bounded() || !after.bounded() {
        return Err("bounded syntax exceeded".into());
    }
    let mut store = WitnessStoreV0::new();
    let body = store
        .insert(WitnessProofV0::ArithmeticTransition {
            actual_boundary: BoundaryChargeV0::zero(),
            declared_boundary: BoundaryChargeV0::zero(),
            before: before.exact(),
            after: after.exact(),
        })
        .map_err(|e| e.to_string())?;
    let seal = store
        .insert(WitnessProofV0::Seal { body: body.clone() })
        .map_err(|e| e.to_string())?;
    Ok(json!({ "body": store.artifact(&body), "seal": store.artifact(&seal) }))
}

fn export_edge(before: &Expr, action: &Move, label: &str) -> Result<Value, String> {
    let step = rewrite(before, &action.path, action.expand)?;
    let proof = witness(before, &step.after)?;
    Ok(json!({
        "before": before, "after": step.after, "move": action, "witness": proof,
        "label": label,
        "lean": format!("theorem {label} (x : Int) : {} = {} := {}\n#print axioms {label}\n",
            before.lean(), step.after.lean(), step.lean),
        "metamath": format!("{label} $p |- ( A e. CC -> {} = {} ) $= {} $.\n",
            before.mm(), step.after.mm(), step.mm),
    }))
}

fn pair(depth: usize) -> (Expr, Expr) {
    let (mut compact, mut expanded) = (Expr::X, Expr::X);
    for _ in 0..depth {
        compact = Expr::mul(Expr::Two, compact);
        expanded = Expr::add(expanded.clone(), expanded);
    }
    (compact, expanded)
}

fn next_random(state: &mut u64) -> u64 {
    // Fixed xorshift64* proposal PRNG; no cryptographic or probabilistic proof claim.
    *state ^= *state >> 12;
    *state ^= *state << 25;
    *state ^= *state >> 27;
    state.wrapping_mul(2_685_821_657_736_338_717)
}

#[derive(Default, Serialize)]
struct Counts {
    enumerated: u64,
    bounded_exclusions: u64,
    witness_checks: u64,
    selected: u64,
    memory_comparisons: u64,
    selection_scans: u64,
    work_units: u64,
}

impl Counts {
    fn charge(&mut self) -> Result<(), String> {
        if self.work_units >= 500_000 {
            return Err("Unknown: batch work budget exhausted".into());
        }
        self.work_units += 1;
        Ok(())
    }
    fn total(&self) -> u64 {
        self.enumerated + self.witness_checks + self.memory_comparisons + self.selection_scans
    }
}

#[derive(Clone, Copy, Debug, Eq, PartialEq, Serialize)]
#[serde(rename_all = "snake_case")]
enum Policy {
    Random,
    Tabu,
    Hybrid,
}

impl Policy {
    fn parse(name: &str) -> Result<Self, String> {
        match name {
            "random" => Ok(Self::Random),
            "tabu" => Ok(Self::Tabu),
            "hybrid" => Ok(Self::Hybrid),
            _ => Err("policy outside frozen contract".into()),
        }
    }
}

fn seen_at(next: &Expr, memory: &[Expr], counts: &mut Counts) -> Result<Option<usize>, String> {
    for (index, previous) in memory.iter().enumerate() {
        counts.charge()?;
        counts.memory_comparisons += 1;
        if previous == next {
            return Ok(Some(index));
        }
    }
    Ok(None)
}

fn selection_pool(
    scores: &[usize],
    seen: &[Option<usize>],
    policy: Policy,
    step: usize,
    counts: &mut Counts,
) -> Result<(Vec<usize>, bool, bool), String> {
    if scores.is_empty() || scores.len() != seen.len() || step >= 48 {
        return Err("invalid bounded selection input".into());
    }
    let mut fresh = Vec::new();
    for (i, prior) in seen.iter().enumerate() {
        counts.charge()?;
        counts.selection_scans += 1;
        if prior.is_none() {
            fresh.push(i);
        }
    }
    let relaxed = policy != Policy::Random && fresh.is_empty();
    let eligible = if policy == Policy::Random || relaxed {
        (0..scores.len()).collect::<Vec<_>>()
    } else {
        fresh
    };
    let explore = policy == Policy::Hybrid && (step + 1) % 4 == 0;
    if policy != Policy::Hybrid || explore {
        return Ok((eligible, relaxed, explore));
    }
    let mut best = usize::MAX;
    let mut pool = Vec::new();
    for index in eligible {
        counts.charge()?;
        counts.selection_scans += 1;
        if scores[index] < best {
            best = scores[index];
            pool.clear();
        }
        if scores[index] == best {
            pool.push(index);
        }
    }
    Ok((pool, relaxed, explore))
}

fn arm(
    depth: usize,
    expand: bool,
    seed: u64,
    policy: Policy,
    counts: &mut Counts,
) -> Result<Value, String> {
    if !(2..=4).contains(&depth) || seed == 0 {
        return Err("arm outside finite input contract".into());
    }
    let before_cost = json!({
        "enumerated": counts.enumerated, "witness_checks": counts.witness_checks,
        "memory_comparisons": counts.memory_comparisons,
        "selection_scans": counts.selection_scans, "work_units": counts.work_units
    });
    let (a, b) = pair(depth);
    let (mut current, target) = if expand { (a, b) } else { (b, a) };
    let initial = current.clone();
    let mut state = seed;
    let mut path = Vec::new();
    let mut memory = vec![current.clone()];
    let (mut revisits, mut relaxed_steps, mut exploration_steps) = (0, 0, 0);
    while current != target && path.len() < 48 {
        let mut choices = Vec::new();
        moves(&current, &mut Vec::new(), &mut choices);
        let mut candidates = Vec::new();
        let mut excluded = Vec::new();
        for action in choices {
            counts.charge()?;
            counts.enumerated += 1;
            let next = rewrite(&current, &action.path, action.expand)?.after;
            if !next.bounded() {
                counts.bounded_exclusions += 1;
                excluded.push(action);
                continue;
            }
            counts.charge()?;
            counts.witness_checks += 1;
            witness(&current, &next)?;
            let prior = if policy == Policy::Random {
                None // No candidate-level visit filter in the baseline.
            } else {
                seen_at(&next, &memory, counts)?
            };
            let score = residual(&next, &target);
            candidates.push((action, next, score, prior));
        }
        let (pool, relaxed, explore) = selection_pool(
            &candidates.iter().map(|c| c.2).collect::<Vec<_>>(),
            &candidates.iter().map(|c| c.3).collect::<Vec<_>>(),
            policy,
            path.len(),
            counts,
        )?;
        let selected = pool[(next_random(&mut state) % pool.len() as u64) as usize];
        let (action, next, score, prior) = &candidates[selected];
        let prior = if policy == Policy::Random {
            seen_at(next, &memory, counts)? // Retained audit of the selected traversal.
        } else {
            *prior
        };
        revisits += usize::from(prior.is_some());
        relaxed_steps += usize::from(relaxed);
        exploration_steps += usize::from(explore);
        counts.charge()?;
        counts.witness_checks += 1;
        let edge = export_edge(&current, action, &format!("adva152e{}", counts.selected))?;
        counts.selected += 1;
        path.push(json!({
            "edge": edge, "selected_index": selected, "eligible_indices": pool,
            "residual_before": residual(&current, &target), "residual_after": score,
            "selected_seen_at": prior, "freshness_relaxed": relaxed, "scheduled_exploration": explore,
            "memory_length_before": memory.len(),
            "candidates": candidates.iter().map(|(m, _, r, seen)| json!({
                "move": m, "residual": r, "seen_at": seen,
                "visit_audited": policy != Policy::Random
            })).collect::<Vec<_>>(),
            "bounded_exclusions": excluded
        }));
        current = next.clone();
        memory.push(current.clone());
    }
    let after_cost = json!({
        "enumerated": counts.enumerated, "witness_checks": counts.witness_checks,
        "memory_comparisons": counts.memory_comparisons,
        "selection_scans": counts.selection_scans, "work_units": counts.work_units
    });
    let mut cost = serde_json::Map::new();
    for (key, value) in after_cost.as_object().expect("cost object") {
        cost.insert(
            key.clone(),
            json!(value.as_u64().expect("cost") - before_cost[key].as_u64().expect("cost")),
        );
    }
    Ok(json!({
        "depth": depth, "expand": expand, "seed": seed, "policy": policy,
        "initial": initial, "target": target, "final": current,
        "status": if current == target { "Reached" } else { "Unknown" },
        "stop_reason": if current == target { "literal_target" } else { "48_step_limit" },
        "residual": residual(&current, &target), "steps": path.len(),
        "revisits": revisits, "relaxed_steps": relaxed_steps,
        "exploration_steps": exploration_steps, "cost": cost, "path": path
    }))
}

fn protected_blocks_match(current: &str, frozen: &str) -> bool {
    fn block<'a>(source: &'a str, start: &str, end: &str) -> Option<&'a str> {
        source
            .split_once(start)?
            .1
            .split_once(end)
            .map(|(body, _)| body)
    }
    [
        ("use adva_witness", "#[derive(Default, Serialize)]"),
        ("\nfn calibration()", "\nfn run("),
    ]
    .iter()
    .all(|(start, end)| {
        let a = block(current, start, end);
        a.is_some() && a == block(frozen, start, end)
    })
}

fn calibration() -> Result<Value, String> {
    let (d, a) = pair(1);
    let fixtures = [
        (
            d.clone(),
            Move {
                path: vec![],
                expand: true,
            },
        ),
        (
            a,
            Move {
                path: vec![],
                expand: false,
            },
        ),
        (
            Expr::add(d.clone(), Expr::X),
            Move {
                path: vec![0],
                expand: true,
            },
        ),
        (
            Expr::mul(Expr::Two, d.clone()),
            Move {
                path: vec![1],
                expand: true,
            },
        ),
    ];
    let edges = fixtures
        .iter()
        .enumerate()
        .map(|(i, (b, m))| export_edge(b, m, &format!("adva152cal{i}")))
        .collect::<Result<Vec<_>, _>>()?;
    let zero = BTreeMap::from([("x".into(), BigInt::from(0))]);
    let controls = json!({
        "unequal_polynomial_rejected": witness(&d, &Expr::X).is_err(),
        "invalid_position_rejected": rewrite(&d, &[2], true).is_err(),
        "nonduplicate_contraction_rejected": rewrite(&Expr::add(Expr::X, Expr::Two), &[], false).is_err(),
        "zero_polynomial_equality": d.exact().normalize() == pair(1).1.exact().normalize(),
        "zero_guard_refused": d.exact().evaluate_guarded(&zero).is_err(),
    });
    if controls
        .as_object()
        .expect("object")
        .values()
        .any(|v| v != true)
    {
        return Err("calibration control failed".into());
    }
    Ok(json!({ "edges": edges, "controls": controls,
        "lean_false": "theorem adva152bad (x : Int) : 2 * x = x := Int.two_mul x\n",
        "lean_sorry": "theorem adva152sorry (x : Int) : 2 * x = x := by sorry\n#print axioms adva152sorry\n",
        "metamath_false": format!("adva152bad $p |- ( A e. CC -> ( 2 x. A ) = A ) $= {PHI} cA {PHI} id 2timesd $.\n") }))
}

fn run(mode: &str, library_dir: &Path) -> Result<Value, String> {
    if !protected_blocks_match(
        include_str!("search_campaign.rs"),
        include_str!("verifier_search.rs"),
    ) {
        return Err("frozen verifier block drift".into());
    }
    let mut budget = LibraryBudgetV0::new(200).map_err(|e| e.to_string())?;
    let library = load_library_v0(library_dir, 1, &mut budget).map_err(|e| e.to_string())?;
    let (before, after) = pair(1);
    let seed = library
        .snapshot()
        .words
        .first()
        .ok_or("missing seed word")?;
    match &seed.nodes[0].proof {
        WitnessProofV0::ArithmeticTransition {
            before: b,
            after: a,
            ..
        } if *b == before.exact() && *a == after.exact() => {}
        _ => return Err("loaded word is not the declared doubling law".into()),
    }
    let mut counts = Counts::default();
    let result = if mode == "calibrate" {
        calibration()?
    } else {
        let fields: Vec<_> = mode.split(':').collect();
        let mut arms = Vec::new();
        match fields.as_slice() {
            ["pilot", depth] => {
                let depth: usize = depth.parse().map_err(|_| "invalid pilot depth")?;
                for expand in [true, false] {
                    for seed in [1, 7, 19] {
                        for policy in [Policy::Random, Policy::Tabu, Policy::Hybrid] {
                            arms.push(arm(depth, expand, seed, policy, &mut counts)?);
                        }
                    }
                }
            }
            ["round", number, expansion, contraction] => {
                let number: usize = number.parse().map_err(|_| "invalid round number")?;
                if !(1..=100).contains(&number) {
                    return Err("round outside the fixed 100-round contract".into());
                }
                let depth = 2 + (number - 1) % 3;
                let seed = 1000 + number as u64;
                for (expand, policy) in [(true, expansion), (false, contraction)] {
                    arms.push(arm(
                        depth,
                        expand,
                        seed,
                        Policy::parse(policy)?,
                        &mut counts,
                    )?);
                }
            }
            _ => {
                return Err(
                    "mode must be calibrate, pilot:2|3|4, or round:1..100:POLICY:POLICY".into(),
                );
            }
        }
        json!({"arms": arms})
    };
    if counts.total() != counts.work_units {
        return Err("work ledger does not balance".into());
    }
    Ok(json!({
        "schema": "adva.search-campaign.batch.research.v0", "mode": mode,
        "status": "ProvisionalRustChecked", "library_digest": library.digest(),
        "library_units": budget.spent(), "counts": counts, "result": result,
        "frozen_blocks_matched": true,
        "source_blake3": blake3::hash(include_bytes!("search_campaign.rs")).to_hex().to_string(),
        "frozen_source_blake3": blake3::hash(include_bytes!("verifier_search.rs")).to_hex().to_string(),
        "contract_blake3": blake3::hash(include_bytes!("../../../docs/research/0153-frozen-verifier-search-campaign.md")).to_hex().to_string()
    }))
}

fn main() {
    let args: Vec<_> = std::env::args().collect();
    if args.len() != 3 {
        eprintln!("usage: search_campaign MODE LIBRARY_DIRECTORY");
        std::process::exit(2);
    }
    match run(&args[1], Path::new(&args[2])) {
        Ok(value) => println!("{}", serde_json::to_string(&value).expect("serializable")),
        Err(error) => {
            eprintln!("{error}");
            std::process::exit(if error.starts_with("Unknown:") { 3 } else { 2 });
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn verifier_and_calibration_blocks_are_identical_to_frozen_source() {
        assert!(protected_blocks_match(
            include_str!("search_campaign.rs"),
            include_str!("verifier_search.rs")
        ));
        assert!(!protected_blocks_match(
            &include_str!("search_campaign.rs").replacen("nodes <= 127", "nodes <= 128", 1),
            include_str!("verifier_search.rs")
        ));
    }

    #[test]
    fn old_negative_controls_still_pass() {
        assert_eq!(calibration().unwrap()["edges"].as_array().unwrap().len(), 4);
    }

    #[test]
    fn tabu_prefers_fresh_but_does_not_erase_revisited_candidates() {
        let mut cost = Counts::default();
        let (pool, relaxed, explore) =
            selection_pool(&[0, 8], &[Some(0), None], Policy::Tabu, 0, &mut cost).unwrap();
        assert_eq!(pool, [1]);
        assert!(!relaxed && !explore);
        let (pool, relaxed, _) =
            selection_pool(&[0, 8], &[Some(0), Some(1)], Policy::Tabu, 1, &mut cost).unwrap();
        assert_eq!(pool, [0, 1]);
        assert!(relaxed);
    }

    #[test]
    fn hybrid_exploration_is_fixed_and_can_choose_uphill() {
        let mut cost = Counts::default();
        for step in 0..48 {
            let (pool, _, explore) =
                selection_pool(&[1, 9], &[None, None], Policy::Hybrid, step, &mut cost).unwrap();
            assert_eq!(explore, (step + 1) % 4 == 0);
            assert_eq!(pool, if explore { vec![0, 1] } else { vec![0] });
        }
    }

    #[test]
    fn random_ignores_visit_marks_and_residuals() {
        let mut cost = Counts::default();
        let (pool, relaxed, explore) =
            selection_pool(&[100, 0], &[Some(0), None], Policy::Random, 0, &mut cost).unwrap();
        assert_eq!(pool, [0, 1]);
        assert!(!relaxed && !explore);
    }

    #[test]
    fn memory_is_syntax_not_polynomial_and_lookup_is_charged() {
        let mut cost = Counts::default();
        let (a, b) = pair(1);
        assert_eq!(a.exact().normalize(), b.exact().normalize());
        assert_eq!(seen_at(&a, &[b, a.clone()], &mut cost).unwrap(), Some(1));
        assert_eq!(cost.memory_comparisons, 2);
        assert_eq!(cost.work_units, 2);
    }

    #[test]
    fn exhausted_budget_does_not_reset() {
        let mut cost = Counts {
            work_units: 500_000,
            ..Counts::default()
        };
        assert!(
            selection_pool(&[0], &[None], Policy::Random, 0, &mut cost)
                .unwrap_err()
                .starts_with("Unknown:")
        );
        assert_eq!(cost.work_units, 500_000);
        assert_eq!(cost.selection_scans, 0);
    }

    #[test]
    fn empty_pool_and_out_of_range_step_are_refused() {
        let mut cost = Counts::default();
        assert!(selection_pool(&[], &[], Policy::Tabu, 0, &mut cost).is_err());
        assert!(selection_pool(&[0], &[None], Policy::Tabu, 48, &mut cost).is_err());
    }
}
