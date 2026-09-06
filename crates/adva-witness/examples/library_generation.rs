//! Research 0151: target-blind, library-driven arithmetic proposal recipes.
//! This is not a ProgramTerm calculus or a generally certified substitution.
use adva_witness::*;
use num_bigint::BigInt;
use serde::{Deserialize, Serialize};
use serde_json::{Value, json};
use std::collections::BTreeMap;
use std::fs::{self, File, OpenOptions};
use std::io::Write;
use std::path::{Path, PathBuf};

type Result<T> = std::result::Result<T, LibraryCheckpointErrorV0>;

fn invalid(message: &str) -> LibraryCheckpointErrorV0 {
    LibraryCheckpointErrorV0::Invalid(message.into())
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
enum Proposal {
    X,
    Two,
    Add(Box<Self>, Box<Self>),
    Multiply(Box<Self>, Box<Self>),
    Use { recipe: usize, argument: Box<Self> },
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
enum Definition {
    Seed {
        snapshot: String,
        witness: ArtifactKeyV0,
        before: ExactExprV0,
        after: ExactExprV0,
    },
    Composite {
        stage: usize,
        proposal: Proposal,
    },
}

// Only checked base loading and completely replayed stages extend this book.
// Definitions propose syntax; none authorize a future pair without rechecking.
struct Book(Vec<Definition>);

#[derive(Clone, Debug, Default, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
struct Costs {
    definition: u32,
    generation: u32,
    expansion: u32,
    checking: u32,
}

enum Work {
    Definition,
    Generation,
    Expansion,
    Checking,
}

struct Meter<'a> {
    budget: &'a mut LibraryBudgetV0,
    costs: Costs,
}

impl Meter<'_> {
    fn charge(&mut self, work: Work) -> Result<()> {
        self.budget.charge()?;
        *match work {
            Work::Definition => &mut self.costs.definition,
            Work::Generation => &mut self.costs.generation,
            Work::Expansion => &mut self.costs.expansion,
            Work::Checking => &mut self.costs.checking,
        } += 1;
        Ok(())
    }
}

struct Expanded {
    expression: ExactExprV0,
    nodes: usize,
    depth: usize,
}

impl Expanded {
    fn x() -> Self {
        Self {
            expression: ExactExprV0::variable("x"),
            nodes: 1,
            depth: 1,
        }
    }

    fn two() -> Self {
        Self {
            expression: ExactExprV0::constant(2),
            nodes: 1,
            depth: 1,
        }
    }

    fn join(left: Self, right: Self, multiply: bool) -> Result<Self> {
        let nodes = 1 + left.nodes + right.nodes;
        let depth = 1 + left.depth.max(right.depth);
        if nodes > 127 || depth > 16 {
            return Err(invalid("expanded tree exceeds 127 nodes or depth 16"));
        }
        Ok(Self {
            expression: if multiply {
                ExactExprV0::product(left.expression, right.expression)
            } else {
                ExactExprV0::sum(left.expression, right.expression)
            },
            nodes,
            depth,
        })
    }
}

// Literal arithmetic-tree replacement, not stable function-hole substitution.
// Traversal and every copied argument node are charged, with bounded outputs.
fn replace_x(
    body: &ExactExprV0,
    argument: Option<&ExactExprV0>,
    depth: usize,
    meter: &mut Meter<'_>,
) -> Result<Expanded> {
    meter.charge(Work::Expansion)?;
    if depth > 16 {
        return Err(invalid("arithmetic input depth bound"));
    }
    match body {
        ExactExprV0::Variable { name } if name == "x" => match argument {
            Some(argument) => replace_x(argument, None, 1, meter),
            None => Ok(Expanded::x()),
        },
        ExactExprV0::Constant { value } if value == &BigInt::from(2) => Ok(Expanded::two()),
        ExactExprV0::Add { left, right } | ExactExprV0::Multiply { left, right } => Expanded::join(
            replace_x(left, argument, depth + 1, meter)?,
            replace_x(right, argument, depth + 1, meter)?,
            matches!(body, ExactExprV0::Multiply { .. }),
        ),
        _ => Err(invalid("only x and literal 2 are in this proposal grammar")),
    }
}

fn inspect_proposal(
    proposal: &Proposal,
    scope: usize,
    nodes: &mut usize,
    meter: &mut Meter<'_>,
) -> Result<()> {
    meter.charge(Work::Definition)?;
    *nodes += 1;
    if *nodes > 3 {
        return Err(invalid("proposal definition exceeds three surface nodes"));
    }
    match proposal {
        Proposal::X | Proposal::Two => Ok(()),
        Proposal::Add(left, right) | Proposal::Multiply(left, right) => {
            inspect_proposal(left, scope, nodes, meter)?;
            inspect_proposal(right, scope, nodes, meter)
        }
        Proposal::Use { recipe, argument } => {
            if *recipe >= scope {
                return Err(invalid("missing, forward or cyclic recipe reference"));
            }
            inspect_proposal(argument, scope, nodes, meter)
        }
    }
}

fn inspect_book(book: &Book, meter: &mut Meter<'_>) -> Result<()> {
    if book.0.is_empty() || book.0.len() > 4 {
        return Err(invalid("recipe book bound"));
    }
    for (index, definition) in book.0.iter().enumerate() {
        meter.charge(Work::Definition)?;
        match definition {
            Definition::Seed { before, after, .. } if index == 0 => {
                replace_x(before, None, 1, meter)?;
                replace_x(after, None, 1, meter)?;
            }
            Definition::Composite { stage, proposal } if index == stage + 1 => {
                inspect_proposal(proposal, index, &mut 0, meter)?;
            }
            _ => return Err(invalid("invalid recipe origin/order")),
        }
    }
    Ok(())
}

fn expand(
    proposal: &Proposal,
    book: &Book,
    scope: usize,
    after: bool,
    depth: usize,
    meter: &mut Meter<'_>,
) -> Result<Expanded> {
    meter.charge(Work::Expansion)?;
    if depth > 16 {
        return Err(invalid("proposal expansion depth bound"));
    }
    match proposal {
        Proposal::X => Ok(Expanded::x()),
        Proposal::Two => Ok(Expanded::two()),
        Proposal::Add(left, right) | Proposal::Multiply(left, right) => Expanded::join(
            expand(left, book, scope, after, depth + 1, meter)?,
            expand(right, book, scope, after, depth + 1, meter)?,
            matches!(proposal, Proposal::Multiply(..)),
        ),
        Proposal::Use { recipe, argument } => {
            if *recipe >= scope || *recipe >= book.0.len() {
                return Err(invalid("missing, forward or cyclic recipe reference"));
            }
            let argument = expand(argument, book, scope, after, depth + 1, meter)?;
            let body = match &book.0[*recipe] {
                Definition::Seed {
                    before,
                    after: other,
                    ..
                } => replace_x(if after { other } else { before }, None, 1, meter)?,
                Definition::Composite { proposal, .. } => {
                    expand(proposal, book, *recipe, after, depth + 1, meter)?
                }
            };
            replace_x(&body.expression, Some(&argument.expression), 1, meter)
        }
    }
}

fn emit(
    proposal: Proposal,
    layer: &mut Vec<Proposal>,
    all: &mut Vec<Proposal>,
    meter: &mut Meter<'_>,
) -> Result<()> {
    meter.charge(Work::Generation)?;
    if all.len() == 64 {
        return Err(LibraryCheckpointErrorV0::Unknown);
    }
    layer.push(proposal.clone());
    all.push(proposal);
    Ok(())
}

// There is deliberately no task, expected value, coefficient or target input.
fn generate(enabled: &[usize], all: &mut Vec<Proposal>, meter: &mut Meter<'_>) -> Result<()> {
    if enabled.len() > 3 || enabled.windows(2).any(|pair| pair[0] <= pair[1]) {
        return Err(invalid(
            "generator requires at most three descending references",
        ));
    }
    let mut layers: Vec<Vec<Proposal>> = vec![vec![]; 4];
    emit(Proposal::X, &mut layers[1], all, meter)?;
    emit(Proposal::Two, &mut layers[1], all, meter)?;
    for size in 2..=3 {
        let mut layer = Vec::new();
        for &recipe in enabled {
            for argument in &layers[size - 1] {
                emit(
                    Proposal::Use {
                        recipe,
                        argument: Box::new(argument.clone()),
                    },
                    &mut layer,
                    all,
                    meter,
                )?;
            }
        }
        for left_size in 1..size - 1 {
            let right_size = size - 1 - left_size;
            for left in &layers[left_size] {
                for right in &layers[right_size] {
                    emit(
                        Proposal::Add(Box::new(left.clone()), Box::new(right.clone())),
                        &mut layer,
                        all,
                        meter,
                    )?;
                    emit(
                        Proposal::Multiply(Box::new(left.clone()), Box::new(right.clone())),
                        &mut layer,
                        all,
                        meter,
                    )?;
                }
            }
        }
        layers[size] = layer;
    }
    Ok(())
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
struct Task {
    stage: usize,
    observations: [(i32, i32); 3],
    authority: String,
}

fn task(stage: usize) -> Result<Task> {
    let observations = match stage {
        0 => [(1, 4), (2, 8), (-1, -4)],
        1 => [(1, 8), (2, 16), (-1, -8)],
        2 => [(1, 32), (2, 64), (-1, -32)],
        _ => return Err(invalid("three-stage continuation limit")),
    };
    Ok(Task {
        stage,
        observations,
        authority: "supplied-calibration-assumptions-not-world-measurements".into(),
    })
}

#[derive(Clone, Copy, Debug, Eq, PartialEq, Serialize, Deserialize)]
enum Outcome {
    AcceptedPair,
    RejectedCalibration,
    CertificateObstruction,
    GuardObstruction,
    Open,
    Unknown,
    FeedbackVerified,
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
struct Pair {
    before: ExactExprV0,
    after: ExactExprV0,
    nodes: [usize; 2],
    variable_occurrences: [BTreeMap<String, usize>; 2],
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
struct Entry {
    ordinal: usize,
    proposal: Proposal,
    pair: Option<Pair>,
    predictions: Vec<[String; 2]>,
    status: Outcome,
    error: Option<String>,
    witnesses: Vec<WitnessArtifactV0>,
}

fn check_entry(entry: &mut Entry, book: &Book, task: &Task, meter: &mut Meter<'_>) -> Result<()> {
    let before = expand(&entry.proposal, book, book.0.len(), false, 1, meter)?;
    let after = expand(&entry.proposal, book, book.0.len(), true, 1, meter)?;
    meter.charge(Work::Checking)?;
    let pair = Pair {
        nodes: [before.nodes, after.nodes],
        variable_occurrences: [
            before.expression.variable_occurrences(),
            after.expression.variable_occurrences(),
        ],
        before: before.expression,
        after: after.expression,
    };
    entry.pair = Some(pair);
    let pair = entry.pair.as_ref().expect("assigned pair");
    meter.charge(Work::Checking)?;
    let before_poly = pair
        .before
        .normalize()
        .map_err(|e| invalid(&e.to_string()))?;
    meter.charge(Work::Checking)?;
    let after_poly = pair
        .after
        .normalize()
        .map_err(|e| invalid(&e.to_string()))?;
    meter.charge(Work::Checking)?;
    if before_poly != after_poly {
        entry.status = Outcome::CertificateObstruction;
        entry.error = Some("expanded polynomial pair differs".into());
        return Ok(());
    }
    let mut agrees = true;
    for (input, expected) in task.observations {
        meter.charge(Work::Checking)?;
        if !(-8..=8).contains(&input) || !(-1_000_000..=1_000_000).contains(&expected) {
            return Err(invalid("calibration bound"));
        }
        let environment = BTreeMap::from([("x".into(), BigInt::from(input))]);
        let mut predictions = Vec::new();
        for expression in [&pair.before, &pair.after] {
            meter.charge(Work::Checking)?;
            match expression.evaluate_guarded(&environment) {
                Ok(value) => {
                    agrees &= value == BigInt::from(expected);
                    predictions.push(value.to_string());
                }
                Err(error) => {
                    entry.status = Outcome::GuardObstruction;
                    entry.error = Some(error.to_string());
                    return Ok(());
                }
            }
        }
        entry
            .predictions
            .push([predictions[0].clone(), predictions[1].clone()]);
    }
    if !agrees {
        entry.status = Outcome::RejectedCalibration;
        return Ok(());
    }
    let mut store = WitnessStoreV0::new();
    meter.charge(Work::Checking)?;
    let body = store
        .insert(WitnessProofV0::ArithmeticTransition {
            actual_boundary: BoundaryChargeV0::zero(),
            declared_boundary: BoundaryChargeV0::zero(),
            before: pair.before.clone(),
            after: pair.after.clone(),
        })
        .map_err(|e| invalid(&e.to_string()))?;
    meter.charge(Work::Checking)?;
    let seal = store
        .insert(WitnessProofV0::Seal { body: body.clone() })
        .map_err(|e| invalid(&e.to_string()))?;
    entry.witnesses = [body, seal]
        .iter()
        .map(|key| store.artifact(key).expect("inserted").clone())
        .collect();
    entry.status = Outcome::AcceptedPair;
    Ok(())
}

#[derive(Clone, Copy, Debug, Eq, PartialEq, Serialize, Deserialize)]
enum Mode {
    LibraryEnabled,
    NewestDisabled,
    OrdinaryMacro,
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
struct Search {
    mode: Mode,
    enabled: Vec<usize>,
    proposals: Vec<Proposal>,
    generation_complete: bool,
    entries: Vec<Entry>,
    pending: usize,
    status: Outcome,
    costs: Costs,
}

fn search(book: &Book, task: &Task, mode: Mode, budget: &mut LibraryBudgetV0) -> Result<Search> {
    let mut meter = Meter {
        budget,
        costs: Costs::default(),
    };
    let enabled = (0..book.0.len())
        .rev()
        .filter(|index| mode != Mode::NewestDisabled || *index + 1 != book.0.len())
        .collect::<Vec<_>>();
    let mut result = Search {
        mode,
        enabled,
        proposals: vec![],
        generation_complete: false,
        entries: vec![],
        pending: 0,
        status: Outcome::Unknown,
        costs: Costs::default(),
    };
    let preparation = inspect_book(book, &mut meter)
        .and_then(|()| generate(&result.enabled, &mut result.proposals, &mut meter));
    match preparation {
        Ok(()) => result.generation_complete = true,
        Err(LibraryCheckpointErrorV0::Unknown) => {
            result.costs = meter.costs;
            return Ok(result);
        }
        Err(error) => return Err(error),
    }
    for (ordinal, proposal) in result.proposals.iter().enumerate() {
        let mut entry = Entry {
            ordinal,
            proposal: proposal.clone(),
            pair: None,
            predictions: vec![],
            status: Outcome::Unknown,
            error: None,
            witnesses: vec![],
        };
        let checked = check_entry(&mut entry, book, task, &mut meter);
        match checked {
            Ok(()) => result.pending = ordinal + 1,
            Err(LibraryCheckpointErrorV0::Unknown) => {
                entry.error = Some("shared budget exhausted; candidate not admitted".into());
                result.entries.push(entry);
                result.costs = meter.costs;
                return Ok(result);
            }
            Err(error) => {
                entry.status = Outcome::CertificateObstruction;
                entry.error = Some(error.to_string());
                result.pending = ordinal + 1;
            }
        }
        result.entries.push(entry);
    }
    result.status = if result
        .entries
        .iter()
        .any(|entry| entry.status == Outcome::AcceptedPair)
    {
        Outcome::AcceptedPair
    } else {
        Outcome::Open
    };
    result.costs = meter.costs;
    Ok(result)
}

fn references(proposal: &Proposal, wanted: usize) -> bool {
    match proposal {
        Proposal::Use { recipe, argument } => *recipe == wanted || references(argument, wanted),
        Proposal::Add(left, right) | Proposal::Multiply(left, right) => {
            references(left, wanted) || references(right, wanted)
        }
        _ => false,
    }
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
struct Stage {
    schema: String,
    revision: String,
    seed_digest: String,
    task: Task,
    definitions_before: Vec<Definition>,
    searches: Vec<Search>,
    selected: Option<Proposal>,
    status: Outcome,
    residuals: Vec<String>,
}

fn revision() -> String {
    let mut hash = blake3::Hasher::new();
    hash.update(include_bytes!("library_generation.rs"));
    hash.update(include_bytes!(
        "../../../docs/research/0151-library-driven-proposal-feedback.md"
    ));
    hash.update(library_checker_revision_v0().as_bytes());
    hash.finalize().to_hex().to_string()
}

fn stage(book: &Book, index: usize, budget: &mut LibraryBudgetV0) -> Result<Stage> {
    if book.0.len() != index + 1 || index >= 3 {
        return Err(invalid("stage/recipe boundary mismatch"));
    }
    let Definition::Seed { snapshot, .. } = &book.0[0] else {
        return Err(invalid("missing seed"));
    };
    let mut result = Stage {
        schema: "adva.proposal-feedback.research.v0".into(), revision: revision(),
        seed_digest: snapshot.clone(), task: task(index)?, definitions_before: book.0.clone(),
        searches: vec![], selected: None, status: Outcome::Unknown,
        residuals: vec![
            "GeneralVocabularyPromotion: CertificateObstruction (no coverage/invariance certificate)".into(),
            "NativeProgramRealization: NotRepresentableInThisExperiment (no source/occurrence or copy certificate)".into(),
            "SelfInterpretation: NotImplemented; Rust-hosted proposal construction only".into(),
            "WorldIdentification: Open; supplied observations are not world measurements".into(),
            "OrdinaryMacroAdvantage: NotDemonstrated; full expanded costs must be compared".into(),
        ],
    };
    for mode in [
        Mode::LibraryEnabled,
        Mode::NewestDisabled,
        Mode::OrdinaryMacro,
    ] {
        let search = search(book, &result.task, mode, budget)?;
        let unknown = search.status == Outcome::Unknown;
        result.searches.push(search);
        if unknown {
            return Ok(result);
        }
    }
    if let Err(error) = budget.charge() {
        return match error {
            LibraryCheckpointErrorV0::Unknown => Ok(result),
            other => Err(other),
        };
    }
    let enabled = &result.searches[0];
    let disabled = &result.searches[1];
    let ordinary = &result.searches[2];
    if enabled.proposals != ordinary.proposals
        || enabled.entries != ordinary.entries
        || enabled.costs != ordinary.costs
    {
        result.status = Outcome::CertificateObstruction;
        return Ok(result);
    }
    let first = enabled
        .entries
        .iter()
        .find(|entry| entry.status == Outcome::AcceptedPair);
    match first {
        Some(entry) if disabled.status == Outcome::Open && references(&entry.proposal, index) => {
            result.selected = Some(entry.proposal.clone());
            result.status = Outcome::FeedbackVerified;
        }
        _ => result.status = Outcome::Open,
    }
    Ok(result)
}

fn extend(book: &mut Book, checked: &Stage) -> Result<()> {
    if checked.status != Outcome::FeedbackVerified || checked.definitions_before != book.0 {
        return Err(invalid(
            "only fully checked feedback extends the proposal book",
        ));
    }
    book.0.push(Definition::Composite {
        stage: checked.task.stage,
        proposal: checked
            .selected
            .clone()
            .ok_or_else(|| invalid("missing selected proposal"))?,
    });
    Ok(())
}

fn load_seed(directory: &Path, budget: &mut LibraryBudgetV0) -> Result<Book> {
    let checked = load_library_v0(directory, 1, budget)?;
    budget.charge()?;
    if checked.digest() != "4480fa1e8b60ab945879f8644820ab8ef242dceaf494470bedb9b68b5fd976ee" {
        return Err(invalid("seed is not the frozen 0150 successor"));
    }
    let word = checked
        .snapshot()
        .words
        .first()
        .ok_or_else(|| invalid("missing seed word"))?;
    let WitnessProofV0::ArithmeticTransition { before, after, .. } = &word.nodes[0].proof else {
        return Err(invalid("seed word has no arithmetic body"));
    };
    Ok(Book(vec![Definition::Seed {
        snapshot: checked.digest().into(),
        witness: word.nodes[1].key.clone(),
        before: before.clone(),
        after: after.clone(),
    }]))
}

fn stage_path(directory: &Path, index: usize) -> Result<PathBuf> {
    if index >= 3 {
        return Err(invalid("stage path bound"));
    }
    Ok(directory.join(format!("stage-{index:04}.json")))
}

fn verify_stage(
    book: &Book,
    index: usize,
    stored: &Stage,
    budget: &mut LibraryBudgetV0,
) -> Result<Stage> {
    budget.charge()?;
    if stored.task != task(index)?
        || stored.revision != revision()
        || stored.definitions_before != book.0
    {
        return Err(invalid("stale task, method or recipe origin"));
    }
    let expected = stage(book, index, budget)?;
    budget.charge()?;
    if expected.status == Outcome::Unknown {
        return Err(LibraryCheckpointErrorV0::Unknown);
    }
    if expected != *stored {
        return Err(invalid("forged or incomplete generation/checking receipt"));
    }
    Ok(expected)
}

fn reload(
    base: &Path,
    directory: &Path,
    count: usize,
    budget: &mut LibraryBudgetV0,
) -> Result<Book> {
    if count > 3 {
        return Err(invalid("journal ancestry bound"));
    }
    let mut book = load_seed(base, budget)?;
    for index in 0..count {
        let bytes = read_library_bytes_v0(&stage_path(directory, index)?, budget)?;
        budget.charge()?;
        let stored: Stage = serde_json::from_slice(&bytes)?;
        let checked = verify_stage(&book, index, &stored, budget)?;
        extend(&mut book, &checked)?;
    }
    Ok(book)
}

fn workflow(
    base: &Path,
    directory: &Path,
    report: &mut Value,
    budget: &mut LibraryBudgetV0,
) -> Result<()> {
    let loading_start = budget.spent();
    let mut book = load_seed(base, budget)?;
    report["initial_load_units"] = json!(budget.spent() - loading_start);
    report["initial_definitions"] = serde_json::to_value(&book.0)?;
    for index in 0..3 {
        report["phase"] = json!({"stage": index, "action": "generate-and-check"});
        let production_start = budget.spent();
        let checked = stage(&book, index, budget)?;
        let status = checked.status;
        report["stages"].as_array_mut().expect("array").push(json!({
            "stage": index, "status": status, "selected": checked.selected,
            "production_units": budget.spent() - production_start,
            "searches": checked.searches.iter().map(|search| json!({
                "mode": search.mode, "candidates": search.proposals.len(), "status": search.status,
                "accepted": search.entries.iter().filter(|entry| entry.status == Outcome::AcceptedPair).count(),
                "costs": search.costs
            })).collect::<Vec<_>>()
        }));
        // Prepaid reserve for this checkpoint, even when the search is Unknown.
        // Reserve is spent before searching in main; no fresh fuel is created.
        publish_prepaid(&stage_path(directory, index)?, &checked)?;
        report["completed_checkpoints"] = json!(index + 1);
        if status != Outcome::FeedbackVerified {
            report["stopping_outcome"] = json!(status);
            return if status == Outcome::Unknown {
                Err(LibraryCheckpointErrorV0::Unknown)
            } else {
                Err(invalid("feedback gate did not pass"))
            };
        }
        drop(book);
        report["phase"] = json!({"stage": index, "action": "disk-replay-before-continuation"});
        let replay_start = budget.spent();
        book = reload(base, directory, index + 1, budget)?;
        report["stages"][index]["reload_and_replay_units"] = json!(budget.spent() - replay_start);
        report["replayed_stages"] = json!(index + 1);
    }
    report["final_definitions"] = serde_json::to_value(&book.0)?;
    report["phase"] = json!("declared-three-stage-limit");
    report["stopping_outcome"] = json!(
        "CertificateObstruction: general promotion lacks coverage and native realization; ordinary macros match"
    );
    Ok(())
}

// The caller prepays one bounded persistence operation. Keeping the same
// implementation prevents the reserve from silently changing write semantics.
fn publish_prepaid(path: &Path, value: &impl Serialize) -> Result<()> {
    write_checkpoint(path, value)
}

fn write_checkpoint(path: &Path, value: &impl Serialize) -> Result<()> {
    let bytes = serde_json::to_vec_pretty(value)?;
    if bytes.len() + 1 >= 1_048_576 {
        return Err(invalid("checkpoint exceeds 1 MiB"));
    }
    let staging = path.with_extension("pending");
    let mut file = OpenOptions::new()
        .write(true)
        .create_new(true)
        .open(&staging)?;
    file.write_all(&bytes)?;
    file.write_all(b"\n")?;
    file.sync_all()?;
    fs::hard_link(&staging, path)?; // No-clobber, including an existing symlink.
    let parent = path.parent().unwrap_or(Path::new("."));
    File::open(parent)?.sync_all()?;
    fs::remove_file(&staging)?; // Only this call's successfully created staging link.
    File::open(parent)?.sync_all()?;
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::sync::atomic::{AtomicU64, Ordering};

    fn fuel() -> LibraryBudgetV0 {
        LibraryBudgetV0::new(50_000).unwrap()
    }

    fn base_path() -> PathBuf {
        Path::new(env!("CARGO_MANIFEST_DIR")).join("../../adva-library/stability")
    }

    fn seed() -> Book {
        load_seed(&base_path(), &mut fuel()).unwrap()
    }

    fn use_recipe(recipe: usize, argument: Proposal) -> Proposal {
        Proposal::Use {
            recipe,
            argument: Box::new(argument),
        }
    }

    struct Scratch(PathBuf);
    impl Scratch {
        fn new() -> Self {
            static NEXT: AtomicU64 = AtomicU64::new(0);
            let path = std::env::temp_dir().join(format!(
                "adva-generation-test-{}-{}",
                std::process::id(),
                NEXT.fetch_add(1, Ordering::Relaxed)
            ));
            fs::create_dir(&path).unwrap();
            Self(path)
        }
    }
    impl Drop for Scratch {
        fn drop(&mut self) {
            // Only this test's newly created flat directory and generated files.
            for entry in fs::read_dir(&self.0).unwrap() {
                fs::remove_file(entry.unwrap().path()).unwrap();
            }
            fs::remove_dir(&self.0).unwrap();
        }
    }

    #[test]
    fn task_changes_checks_not_generation() {
        let book = seed();
        let mut ledger = fuel();
        let first = search(&book, &task(0).unwrap(), Mode::LibraryEnabled, &mut ledger).unwrap();
        let later = search(&book, &task(1).unwrap(), Mode::LibraryEnabled, &mut ledger).unwrap();
        assert_eq!(first.proposals, later.proposals);
        assert_eq!(first.proposals.len(), 14);
        assert_eq!(first.status, Outcome::AcceptedPair);
        assert_eq!(later.status, Outcome::Open);
        assert!(
            first
                .entries
                .iter()
                .any(|entry| entry.status == Outcome::RejectedCalibration)
        );
    }

    #[test]
    fn three_stages_feed_checked_recipes_back_with_honest_macro_control() {
        let mut ledger = fuel();
        let mut book = load_seed(&base_path(), &mut ledger).unwrap();
        for (index, count) in [14, 22, 34].into_iter().enumerate() {
            let checked = stage(&book, index, &mut ledger).unwrap();
            assert_eq!(checked.status, Outcome::FeedbackVerified);
            assert_eq!(checked.searches[0].proposals.len(), count);
            assert_eq!(checked.searches[1].status, Outcome::Open);
            assert_eq!(checked.searches[0].entries, checked.searches[2].entries);
            assert_eq!(checked.searches[0].costs, checked.searches[2].costs);
            assert!(references(checked.selected.as_ref().unwrap(), index));
            let pair = checked.searches[0]
                .entries
                .iter()
                .find(|entry| entry.status == Outcome::AcceptedPair)
                .unwrap()
                .pair
                .as_ref()
                .unwrap();
            assert_ne!(pair.before, pair.after);
            assert_eq!(pair.variable_occurrences[0]["x"], 1);
            assert!(pair.variable_occurrences[1]["x"] > 1);
            extend(&mut book, &checked).unwrap();
        }
        assert_eq!(book.0.len(), 4);
        assert!(stage(&book, 3, &mut ledger).is_err());
    }

    #[test]
    fn zero_fuel_and_partial_prefix_are_not_admitted() {
        let book = seed();
        let empty = search(
            &book,
            &task(0).unwrap(),
            Mode::LibraryEnabled,
            &mut LibraryBudgetV0::new(0).unwrap(),
        )
        .unwrap();
        assert_eq!(empty.status, Outcome::Unknown);
        assert!(!empty.generation_complete);
        assert!(empty.entries.is_empty());
        let partial = search(
            &book,
            &task(0).unwrap(),
            Mode::LibraryEnabled,
            &mut LibraryBudgetV0::new(45).unwrap(),
        )
        .unwrap();
        assert_eq!(partial.status, Outcome::Unknown);
        assert!(partial.generation_complete);
        assert!(
            partial
                .entries
                .iter()
                .any(|entry| entry.status == Outcome::RejectedCalibration)
        );
        assert_eq!(partial.entries.last().unwrap().status, Outcome::Unknown);
        assert_eq!(partial.pending + 1, partial.entries.len());
    }

    #[test]
    fn generation_exhaustion_retains_its_syntax_prefix() {
        let mut ledger = LibraryBudgetV0::new(3).unwrap();
        let mut meter = Meter {
            budget: &mut ledger,
            costs: Costs::default(),
        };
        let mut proposals = vec![];
        assert!(matches!(
            generate(&[0], &mut proposals, &mut meter),
            Err(LibraryCheckpointErrorV0::Unknown)
        ));
        assert_eq!(
            proposals,
            [Proposal::X, Proposal::Two, use_recipe(0, Proposal::X)]
        );
        assert_eq!(meter.budget.spent(), 3);
    }

    #[test]
    fn zero_is_guard_obstruction_even_when_polynomials_agree() {
        let mut zero_task = task(0).unwrap();
        zero_task.observations[0] = (0, 0);
        let result = search(&seed(), &zero_task, Mode::LibraryEnabled, &mut fuel()).unwrap();
        let entry = result
            .entries
            .iter()
            .find(|entry| entry.proposal == use_recipe(0, use_recipe(0, Proposal::X)))
            .unwrap();
        assert_eq!(entry.status, Outcome::GuardObstruction);
        assert!(entry.witnesses.is_empty());
    }

    #[test]
    fn missing_and_cyclic_references_are_blocked() {
        let mut book = seed();
        let mut ledger = fuel();
        let mut meter = Meter {
            budget: &mut ledger,
            costs: Costs::default(),
        };
        assert!(expand(&use_recipe(1, Proposal::X), &book, 1, false, 1, &mut meter).is_err());
        book.0.push(Definition::Composite {
            stage: 0,
            proposal: use_recipe(1, Proposal::X),
        });
        assert!(inspect_book(&book, &mut meter).is_err());
        assert!(expand(&use_recipe(1, Proposal::X), &book, 2, false, 1, &mut meter).is_err());
    }

    #[test]
    fn expanded_pair_is_rechecked_not_authorized_by_recipe_name() {
        let mut book = seed();
        let Definition::Seed { after, .. } = &mut book.0[0] else {
            panic!("seed");
        };
        *after = ExactExprV0::variable("x");
        let result = search(&book, &task(0).unwrap(), Mode::LibraryEnabled, &mut fuel()).unwrap();
        let entry = result
            .entries
            .iter()
            .find(|entry| entry.proposal == use_recipe(0, Proposal::X))
            .unwrap();
        assert_eq!(entry.status, Outcome::CertificateObstruction);
        assert!(entry.witnesses.is_empty());
    }

    #[test]
    fn input_and_expansion_bounds_precede_normalization() {
        let mut ledger = fuel();
        let mut meter = Meter {
            budget: &mut ledger,
            costs: Costs::default(),
        };
        assert!(replace_x(&ExactExprV0::variable("y"), None, 1, &mut meter).is_err());
        assert!(replace_x(&ExactExprV0::constant(3), None, 1, &mut meter).is_err());
        let mut tree = ExactExprV0::variable("x");
        for _ in 0..7 {
            tree = ExactExprV0::sum(tree.clone(), tree);
        }
        assert!(replace_x(&tree, None, 1, &mut meter).is_err());
        let mut proposals = vec![];
        assert!(generate(&[0, 1], &mut proposals, &mut meter).is_err());
    }

    #[test]
    fn forged_receipts_and_changed_task_do_not_extend_book() {
        let book = seed();
        let mut ledger = fuel();
        let original = stage(&book, 0, &mut ledger).unwrap();
        let mut forged = original.clone();
        forged.searches[0].entries[0].status = Outcome::AcceptedPair;
        assert!(verify_stage(&book, 0, &forged, &mut ledger).is_err());
        let mut changed = original.clone();
        changed.task.observations[0].1 = 5;
        assert!(verify_stage(&book, 0, &changed, &mut ledger).is_err());
        let mut origin = original.clone();
        origin.seed_digest.push('0');
        assert!(verify_stage(&book, 0, &origin, &mut ledger).is_err());
        assert_eq!(
            verify_stage(&book, 0, &original, &mut ledger).unwrap(),
            original
        );
        let mut unknown = original;
        unknown.status = Outcome::Unknown;
        assert!(extend(&mut seed(), &unknown).is_err());
    }

    #[test]
    fn checkpoint_no_clobber_and_reload_are_real_disk_operations() {
        let scratch = Scratch::new();
        let book = seed();
        let mut ledger = fuel();
        let checked = stage(&book, 0, &mut ledger).unwrap();
        let path = stage_path(&scratch.0, 0).unwrap();
        ledger.charge().unwrap();
        publish_prepaid(&path, &checked).unwrap();
        let original = fs::read(&path).unwrap();
        let loaded = reload(&base_path(), &scratch.0, 1, &mut ledger).unwrap();
        assert_eq!(loaded.0.len(), 2);
        ledger.charge().unwrap();
        assert!(publish_prepaid(&path, &json!({"tampered": true})).is_err());
        assert_eq!(fs::read(&path).unwrap(), original);
        assert!(path.with_extension("pending").exists());
        assert!(stage_path(&scratch.0, 3).is_err());
    }

    #[test]
    fn unknown_journal_is_retained_but_cannot_be_loaded_as_knowledge() {
        let scratch = Scratch::new();
        let checked = stage(&seed(), 0, &mut LibraryBudgetV0::new(0).unwrap()).unwrap();
        assert_eq!(checked.status, Outcome::Unknown);
        publish_prepaid(&stage_path(&scratch.0, 0).unwrap(), &checked).unwrap();
        assert!(reload(&base_path(), &scratch.0, 1, &mut fuel()).is_err());
        assert!(stage_path(&scratch.0, 0).unwrap().exists());
    }

    #[test]
    fn oversized_checkpoint_and_symlink_read_are_refused() {
        let scratch = Scratch::new();
        let path = scratch.0.join("oversize.json");
        assert!(publish_prepaid(&path, &"x".repeat(1_048_576)).is_err());
        assert!(!path.exists());
        #[cfg(unix)]
        {
            let link = scratch.0.join("linked.json");
            std::os::unix::fs::symlink(base_path().join("epoch-0001.json"), &link).unwrap();
            assert!(read_library_bytes_v0(&link, &mut fuel()).is_err());
        }
    }
}

fn main() -> std::result::Result<(), Box<dyn std::error::Error>> {
    let args = std::env::args().skip(1).collect::<Vec<_>>();
    if args.len() != 4 || !["run", "replay"].contains(&args[0].as_str()) {
        return Err(
            "usage: library_generation run|replay BASE-STORE JOURNAL-DIR NEW-REPORT".into(),
        );
    }
    let base = Path::new(&args[1]);
    let directory = Path::new(&args[2]);
    let report_path = Path::new(&args[3]);
    if report_path.exists() || report_path.with_extension("pending").exists() {
        return Err("refusing existing report/staging path".into());
    }
    let mut budget = LibraryBudgetV0::new(50_000)?;
    for _ in 0..4 {
        budget.charge()?;
    } // Three stage checkpoints plus final report.
    let mut report = json!({
        "schema": "adva.proposal-feedback-workflow.research.v0", "mode": args[0],
        "revision": revision(), "status": "Unknown", "phase": "preflight",
        "stages": [], "completed_checkpoints": 0, "replayed_stages": 0,
        "checkpoint_units_prepaid": 4,
        "native_promotion": "NotGranted", "error": null
    });
    let outcome = if args[0] == "run" {
        fs::create_dir(directory)
            .map_err(LibraryCheckpointErrorV0::from)
            .and_then(|()| workflow(base, directory, &mut report, &mut budget))
    } else {
        reload(base, directory, 3, &mut budget).and_then(|book| {
            report["final_definitions"] = serde_json::to_value(&book.0)?;
            report["replayed_stages"] = json!(3);
            report["phase"] = json!("read-only-replay-complete");
            Ok(())
        })
    };
    report["status"] = json!(match &outcome {
        Ok(()) => "Completed",
        Err(LibraryCheckpointErrorV0::Unknown) => "Unknown",
        Err(_) => "Blocked",
    });
    if let Err(error) = &outcome {
        report["error"] = json!(error.to_string());
    }
    report["fuel_spent"] = json!(budget.spent());
    report["fuel_remaining"] = json!(budget.remaining());
    report["non_search_units"] = json!(
        "total minus reported search vectors; includes base loading, replay, comparison and prepaid persistence"
    );
    publish_prepaid(report_path, &report)?;
    println!(
        "{}; {} shared units; {} disk-replayed stages",
        report["status"],
        budget.spent(),
        report["replayed_stages"]
    );
    outcome?;
    Ok(())
}
