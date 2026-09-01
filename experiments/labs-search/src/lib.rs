//! Research-local bounded triadic search for low-autocorrelation binary sequences.
//!
//! This crate deliberately lives outside Adva's stable semantic API. It provides
//! one exact finite benchmark in which three independently injectable search
//! programs share a verifier, an observation environment, an adaptive scheduler,
//! and an auditable trace:
//!
//! - the temporal program advances a trajectory by exact incremental flips;
//! - the spatial program reads the residual autocorrelation field;
//! - the constructive program splices and mutates archived witnesses.
//!
//! The implementation is a bounded calibration. It is not a universal Adva
//! machine, a stable energy API, or evidence that the three-program form dominates
//! conventional LABS solvers.

use serde::{Deserialize, Serialize};
use std::cmp::Ordering;
use std::collections::{HashSet, VecDeque};
use std::fmt::{Display, Formatter};
use std::fs::File;
use std::io::{BufReader, BufWriter};
use std::path::Path;
use std::thread;

pub const SCHEMA_VERSION: u32 = 1;
pub type Spin = i8;
pub type Energy = i64;
pub type Correlation = i64;

#[derive(Debug)]
pub enum LabsError {
    InvalidConfig(String),
    InvalidSequence(String),
    ArithmeticOverflow(String),
    WitnessMismatch(String),
    Io(std::io::Error),
    Json(serde_json::Error),
    WorkerPanic,
}

impl Display for LabsError {
    fn fmt(&self, formatter: &mut Formatter<'_>) -> std::fmt::Result {
        match self {
            Self::InvalidConfig(message) => write!(formatter, "invalid configuration: {message}"),
            Self::InvalidSequence(message) => write!(formatter, "invalid sequence: {message}"),
            Self::ArithmeticOverflow(message) => {
                write!(formatter, "arithmetic overflow: {message}")
            }
            Self::WitnessMismatch(message) => write!(formatter, "witness mismatch: {message}"),
            Self::Io(error) => Display::fmt(error, formatter),
            Self::Json(error) => Display::fmt(error, formatter),
            Self::WorkerPanic => formatter.write_str("a search worker panicked"),
        }
    }
}

impl std::error::Error for LabsError {}

impl From<std::io::Error> for LabsError {
    fn from(error: std::io::Error) -> Self {
        Self::Io(error)
    }
}

impl From<serde_json::Error> for LabsError {
    fn from(error: serde_json::Error) -> Self {
        Self::Json(error)
    }
}

pub type LabsResult<T> = Result<T, LabsError>;

#[derive(Clone, Debug, Serialize, Deserialize, PartialEq, Eq)]
pub struct Evaluation {
    pub correlations: Vec<Correlation>,
    pub energy: Energy,
}

pub fn validate_sequence(sequence: &[Spin]) -> LabsResult<()> {
    if sequence.len() < 2 {
        return Err(LabsError::InvalidSequence(
            "LABS requires at least two spins".to_owned(),
        ));
    }
    for (index, spin) in sequence.iter().copied().enumerate() {
        if spin != -1 && spin != 1 {
            return Err(LabsError::InvalidSequence(format!(
                "spin {index} is {spin}; expected -1 or +1"
            )));
        }
    }
    Ok(())
}

pub fn evaluate_sequence(sequence: &[Spin]) -> LabsResult<Evaluation> {
    validate_sequence(sequence)?;
    let length = sequence.len();
    let mut correlations = Vec::with_capacity(length - 1);
    let mut energy = 0_i64;

    for lag in 1..length {
        let mut correlation = 0_i64;
        for index in 0..(length - lag) {
            let product = i64::from(sequence[index]) * i64::from(sequence[index + lag]);
            correlation = correlation.checked_add(product).ok_or_else(|| {
                LabsError::ArithmeticOverflow("autocorrelation accumulation".to_owned())
            })?;
        }
        let contribution = correlation.checked_mul(correlation).ok_or_else(|| {
            LabsError::ArithmeticOverflow("squared autocorrelation".to_owned())
        })?;
        energy = energy.checked_add(contribution).ok_or_else(|| {
            LabsError::ArithmeticOverflow("LABS energy accumulation".to_owned())
        })?;
        correlations.push(correlation);
    }

    Ok(Evaluation {
        correlations,
        energy,
    })
}

pub fn merit_factor(length: usize, energy: Energy) -> LabsResult<f64> {
    if energy <= 0 {
        return Err(LabsError::InvalidSequence(
            "positive LABS energy is required for a finite merit factor".to_owned(),
        ));
    }
    let length_f64 = length as f64;
    Ok(length_f64 * length_f64 / (2.0 * energy as f64))
}

fn global_sign_normalize(sequence: &mut [Spin]) {
    if sequence.first() == Some(&-1) {
        for spin in sequence {
            *spin = -*spin;
        }
    }
}

pub fn canonical_sequence(sequence: &[Spin]) -> LabsResult<Vec<Spin>> {
    validate_sequence(sequence)?;
    let length = sequence.len();
    let mut best: Option<Vec<Spin>> = None;

    for reverse in [false, true] {
        for alternating in [false, true] {
            for negate in [false, true] {
                let mut transformed = Vec::with_capacity(length);
                for output_index in 0..length {
                    let source_index = if reverse {
                        length - 1 - output_index
                    } else {
                        output_index
                    };
                    let mut spin = sequence[source_index];
                    if alternating && output_index % 2 == 1 {
                        spin = -spin;
                    }
                    if negate {
                        spin = -spin;
                    }
                    transformed.push(spin);
                }
                if best
                    .as_ref()
                    .is_none_or(|incumbent| transformed < *incumbent)
                {
                    best = Some(transformed);
                }
            }
        }
    }

    best.ok_or_else(|| LabsError::InvalidSequence("empty symmetry orbit".to_owned()))
}

#[derive(Clone, Debug, Serialize, Deserialize, PartialEq)]
pub struct Witness {
    pub length: usize,
    pub sequence: Vec<Spin>,
    pub correlations: Vec<Correlation>,
    pub energy: Energy,
    pub merit_factor: f64,
}

impl Witness {
    fn from_state(state: &CandidateState) -> LabsResult<Self> {
        Ok(Self {
            length: state.sequence.len(),
            sequence: state.sequence.clone(),
            correlations: state.correlations.clone(),
            energy: state.energy,
            merit_factor: merit_factor(state.sequence.len(), state.energy)?,
        })
    }
}

pub fn verify_witness(witness: &Witness) -> LabsResult<Evaluation> {
    if witness.length != witness.sequence.len() {
        return Err(LabsError::WitnessMismatch(format!(
            "declared length {} differs from sequence length {}",
            witness.length,
            witness.sequence.len()
        )));
    }
    let evaluation = evaluate_sequence(&witness.sequence)?;
    if evaluation.correlations != witness.correlations {
        return Err(LabsError::WitnessMismatch(
            "stored autocorrelation vector is not exact".to_owned(),
        ));
    }
    if evaluation.energy != witness.energy {
        return Err(LabsError::WitnessMismatch(format!(
            "stored energy {} differs from exact energy {}",
            witness.energy, evaluation.energy
        )));
    }
    let expected_merit = merit_factor(witness.length, witness.energy)?;
    if (witness.merit_factor - expected_merit).abs() > 1e-12 {
        return Err(LabsError::WitnessMismatch(format!(
            "stored merit factor {} differs from recomputed merit factor {}",
            witness.merit_factor, expected_merit
        )));
    }
    Ok(evaluation)
}

#[derive(Clone, Debug, Serialize, Deserialize, PartialEq, Eq)]
struct CandidateState {
    sequence: Vec<Spin>,
    correlations: Vec<Correlation>,
    energy: Energy,
}

impl CandidateState {
    fn from_sequence(sequence: Vec<Spin>) -> LabsResult<Self> {
        let evaluation = evaluate_sequence(&sequence)?;
        Ok(Self {
            sequence,
            correlations: evaluation.correlations,
            energy: evaluation.energy,
        })
    }

    fn correlation_delta(&self, index: usize, lag: usize) -> Correlation {
        let spin = i64::from(self.sequence[index]);
        let mut neighbor_sum = 0_i64;
        if index >= lag {
            neighbor_sum += i64::from(self.sequence[index - lag]);
        }
        if index + lag < self.sequence.len() {
            neighbor_sum += i64::from(self.sequence[index + lag]);
        }
        -2 * spin * neighbor_sum
    }

    fn flip_delta(&self, index: usize) -> LabsResult<Energy> {
        if index >= self.sequence.len() {
            return Err(LabsError::InvalidSequence(format!(
                "flip index {index} is outside length {}",
                self.sequence.len()
            )));
        }
        let mut energy_delta = 0_i64;
        for lag in 1..self.sequence.len() {
            let correlation = self.correlations[lag - 1];
            let delta = self.correlation_delta(index, lag);
            let linear = correlation
                .checked_mul(delta)
                .and_then(|value| value.checked_mul(2))
                .ok_or_else(|| {
                    LabsError::ArithmeticOverflow("incremental flip linear term".to_owned())
                })?;
            let quadratic = delta.checked_mul(delta).ok_or_else(|| {
                LabsError::ArithmeticOverflow("incremental flip quadratic term".to_owned())
            })?;
            energy_delta = energy_delta
                .checked_add(linear)
                .and_then(|value| value.checked_add(quadratic))
                .ok_or_else(|| {
                    LabsError::ArithmeticOverflow("incremental flip energy".to_owned())
                })?;
        }
        Ok(energy_delta)
    }

    fn restricted_flip_delta(&self, index: usize, lags: &[usize]) -> LabsResult<Energy> {
        let mut energy_delta = 0_i64;
        for lag in lags.iter().copied() {
            let correlation = self.correlations[lag - 1];
            let delta = self.correlation_delta(index, lag);
            let contribution = correlation
                .checked_mul(delta)
                .and_then(|value| value.checked_mul(2))
                .and_then(|value| value.checked_add(delta.checked_mul(delta)?))
                .ok_or_else(|| {
                    LabsError::ArithmeticOverflow("restricted flip energy".to_owned())
                })?;
            energy_delta = energy_delta.checked_add(contribution).ok_or_else(|| {
                LabsError::ArithmeticOverflow("restricted flip accumulation".to_owned())
            })?;
        }
        Ok(energy_delta)
    }

    fn apply_flip(&mut self, index: usize) -> LabsResult<Energy> {
        let energy_delta = self.flip_delta(index)?;
        let deltas: Vec<Correlation> = (1..self.sequence.len())
            .map(|lag| self.correlation_delta(index, lag))
            .collect();
        for (correlation, delta) in self.correlations.iter_mut().zip(deltas) {
            *correlation = correlation.checked_add(delta).ok_or_else(|| {
                LabsError::ArithmeticOverflow("autocorrelation flip update".to_owned())
            })?;
        }
        self.energy = self.energy.checked_add(energy_delta).ok_or_else(|| {
            LabsError::ArithmeticOverflow("energy flip update".to_owned())
        })?;
        self.sequence[index] = -self.sequence[index];
        Ok(energy_delta)
    }

    fn checked(&self) -> LabsResult<()> {
        let evaluation = evaluate_sequence(&self.sequence)?;
        if evaluation.correlations != self.correlations || evaluation.energy != self.energy {
            return Err(LabsError::WitnessMismatch(
                "incremental candidate state failed exact recomputation".to_owned(),
            ));
        }
        Ok(())
    }
}

#[derive(Clone, Copy, Debug, Serialize, Deserialize, PartialEq, Eq, Hash, PartialOrd, Ord)]
#[serde(rename_all = "snake_case")]
pub enum ProgramKind {
    Temporal,
    Spatial,
    Constructive,
}

impl ProgramKind {
    pub const ALL: [Self; 3] = [Self::Temporal, Self::Spatial, Self::Constructive];

    const fn index(self) -> usize {
        match self {
            Self::Temporal => 0,
            Self::Spatial => 1,
            Self::Constructive => 2,
        }
    }

    pub const fn as_str(self) -> &'static str {
        match self {
            Self::Temporal => "temporal",
            Self::Spatial => "spatial",
            Self::Constructive => "constructive",
        }
    }

    pub fn parse(name: &str) -> LabsResult<Self> {
        match name.trim().to_ascii_lowercase().as_str() {
            "temporal" | "t" => Ok(Self::Temporal),
            "spatial" | "x" => Ok(Self::Spatial),
            "constructive" | "construction" | "k" => Ok(Self::Constructive),
            other => Err(LabsError::InvalidConfig(format!(
                "unknown program {other:?}; expected temporal, spatial, or constructive"
            ))),
        }
    }
}

#[derive(Clone, Debug, Serialize, Deserialize, PartialEq)]
pub struct SearchConfig {
    pub length: usize,
    pub seed: u64,
    pub enabled_programs: Vec<ProgramKind>,
    pub initial_population: usize,
    pub move_samples: usize,
    pub temporal_top_k: usize,
    pub spatial_lags: usize,
    pub construction_trials: usize,
    pub construction_mutations: usize,
    pub construction_interval: u64,
    pub archive_size: usize,
    pub recent_flip_window: usize,
    pub restart_after: u64,
    pub scheduler_exploration: f64,
    pub trace_stride: u64,
    pub max_trace_events: usize,
}

impl SearchConfig {
    pub fn for_length(length: usize, seed: u64) -> Self {
        Self {
            length,
            seed,
            enabled_programs: ProgramKind::ALL.to_vec(),
            initial_population: 8,
            move_samples: length.min(32),
            temporal_top_k: 4,
            spatial_lags: length.saturating_sub(1).min(8),
            construction_trials: 4,
            construction_mutations: 2,
            construction_interval: 32,
            archive_size: 16,
            recent_flip_window: 8,
            restart_after: 512,
            scheduler_exploration: 2.0,
            trace_stride: 1_000,
            max_trace_events: 100_000,
        }
    }

    pub fn validate(&self) -> LabsResult<()> {
        if self.length < 2 {
            return Err(LabsError::InvalidConfig(
                "length must be at least two".to_owned(),
            ));
        }
        if self.enabled_programs.is_empty() {
            return Err(LabsError::InvalidConfig(
                "at least one program must be enabled".to_owned(),
            ));
        }
        let unique: HashSet<ProgramKind> = self.enabled_programs.iter().copied().collect();
        if unique.len() != self.enabled_programs.len() {
            return Err(LabsError::InvalidConfig(
                "enabled programs must not contain duplicates".to_owned(),
            ));
        }
        if self.initial_population == 0 {
            return Err(LabsError::InvalidConfig(
                "initial population must be positive".to_owned(),
            ));
        }
        if self.move_samples == 0 {
            return Err(LabsError::InvalidConfig(
                "move sample count must be positive".to_owned(),
            ));
        }
        if self.temporal_top_k == 0 {
            return Err(LabsError::InvalidConfig(
                "temporal top-k must be positive".to_owned(),
            ));
        }
        if self.spatial_lags == 0 || self.spatial_lags >= self.length {
            return Err(LabsError::InvalidConfig(format!(
                "spatial lag count must be in 1..{}",
                self.length
            )));
        }
        if self.construction_trials == 0 {
            return Err(LabsError::InvalidConfig(
                "construction trial count must be positive".to_owned(),
            ));
        }
        if self.construction_interval == 0 {
            return Err(LabsError::InvalidConfig(
                "construction interval must be positive".to_owned(),
            ));
        }
        if self.archive_size == 0 {
            return Err(LabsError::InvalidConfig(
                "archive size must be positive".to_owned(),
            ));
        }
        if self.restart_after == 0 {
            return Err(LabsError::InvalidConfig(
                "restart interval must be positive".to_owned(),
            ));
        }
        if !self.scheduler_exploration.is_finite() || self.scheduler_exploration < 0.0 {
            return Err(LabsError::InvalidConfig(
                "scheduler exploration must be finite and nonnegative".to_owned(),
            ));
        }
        Ok(())
    }
}

#[derive(Clone, Debug, Serialize, Deserialize, PartialEq, Eq)]
struct SplitMix64 {
    state: u64,
}

impl SplitMix64 {
    const GAMMA: u64 = 0x9E37_79B9_7F4A_7C15;

    const fn new(seed: u64) -> Self {
        Self { state: seed }
    }

    fn next_u64(&mut self) -> u64 {
        self.state = self.state.wrapping_add(Self::GAMMA);
        let mut value = self.state;
        value = (value ^ (value >> 30)).wrapping_mul(0xBF58_476D_1CE4_E5B9);
        value = (value ^ (value >> 27)).wrapping_mul(0x94D0_49BB_1331_11EB);
        value ^ (value >> 31)
    }

    fn index(&mut self, upper_bound: usize) -> usize {
        assert!(upper_bound > 0, "upper bound must be positive");
        (self.next_u64() % upper_bound as u64) as usize
    }

    fn one_in(&mut self, denominator: u64) -> bool {
        denominator <= 1 || self.next_u64() % denominator == 0
    }
}

fn random_sequence(length: usize, rng: &mut SplitMix64) -> Vec<Spin> {
    let mut sequence = Vec::with_capacity(length);
    sequence.push(1);
    for _ in 1..length {
        sequence.push(if rng.next_u64() & 1 == 0 { -1 } else { 1 });
    }
    sequence
}

fn sampled_indices(length: usize, count: usize, rng: &mut SplitMix64) -> Vec<usize> {
    if count >= length {
        return (0..length).collect();
    }
    let mut selected = HashSet::with_capacity(count);
    while selected.len() < count {
        selected.insert(rng.index(length));
    }
    let mut indices: Vec<usize> = selected.into_iter().collect();
    indices.sort_unstable();
    indices
}

#[derive(Clone, Debug, Serialize, Deserialize, PartialEq, Eq)]
struct ArchiveEntry {
    canonical: Vec<Spin>,
    state: CandidateState,
}

#[derive(Clone, Debug, Serialize, Deserialize, PartialEq)]
struct ProgramStats {
    uses: u64,
    accepted: u64,
    improving_accepts: u64,
    best_updates: u64,
    cumulative_current_gain: Energy,
    cumulative_best_gain: Energy,
    reward_sum: f64,
}

impl Default for ProgramStats {
    fn default() -> Self {
        Self {
            uses: 0,
            accepted: 0,
            improving_accepts: 0,
            best_updates: 0,
            cumulative_current_gain: 0,
            cumulative_best_gain: 0,
            reward_sum: 0.0,
        }
    }
}

#[derive(Clone, Debug, Serialize, Deserialize, PartialEq)]
struct AdaptiveScheduler {
    stats: [ProgramStats; 3],
}

impl Default for AdaptiveScheduler {
    fn default() -> Self {
        Self {
            stats: std::array::from_fn(|_| ProgramStats::default()),
        }
    }
}

impl AdaptiveScheduler {
    fn choose(
        &self,
        enabled: &[ProgramKind],
        construction_allowed: bool,
        exploration: f64,
    ) -> ProgramKind {
        let mut eligible: Vec<ProgramKind> = enabled
            .iter()
            .copied()
            .filter(|kind| *kind != ProgramKind::Constructive || construction_allowed)
            .collect();
        if eligible.is_empty() {
            eligible = enabled.to_vec();
        }

        for kind in &eligible {
            if self.stats[kind.index()].uses == 0 {
                return *kind;
            }
        }

        let total_uses: u64 = eligible
            .iter()
            .map(|kind| self.stats[kind.index()].uses)
            .sum();
        eligible
            .into_iter()
            .max_by(|left, right| {
                let score = |kind: ProgramKind| {
                    let stats = &self.stats[kind.index()];
                    let mean = stats.reward_sum / stats.uses as f64;
                    let explore = exploration
                        * ((total_uses as f64 + 1.0).ln() / stats.uses as f64).sqrt();
                    mean + explore
                };
                score(*left)
                    .partial_cmp(&score(*right))
                    .unwrap_or(Ordering::Equal)
                    .then_with(|| right.cmp(left))
            })
            .expect("eligible program set is nonempty")
    }

    fn update(
        &mut self,
        kind: ProgramKind,
        accepted: bool,
        current_gain: Energy,
        best_gain: Energy,
    ) {
        let stats = &mut self.stats[kind.index()];
        stats.uses += 1;
        if accepted {
            stats.accepted += 1;
        }
        if current_gain > 0 {
            stats.improving_accepts += 1;
            stats.cumulative_current_gain += current_gain;
        }
        if best_gain > 0 {
            stats.best_updates += 1;
            stats.cumulative_best_gain += best_gain;
        }
        let acceptance_credit = if accepted { 0.05 } else { 0.0 };
        stats.reward_sum +=
            current_gain.max(0) as f64 + 10.0 * best_gain.max(0) as f64 + acceptance_credit;
    }
}

#[derive(Clone, Debug)]
struct Proposal {
    kind: ProgramKind,
    candidate: CandidateState,
    touched_indices: Vec<usize>,
    summary: String,
}

#[derive(Clone, Debug, Serialize, Deserialize, PartialEq)]
pub struct TraceEvent {
    pub iteration: u64,
    pub program: ProgramKind,
    pub accepted: bool,
    pub current_energy_before: Energy,
    pub proposal_energy: Energy,
    pub current_energy_after: Energy,
    pub best_energy: Energy,
    pub current_gain: Energy,
    pub best_gain: Energy,
    pub move_summary: String,
}

#[derive(Clone, Debug, Serialize, Deserialize, PartialEq)]
pub struct SearchEngine {
    config: SearchConfig,
    rng: SplitMix64,
    current: CandidateState,
    best: CandidateState,
    archive: Vec<ArchiveEntry>,
    scheduler: AdaptiveScheduler,
    recent_flips: VecDeque<usize>,
    iteration: u64,
    stagnation: u64,
    restarts: u64,
    trace: Vec<TraceEvent>,
}

impl SearchEngine {
    pub fn new(config: SearchConfig) -> LabsResult<Self> {
        config.validate()?;
        let mut rng = SplitMix64::new(config.seed);
        let mut population = Vec::with_capacity(config.initial_population);
        for _ in 0..config.initial_population {
            population.push(CandidateState::from_sequence(random_sequence(
                config.length,
                &mut rng,
            ))?);
        }
        population.sort_by(candidate_order);
        let best = population[0].clone();
        let current = best.clone();
        let mut engine = Self {
            config,
            rng,
            current,
            best,
            archive: Vec::new(),
            scheduler: AdaptiveScheduler::default(),
            recent_flips: VecDeque::new(),
            iteration: 0,
            stagnation: 0,
            restarts: 0,
            trace: Vec::new(),
        };
        for state in population {
            engine.consider_archive(state)?;
        }
        Ok(engine)
    }

    pub const fn iteration(&self) -> u64 {
        self.iteration
    }

    pub const fn best_energy(&self) -> Energy {
        self.best.energy
    }

    pub fn best_witness(&self) -> LabsResult<Witness> {
        Witness::from_state(&self.best)
    }

    pub fn report(&self) -> LabsResult<RunReport> {
        let worker = self.worker_report(0)?;
        Ok(RunReport {
            schema_version: SCHEMA_VERSION,
            benchmark: "low_autocorrelation_binary_sequence".to_owned(),
            config: self.config.clone(),
            workers_requested: 1,
            iterations_per_worker: self.iteration,
            best_worker: 0,
            best: worker.best.clone(),
            workers: vec![worker],
        })
    }

    pub fn run_steps(&mut self, steps: u64) -> LabsResult<()> {
        for _ in 0..steps {
            self.step()?;
        }
        Ok(())
    }

    pub fn save_checkpoint(&self, path: impl AsRef<Path>) -> LabsResult<()> {
        let writer = BufWriter::new(File::create(path)?);
        serde_json::to_writer_pretty(writer, self)?;
        Ok(())
    }

    pub fn load_checkpoint(path: impl AsRef<Path>) -> LabsResult<Self> {
        let reader = BufReader::new(File::open(path)?);
        let engine: Self = serde_json::from_reader(reader)?;
        engine.config.validate()?;
        engine.current.checked()?;
        engine.best.checked()?;
        if engine.archive.is_empty() {
            return Err(LabsError::WitnessMismatch(
                "checkpoint archive must not be empty".to_owned(),
            ));
        }
        for entry in &engine.archive {
            entry.state.checked()?;
            if entry.canonical != canonical_sequence(&entry.state.sequence)? {
                return Err(LabsError::WitnessMismatch(
                    "checkpoint archive canonical key is invalid".to_owned(),
                ));
            }
        }
        Ok(engine)
    }

    fn step(&mut self) -> LabsResult<()> {
        let constructive_only = self.config.enabled_programs.len() == 1
            && self.config.enabled_programs[0] == ProgramKind::Constructive;
        let construction_allowed = constructive_only
            || self.iteration % self.config.construction_interval == 0;
        let kind = self.scheduler.choose(
            &self.config.enabled_programs,
            construction_allowed,
            self.config.scheduler_exploration,
        );
        let proposal = match kind {
            ProgramKind::Temporal => self.temporal_proposal()?,
            ProgramKind::Spatial => self.spatial_proposal()?,
            ProgramKind::Constructive => self.constructive_proposal()?,
        };
        debug_assert_eq!(proposal.kind, kind);

        let before = self.current.energy;
        let best_before = self.best.energy;
        let accepted = self.should_accept(proposal.candidate.energy);
        if accepted {
            self.current = proposal.candidate.clone();
            if proposal.touched_indices.len() == 1 {
                self.remember_flip(proposal.touched_indices[0]);
            } else {
                self.recent_flips.clear();
            }
        }

        let mut best_gain = 0;
        if proposal.candidate.energy < self.best.energy {
            best_gain = self.best.energy - proposal.candidate.energy;
            self.best = proposal.candidate.clone();
            self.stagnation = 0;
        } else {
            self.stagnation += 1;
        }
        self.consider_archive(proposal.candidate.clone())?;
        if accepted {
            self.consider_archive(self.current.clone())?;
        }

        let current_gain = if accepted {
            before - self.current.energy
        } else {
            0
        };
        self.scheduler
            .update(kind, accepted, current_gain, best_gain);
        self.iteration += 1;

        let should_trace = best_gain > 0
            || self.config.trace_stride > 0
                && self.iteration % self.config.trace_stride == 0;
        if should_trace && self.trace.len() < self.config.max_trace_events {
            self.trace.push(TraceEvent {
                iteration: self.iteration,
                program: kind,
                accepted,
                current_energy_before: before,
                proposal_energy: proposal.candidate.energy,
                current_energy_after: self.current.energy,
                best_energy: self.best.energy,
                current_gain,
                best_gain: best_before - self.best.energy,
                move_summary: proposal.summary,
            });
        }

        if self.stagnation >= self.config.restart_after {
            self.restart()?;
        }
        Ok(())
    }

    fn temporal_proposal(&mut self) -> LabsResult<Proposal> {
        let indices = sampled_indices(
            self.current.sequence.len(),
            self.config.move_samples,
            &mut self.rng,
        );
        let mut ranked = Vec::with_capacity(indices.len());
        for index in indices {
            let delta = self.current.flip_delta(index)?;
            let tabu = self.recent_flips.contains(&index);
            ranked.push((tabu, delta, index));
        }
        ranked.sort_unstable();

        let non_tabu_count = ranked.iter().take_while(|entry| !entry.0).count();
        let candidate_count = if non_tabu_count > 0 {
            non_tabu_count.min(self.config.temporal_top_k)
        } else {
            ranked.len().min(self.config.temporal_top_k)
        };
        let first_draw = self.rng.index(candidate_count);
        let second_draw = self.rng.index(candidate_count);
        let selected_rank = first_draw.min(second_draw);
        let (tabu, delta, index) = ranked[selected_rank];
        let mut candidate = self.current.clone();
        candidate.apply_flip(index)?;
        Ok(Proposal {
            kind: ProgramKind::Temporal,
            candidate,
            touched_indices: vec![index],
            summary: format!("single_flip index={index} delta={delta} tabu={tabu}"),
        })
    }

    fn spatial_proposal(&mut self) -> LabsResult<Proposal> {
        let mut lag_scores: Vec<(Energy, usize)> = self
            .current
            .correlations
            .iter()
            .copied()
            .enumerate()
            .map(|(index, correlation)| (correlation * correlation, index + 1))
            .collect();
        lag_scores.sort_unstable_by(|left, right| right.cmp(left));
        let lags: Vec<usize> = lag_scores
            .into_iter()
            .take(self.config.spatial_lags)
            .map(|(_, lag)| lag)
            .collect();
        let indices = sampled_indices(
            self.current.sequence.len(),
            self.config.move_samples,
            &mut self.rng,
        );
        let mut ranked = Vec::with_capacity(indices.len());
        for index in indices {
            let restricted_delta = self.current.restricted_flip_delta(index, &lags)?;
            let full_delta = self.current.flip_delta(index)?;
            ranked.push((restricted_delta, full_delta, index));
        }
        ranked.sort_unstable();
        let best_restricted = ranked[0].0;
        let tied = ranked
            .iter()
            .take_while(|entry| entry.0 == best_restricted)
            .count();
        let selected = ranked[self.rng.index(tied)];
        let (restricted_delta, full_delta, index) = selected;
        let mut candidate = self.current.clone();
        candidate.apply_flip(index)?;
        Ok(Proposal {
            kind: ProgramKind::Spatial,
            candidate,
            touched_indices: vec![index],
            summary: format!(
                "residual_flip index={index} lags={lags:?} restricted_delta={restricted_delta} full_delta={full_delta}"
            ),
        })
    }

    fn constructive_proposal(&mut self) -> LabsResult<Proposal> {
        let mut best_candidate: Option<(CandidateState, Vec<usize>, String)> = None;
        let partner_limit = self.archive.len();

        for trial in 0..self.config.construction_trials {
            let partner_index = self.rng.index(partner_limit);
            let partner = self.archive[partner_index].state.clone();
            let length = self.current.sequence.len();
            let mut left = self.rng.index(length);
            let mut right = self.rng.index(length);
            if left > right {
                std::mem::swap(&mut left, &mut right);
            }
            if left == right {
                right = (right + 1).min(length);
                if left == right {
                    left = left.saturating_sub(1);
                }
            }

            let mut child = self.current.sequence.clone();
            child[left..right].copy_from_slice(&partner.sequence[left..right]);
            let mutation_count = self.config.construction_mutations.min(length).max(1);
            let mutations = sampled_indices(length, mutation_count, &mut self.rng);
            for index in &mutations {
                child[*index] = -child[*index];
            }
            global_sign_normalize(&mut child);
            let candidate = CandidateState::from_sequence(child)?;
            let summary = format!(
                "splice trial={trial} partner_energy={} interval=[{left},{right}) mutations={mutations:?}",
                partner.energy
            );
            if best_candidate
                .as_ref()
                .is_none_or(|(incumbent, _, _)| candidate_order(&candidate, incumbent).is_lt())
            {
                best_candidate = Some((candidate, mutations, summary));
            }
        }

        let (candidate, mutations, summary) = best_candidate.ok_or_else(|| {
            LabsError::InvalidConfig("constructive program produced no trial".to_owned())
        })?;
        Ok(Proposal {
            kind: ProgramKind::Constructive,
            candidate,
            touched_indices: mutations,
            summary,
        })
    }

    fn should_accept(&mut self, proposal_energy: Energy) -> bool {
        if proposal_energy <= self.current.energy {
            return true;
        }
        let delta = proposal_energy - self.current.energy;
        let length = self.current.sequence.len() as Energy;
        let base_scale = (self.current.energy / length.max(1) / 4).max(1);
        let stagnation_boost = 1 + (self.stagnation / 64).min(8) as Energy;
        let cap = base_scale * stagnation_boost * 4;
        if delta > cap {
            return false;
        }
        let denominator = 2 + (delta / base_scale.max(1)) as u64;
        self.rng.one_in(denominator)
    }

    fn remember_flip(&mut self, index: usize) {
        self.recent_flips.push_back(index);
        while self.recent_flips.len() > self.config.recent_flip_window {
            self.recent_flips.pop_front();
        }
    }

    fn consider_archive(&mut self, state: CandidateState) -> LabsResult<()> {
        let canonical = canonical_sequence(&state.sequence)?;
        if self
            .archive
            .iter()
            .any(|entry| entry.canonical == canonical)
        {
            return Ok(());
        }
        self.archive.push(ArchiveEntry { canonical, state });
        self.archive
            .sort_by(|left, right| candidate_order(&left.state, &right.state));
        self.archive.truncate(self.config.archive_size);
        Ok(())
    }

    fn restart(&mut self) -> LabsResult<()> {
        let archive_window = self.archive.len().div_ceil(2).max(1);
        let mut restarted = self.archive[self.rng.index(archive_window)].state.clone();
        let perturbations = (restarted.sequence.len() / 16).max(1);
        for index in sampled_indices(restarted.sequence.len(), perturbations, &mut self.rng) {
            restarted.apply_flip(index)?;
        }
        restarted.checked()?;
        self.current = restarted;
        self.recent_flips.clear();
        self.stagnation = 0;
        self.restarts += 1;
        Ok(())
    }

    fn program_reports(&self) -> Vec<ProgramReport> {
        ProgramKind::ALL
            .into_iter()
            .map(|kind| {
                let stats = &self.scheduler.stats[kind.index()];
                ProgramReport {
                    program: kind,
                    enabled: self.config.enabled_programs.contains(&kind),
                    uses: stats.uses,
                    accepted: stats.accepted,
                    improving_accepts: stats.improving_accepts,
                    best_updates: stats.best_updates,
                    cumulative_current_gain: stats.cumulative_current_gain,
                    cumulative_best_gain: stats.cumulative_best_gain,
                    mean_scheduler_reward: if stats.uses == 0 {
                        0.0
                    } else {
                        stats.reward_sum / stats.uses as f64
                    },
                }
            })
            .collect()
    }

    fn worker_report(&self, worker: usize) -> LabsResult<WorkerReport> {
        Ok(WorkerReport {
            worker,
            seed: self.config.seed,
            iterations_completed: self.iteration,
            final_energy: self.current.energy,
            best: self.best_witness()?,
            restarts: self.restarts,
            programs: self.program_reports(),
            trace: self.trace.clone(),
        })
    }
}

fn candidate_order(left: &CandidateState, right: &CandidateState) -> Ordering {
    left.energy
        .cmp(&right.energy)
        .then_with(|| left.sequence.cmp(&right.sequence))
}

#[derive(Clone, Debug, Serialize, Deserialize, PartialEq)]
pub struct ProgramReport {
    pub program: ProgramKind,
    pub enabled: bool,
    pub uses: u64,
    pub accepted: u64,
    pub improving_accepts: u64,
    pub best_updates: u64,
    pub cumulative_current_gain: Energy,
    pub cumulative_best_gain: Energy,
    pub mean_scheduler_reward: f64,
}

#[derive(Clone, Debug, Serialize, Deserialize, PartialEq)]
pub struct WorkerReport {
    pub worker: usize,
    pub seed: u64,
    pub iterations_completed: u64,
    pub final_energy: Energy,
    pub best: Witness,
    pub restarts: u64,
    pub programs: Vec<ProgramReport>,
    pub trace: Vec<TraceEvent>,
}

#[derive(Clone, Debug, Serialize, Deserialize, PartialEq)]
pub struct RunReport {
    pub schema_version: u32,
    pub benchmark: String,
    pub config: SearchConfig,
    pub workers_requested: usize,
    pub iterations_per_worker: u64,
    pub best_worker: usize,
    pub best: Witness,
    pub workers: Vec<WorkerReport>,
}

impl RunReport {
    pub fn verify(&self) -> LabsResult<Evaluation> {
        if self.schema_version != SCHEMA_VERSION {
            return Err(LabsError::WitnessMismatch(format!(
                "unsupported report schema {}",
                self.schema_version
            )));
        }
        verify_witness(&self.best)
    }
}

pub fn run_parallel(
    config: SearchConfig,
    iterations_per_worker: u64,
    workers: usize,
) -> LabsResult<RunReport> {
    config.validate()?;
    if workers == 0 {
        return Err(LabsError::InvalidConfig(
            "worker count must be positive".to_owned(),
        ));
    }

    let mut handles = Vec::with_capacity(workers);
    for worker in 0..workers {
        let mut worker_config = config.clone();
        worker_config.seed = config
            .seed
            .wrapping_add(SplitMix64::GAMMA.wrapping_mul(worker as u64));
        handles.push(thread::spawn(move || -> LabsResult<WorkerReport> {
            let mut engine = SearchEngine::new(worker_config)?;
            engine.run_steps(iterations_per_worker)?;
            engine.worker_report(worker)
        }));
    }

    let mut reports = Vec::with_capacity(workers);
    for handle in handles {
        reports.push(handle.join().map_err(|_| LabsError::WorkerPanic)??);
    }
    reports.sort_by_key(|report| report.worker);
    let best_report = reports
        .iter()
        .min_by(|left, right| {
            left.best
                .energy
                .cmp(&right.best.energy)
                .then_with(|| left.best.sequence.cmp(&right.best.sequence))
        })
        .expect("positive worker count produces reports");
    let best_worker = best_report.worker;
    let best = best_report.best.clone();

    Ok(RunReport {
        schema_version: SCHEMA_VERSION,
        benchmark: "low_autocorrelation_binary_sequence".to_owned(),
        config,
        workers_requested: workers,
        iterations_per_worker,
        best_worker,
        best,
        workers: reports,
    })
}

pub fn write_json(path: impl AsRef<Path>, value: &impl Serialize) -> LabsResult<()> {
    let writer = BufWriter::new(File::create(path)?);
    serde_json::to_writer_pretty(writer, value)?;
    Ok(())
}

pub fn read_run_report(path: impl AsRef<Path>) -> LabsResult<RunReport> {
    let reader = BufReader::new(File::open(path)?);
    Ok(serde_json::from_reader(reader)?)
}

#[derive(Clone, Debug, Serialize, Deserialize, PartialEq)]
pub struct ExhaustiveReport {
    pub schema_version: u32,
    pub benchmark: String,
    pub length: usize,
    pub states_checked: u64,
    pub optimum: Witness,
}

pub fn exhaustive_optimum(length: usize) -> LabsResult<ExhaustiveReport> {
    if !(2..=25).contains(&length) {
        return Err(LabsError::InvalidConfig(
            "exhaustive calibration is restricted to lengths 2 through 25".to_owned(),
        ));
    }
    let states = 1_u64 << (length - 1);
    let mut current = CandidateState::from_sequence(vec![1; length])?;
    let mut best = current.clone();

    for step in 1..states {
        let changed_bit = step.trailing_zeros() as usize;
        current.apply_flip(changed_bit + 1)?;
        if candidate_order(&current, &best).is_lt() {
            best = current.clone();
        }
    }
    best.checked()?;

    Ok(ExhaustiveReport {
        schema_version: SCHEMA_VERSION,
        benchmark: "low_autocorrelation_binary_sequence".to_owned(),
        length,
        states_checked: states,
        optimum: Witness::from_state(&best)?,
    })
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::fs;

    #[test]
    fn exact_energy_matches_known_sequence() {
        let sequence = vec![1, 1, 1, -1, 1, -1, -1];
        let evaluation = evaluate_sequence(&sequence).expect("valid LABS sequence");
        assert_eq!(evaluation.correlations, vec![0, 1, 0, -1, -2, -1]);
        assert_eq!(evaluation.energy, 7);
    }

    #[test]
    fn incremental_flip_matches_full_recomputation() {
        let state = CandidateState::from_sequence(vec![1, -1, 1, 1, -1, -1, 1, -1])
            .expect("valid state");
        for index in 0..state.sequence.len() {
            let before = state.clone();
            let predicted = before.flip_delta(index).expect("finite delta");
            let mut after = before.clone();
            let applied = after.apply_flip(index).expect("valid flip");
            assert_eq!(predicted, applied);
            assert_eq!(after.energy - before.energy, predicted);
            after.checked().expect("incremental state remains exact");
        }
    }

    #[test]
    fn labs_symmetry_orbit_preserves_energy() {
        let sequence = vec![1, -1, -1, 1, -1, 1, 1, -1, 1];
        let canonical = canonical_sequence(&sequence).expect("valid orbit");
        assert_eq!(
            evaluate_sequence(&sequence).expect("valid sequence").energy,
            evaluate_sequence(&canonical)
                .expect("valid canonical sequence")
                .energy
        );
    }

    #[test]
    fn exhaustive_small_optima_match_reference_values() {
        let expected = [(5, 2), (7, 3), (8, 8), (10, 13), (11, 5), (13, 6)];
        for (length, energy) in expected {
            let report = exhaustive_optimum(length).expect("bounded exhaustive search");
            assert_eq!(report.optimum.energy, energy, "length {length}");
            verify_witness(&report.optimum).expect("exact optimum witness");
        }
    }

    #[test]
    fn each_program_returns_an_exact_candidate() {
        let mut config = SearchConfig::for_length(12, 7);
        config.construction_interval = 1;
        let mut engine = SearchEngine::new(config).expect("valid engine");
        engine
            .temporal_proposal()
            .expect("temporal proposal")
            .candidate
            .checked()
            .expect("exact temporal candidate");
        engine
            .spatial_proposal()
            .expect("spatial proposal")
            .candidate
            .checked()
            .expect("exact spatial candidate");
        engine
            .constructive_proposal()
            .expect("constructive proposal")
            .candidate
            .checked()
            .expect("exact constructive candidate");
    }

    #[test]
    fn bounded_triadic_search_reaches_the_length_eleven_optimum() {
        let mut config = SearchConfig::for_length(11, 19);
        config.initial_population = 16;
        config.restart_after = 128;
        config.construction_interval = 8;
        config.trace_stride = 0;
        let mut engine = SearchEngine::new(config).expect("valid engine");
        engine.run_steps(8_000).expect("bounded search");
        assert_eq!(engine.best_energy(), 5);
        verify_witness(&engine.best_witness().expect("best witness"))
            .expect("exact best witness");
    }

    #[test]
    fn ablation_can_run_each_program_in_isolation() {
        for kind in ProgramKind::ALL {
            let mut config = SearchConfig::for_length(9, 31 + kind.index() as u64);
            config.enabled_programs = vec![kind];
            config.trace_stride = 0;
            let mut engine = SearchEngine::new(config).expect("valid isolated engine");
            engine.run_steps(128).expect("isolated bounded run");
            engine
                .best_witness()
                .and_then(|witness| verify_witness(&witness))
                .expect("isolated program preserves exactness");
        }
    }

    #[test]
    fn checkpoint_round_trip_preserves_a_deterministic_run() {
        let mut config = SearchConfig::for_length(10, 41);
        config.trace_stride = 17;
        let mut uninterrupted = SearchEngine::new(config.clone()).expect("valid engine");
        uninterrupted.run_steps(500).expect("bounded run");

        let mut interrupted = SearchEngine::new(config).expect("valid engine");
        interrupted.run_steps(200).expect("first segment");
        let path = std::env::temp_dir().join(format!(
            "adva-labs-checkpoint-{}-{}.json",
            std::process::id(),
            interrupted.iteration()
        ));
        interrupted
            .save_checkpoint(&path)
            .expect("write checkpoint");
        let mut resumed = SearchEngine::load_checkpoint(&path).expect("read checkpoint");
        resumed.run_steps(300).expect("second segment");
        fs::remove_file(path).expect("remove checkpoint");

        assert_eq!(uninterrupted, resumed);
    }

    #[test]
    fn parallel_report_has_an_independently_verifiable_best_witness() {
        let mut config = SearchConfig::for_length(9, 53);
        config.trace_stride = 0;
        let report = run_parallel(config, 256, 2).expect("parallel bounded search");
        report.verify().expect("exact report witness");
        assert_eq!(report.workers.len(), 2);
    }
}
