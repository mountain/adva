//! Research 0152. Arithmetic syntax only: NOT ProgramTerm or native sharing.
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
    enumerated: usize,
    bounded_exclusions: usize,
    witness_checks: usize,
    selected: usize,
}

fn arm(
    depth: usize,
    expand: bool,
    seed: u64,
    guided: bool,
    counts: &mut Counts,
) -> Result<Value, String> {
    let (a, b) = pair(depth);
    let (mut current, target) = if expand { (a, b) } else { (b, a) };
    let initial = current.clone();
    let mut state = seed;
    let mut path = Vec::new();
    while current != target && path.len() < 48 {
        let mut choices = Vec::new();
        moves(&current, &mut Vec::new(), &mut choices);
        let mut candidates = Vec::new();
        let mut excluded = Vec::new();
        for action in choices {
            counts.enumerated += 1;
            if counts.enumerated > 250_000 {
                return Err("Unknown: candidate budget exhausted".into());
            }
            let next = rewrite(&current, &action.path, action.expand)?.after;
            if !next.bounded() {
                counts.bounded_exclusions += 1;
                excluded.push(action);
                continue;
            }
            witness(&current, &next)?;
            counts.witness_checks += 1;
            let score = residual(&next, &target);
            candidates.push((action, next, score));
        }
        if candidates.is_empty() {
            return Err("Unknown: bounded neighborhood empty".into());
        }
        let best = candidates.iter().map(|c| c.2).min().expect("nonempty");
        let selectable: Vec<_> = candidates
            .iter()
            .enumerate()
            .filter(|(_, c)| !guided || c.2 == best)
            .map(|(i, _)| i)
            .collect();
        let selected = selectable[(next_random(&mut state) % selectable.len() as u64) as usize];
        let (action, next, score) = &candidates[selected];
        let label = format!("adva152e{}", counts.selected);
        let edge = export_edge(&current, action, &label)?;
        counts.witness_checks += 1; // Export rechecks; not hidden in candidate costs.
        counts.selected += 1;
        path.push(json!({ "edge": edge, "selected_index": selected,
            "residual_before": residual(&current, &target), "residual_after": score,
            "candidates": candidates.iter().map(|(m, _, r)| json!({"move": m, "residual": r})).collect::<Vec<_>>(),
            "bounded_exclusions": excluded }));
        current = next.clone();
    }
    Ok(json!({ "depth": depth, "expand": expand, "seed": seed,
        "policy": if guided { "residual" } else { "random" }, "initial": initial, "target": target,
        "status": if current == target { "Reached" } else { "Unknown" },
        "stop_reason": if current == target { "literal_target" } else { "48_step_limit" },
        "final": current, "residual": residual(&current, &target), "steps": path.len(), "path": path }))
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
    let mut budget = LibraryBudgetV0::new(50_000).map_err(|e| e.to_string())?;
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
        let depth: usize = mode
            .parse()
            .map_err(|_| "mode must be calibrate or depth 2, 3, 4")?;
        if !(2..=4).contains(&depth) {
            return Err("depth outside the finite contract".into());
        }
        let mut arms = Vec::new();
        for expand in [true, false] {
            for seed in [1, 7, 19] {
                for guided in [false, true] {
                    arms.push(arm(depth, expand, seed, guided, &mut counts)?);
                }
            }
        }
        json!({"arms": arms})
    };
    Ok(
        json!({ "schema": "adva.three-verifier-search.research.v0", "mode": mode,
        "status": "ProvisionalRustChecked", "library_digest": library.digest(),
        "library_units": budget.spent(), "counts": counts, "result": result,
        "source_blake3": blake3::hash(include_bytes!("verifier_search.rs")).to_hex().to_string(),
        "contract_blake3": blake3::hash(include_bytes!("../../../docs/research/0152-three-verifier-residual-search.md")).to_hex().to_string() }),
    )
}

fn main() {
    let args: Vec<_> = std::env::args().collect();
    if args.len() != 3 {
        eprintln!("usage: verifier_search calibrate|2|3|4 LIBRARY_DIRECTORY");
        std::process::exit(2);
    }
    match run(&args[1], Path::new(&args[2])) {
        Ok(value) => println!("{}", serde_json::to_string(&value).expect("serializable")),
        Err(error) => {
            eprintln!("{error}");
            std::process::exit(2);
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn calibration_has_guard_and_rejection_controls() {
        assert_eq!(calibration().unwrap()["edges"].as_array().unwrap().len(), 4);
    }
    #[test]
    fn residual_is_syntactic_not_polynomial_equality() {
        let (a, b) = pair(3);
        assert_eq!(a.exact().normalize(), b.exact().normalize());
        assert!(residual(&a, &b) > 0);
        assert_eq!(residual(&a, &a), 0);
    }
    #[test]
    fn zigzag_retains_distinct_directions_and_original_endpoint() {
        let (a, _) = pair(2);
        let forward = rewrite(&a, &[], true).unwrap();
        let backward = rewrite(&forward.after, &[], false).unwrap();
        assert_eq!(backward.after, a);
        assert_ne!(forward.mm, backward.mm);
        assert!(witness(&a, &forward.after).is_ok());
    }
    #[test]
    fn contextual_rewrite_preserves_untouched_branch() {
        let (a, b) = pair(1);
        let start = Expr::add(a, Expr::Two);
        assert_eq!(
            rewrite(&start, &[0], true).unwrap().after,
            Expr::add(b, Expr::Two)
        );
        assert!(rewrite(&start, &[1], true).is_err());
        assert!(rewrite(&start, &[0, 1, 0], true).is_err());
    }
    #[test]
    fn finite_tree_bound_is_enforced_before_witness() {
        assert!(witness(&pair(7).1, &pair(7).0).is_err());
    }
    #[test]
    fn mm_class_constructor_uses_floating_hypothesis_order() {
        assert_eq!(pair(1).0.class_proof(), "c2 cA cmul co");
        assert!(
            rewrite(&pair(1).0, &[], true)
                .unwrap()
                .mm
                .ends_with("id 2timesd")
        );
    }
}
