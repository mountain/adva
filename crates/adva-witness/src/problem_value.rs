use crate::{
    ArtifactKeyV0, InputLabelV0, InquiryInterfaceV0, InquirySaveReceiptV0, MechanismV0,
    OutputLabelV0,
};
use adva_ir::CheckStatus;
use serde::{Deserialize, Serialize};
use std::collections::BTreeSet;
use std::fs;
use std::path::{Path, PathBuf};
use thiserror::Error;

pub const PROBLEM_AWARENESS_SCHEMA_V0: &str = "adva.problem-awareness.research";
pub const PROBLEM_FORMATION_CONTRACT_SCHEMA_V0: &str = "adva.problem-formation-contract.research";
pub const IMAGINATION_RESOURCE_SCHEMA_V0: &str = "adva.imagination-resource.research";
pub const PROBLEM_FORMATION_TRANSITION_SCHEMA_V0: &str =
    "adva.problem-formation-transition.research";
pub const FORMED_PROBLEM_SCHEMA_V0: &str = "adva.formed-problem.research";
pub const PROBLEM_VALUE_FRONTIER_SCHEMA_V0: &str = "adva.problem-value-frontier.research";
pub const VALUE_SEEKING_CONTRACT_SCHEMA_V0: &str = "adva.value-seeking-contract.research";
pub const VALUE_SEEKING_RESOURCE_SCHEMA_V0: &str = "adva.value-seeking-resource.research";
pub const TRUST_CONTINUATION_WITNESS_SCHEMA_V0: &str = "adva.trust-continuation-witness.research";
pub const VALUE_SEEKING_TRANSITION_SCHEMA_V0: &str = "adva.value-seeking-transition.research";
pub const PROBLEM_VALUE_VERSION_V0: u32 = 0;

const DOMAIN_COUNT: u8 = 5;
const CURRENT_THRESHOLD: u8 = 3;
const FAULT_BUDGET: u8 = 1;
const FEATURE_COUNT: u8 = 5;
const CANDIDATE_COUNT: u64 = 160;

const RETAINED_CONTEXT: [&str; 10] = [
    "finite-boundary",
    "reality",
    "custody",
    "provenance",
    "replay",
    "challenge",
    "succession",
    "hypothesis-formation",
    "search",
    "trust-continuity",
];

#[derive(Clone, Copy, Debug, Eq, Ord, PartialEq, PartialOrd, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum TrustInvariantV0 {
    Provenance,
    Replay,
    Challenge,
    Succession,
}

impl TrustInvariantV0 {
    pub const ALL: [Self; 4] = [
        Self::Provenance,
        Self::Replay,
        Self::Challenge,
        Self::Succession,
    ];
}

#[derive(Clone, Copy, Debug, Eq, Ord, PartialEq, PartialOrd, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum ValueFeatureV0 {
    SignedParent,
    ReplayBundle,
    ForkLedger,
    RecoveryHandoff,
    IndependentRemeasurement,
}

impl ValueFeatureV0 {
    pub const ALL: [Self; 5] = [
        Self::SignedParent,
        Self::ReplayBundle,
        Self::ForkLedger,
        Self::RecoveryHandoff,
        Self::IndependentRemeasurement,
    ];

    const fn supports(self) -> TrustInvariantV0 {
        match self {
            Self::SignedParent => TrustInvariantV0::Provenance,
            Self::ReplayBundle | Self::IndependentRemeasurement => TrustInvariantV0::Replay,
            Self::ForkLedger => TrustInvariantV0::Challenge,
            Self::RecoveryHandoff => TrustInvariantV0::Succession,
        }
    }

    const fn capability(self) -> &'static str {
        match self {
            Self::SignedParent => "content-addressed signed parent handoff",
            Self::ReplayBundle => "versioned method, checker, inputs, and residual replay bundle",
            Self::ForkLedger => "append-only challenge and fork ledger",
            Self::RecoveryHandoff => "recoverable successor boundary across failure domains",
            Self::IndependentRemeasurement => {
                "independent protocol-conforming reality remeasurement"
            }
        }
    }
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct ProblemAwarenessV0 {
    pub schema: String,
    pub version: u32,
    pub interface: InquiryInterfaceV0,
    pub scope: String,
    pub independent_domains: Vec<String>,
    pub current_receipt_threshold: u8,
    pub adversarial_fault_budget: u8,
    pub observed_gap: String,
    pub protected_invariants: Vec<TrustInvariantV0>,
    pub retained_context: Vec<String>,
    pub parent_artifacts: Vec<String>,
}

impl ProblemAwarenessV0 {
    #[must_use]
    pub fn first() -> Self {
        Self {
            schema: PROBLEM_AWARENESS_SCHEMA_V0.to_owned(),
            version: PROBLEM_VALUE_VERSION_V0,
            interface: InquiryInterfaceV0::canonical(),
            scope: "five-domain custody quorum-overlap model; one unavailable or adversarial domain"
                .to_owned(),
            independent_domains: (0..DOMAIN_COUNT)
                .map(|index| format!("custody-domain-{index}"))
                .collect(),
            current_receipt_threshold: CURRENT_THRESHOLD,
            adversarial_fault_budget: FAULT_BUDGET,
            observed_gap: "the existing three-of-five receipt threshold has no recorded proof that two accepted successor sets retain an honest common custodian under one adversarial fault"
                .to_owned(),
            protected_invariants: TrustInvariantV0::ALL.to_vec(),
            retained_context: RETAINED_CONTEXT.map(str::to_owned).to_vec(),
            parent_artifacts: vec![
                "programs/bootstrap-0/trust-continuity-session-witness.adva".to_owned(),
                "programs/bootstrap-0/hypothesis-formation-frontier-6.adva".to_owned(),
            ],
        }
    }

    pub fn check(&self) -> Result<(), ProblemValueErrorV0> {
        if self != &Self::first() {
            return Err(invalid("the problem-awareness input has drifted"));
        }
        Ok(())
    }

    pub fn from_json(source: &str) -> Result<Self, ProblemValueErrorV0> {
        let value: Self = serde_json::from_str(source)
            .map_err(|error| ProblemValueErrorV0::Json(error.to_string()))?;
        value.check()?;
        Ok(value)
    }

    pub fn to_json(&self) -> Result<String, ProblemValueErrorV0> {
        self.check()?;
        pretty_json(self)
    }

    pub fn digest(&self) -> Result<String, ProblemValueErrorV0> {
        self.check()?;
        digest_serialized(self)
    }
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct ProblemFormationContractV0 {
    pub schema: String,
    pub version: u32,
    pub interface: InquiryInterfaceV0,
    pub program_name: String,
    pub display_name_zh: String,
    pub mechanism: MechanismV0,
    pub counterexample_search: String,
    pub formation_rule: String,
    pub imagination_boundary: String,
    pub output_schema: String,
}

impl ProblemFormationContractV0 {
    #[must_use]
    pub fn first() -> Self {
        Self {
            schema: PROBLEM_FORMATION_CONTRACT_SCHEMA_V0.to_owned(),
            version: PROBLEM_VALUE_VERSION_V0,
            interface: InquiryInterfaceV0::canonical(),
            program_name: "problem-formation".to_owned(),
            display_name_zh: "问题形成".to_owned(),
            mechanism: MechanismV0::Learn,
            counterexample_search: "lexicographic pairs of current-threshold quorums, then lexicographic one-domain fault sets"
                .to_owned(),
            formation_rule: "admit a problem only with an exact retained counterexample, externally supplied candidate directions, an external need, a help-first contribution, falsifiers, and a finite cost boundary"
                .to_owned(),
            imagination_boundary: "imagination proposes charts and directions at the interface; this program may select and test them but does not derive imagination from the sealed formal system"
                .to_owned(),
            output_schema: PROBLEM_VALUE_FRONTIER_SCHEMA_V0.to_owned(),
        }
    }

    pub fn check(&self) -> Result<(), ProblemValueErrorV0> {
        if self != &Self::first() {
            return Err(invalid("the problem-formation contract has drifted"));
        }
        Ok(())
    }

    pub fn from_json(source: &str) -> Result<Self, ProblemValueErrorV0> {
        let value: Self = serde_json::from_str(source)
            .map_err(|error| ProblemValueErrorV0::Json(error.to_string()))?;
        value.check()?;
        Ok(value)
    }

    pub fn to_json(&self) -> Result<String, ProblemValueErrorV0> {
        self.check()?;
        pretty_json(self)
    }

    pub fn digest(&self) -> Result<String, ProblemValueErrorV0> {
        self.check()?;
        digest_serialized(self)
    }
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct ImaginationDirectionV0 {
    pub feature: ValueFeatureV0,
    pub capability: String,
    pub supports: TrustInvariantV0,
    pub cost_units: u8,
}

impl ImaginationDirectionV0 {
    fn first(feature: ValueFeatureV0) -> Self {
        Self {
            feature,
            capability: feature.capability().to_owned(),
            supports: feature.supports(),
            cost_units: 1,
        }
    }
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct ImaginationResourceV0 {
    pub schema: String,
    pub version: u32,
    pub interface: InquiryInterfaceV0,
    pub origin: String,
    pub status: String,
    pub candidate_thresholds: Vec<u8>,
    pub directions: Vec<ImaginationDirectionV0>,
    pub external_need: String,
    pub help_first_contribution: String,
    pub falsifiers: Vec<String>,
    pub finite_cost_boundary: String,
    pub vocabulary: Vec<String>,
}

impl ImaginationResourceV0 {
    #[must_use]
    pub fn first() -> Self {
        Self {
            schema: IMAGINATION_RESOURCE_SCHEMA_V0.to_owned(),
            version: PROBLEM_VALUE_VERSION_V0,
            interface: InquiryInterfaceV0::canonical(),
            origin: "external:conversation-rereading:2026-09-05".to_owned(),
            status: "externally-proposed-candidate-directions".to_owned(),
            candidate_thresholds: (1..=DOMAIN_COUNT).collect(),
            directions: ValueFeatureV0::ALL
                .into_iter()
                .map(ImaginationDirectionV0::first)
                .collect(),
            external_need: "independently controlled custodians must later instantiate the declared domains and perform protocol-conforming remeasurement and recovery drills"
                .to_owned(),
            help_first_contribution: "publish the exact counterexample, candidate enumeration, checker, replay fixture, and residual deployment obligations without asking a later observer to endorse the claim"
                .to_owned(),
            falsifiers: vec![
                "no policy in the declared finite candidate space satisfies honest overlap and one-fault availability"
                    .to_owned(),
                "the retained counterexample does not replay under the frozen quorum model".to_owned(),
                "a selected feature bundle drops provenance, replay, challenge, succession, or the compatible reserve"
                    .to_owned(),
                "the declared cost exceeds the finite value-seeking budget".to_owned(),
            ],
            finite_cost_boundary: "five thresholds times thirty-two feature subsets; every selected threshold approval and feature costs one unit"
                .to_owned(),
            vocabulary: vec!["imagination".to_owned(), "candidate-direction".to_owned()],
        }
    }

    pub fn check(&self) -> Result<(), ProblemValueErrorV0> {
        if self != &Self::first() {
            return Err(invalid("the imagination resource has drifted"));
        }
        Ok(())
    }

    pub fn from_json(source: &str) -> Result<Self, ProblemValueErrorV0> {
        let value: Self = serde_json::from_str(source)
            .map_err(|error| ProblemValueErrorV0::Json(error.to_string()))?;
        value.check()?;
        Ok(value)
    }

    pub fn to_json(&self) -> Result<String, ProblemValueErrorV0> {
        self.check()?;
        pretty_json(self)
    }

    pub fn digest(&self) -> Result<String, ProblemValueErrorV0> {
        self.check()?;
        digest_serialized(self)
    }
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct QuorumCounterexampleV0 {
    pub left_receipts: Vec<u8>,
    pub right_receipts: Vec<u8>,
    pub shared_domains: Vec<u8>,
    pub adversarial_domains: Vec<u8>,
    pub honest_shared_domains: Vec<u8>,
}

impl QuorumCounterexampleV0 {
    fn check_against(&self, awareness: &ProblemAwarenessV0) -> Result<(), ProblemValueErrorV0> {
        let domain_count = u8::try_from(awareness.independent_domains.len())
            .map_err(|_| invalid("domain count overflow"))?;
        if self.left_receipts.len() != usize::from(awareness.current_receipt_threshold)
            || self.right_receipts.len() != usize::from(awareness.current_receipt_threshold)
            || self.adversarial_domains.len() != usize::from(awareness.adversarial_fault_budget)
            || !ordered_unique_within(&self.left_receipts, domain_count)
            || !ordered_unique_within(&self.right_receipts, domain_count)
            || !ordered_unique_within(&self.adversarial_domains, domain_count)
        {
            return Err(invalid("the quorum counterexample has invalid coordinates"));
        }
        let shared = intersection(&self.left_receipts, &self.right_receipts);
        let honest = difference(&shared, &self.adversarial_domains);
        if self.shared_domains != shared
            || self.honest_shared_domains != honest
            || !honest.is_empty()
        {
            return Err(invalid(
                "the current quorum counterexample does not erase honest overlap",
            ));
        }
        Ok(())
    }
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct FormedProblemV0 {
    pub schema: String,
    pub version: u32,
    pub interface: InquiryInterfaceV0,
    pub occurrence: ArtifactKeyV0,
    pub statement: String,
    pub awareness_digest: String,
    pub method_digest: String,
    pub imagination_digest: String,
    pub current_domain_count: u8,
    pub current_threshold: u8,
    pub fault_budget: u8,
    pub counterexample: QuorumCounterexampleV0,
    pub candidate_thresholds: Vec<u8>,
    pub candidate_directions: Vec<ImaginationDirectionV0>,
    pub protected_invariants: Vec<TrustInvariantV0>,
    pub external_need: String,
    pub help_first_contribution: String,
    pub falsifiers: Vec<String>,
    pub finite_cost_boundary: String,
    pub value_target: String,
    pub retained_vocabulary: Vec<String>,
    pub introduced_vocabulary: Vec<String>,
}

impl FormedProblemV0 {
    pub fn check(&self) -> Result<(), ProblemValueErrorV0> {
        check_header(
            &self.schema,
            self.version,
            FORMED_PROBLEM_SCHEMA_V0,
            &self.interface,
        )?;
        if self.occurrence.as_str().is_empty()
            || self.current_domain_count != DOMAIN_COUNT
            || self.current_threshold != CURRENT_THRESHOLD
            || self.fault_budget != FAULT_BUDGET
            || self.candidate_thresholds != (1..=DOMAIN_COUNT).collect::<Vec<_>>()
            || self.candidate_directions
                != ValueFeatureV0::ALL
                    .into_iter()
                    .map(ImaginationDirectionV0::first)
                    .collect::<Vec<_>>()
            || self.protected_invariants != TrustInvariantV0::ALL
            || self.external_need.trim().is_empty()
            || self.help_first_contribution.trim().is_empty()
            || self.falsifiers.is_empty()
            || self.falsifiers.iter().any(|value| value.trim().is_empty())
            || self.finite_cost_boundary.trim().is_empty()
            || self.value_target.trim().is_empty()
            || self.introduced_vocabulary
                != vec!["problem-formation".to_owned(), "problem".to_owned()]
            || self.retained_vocabulary
                != RETAINED_CONTEXT
                    .map(str::to_owned)
                    .into_iter()
                    .chain(["imagination".to_owned(), "candidate-direction".to_owned()])
                    .chain(["problem-formation".to_owned(), "problem".to_owned()])
                    .collect::<Vec<_>>()
        {
            return Err(invalid("the formed problem lost its declared boundary"));
        }
        check_digest(&self.awareness_digest)?;
        check_digest(&self.method_digest)?;
        check_digest(&self.imagination_digest)?;
        self.counterexample
            .check_against(&ProblemAwarenessV0::first())
    }

    pub fn from_json(source: &str) -> Result<Self, ProblemValueErrorV0> {
        let value: Self = serde_json::from_str(source)
            .map_err(|error| ProblemValueErrorV0::Json(error.to_string()))?;
        value.check()?;
        Ok(value)
    }

    pub fn to_json(&self) -> Result<String, ProblemValueErrorV0> {
        self.check()?;
        pretty_json(self)
    }

    pub fn digest(&self) -> Result<String, ProblemValueErrorV0> {
        self.check()?;
        digest_serialized(self)
    }
}

#[derive(Clone, Copy, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum ProblemValueFrontierStateV0 {
    Open,
    Completed,
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct ProblemValueFrontierV0 {
    pub schema: String,
    pub version: u32,
    pub interface: InquiryInterfaceV0,
    pub sequence: u64,
    pub state: ProblemValueFrontierStateV0,
    pub problem: FormedProblemV0,
    pub source_problem_digest: String,
    pub candidate_cursor: u64,
    pub witness_digest: Option<String>,
    pub parent_frontier_digest: Option<String>,
}

impl ProblemValueFrontierV0 {
    fn initial(problem: FormedProblemV0) -> Result<Self, ProblemValueErrorV0> {
        let source_problem_digest = problem.digest()?;
        let value = Self {
            schema: PROBLEM_VALUE_FRONTIER_SCHEMA_V0.to_owned(),
            version: PROBLEM_VALUE_VERSION_V0,
            interface: InquiryInterfaceV0::canonical(),
            sequence: 0,
            state: ProblemValueFrontierStateV0::Open,
            problem,
            source_problem_digest,
            candidate_cursor: 0,
            witness_digest: None,
            parent_frontier_digest: None,
        };
        value.check()?;
        Ok(value)
    }

    pub fn check(&self) -> Result<(), ProblemValueErrorV0> {
        check_header(
            &self.schema,
            self.version,
            PROBLEM_VALUE_FRONTIER_SCHEMA_V0,
            &self.interface,
        )?;
        self.problem.check()?;
        if self.source_problem_digest != self.problem.digest()?
            || self.candidate_cursor > CANDIDATE_COUNT
        {
            return Err(invalid(
                "the value frontier lost its source problem or cursor",
            ));
        }
        match self.state {
            ProblemValueFrontierStateV0::Open => {
                if self.candidate_cursor == CANDIDATE_COUNT || self.witness_digest.is_some() {
                    return Err(invalid("an open value frontier has terminal state"));
                }
            }
            ProblemValueFrontierStateV0::Completed => {
                if let Some(digest) = &self.witness_digest {
                    check_digest(digest)?;
                } else if self.candidate_cursor != CANDIDATE_COUNT {
                    return Err(invalid(
                        "a witnessless completed value frontier did not exhaust candidates",
                    ));
                }
            }
        }
        match (self.sequence, self.parent_frontier_digest.as_deref()) {
            (0, None) => {}
            (0, Some(_)) => return Err(invalid("the initial value frontier has a parent")),
            (_, Some(digest)) => check_digest(digest)?,
            (_, None) => return Err(invalid("a continued value frontier lost its parent")),
        }
        Ok(())
    }

    pub fn from_json(source: &str) -> Result<Self, ProblemValueErrorV0> {
        let value: Self = serde_json::from_str(source)
            .map_err(|error| ProblemValueErrorV0::Json(error.to_string()))?;
        value.check()?;
        Ok(value)
    }

    pub fn to_json(&self) -> Result<String, ProblemValueErrorV0> {
        self.check()?;
        pretty_json(self)
    }

    pub fn digest(&self) -> Result<String, ProblemValueErrorV0> {
        self.check()?;
        digest_serialized(self)
    }
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct ProblemFormationInputV0 {
    pub subject: ProblemAwarenessV0,
    pub method: ProblemFormationContractV0,
    pub object: ImaginationResourceV0,
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct ProblemFormationHistoryV0 {
    pub mechanism: MechanismV0,
    pub awareness_digest: String,
    pub method_digest: String,
    pub imagination_digest: String,
    pub quorum_fault_cases_examined: u64,
    pub generation_trace: Vec<String>,
}

#[derive(Clone, Copy, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum ProblemFormationStateV0 {
    Formed,
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct ProblemFormationResultV0 {
    pub state: ProblemFormationStateV0,
    pub problem_occurrence: ArtifactKeyV0,
    pub problem_digest: String,
    pub introduced_vocabulary: Vec<String>,
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct ProblemFormationEvidenceV0 {
    pub current_policy_counterexample: CheckStatus,
    pub history_retained: CheckStatus,
    pub imagination_source_explicit: CheckStatus,
    pub external_need_explicit: CheckStatus,
    pub help_first_explicit: CheckStatus,
    pub falsifiers_explicit: CheckStatus,
    pub finite_cost_explicit: CheckStatus,
    pub next_frontier: ProblemValueFrontierV0,
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct ProblemFormationOutputV0 {
    pub history: ProblemFormationHistoryV0,
    pub result: ProblemFormationResultV0,
    pub evidence: ProblemFormationEvidenceV0,
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct ProblemFormationTransitionV0 {
    pub schema: String,
    pub version: u32,
    pub input: ProblemFormationInputV0,
    pub output: ProblemFormationOutputV0,
}

impl ProblemFormationTransitionV0 {
    pub fn check(&self) -> Result<(), ProblemValueErrorV0> {
        if self.schema != PROBLEM_FORMATION_TRANSITION_SCHEMA_V0
            || self.version != PROBLEM_VALUE_VERSION_V0
        {
            return Err(invalid("unsupported problem-formation transition header"));
        }
        self.input.subject.check()?;
        self.input.method.check()?;
        self.input.object.check()?;
        if self.output != derive_problem_output(&self.input)? {
            return Err(invalid("the stored problem formation does not replay"));
        }
        Ok(())
    }

    pub fn from_json(source: &str) -> Result<Self, ProblemValueErrorV0> {
        let value: Self = serde_json::from_str(source)
            .map_err(|error| ProblemValueErrorV0::Json(error.to_string()))?;
        value.check()?;
        Ok(value)
    }

    pub fn to_json(&self) -> Result<String, ProblemValueErrorV0> {
        self.check()?;
        pretty_json(self)
    }

    pub fn digest(&self) -> Result<String, ProblemValueErrorV0> {
        self.check()?;
        digest_serialized(self)
    }
}

pub fn run_problem_formation_v0(
    subject: &ProblemAwarenessV0,
    method: &ProblemFormationContractV0,
    object: &ImaginationResourceV0,
) -> Result<ProblemFormationTransitionV0, ProblemValueErrorV0> {
    subject.check()?;
    method.check()?;
    object.check()?;
    let input = ProblemFormationInputV0 {
        subject: subject.clone(),
        method: method.clone(),
        object: object.clone(),
    };
    let transition = ProblemFormationTransitionV0 {
        schema: PROBLEM_FORMATION_TRANSITION_SCHEMA_V0.to_owned(),
        version: PROBLEM_VALUE_VERSION_V0,
        output: derive_problem_output(&input)?,
        input,
    };
    transition.check()?;
    Ok(transition)
}

fn derive_problem_output(
    input: &ProblemFormationInputV0,
) -> Result<ProblemFormationOutputV0, ProblemValueErrorV0> {
    let (counterexample, examined) =
        first_quorum_counterexample(DOMAIN_COUNT, CURRENT_THRESHOLD, FAULT_BUDGET)
            .ok_or_else(|| invalid("the declared awareness gap has no exact counterexample"))?;
    counterexample.check_against(&input.subject)?;

    let awareness_digest = input.subject.digest()?;
    let method_digest = input.method.digest()?;
    let imagination_digest = input.object.digest()?;
    let mut retained_vocabulary = input.subject.retained_context.clone();
    retained_vocabulary.extend(input.object.vocabulary.clone());
    retained_vocabulary.extend(["problem-formation".to_owned(), "problem".to_owned()]);
    let problem = FormedProblemV0 {
        schema: FORMED_PROBLEM_SCHEMA_V0.to_owned(),
        version: PROBLEM_VALUE_VERSION_V0,
        interface: InquiryInterfaceV0::canonical(),
        occurrence: key("experiment:0122:problem:honest-quorum-continuation")?,
        statement: "within five declared independent custody domains and one adversarial fault, find the least receipt threshold and finite feature bundle that remain available after one domain loss, force honest overlap between any two accepted successors, retain provenance, replay, challenge, and succession, and leave one compatible reserve"
            .to_owned(),
        awareness_digest: awareness_digest.clone(),
        method_digest: method_digest.clone(),
        imagination_digest: imagination_digest.clone(),
        current_domain_count: DOMAIN_COUNT,
        current_threshold: CURRENT_THRESHOLD,
        fault_budget: FAULT_BUDGET,
        counterexample,
        candidate_thresholds: input.object.candidate_thresholds.clone(),
        candidate_directions: input.object.directions.clone(),
        protected_invariants: input.subject.protected_invariants.clone(),
        external_need: input.object.external_need.clone(),
        help_first_contribution: input.object.help_first_contribution.clone(),
        falsifiers: input.object.falsifiers.clone(),
        finite_cost_boundary: input.object.finite_cost_boundary.clone(),
        value_target: "stable trust continuation: admissibility is noncompensating; cost orders only candidates that already preserve every invariant"
            .to_owned(),
        retained_vocabulary,
        introduced_vocabulary: vec!["problem-formation".to_owned(), "problem".to_owned()],
    };
    problem.check()?;
    let problem_digest = problem.digest()?;
    let next_frontier = ProblemValueFrontierV0::initial(problem.clone())?;
    Ok(ProblemFormationOutputV0 {
        history: ProblemFormationHistoryV0 {
            mechanism: MechanismV0::Learn,
            awareness_digest,
            method_digest,
            imagination_digest,
            quorum_fault_cases_examined: examined,
            generation_trace: vec![
                "retain the reality-facing custody gap".to_owned(),
                "search an exact current-policy counterexample".to_owned(),
                "attach externally proposed directions without promoting them to facts".to_owned(),
                "publish the external need, help-first contribution, falsifiers, and finite cost"
                    .to_owned(),
            ],
        },
        result: ProblemFormationResultV0 {
            state: ProblemFormationStateV0::Formed,
            problem_occurrence: problem.occurrence,
            problem_digest,
            introduced_vocabulary: problem.introduced_vocabulary,
        },
        evidence: ProblemFormationEvidenceV0 {
            current_policy_counterexample: CheckStatus::Checked,
            history_retained: CheckStatus::Checked,
            imagination_source_explicit: CheckStatus::Checked,
            external_need_explicit: CheckStatus::Checked,
            help_first_explicit: CheckStatus::Checked,
            falsifiers_explicit: CheckStatus::Checked,
            finite_cost_explicit: CheckStatus::Checked,
            next_frontier,
        },
    })
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct ValueSeekingContractV0 {
    pub schema: String,
    pub version: u32,
    pub interface: InquiryInterfaceV0,
    pub program_name: String,
    pub display_name_zh: String,
    pub mechanism: MechanismV0,
    pub candidate_count: u64,
    pub enumeration: String,
    pub admission_rule: String,
    pub value_boundary: String,
    pub output_schema: String,
}

impl ValueSeekingContractV0 {
    #[must_use]
    pub fn first() -> Self {
        Self {
            schema: VALUE_SEEKING_CONTRACT_SCHEMA_V0.to_owned(),
            version: PROBLEM_VALUE_VERSION_V0,
            interface: InquiryInterfaceV0::canonical(),
            program_name: "value-seeking".to_owned(),
            display_name_zh: "价值寻求".to_owned(),
            mechanism: MechanismV0::Learn,
            candidate_count: CANDIDATE_COUNT,
            enumeration: "receipt threshold ascending, then five-bit feature mask ascending"
                .to_owned(),
            admission_rule: "first require one-fault availability, honest successor overlap, all four noncompensating trust invariants, a distinct typed matching, one compatible reserve, and payable finite cost; only then prefer the first lower-burden candidate"
                .to_owned(),
            value_boundary: "the program optimizes an externally declared value policy; it does not derive value, truth, consent, social trust, or custodian independence from arithmetic"
                .to_owned(),
            output_schema: VALUE_SEEKING_TRANSITION_SCHEMA_V0.to_owned(),
        }
    }

    pub fn check(&self) -> Result<(), ProblemValueErrorV0> {
        if self != &Self::first() {
            return Err(invalid("the value-seeking contract has drifted"));
        }
        Ok(())
    }

    pub fn from_json(source: &str) -> Result<Self, ProblemValueErrorV0> {
        let value: Self = serde_json::from_str(source)
            .map_err(|error| ProblemValueErrorV0::Json(error.to_string()))?;
        value.check()?;
        Ok(value)
    }

    pub fn to_json(&self) -> Result<String, ProblemValueErrorV0> {
        self.check()?;
        pretty_json(self)
    }

    pub fn digest(&self) -> Result<String, ProblemValueErrorV0> {
        self.check()?;
        digest_serialized(self)
    }
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct ValueSeekingResourceV0 {
    pub schema: String,
    pub version: u32,
    pub interface: InquiryInterfaceV0,
    pub candidate_fuel: u64,
    pub spacetime_cost_budget: u8,
    pub threshold_approval_cost: u8,
    pub feature_cost: u8,
}

impl ValueSeekingResourceV0 {
    #[must_use]
    pub fn bounded(candidate_fuel: u64, spacetime_cost_budget: u8) -> Self {
        Self {
            schema: VALUE_SEEKING_RESOURCE_SCHEMA_V0.to_owned(),
            version: PROBLEM_VALUE_VERSION_V0,
            interface: InquiryInterfaceV0::canonical(),
            candidate_fuel,
            spacetime_cost_budget,
            threshold_approval_cost: 1,
            feature_cost: 1,
        }
    }

    #[must_use]
    pub fn first() -> Self {
        Self::bounded(CANDIDATE_COUNT, 9)
    }

    pub fn check(&self) -> Result<(), ProblemValueErrorV0> {
        check_header(
            &self.schema,
            self.version,
            VALUE_SEEKING_RESOURCE_SCHEMA_V0,
            &self.interface,
        )?;
        if self.candidate_fuel == 0
            || self.candidate_fuel > CANDIDATE_COUNT
            || self.spacetime_cost_budget == 0
            || self.threshold_approval_cost != 1
            || self.feature_cost != 1
        {
            return Err(invalid(
                "the value-seeking resource is outside its finite boundary",
            ));
        }
        Ok(())
    }

    pub fn from_json(source: &str) -> Result<Self, ProblemValueErrorV0> {
        let value: Self = serde_json::from_str(source)
            .map_err(|error| ProblemValueErrorV0::Json(error.to_string()))?;
        value.check()?;
        Ok(value)
    }

    pub fn to_json(&self) -> Result<String, ProblemValueErrorV0> {
        self.check()?;
        pretty_json(self)
    }

    pub fn digest(&self) -> Result<String, ProblemValueErrorV0> {
        self.check()?;
        digest_serialized(self)
    }
}

#[derive(Clone, Copy, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum ContinuityComparisonV0 {
    Greater,
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct ValueAssignmentV0 {
    pub obligation: TrustInvariantV0,
    pub resource: ValueFeatureV0,
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct TrustContinuationWitnessV0 {
    pub schema: String,
    pub version: u32,
    pub occurrence: ArtifactKeyV0,
    pub problem_digest: String,
    pub contract_digest: String,
    pub resource_digest: String,
    pub candidate_ordinal: u64,
    pub selected_threshold: u8,
    pub selected_features: Vec<ValueFeatureV0>,
    pub successor_quorums: Vec<Vec<u8>>,
    pub minimum_pair_intersection: u8,
    pub guaranteed_honest_overlap: u8,
    pub remaining_domains_after_fault: u8,
    pub typed_matching: Vec<ValueAssignmentV0>,
    pub compatible_reserve: ValueFeatureV0,
    pub merge_capacity: u8,
    pub rupture_load: u8,
    pub comparison: ContinuityComparisonV0,
    pub total_cost: u8,
    pub retained_vocabulary: Vec<String>,
    pub introduced_vocabulary: Vec<String>,
    pub external_residual: String,
}

impl TrustContinuationWitnessV0 {
    fn check_against(
        &self,
        frontier: &ProblemValueFrontierV0,
        contract: &ValueSeekingContractV0,
        resource: &ValueSeekingResourceV0,
    ) -> Result<(), ProblemValueErrorV0> {
        if self.schema != TRUST_CONTINUATION_WITNESS_SCHEMA_V0
            || self.version != PROBLEM_VALUE_VERSION_V0
        {
            return Err(invalid("the retained value witness header drifted"));
        }
        let candidate = candidate_from_ordinal(&frontier.problem, self.candidate_ordinal)?;
        let admission = admit_candidate(&frontier.problem, &candidate, resource);
        if !admission.admitted {
            return Err(invalid("the retained value witness is not admissible"));
        }
        let expected =
            witness_from_admission(frontier, contract, resource, &candidate, &admission)?;
        if self != &expected {
            return Err(invalid("the retained value witness does not replay"));
        }
        Ok(())
    }

    pub fn digest(
        &self,
        frontier: &ProblemValueFrontierV0,
        contract: &ValueSeekingContractV0,
        resource: &ValueSeekingResourceV0,
    ) -> Result<String, ProblemValueErrorV0> {
        self.check_against(frontier, contract, resource)?;
        digest_serialized(self)
    }
}

#[derive(Clone, Copy, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum ValueSeekingRunStateV0 {
    Witness,
    NoWitness,
    Suspended,
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct ValueSeekingInputV0 {
    pub subject: ProblemValueFrontierV0,
    pub method: ValueSeekingContractV0,
    pub object: ValueSeekingResourceV0,
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct ValueSeekingHistoryV0 {
    pub mechanism: MechanismV0,
    pub subject_digest: String,
    pub method_digest: String,
    pub object_digest: String,
    pub cursor_before: u64,
    pub cursor_after: u64,
    pub candidates_examined: u64,
    pub rejected_by_availability: u64,
    pub rejected_by_overlap: u64,
    pub rejected_by_invariant_coverage: u64,
    pub rejected_by_reserve: u64,
    pub rejected_by_budget: u64,
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct ValueSeekingResultV0 {
    pub state: ValueSeekingRunStateV0,
    pub witness: Option<TrustContinuationWitnessV0>,
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct ValueSeekingEvidenceV0 {
    pub finite_candidate_enumeration: CheckStatus,
    pub one_fault_availability: CheckStatus,
    pub honest_successor_overlap: CheckStatus,
    pub noncompensating_invariants: CheckStatus,
    pub distinct_typed_matching: CheckStatus,
    pub compatible_reserve: CheckStatus,
    pub cost_within_budget: CheckStatus,
    pub imagination_remains_external: CheckStatus,
    pub next_frontier: ProblemValueFrontierV0,
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct ValueSeekingOutputV0 {
    pub history: ValueSeekingHistoryV0,
    pub result: ValueSeekingResultV0,
    pub evidence: ValueSeekingEvidenceV0,
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct ValueSeekingTransitionV0 {
    pub schema: String,
    pub version: u32,
    pub input: ValueSeekingInputV0,
    pub output: ValueSeekingOutputV0,
}

impl ValueSeekingTransitionV0 {
    pub fn check(&self) -> Result<(), ProblemValueErrorV0> {
        if self.schema != VALUE_SEEKING_TRANSITION_SCHEMA_V0
            || self.version != PROBLEM_VALUE_VERSION_V0
        {
            return Err(invalid("unsupported value-seeking transition header"));
        }
        self.input.subject.check()?;
        self.input.method.check()?;
        self.input.object.check()?;
        if self.input.subject.state != ProblemValueFrontierStateV0::Open {
            return Err(invalid("value seeking requires an open problem frontier"));
        }
        if self.output != derive_value_output(&self.input)? {
            return Err(invalid("the stored value-seeking output does not replay"));
        }
        Ok(())
    }

    pub fn from_json(source: &str) -> Result<Self, ProblemValueErrorV0> {
        let value: Self = serde_json::from_str(source)
            .map_err(|error| ProblemValueErrorV0::Json(error.to_string()))?;
        value.check()?;
        Ok(value)
    }

    pub fn to_json(&self) -> Result<String, ProblemValueErrorV0> {
        self.check()?;
        pretty_json(self)
    }

    pub fn digest(&self) -> Result<String, ProblemValueErrorV0> {
        self.check()?;
        digest_serialized(self)
    }
}

pub fn run_value_seeking_v0(
    subject: &ProblemValueFrontierV0,
    method: &ValueSeekingContractV0,
    object: &ValueSeekingResourceV0,
) -> Result<ValueSeekingTransitionV0, ProblemValueErrorV0> {
    subject.check()?;
    method.check()?;
    object.check()?;
    if subject.state != ProblemValueFrontierStateV0::Open {
        return Err(invalid("value seeking requires an open problem frontier"));
    }
    let input = ValueSeekingInputV0 {
        subject: subject.clone(),
        method: method.clone(),
        object: object.clone(),
    };
    let transition = ValueSeekingTransitionV0 {
        schema: VALUE_SEEKING_TRANSITION_SCHEMA_V0.to_owned(),
        version: PROBLEM_VALUE_VERSION_V0,
        output: derive_value_output(&input)?,
        input,
    };
    transition.check()?;
    Ok(transition)
}

#[derive(Clone, Debug)]
struct ValueCandidateV0 {
    ordinal: u64,
    threshold: u8,
    features: Vec<ValueFeatureV0>,
}

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
enum RejectionV0 {
    Availability,
    Overlap,
    InvariantCoverage,
    Reserve,
    Budget,
}

#[derive(Clone, Debug)]
struct CandidateAdmissionV0 {
    admitted: bool,
    rejection: Option<RejectionV0>,
    quorums: Vec<Vec<u8>>,
    minimum_pair_intersection: u8,
    honest_overlap: u8,
    matching: Vec<ValueAssignmentV0>,
    reserve: Option<ValueFeatureV0>,
    total_cost: u8,
}

fn derive_value_output(
    input: &ValueSeekingInputV0,
) -> Result<ValueSeekingOutputV0, ProblemValueErrorV0> {
    let cursor_before = input.subject.candidate_cursor;
    let mut examined = 0_u64;
    let mut rejected_by_availability = 0_u64;
    let mut rejected_by_overlap = 0_u64;
    let mut rejected_by_invariant_coverage = 0_u64;
    let mut rejected_by_reserve = 0_u64;
    let mut rejected_by_budget = 0_u64;
    let mut found = None;

    for ordinal in cursor_before..CANDIDATE_COUNT {
        if examined == input.object.candidate_fuel {
            break;
        }
        examined += 1;
        let candidate = candidate_from_ordinal(&input.subject.problem, ordinal)?;
        let admission = admit_candidate(&input.subject.problem, &candidate, &input.object);
        if admission.admitted {
            found = Some(witness_from_admission(
                &input.subject,
                &input.method,
                &input.object,
                &candidate,
                &admission,
            )?);
            break;
        }
        match admission.rejection {
            Some(RejectionV0::Availability) => rejected_by_availability += 1,
            Some(RejectionV0::Overlap) => rejected_by_overlap += 1,
            Some(RejectionV0::InvariantCoverage) => rejected_by_invariant_coverage += 1,
            Some(RejectionV0::Reserve) => rejected_by_reserve += 1,
            Some(RejectionV0::Budget) => rejected_by_budget += 1,
            None => return Err(invalid("a rejected value candidate has no reason")),
        }
    }

    let cursor_after = cursor_before + examined;
    let state = if found.is_some() {
        ValueSeekingRunStateV0::Witness
    } else if cursor_after == CANDIDATE_COUNT {
        ValueSeekingRunStateV0::NoWitness
    } else {
        ValueSeekingRunStateV0::Suspended
    };
    let witness_digest = found
        .as_ref()
        .map(|witness| witness.digest(&input.subject, &input.method, &input.object))
        .transpose()?;
    let next_frontier = ProblemValueFrontierV0 {
        schema: PROBLEM_VALUE_FRONTIER_SCHEMA_V0.to_owned(),
        version: PROBLEM_VALUE_VERSION_V0,
        interface: InquiryInterfaceV0::canonical(),
        sequence: input.subject.sequence + 1,
        state: if state == ValueSeekingRunStateV0::Suspended {
            ProblemValueFrontierStateV0::Open
        } else {
            ProblemValueFrontierStateV0::Completed
        },
        problem: input.subject.problem.clone(),
        source_problem_digest: input.subject.source_problem_digest.clone(),
        candidate_cursor: cursor_after,
        witness_digest,
        parent_frontier_digest: Some(input.subject.digest()?),
    };
    next_frontier.check()?;
    let checked = if found.is_some() {
        CheckStatus::Checked
    } else {
        CheckStatus::Unchecked
    };
    Ok(ValueSeekingOutputV0 {
        history: ValueSeekingHistoryV0 {
            mechanism: MechanismV0::Learn,
            subject_digest: input.subject.digest()?,
            method_digest: input.method.digest()?,
            object_digest: input.object.digest()?,
            cursor_before,
            cursor_after,
            candidates_examined: examined,
            rejected_by_availability,
            rejected_by_overlap,
            rejected_by_invariant_coverage,
            rejected_by_reserve,
            rejected_by_budget,
        },
        result: ValueSeekingResultV0 {
            state,
            witness: found,
        },
        evidence: ValueSeekingEvidenceV0 {
            finite_candidate_enumeration: CheckStatus::Checked,
            one_fault_availability: checked,
            honest_successor_overlap: checked,
            noncompensating_invariants: checked,
            distinct_typed_matching: checked,
            compatible_reserve: checked,
            cost_within_budget: checked,
            imagination_remains_external: CheckStatus::Checked,
            next_frontier,
        },
    })
}

fn candidate_from_ordinal(
    problem: &FormedProblemV0,
    ordinal: u64,
) -> Result<ValueCandidateV0, ProblemValueErrorV0> {
    if ordinal >= CANDIDATE_COUNT {
        return Err(invalid("value candidate ordinal exceeds the frozen space"));
    }
    let masks = 1_u64 << FEATURE_COUNT;
    let threshold_index =
        usize::try_from(ordinal / masks).map_err(|_| invalid("threshold index overflow"))?;
    let mask = ordinal % masks;
    let threshold = *problem
        .candidate_thresholds
        .get(threshold_index)
        .ok_or_else(|| invalid("candidate threshold is missing"))?;
    let features = ValueFeatureV0::ALL
        .into_iter()
        .enumerate()
        .filter_map(|(bit, feature)| (mask & (1_u64 << bit) != 0).then_some(feature))
        .collect();
    Ok(ValueCandidateV0 {
        ordinal,
        threshold,
        features,
    })
}

fn admit_candidate(
    problem: &FormedProblemV0,
    candidate: &ValueCandidateV0,
    resource: &ValueSeekingResourceV0,
) -> CandidateAdmissionV0 {
    let remaining_domains = problem.current_domain_count - problem.fault_budget;
    let quorums = combinations(problem.current_domain_count, candidate.threshold);
    let minimum_pair_intersection = minimum_distinct_intersection(&quorums);
    let honest_overlap = minimum_pair_intersection.saturating_sub(problem.fault_budget);
    let matching = first_typed_matching(&candidate.features, &problem.protected_invariants)
        .unwrap_or_default();
    let matched_resources = matching
        .iter()
        .map(|assignment| assignment.resource)
        .collect::<BTreeSet<_>>();
    let reserve = candidate.features.iter().copied().find(|feature| {
        !matched_resources.contains(feature)
            && problem.protected_invariants.contains(&feature.supports())
    });
    let total_cost = candidate
        .threshold
        .saturating_mul(resource.threshold_approval_cost)
        .saturating_add(
            u8::try_from(candidate.features.len())
                .unwrap_or(u8::MAX)
                .saturating_mul(resource.feature_cost),
        );
    let rejection = if candidate.threshold > remaining_domains {
        Some(RejectionV0::Availability)
    } else if honest_overlap == 0 {
        Some(RejectionV0::Overlap)
    } else if matching.len() != problem.protected_invariants.len() {
        Some(RejectionV0::InvariantCoverage)
    } else if reserve.is_none() {
        Some(RejectionV0::Reserve)
    } else if total_cost > resource.spacetime_cost_budget {
        Some(RejectionV0::Budget)
    } else {
        None
    };
    CandidateAdmissionV0 {
        admitted: rejection.is_none(),
        rejection,
        quorums,
        minimum_pair_intersection,
        honest_overlap,
        matching,
        reserve,
        total_cost,
    }
}

fn witness_from_admission(
    frontier: &ProblemValueFrontierV0,
    contract: &ValueSeekingContractV0,
    resource: &ValueSeekingResourceV0,
    candidate: &ValueCandidateV0,
    admission: &CandidateAdmissionV0,
) -> Result<TrustContinuationWitnessV0, ProblemValueErrorV0> {
    if !admission.admitted {
        return Err(invalid("cannot form a witness from a rejected candidate"));
    }
    let mut retained_vocabulary = frontier.problem.retained_vocabulary.clone();
    retained_vocabulary.extend(["value-seeking".to_owned(), "value".to_owned()]);
    Ok(TrustContinuationWitnessV0 {
        schema: TRUST_CONTINUATION_WITNESS_SCHEMA_V0.to_owned(),
        version: PROBLEM_VALUE_VERSION_V0,
        occurrence: key("experiment:0122:value:trust-continuation")?,
        problem_digest: frontier.problem.digest()?,
        contract_digest: contract.digest()?,
        resource_digest: resource.digest()?,
        candidate_ordinal: candidate.ordinal,
        selected_threshold: candidate.threshold,
        selected_features: candidate.features.clone(),
        successor_quorums: admission.quorums.clone(),
        minimum_pair_intersection: admission.minimum_pair_intersection,
        guaranteed_honest_overlap: admission.honest_overlap,
        remaining_domains_after_fault: frontier.problem.current_domain_count
            - frontier.problem.fault_budget,
        typed_matching: admission.matching.clone(),
        compatible_reserve: admission
            .reserve
            .ok_or_else(|| invalid("admitted candidate lost its reserve"))?,
        merge_capacity: u8::try_from(candidate.features.len())
            .map_err(|_| invalid("merge capacity overflow"))?,
        rupture_load: u8::try_from(frontier.problem.protected_invariants.len())
            .map_err(|_| invalid("rupture load overflow"))?,
        comparison: ContinuityComparisonV0::Greater,
        total_cost: admission.total_cost,
        retained_vocabulary,
        introduced_vocabulary: vec!["value-seeking".to_owned(), "value".to_owned()],
        external_residual: "arithmetic witnesses a policy shape only; actual independent custodians, signatures, availability, remeasurement, recovery, consent, and truth remain outside this run"
            .to_owned(),
    })
}

fn first_typed_matching(
    features: &[ValueFeatureV0],
    obligations: &[TrustInvariantV0],
) -> Option<Vec<ValueAssignmentV0>> {
    fn extend(
        features: &[ValueFeatureV0],
        obligations: &[TrustInvariantV0],
        cursor: usize,
        used: &mut BTreeSet<ValueFeatureV0>,
        assignments: &mut Vec<ValueAssignmentV0>,
    ) -> bool {
        if cursor == obligations.len() {
            return true;
        }
        let obligation = obligations[cursor];
        for feature in features.iter().copied() {
            if feature.supports() == obligation && used.insert(feature) {
                assignments.push(ValueAssignmentV0 {
                    obligation,
                    resource: feature,
                });
                if extend(features, obligations, cursor + 1, used, assignments) {
                    return true;
                }
                assignments.pop();
                used.remove(&feature);
            }
        }
        false
    }

    let mut used = BTreeSet::new();
    let mut assignments = Vec::new();
    extend(features, obligations, 0, &mut used, &mut assignments).then_some(assignments)
}

fn first_quorum_counterexample(
    domain_count: u8,
    threshold: u8,
    fault_budget: u8,
) -> Option<(QuorumCounterexampleV0, u64)> {
    if fault_budget != 1 {
        return None;
    }
    let quorums = combinations(domain_count, threshold);
    let mut examined = 0_u64;
    for (left_index, left) in quorums.iter().enumerate() {
        for right in quorums.iter().skip(left_index + 1) {
            let shared = intersection(left, right);
            for fault in 0..domain_count {
                examined += 1;
                let adversarial = vec![fault];
                let honest = difference(&shared, &adversarial);
                if honest.is_empty() {
                    return Some((
                        QuorumCounterexampleV0 {
                            left_receipts: left.clone(),
                            right_receipts: right.clone(),
                            shared_domains: shared,
                            adversarial_domains: adversarial,
                            honest_shared_domains: honest,
                        },
                        examined,
                    ));
                }
            }
        }
    }
    None
}

fn combinations(domain_count: u8, choose: u8) -> Vec<Vec<u8>> {
    fn visit(
        domain_count: u8,
        choose: usize,
        next: u8,
        current: &mut Vec<u8>,
        output: &mut Vec<Vec<u8>>,
    ) {
        if current.len() == choose {
            output.push(current.clone());
            return;
        }
        for value in next..domain_count {
            current.push(value);
            visit(domain_count, choose, value + 1, current, output);
            current.pop();
        }
    }

    if choose == 0 || choose > domain_count {
        return Vec::new();
    }
    let mut output = Vec::new();
    visit(
        domain_count,
        usize::from(choose),
        0,
        &mut Vec::new(),
        &mut output,
    );
    output
}

fn minimum_distinct_intersection(sets: &[Vec<u8>]) -> u8 {
    if sets.len() < 2 {
        return u8::try_from(sets.first().map_or(0, Vec::len)).unwrap_or(u8::MAX);
    }
    sets.iter()
        .enumerate()
        .flat_map(|(left_index, left)| {
            sets.iter()
                .skip(left_index + 1)
                .map(move |right| intersection(left, right).len())
        })
        .min()
        .and_then(|value| u8::try_from(value).ok())
        .unwrap_or(0)
}

fn intersection(left: &[u8], right: &[u8]) -> Vec<u8> {
    left.iter()
        .copied()
        .filter(|value| right.contains(value))
        .collect()
}

fn difference(left: &[u8], right: &[u8]) -> Vec<u8> {
    left.iter()
        .copied()
        .filter(|value| !right.contains(value))
        .collect()
}

fn ordered_unique_within(values: &[u8], upper: u8) -> bool {
    values.iter().all(|value| *value < upper) && values.windows(2).all(|pair| pair[0] < pair[1])
}

pub fn load_problem_awareness_v0(
    path: impl AsRef<Path>,
) -> Result<ProblemAwarenessV0, ProblemValueErrorV0> {
    load_checked(path, ProblemAwarenessV0::from_json)
}

pub fn load_problem_formation_contract_v0(
    path: impl AsRef<Path>,
) -> Result<ProblemFormationContractV0, ProblemValueErrorV0> {
    load_checked(path, ProblemFormationContractV0::from_json)
}

pub fn load_imagination_resource_v0(
    path: impl AsRef<Path>,
) -> Result<ImaginationResourceV0, ProblemValueErrorV0> {
    load_checked(path, ImaginationResourceV0::from_json)
}

pub fn load_problem_value_frontier_v0(
    path: impl AsRef<Path>,
) -> Result<ProblemValueFrontierV0, ProblemValueErrorV0> {
    load_checked(path, ProblemValueFrontierV0::from_json)
}

pub fn load_value_seeking_contract_v0(
    path: impl AsRef<Path>,
) -> Result<ValueSeekingContractV0, ProblemValueErrorV0> {
    load_checked(path, ValueSeekingContractV0::from_json)
}

pub fn load_value_seeking_resource_v0(
    path: impl AsRef<Path>,
) -> Result<ValueSeekingResourceV0, ProblemValueErrorV0> {
    load_checked(path, ValueSeekingResourceV0::from_json)
}

pub fn load_problem_formation_transition_v0(
    path: impl AsRef<Path>,
) -> Result<ProblemFormationTransitionV0, ProblemValueErrorV0> {
    load_checked(path, ProblemFormationTransitionV0::from_json)
}

pub fn load_value_seeking_transition_v0(
    path: impl AsRef<Path>,
) -> Result<ValueSeekingTransitionV0, ProblemValueErrorV0> {
    load_checked(path, ValueSeekingTransitionV0::from_json)
}

pub fn save_problem_formation_transition_v0(
    path: impl AsRef<Path>,
    transition: &ProblemFormationTransitionV0,
) -> Result<InquirySaveReceiptV0, ProblemValueErrorV0> {
    save_checked(path, transition.to_json()?)
}

pub fn save_problem_value_frontier_v0(
    path: impl AsRef<Path>,
    frontier: &ProblemValueFrontierV0,
) -> Result<InquirySaveReceiptV0, ProblemValueErrorV0> {
    save_checked(path, frontier.to_json()?)
}

pub fn save_value_seeking_transition_v0(
    path: impl AsRef<Path>,
    transition: &ValueSeekingTransitionV0,
) -> Result<InquirySaveReceiptV0, ProblemValueErrorV0> {
    save_checked(path, transition.to_json()?)
}

fn check_header(
    schema: &str,
    version: u32,
    expected_schema: &str,
    interface: &InquiryInterfaceV0,
) -> Result<(), ProblemValueErrorV0> {
    if schema != expected_schema
        || version != PROBLEM_VALUE_VERSION_V0
        || interface != &InquiryInterfaceV0::canonical()
        || interface.inputs != InputLabelV0::ALL
        || interface.outputs != OutputLabelV0::ALL
    {
        return Err(invalid(
            "unsupported problem/value schema, version, or three-port interface",
        ));
    }
    Ok(())
}

fn key(value: impl Into<String>) -> Result<ArtifactKeyV0, ProblemValueErrorV0> {
    ArtifactKeyV0::cache_label(value)
        .map_err(|error| ProblemValueErrorV0::InvalidArtifact(error.to_string()))
}

fn pretty_json<T: Serialize>(value: &T) -> Result<String, ProblemValueErrorV0> {
    serde_json::to_string_pretty(value)
        .map_err(|error| ProblemValueErrorV0::Json(error.to_string()))
}

fn check_digest(digest: &str) -> Result<(), ProblemValueErrorV0> {
    let Some(hex) = digest.strip_prefix("blake3:") else {
        return Err(invalid("a retained coordinate must use BLAKE3"));
    };
    if hex.len() != 64
        || !hex
            .bytes()
            .all(|byte| byte.is_ascii_digit() || (b'a'..=b'f').contains(&byte))
    {
        return Err(invalid("a retained coordinate is not lowercase BLAKE3"));
    }
    Ok(())
}

fn digest_serialized<T: Serialize>(value: &T) -> Result<String, ProblemValueErrorV0> {
    let encoded = format!("{}\n", pretty_json(value)?);
    Ok(format!(
        "blake3:{}",
        blake3::hash(encoded.as_bytes()).to_hex()
    ))
}

fn invalid(detail: impl Into<String>) -> ProblemValueErrorV0 {
    ProblemValueErrorV0::InvalidArtifact(detail.into())
}

fn load_checked<T>(
    path: impl AsRef<Path>,
    decode: impl FnOnce(&str) -> Result<T, ProblemValueErrorV0>,
) -> Result<T, ProblemValueErrorV0> {
    let path = path.as_ref();
    crate::persistence::require_adva_extension(path)
        .map_err(|error| ProblemValueErrorV0::Persistence(error.to_string()))?;
    let source = fs::read_to_string(path).map_err(|error| ProblemValueErrorV0::Io {
        path: path.to_path_buf(),
        detail: error.to_string(),
    })?;
    decode(&source)
}

fn save_checked(
    path: impl AsRef<Path>,
    json: String,
) -> Result<InquirySaveReceiptV0, ProblemValueErrorV0> {
    let path = path.as_ref();
    crate::persistence::require_adva_extension(path)
        .map_err(|error| ProblemValueErrorV0::Persistence(error.to_string()))?;
    let encoded = format!("{json}\n");
    crate::persistence::write_atomically(path, encoded.as_bytes())
        .map_err(|error| ProblemValueErrorV0::Persistence(error.to_string()))?;
    Ok(InquirySaveReceiptV0 {
        path: path.to_path_buf(),
        artifact_digest: format!("blake3:{}", blake3::hash(encoded.as_bytes()).to_hex()),
        bytes_written: u64::try_from(encoded.len()).unwrap_or(u64::MAX),
    })
}

#[derive(Debug, Error)]
pub enum ProblemValueErrorV0 {
    #[error("invalid problem/value artifact: {0}")]
    InvalidArtifact(String),
    #[error("problem/value JSON error: {0}")]
    Json(String),
    #[error("problem/value persistence error: {0}")]
    Persistence(String),
    #[error("problem/value I/O error at {path}: {detail}")]
    Io { path: PathBuf, detail: String },
}
