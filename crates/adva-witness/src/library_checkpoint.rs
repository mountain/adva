//! Bounded, immutable research library epochs (Research 0150).
//! No stable IR, semantic identity, builtin, or program rewrite is added.

use crate::{
    ArtifactKeyV0, BoundaryChargeV0, ExactExprV0, WitnessArtifactV0, WitnessProofV0, WitnessStoreV0,
};
use num_bigint::BigInt;
use serde::{Deserialize, Serialize};
use std::collections::BTreeMap;
use std::fs::{self, File, OpenOptions};
use std::io::{Read, Write};
use std::path::{Path, PathBuf};
use thiserror::Error;

const SCHEMA: &str = "adva.library-epoch.research.v0";
const MAX_BYTES: usize = 1_048_576;

/// All nested checks and persistence in one workflow debit this same account.
#[derive(Debug, Serialize)]
pub struct LibraryBudgetV0 {
    limit: u32,
    spent: u32,
}

impl LibraryBudgetV0 {
    /// A fresh, explicitly authorized finite workflow; not a resumed account.
    pub fn new(limit: u32) -> Result<Self, LibraryCheckpointErrorV0> {
        if limit > 50_000 {
            return Err(invalid("budget exceeds 50000"));
        }
        Ok(Self { limit, spent: 0 })
    }

    pub fn charge(&mut self) -> Result<(), LibraryCheckpointErrorV0> {
        if self.spent == self.limit {
            return Err(LibraryCheckpointErrorV0::Unknown);
        }
        self.spent += 1;
        Ok(())
    }

    pub fn spent(&self) -> u32 {
        self.spent
    }
    pub fn remaining(&self) -> u32 {
        self.limit - self.spent
    }
}

#[derive(Debug, Error)]
pub enum LibraryCheckpointErrorV0 {
    #[error("Unknown: shared workflow fuel exhausted")]
    Unknown,
    #[error("Blocked: {0}")]
    Invalid(String),
    #[error("I/O failed; inspect retained files before any continuation: {0}")]
    Io(#[from] std::io::Error),
    #[error("invalid bounded JSON: {0}")]
    Json(#[from] serde_json::Error),
}

fn invalid(message: &str) -> LibraryCheckpointErrorV0 {
    LibraryCheckpointErrorV0::Invalid(message.into())
}

/// Observation assumptions and stuttering history, not causal program events.
#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub enum LibraryRoundV0 {
    Observe { input: i32, value: i32 },
    Revisit,
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct LibraryOriginV0 {
    pub artifact_blake3: String,
    pub case: String,
    pub prior_checker: String,
    pub observation_authority: String,
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct LibraryInputV0 {
    pub catalogue: Vec<ExactExprV0>,
    pub rounds: Vec<LibraryRoundV0>,
}

#[derive(Clone, Copy, Debug, Eq, PartialEq, Serialize, Deserialize)]
pub enum LibraryStatusV0 {
    FeatureClosed,
    Open,
    ModelGap,
}

/// A complete finite feature reading, never an identity quotient.
#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct LibraryReadingV0 {
    pub active: Vec<usize>,
    pub features: Vec<String>,
    pub representative: Option<usize>,
    pub status: LibraryStatusV0,
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct LibraryComparisonV0 {
    pub round: usize,
    pub candidate: usize,
    pub input: i32,
    pub expected: i32,
    pub predicted: String,
    pub agrees: bool,
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct LibraryAnalysisV0 {
    /// Initial reading followed by one reading per retained round.
    pub readings: Vec<LibraryReadingV0>,
    pub comparisons: Vec<LibraryComparisonV0>,
}

impl LibraryAnalysisV0 {
    pub fn terminal(&self) -> &LibraryReadingV0 {
        self.readings.last().expect("derived initial reading")
    }
}

/// A scoped pair of expression ordinals plus replayable native witness nodes.
#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct LibraryWordV0 {
    pub left: usize,
    pub right: usize,
    pub nodes: [WitnessArtifactV0; 2],
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct LibraryParentV0 {
    pub epoch: u32,
    pub digest: String,
}

/// Untrusted until the Rust loader rederives all fields and the parent chain.
#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct LibrarySnapshotV0 {
    pub schema: String,
    pub checker_revision: String,
    pub epoch: u32,
    pub parent: Option<LibraryParentV0>,
    pub origin: LibraryOriginV0,
    pub input: LibraryInputV0,
    pub analysis: LibraryAnalysisV0,
    pub words: Vec<LibraryWordV0>,
}

/// No public constructor: only complete checking can create this handle.
#[derive(Debug)]
pub struct CheckedLibraryV0 {
    snapshot: LibrarySnapshotV0,
    digest: String,
    store: WitnessStoreV0,
}

impl CheckedLibraryV0 {
    pub fn snapshot(&self) -> &LibrarySnapshotV0 {
        &self.snapshot
    }
    pub fn digest(&self) -> &str {
        &self.digest
    }
}

/// The supported checker sources and dependency resolution, not authentication.
pub fn library_checker_revision_v0() -> String {
    let mut hash = blake3::Hasher::new();
    for source in [
        include_bytes!("library_checkpoint.rs").as_slice(),
        include_bytes!("arithmetic.rs").as_slice(),
        include_bytes!("witness.rs").as_slice(),
        include_bytes!("boundary.rs").as_slice(),
        include_bytes!("seed.rs").as_slice(),
        include_bytes!("../../../Cargo.lock").as_slice(),
    ] {
        hash.update(source);
    }
    hash.finalize().to_hex().to_string()
}

fn content_digest<T: Serialize>(
    value: &T,
    budget: &mut LibraryBudgetV0,
) -> Result<String, LibraryCheckpointErrorV0> {
    budget.charge()?;
    let bytes = serde_json::to_vec(value)?;
    if bytes.len() >= MAX_BYTES {
        return Err(invalid("serialized content exceeds byte bound"));
    }
    Ok(blake3::hash(&bytes).to_hex().to_string())
}

fn validate_expression(
    expression: &ExactExprV0,
    budget: &mut LibraryBudgetV0,
) -> Result<(), LibraryCheckpointErrorV0> {
    let mut pending = vec![(expression, 1)];
    let mut count = 0;
    while let Some((node, depth)) = pending.pop() {
        budget.charge()?;
        count += 1;
        if count > 31 || depth > 8 {
            return Err(invalid("expression exceeds node/depth bound"));
        }
        match node {
            ExactExprV0::Variable { name } if name == "x" => {}
            ExactExprV0::Variable { .. } => return Err(invalid("only x is admitted")),
            ExactExprV0::Constant { value } => {
                if value < &BigInt::from(-16) || value > &BigInt::from(16) {
                    return Err(invalid("constant bound"));
                }
            }
            ExactExprV0::Add { left, right } | ExactExprV0::Multiply { left, right } => {
                pending.push((right, depth + 1));
                pending.push((left, depth + 1));
            }
        }
    }
    Ok(())
}

/// Recompute diagnostic polynomial observations; zero is not guarded execution.
pub fn analyze_library_input_v0(
    input: &LibraryInputV0,
    budget: &mut LibraryBudgetV0,
) -> Result<LibraryAnalysisV0, LibraryCheckpointErrorV0> {
    budget.charge()?;
    if input.catalogue.is_empty() || input.catalogue.len() > 8 || input.rounds.len() > 16 {
        return Err(invalid("catalogue/round bound"));
    }
    let mut polynomials = Vec::new();
    for expression in &input.catalogue {
        validate_expression(expression, budget)?;
        budget.charge()?;
        polynomials.push(
            expression
                .normalize()
                .map_err(|e| invalid(&e.to_string()))?,
        );
    }
    for round in &input.rounds {
        budget.charge()?;
        if matches!(round, LibraryRoundV0::Observe { input, value }
            if !(-8..=8).contains(input) || !(-1_000_000..=1_000_000).contains(value))
        {
            return Err(invalid("observation bound"));
        }
    }
    let reading = |active: Vec<usize>,
                   budget: &mut LibraryBudgetV0|
     -> Result<LibraryReadingV0, LibraryCheckpointErrorV0> {
        let mut features = Vec::new();
        for &candidate in &active {
            budget.charge()?;
            features.push(serde_json::to_string(&polynomials[candidate])?);
        }
        let mut same = true;
        for feature in features.iter().skip(1) {
            budget.charge()?;
            same &= feature == &features[0];
        }
        budget.charge()?;
        let status = if active.is_empty() {
            LibraryStatusV0::ModelGap
        } else if same {
            LibraryStatusV0::FeatureClosed
        } else {
            LibraryStatusV0::Open
        };
        Ok(LibraryReadingV0 {
            representative: active.first().copied(),
            active,
            features,
            status,
        })
    };
    let mut result = LibraryAnalysisV0 {
        readings: vec![reading((0..input.catalogue.len()).collect(), budget)?],
        comparisons: Vec::new(),
    };
    for (round, step) in input.rounds.iter().enumerate() {
        budget.charge()?;
        let mut active = Vec::new();
        let previous = result.terminal().active.clone();
        for candidate in previous {
            match step {
                LibraryRoundV0::Revisit => active.push(candidate),
                &LibraryRoundV0::Observe { input, value } => {
                    budget.charge()?;
                    let predicted = polynomials[candidate]
                        .evaluate(&BTreeMap::from([("x".into(), BigInt::from(input))]))
                        .map_err(|e| invalid(&e.to_string()))?;
                    let agrees = predicted == BigInt::from(value);
                    result.comparisons.push(LibraryComparisonV0 {
                        round,
                        candidate,
                        input,
                        expected: value,
                        predicted: predicted.to_string(),
                        agrees,
                    });
                    if agrees {
                        active.push(candidate);
                    }
                }
            }
        }
        result.readings.push(reading(active, budget)?);
    }
    Ok(result)
}

fn derive_words(
    input: &LibraryInputV0,
    active: &[usize],
    budget: &mut LibraryBudgetV0,
) -> Result<(Vec<LibraryWordV0>, WitnessStoreV0), LibraryCheckpointErrorV0> {
    let mut store = WitnessStoreV0::new();
    let mut words = Vec::new();
    let left = active[0];
    for &right in active.iter().skip(1) {
        budget.charge()?;
        let body = store
            .insert(WitnessProofV0::ArithmeticTransition {
                actual_boundary: BoundaryChargeV0::zero(),
                declared_boundary: BoundaryChargeV0::zero(),
                before: input.catalogue[left].clone(),
                after: input.catalogue[right].clone(),
            })
            .map_err(|e| invalid(&e.to_string()))?;
        budget.charge()?;
        let seal = store
            .insert(WitnessProofV0::Seal { body: body.clone() })
            .map_err(|e| invalid(&e.to_string()))?;
        words.push(LibraryWordV0 {
            left,
            right,
            nodes: [
                store.artifact(&body).unwrap().clone(),
                store.artifact(&seal).unwrap().clone(),
            ],
        });
    }
    Ok((words, store))
}

fn derive_snapshot(
    epoch: u32,
    parent: Option<LibraryParentV0>,
    origin: LibraryOriginV0,
    input: LibraryInputV0,
    budget: &mut LibraryBudgetV0,
) -> Result<CheckedLibraryV0, LibraryCheckpointErrorV0> {
    budget.charge()?;
    if epoch > 3
        || origin.artifact_blake3.len() != 64
        || !origin
            .artifact_blake3
            .bytes()
            .all(|b| b.is_ascii_hexdigit())
        || origin.case.is_empty()
        || origin.case.len() > 128
        || origin.prior_checker.len() > 128
        || origin.observation_authority != "supplied-calibration-assumptions-not-world-measurements"
    {
        return Err(invalid("epoch/origin boundary"));
    }
    let analysis = analyze_library_input_v0(&input, budget)?;
    if analysis.terminal().status != LibraryStatusV0::FeatureClosed {
        return Err(invalid("only nonempty FeatureClosed snapshots may publish"));
    }
    let (words, store) = derive_words(&input, &analysis.terminal().active, budget)?;
    let snapshot = LibrarySnapshotV0 {
        schema: SCHEMA.into(),
        checker_revision: library_checker_revision_v0(),
        epoch,
        parent,
        origin,
        input,
        analysis,
        words,
    };
    let digest = content_digest(&snapshot, budget)?;
    Ok(CheckedLibraryV0 {
        snapshot,
        digest,
        store,
    })
}

pub fn bootstrap_library_v0(
    origin: LibraryOriginV0,
    input: LibraryInputV0,
    budget: &mut LibraryBudgetV0,
) -> Result<CheckedLibraryV0, LibraryCheckpointErrorV0> {
    derive_snapshot(0, None, origin, input, budget)
}

/// Append at most one candidate at the next epoch boundary and one observation.
pub fn advance_library_v0(
    parent: &CheckedLibraryV0,
    proposed: Option<ExactExprV0>,
    observation: LibraryRoundV0,
    budget: &mut LibraryBudgetV0,
) -> Result<CheckedLibraryV0, LibraryCheckpointErrorV0> {
    let mut input = parent.snapshot.input.clone();
    if let Some(expression) = proposed {
        input.catalogue.push(expression);
    }
    input.rounds.push(observation);
    derive_snapshot(
        parent.snapshot.epoch + 1,
        Some(LibraryParentV0 {
            epoch: parent.snapshot.epoch,
            digest: parent.digest.clone(),
        }),
        parent.snapshot.origin.clone(),
        input,
        budget,
    )
}

pub fn library_snapshot_path_v0(
    directory: &Path,
    epoch: u32,
) -> Result<PathBuf, LibraryCheckpointErrorV0> {
    if epoch > 3 {
        return Err(invalid("epoch/ancestry cap"));
    }
    Ok(directory.join(format!("epoch-{epoch:04}.json")))
}

/// Bounded read before Serde. Inputs must be regular files, not device streams.
pub fn read_library_bytes_v0(
    path: &Path,
    budget: &mut LibraryBudgetV0,
) -> Result<Vec<u8>, LibraryCheckpointErrorV0> {
    budget.charge()?;
    if !fs::symlink_metadata(path)?.file_type().is_file() {
        return Err(invalid("expected a regular nonsymlink file"));
    }
    let file = File::open(path)?;
    if !file.metadata()?.is_file() || file.metadata()?.len() > MAX_BYTES as u64 {
        return Err(invalid("input file shape/byte bound"));
    }
    let mut bytes = Vec::new();
    file.take(MAX_BYTES as u64 + 1).read_to_end(&mut bytes)?;
    if bytes.len() > MAX_BYTES {
        return Err(invalid("input grew past byte bound"));
    }
    Ok(bytes)
}

fn check_snapshot(
    directory: &Path,
    snapshot: &LibrarySnapshotV0,
    budget: &mut LibraryBudgetV0,
) -> Result<CheckedLibraryV0, LibraryCheckpointErrorV0> {
    budget.charge()?;
    if snapshot.schema != SCHEMA
        || snapshot.checker_revision != library_checker_revision_v0()
        || snapshot.epoch > 3
        || snapshot.words.len() > 8
        || snapshot.analysis.readings.len() > 17
        || snapshot.analysis.comparisons.len() > 128
    {
        return Err(invalid("snapshot schema/checker/epoch mismatch"));
    }
    match &snapshot.parent {
        None if snapshot.epoch == 0 => {}
        Some(link) if snapshot.epoch > 0 && link.epoch == snapshot.epoch - 1 => {
            let parent = load_library_v0(directory, link.epoch, budget)?;
            budget.charge()?;
            if link.digest != parent.digest
                || snapshot.origin != parent.snapshot.origin
                || !snapshot
                    .input
                    .catalogue
                    .starts_with(&parent.snapshot.input.catalogue)
                || snapshot.input.catalogue.len() > parent.snapshot.input.catalogue.len() + 1
                || !snapshot
                    .input
                    .rounds
                    .starts_with(&parent.snapshot.input.rounds)
                || snapshot.input.rounds.len() != parent.snapshot.input.rounds.len() + 1
            {
                return Err(invalid("parent binding or append-only delta mismatch"));
            }
        }
        _ => return Err(invalid("invalid parent ancestry")),
    }
    let checked = derive_snapshot(
        snapshot.epoch,
        snapshot.parent.clone(),
        snapshot.origin.clone(),
        snapshot.input.clone(),
        budget,
    )?;
    budget.charge()?;
    if snapshot != &checked.snapshot {
        return Err(invalid(
            "stored certificate or witness differs from Rust replay",
        ));
    }
    Ok(checked)
}

/// Rebuild native WitnessStore content; decoding a snapshot is not admission.
pub fn load_library_v0(
    directory: &Path,
    epoch: u32,
    budget: &mut LibraryBudgetV0,
) -> Result<CheckedLibraryV0, LibraryCheckpointErrorV0> {
    let bytes = read_library_bytes_v0(&library_snapshot_path_v0(directory, epoch)?, budget)?;
    budget.charge()?;
    let snapshot: LibrarySnapshotV0 = serde_json::from_slice(&bytes)?;
    if snapshot.epoch != epoch {
        return Err(invalid("file coordinate differs from embedded epoch"));
    }
    check_snapshot(directory, &snapshot, budget)
}

/// Atomic no-clobber publication. Staging remnants on failure are not commits.
pub fn publish_library_v0(
    directory: &Path,
    library: &CheckedLibraryV0,
    budget: &mut LibraryBudgetV0,
) -> Result<PathBuf, LibraryCheckpointErrorV0> {
    let checked = check_snapshot(directory, &library.snapshot, budget)?;
    let path = library_snapshot_path_v0(directory, checked.snapshot.epoch)?;
    if path.try_exists()? {
        return Err(invalid("snapshot already exists; no overwrite"));
    }
    let staged = directory.join(format!("epoch-{:04}.pending", checked.snapshot.epoch));
    budget.charge()?; // Serialization, staging, flush, link and directory sync.
    let bytes = serde_json::to_vec_pretty(&checked.snapshot)?;
    if bytes.len() >= MAX_BYTES {
        return Err(invalid("output byte cap"));
    }
    let mut file = OpenOptions::new()
        .write(true)
        .create_new(true)
        .open(&staged)?;
    file.write_all(&bytes)?;
    file.write_all(b"\n")?;
    file.sync_all()?;
    fs::hard_link(&staged, &path)?; // Fails atomically when another final path exists.
    File::open(directory)?.sync_all()?;
    fs::remove_file(&staged)?; // Only this successfully published temporary link.
    File::open(directory)?.sync_all()?;
    Ok(path)
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
pub struct LibraryReuseV0 {
    pub snapshot_digest: String,
    pub witness: ArtifactKeyV0,
    pub input: i32,
    pub guarded_values: Vec<String>,
}

/// Reuse a loaded symbolic witness only after checking each retained zero guard.
pub fn reuse_library_word_v0(
    library: &CheckedLibraryV0,
    word: usize,
    input: i32,
    budget: &mut LibraryBudgetV0,
) -> Result<LibraryReuseV0, LibraryCheckpointErrorV0> {
    budget.charge()?;
    if !(-8..=8).contains(&input) {
        return Err(invalid("reuse input bound"));
    }
    let word = library
        .snapshot
        .words
        .get(word)
        .ok_or_else(|| invalid("unknown scoped word"))?;
    let key = &word.nodes[1].key;
    let artifact = library
        .store
        .artifact(key)
        .ok_or_else(|| invalid("missing replayed witness"))?;
    let mut guarded_values = Vec::new();
    for expression in &artifact.summary.nonzero_obligations {
        budget.charge()?;
        guarded_values.push(
            expression
                .evaluate_guarded(&BTreeMap::from([("x".into(), BigInt::from(input))]))
                .map_err(|e| invalid(&e.to_string()))?
                .to_string(),
        );
    }
    Ok(LibraryReuseV0 {
        snapshot_digest: library.digest.clone(),
        witness: key.clone(),
        input,
        guarded_values,
    })
}
