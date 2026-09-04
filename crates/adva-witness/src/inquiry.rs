use crate::{
    ArtifactKeyV0, InputLabelV0, MechanismV0, ObserverDomainV0, OutputLabelV0,
    TraceArithmeticCalibrationV0, TraceArithmeticErrorV0, TraceArithmeticQuestionKindV0,
    load_trace_arithmetic_v0,
};
use adva_ir::CheckStatus;
use serde::{Deserialize, Serialize};
use std::collections::BTreeSet;
use std::fs;
use std::path::{Path, PathBuf};
use thiserror::Error;

pub const INQUIRY_INTERFACE_SCHEMA_V0: &str = "adva.inquiry-interface.research";
pub const INQUIRY_FRONTIER_SCHEMA_V0: &str = "adva.inquiry-frontier.research";
pub const EXPLORATION_CONTRACT_SCHEMA_V0: &str = "adva.exploration-contract.research";
pub const RESOURCE_SNAPSHOT_SCHEMA_V0: &str = "adva.resource-snapshot.research";
pub const HYPOTHESIS_TRANSITION_SCHEMA_V0: &str = "adva.hypothesis-transition.research";
pub const INQUIRY_VERSION_V0: u32 = 0;

const FIRST_EXPLORATION_NAME: &str = "first:algorithm:recorded-resource-candidate";

/// The common boundary is deliberately smaller than any one artifact schema.
/// It fixes where a carrier comes from and goes to without identifying the
/// meanings stored in those positions.
#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct InquiryInterfaceV0 {
    pub schema: String,
    pub version: u32,
    pub inputs: [InputLabelV0; 3],
    pub outputs: [OutputLabelV0; 3],
}

impl InquiryInterfaceV0 {
    #[must_use]
    pub fn canonical() -> Self {
        Self {
            schema: INQUIRY_INTERFACE_SCHEMA_V0.to_owned(),
            version: INQUIRY_VERSION_V0,
            inputs: InputLabelV0::ALL,
            outputs: OutputLabelV0::ALL,
        }
    }
}

#[derive(Clone, Copy, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(tag = "kind", rename_all = "snake_case")]
pub enum TypedUnitV0 {
    CharacteristicWitness { target: ObserverDomainV0 },
    MultiplicativeIdentity,
    SharedTruthCoordinate,
}

#[derive(Clone, Copy, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum InquiryObligationStateV0 {
    Open,
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct InquiryObligationV0 {
    pub id: ArtifactKeyV0,
    pub kind: TraceArithmeticQuestionKindV0,
    pub typed_unit: TypedUnitV0,
    pub detail: String,
    pub state: InquiryObligationStateV0,
}

#[derive(Clone, Copy, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum VocabularyRoleV0 {
    Frontier,
    Hypothesis,
    Candidate,
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct VocabularyEntryV0 {
    pub local_name: String,
    pub role: VocabularyRoleV0,
    pub introduced_at: u64,
    pub definition: String,
}

#[derive(Clone, Copy, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum FrontierPauseReasonV0 {
    ExternalKnowledgeRequired,
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct FrontierLineageV0 {
    pub sequence: u64,
    pub parent_frontier_digest: Option<String>,
    pub algorithm_contract_digest: Option<String>,
    pub consumed_resource_digests: Vec<String>,
    pub retained_hypothesis_digests: Vec<String>,
}

/// A resumable finite boundary. The source calibration and its five question
/// coordinates remain embedded so a later observer need not trust a renamed
/// summary.
#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct InquiryFrontierV0 {
    pub schema: String,
    pub version: u32,
    pub interface: InquiryInterfaceV0,
    pub source_calibration_digest: String,
    pub source_calibration: TraceArithmeticCalibrationV0,
    pub obligations: Vec<InquiryObligationV0>,
    pub vocabulary: Vec<VocabularyEntryV0>,
    pub lineage: FrontierLineageV0,
    pub pause_reason: FrontierPauseReasonV0,
}

impl InquiryFrontierV0 {
    pub fn from_json(source: &str) -> Result<Self, InquiryErrorV0> {
        let artifact: Self = serde_json::from_str(source)
            .map_err(|error| InquiryErrorV0::Json(error.to_string()))?;
        artifact.check()?;
        Ok(artifact)
    }

    pub fn to_json(&self) -> Result<String, InquiryErrorV0> {
        self.check()?;
        serde_json::to_string_pretty(self).map_err(|error| InquiryErrorV0::Json(error.to_string()))
    }

    pub fn digest(&self) -> Result<String, InquiryErrorV0> {
        digest_checked_json(self.to_json()?)
    }

    pub fn check(&self) -> Result<(), InquiryErrorV0> {
        check_header(
            &self.schema,
            self.version,
            INQUIRY_FRONTIER_SCHEMA_V0,
            &self.interface,
        )?;
        self.source_calibration.check()?;
        let expected_calibration_digest = trace_calibration_digest(&self.source_calibration)?;
        if self.source_calibration_digest != expected_calibration_digest {
            return Err(InquiryErrorV0::InvalidArtifact(
                "the embedded calibration digest is stale or malformed",
            ));
        }
        if self.obligations != obligations_from_calibration(&self.source_calibration) {
            return Err(InquiryErrorV0::InvalidArtifact(
                "the inquiry obligations do not exactly retain the five arithmetic questions",
            ));
        }
        check_vocabulary(&self.vocabulary, self.lineage.sequence)?;
        check_digest_list(&self.lineage.consumed_resource_digests)?;
        check_digest_list(&self.lineage.retained_hypothesis_digests)?;
        if self.lineage.consumed_resource_digests.len()
            != self.lineage.retained_hypothesis_digests.len()
            || usize::try_from(self.lineage.sequence).ok()
                != Some(self.lineage.consumed_resource_digests.len())
        {
            return Err(InquiryErrorV0::InvalidArtifact(
                "the frontier sequence must count paired resource and hypothesis receipts",
            ));
        }
        if self.lineage.sequence == 0 {
            if self.lineage.parent_frontier_digest.is_some()
                || self.lineage.algorithm_contract_digest.is_some()
                || self.vocabulary != initial_vocabulary()
            {
                return Err(InquiryErrorV0::InvalidArtifact(
                    "the initial frontier has no parent, contract, or learned vocabulary",
                ));
            }
        } else {
            let parent = self.lineage.parent_frontier_digest.as_deref().ok_or(
                InquiryErrorV0::InvalidArtifact("a continued frontier must retain its parent"),
            )?;
            let contract = self.lineage.algorithm_contract_digest.as_deref().ok_or(
                InquiryErrorV0::InvalidArtifact(
                    "a continued frontier must freeze its algorithm contract",
                ),
            )?;
            check_digest(parent)?;
            check_digest(contract)?;
        }
        Ok(())
    }
}

#[derive(Clone, Copy, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum CandidateSelectionV0 {
    FirstRecordedCandidate,
}

#[derive(Clone, Copy, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum ExternalClaimPolicyV0 {
    ProposedOnly,
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct ExplorationContractV0 {
    pub schema: String,
    pub version: u32,
    pub interface: InquiryInterfaceV0,
    pub name: String,
    pub mechanism: MechanismV0,
    pub input_schemas: [String; 3],
    pub output_schema: String,
    pub selection: CandidateSelectionV0,
    pub external_claim_policy: ExternalClaimPolicyV0,
}

impl ExplorationContractV0 {
    #[must_use]
    pub fn first_calibration() -> Self {
        Self {
            schema: EXPLORATION_CONTRACT_SCHEMA_V0.to_owned(),
            version: INQUIRY_VERSION_V0,
            interface: InquiryInterfaceV0::canonical(),
            name: FIRST_EXPLORATION_NAME.to_owned(),
            mechanism: MechanismV0::Learn,
            input_schemas: [
                INQUIRY_FRONTIER_SCHEMA_V0.to_owned(),
                EXPLORATION_CONTRACT_SCHEMA_V0.to_owned(),
                RESOURCE_SNAPSHOT_SCHEMA_V0.to_owned(),
            ],
            output_schema: HYPOTHESIS_TRANSITION_SCHEMA_V0.to_owned(),
            selection: CandidateSelectionV0::FirstRecordedCandidate,
            external_claim_policy: ExternalClaimPolicyV0::ProposedOnly,
        }
    }

    pub fn from_json(source: &str) -> Result<Self, InquiryErrorV0> {
        let artifact: Self = serde_json::from_str(source)
            .map_err(|error| InquiryErrorV0::Json(error.to_string()))?;
        artifact.check()?;
        Ok(artifact)
    }

    pub fn to_json(&self) -> Result<String, InquiryErrorV0> {
        self.check()?;
        serde_json::to_string_pretty(self).map_err(|error| InquiryErrorV0::Json(error.to_string()))
    }

    pub fn digest(&self) -> Result<String, InquiryErrorV0> {
        digest_checked_json(self.to_json()?)
    }

    pub fn check(&self) -> Result<(), InquiryErrorV0> {
        if self != &Self::first_calibration() {
            return Err(InquiryErrorV0::InvalidArtifact(
                "the version-zero exploration contract is not the frozen first algorithm",
            ));
        }
        Ok(())
    }
}

#[derive(Clone, Copy, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum ResourceProvenanceV0 {
    UnauthenticatedExternalSession,
}

#[derive(Clone, Copy, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum EntropyReplayV0 {
    RecordedOutput,
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct EntropyReceiptV0 {
    pub source: String,
    pub value: String,
    pub replay: EntropyReplayV0,
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct HypothesisCandidateV0 {
    pub local_name: String,
    pub claim: String,
    pub addressed_obligations: Vec<ArtifactKeyV0>,
    pub assumptions: Vec<String>,
    pub required_observations: Vec<String>,
    pub falsifiers: Vec<String>,
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct ResourceSnapshotV0 {
    pub schema: String,
    pub version: u32,
    pub interface: InquiryInterfaceV0,
    pub resource_label: String,
    pub snapshot_coordinate: String,
    pub provenance: ResourceProvenanceV0,
    pub entropy: EntropyReceiptV0,
    pub candidates: Vec<HypothesisCandidateV0>,
}

impl ResourceSnapshotV0 {
    pub fn from_json(source: &str) -> Result<Self, InquiryErrorV0> {
        let artifact: Self = serde_json::from_str(source)
            .map_err(|error| InquiryErrorV0::Json(error.to_string()))?;
        artifact.check()?;
        Ok(artifact)
    }

    pub fn to_json(&self) -> Result<String, InquiryErrorV0> {
        self.check()?;
        serde_json::to_string_pretty(self).map_err(|error| InquiryErrorV0::Json(error.to_string()))
    }

    pub fn digest(&self) -> Result<String, InquiryErrorV0> {
        digest_checked_json(self.to_json()?)
    }

    pub fn check(&self) -> Result<(), InquiryErrorV0> {
        check_header(
            &self.schema,
            self.version,
            RESOURCE_SNAPSHOT_SCHEMA_V0,
            &self.interface,
        )?;
        if self.resource_label.trim().is_empty()
            || self.snapshot_coordinate.trim().is_empty()
            || self.entropy.source.trim().is_empty()
        {
            return Err(InquiryErrorV0::InvalidArtifact(
                "resource labels, coordinates, and entropy sources must be nonempty",
            ));
        }
        if self.entropy.value.len() != 64
            || !self
                .entropy
                .value
                .bytes()
                .all(|byte| byte.is_ascii_digit() || (b'a'..=b'f').contains(&byte))
        {
            return Err(InquiryErrorV0::InvalidArtifact(
                "the entropy receipt must retain exactly 32 lowercase hexadecimal bytes",
            ));
        }
        if self.candidates.is_empty() {
            return Err(InquiryErrorV0::InvalidArtifact(
                "a resource snapshot must contain at least one candidate",
            ));
        }
        let mut names = BTreeSet::new();
        let mut identities = BTreeSet::new();
        for candidate in &self.candidates {
            check_candidate(candidate)?;
            if !names.insert(&candidate.local_name)
                || !identities.insert(candidate_identity_digest(candidate)?)
            {
                return Err(InquiryErrorV0::InvalidArtifact(
                    "candidate names and name-independent content identities must be unique",
                ));
            }
        }
        Ok(())
    }
}

#[derive(Clone, Copy, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum HypothesisStateV0 {
    Proposed,
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct HypothesisV0 {
    pub identity_digest: String,
    pub local_name: String,
    pub state: HypothesisStateV0,
    pub claim: String,
    pub addressed_obligations: Vec<ArtifactKeyV0>,
    pub assumptions: Vec<String>,
    pub required_observations: Vec<String>,
    pub falsifiers: Vec<String>,
    pub parent_frontier_digest: String,
    pub resource_digest: String,
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct InquiryHistoryV0 {
    pub mechanism: MechanismV0,
    pub interface: InquiryInterfaceV0,
    pub subject_frontier_digest: String,
    pub method_contract_digest: String,
    pub object_resource_digest: String,
    pub selected_candidate_ordinal: u32,
    pub entropy: EntropyReceiptV0,
    pub introduced_words: Vec<String>,
    pub retained_obligations: Vec<ArtifactKeyV0>,
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct NextInquiryInputV0 {
    pub subject_frontier_digest: String,
    pub method_contract_digest: String,
    pub object_schema: String,
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct ContinuationEvidenceV0 {
    pub interface: InquiryInterfaceV0,
    pub all_obligations_retained: CheckStatus,
    pub external_content_not_truth: CheckStatus,
    pub candidate_copied_exactly: CheckStatus,
    pub interface_preserved: CheckStatus,
    pub next_frontier: InquiryFrontierV0,
    pub next_input: NextInquiryInputV0,
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct InquiryInputV0 {
    pub subject: InquiryFrontierV0,
    pub method: ExplorationContractV0,
    pub object: ResourceSnapshotV0,
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct InquiryOutputV0 {
    pub history: InquiryHistoryV0,
    pub result: HypothesisV0,
    pub evidence: ContinuationEvidenceV0,
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct HypothesisTransitionV0 {
    pub schema: String,
    pub version: u32,
    pub interface: InquiryInterfaceV0,
    pub input: InquiryInputV0,
    pub output: InquiryOutputV0,
}

impl HypothesisTransitionV0 {
    pub fn from_json(source: &str) -> Result<Self, InquiryErrorV0> {
        let artifact: Self = serde_json::from_str(source)
            .map_err(|error| InquiryErrorV0::Json(error.to_string()))?;
        artifact.check()?;
        Ok(artifact)
    }

    pub fn to_json(&self) -> Result<String, InquiryErrorV0> {
        self.check()?;
        serde_json::to_string_pretty(self).map_err(|error| InquiryErrorV0::Json(error.to_string()))
    }

    pub fn digest(&self) -> Result<String, InquiryErrorV0> {
        digest_checked_json(self.to_json()?)
    }

    pub fn check(&self) -> Result<(), InquiryErrorV0> {
        check_header(
            &self.schema,
            self.version,
            HYPOTHESIS_TRANSITION_SCHEMA_V0,
            &self.interface,
        )?;
        let expected =
            learn_hypothesis_v0(&self.input.subject, &self.input.method, &self.input.object)?;
        if self != &expected {
            return Err(InquiryErrorV0::InvalidArtifact(
                "the hypothesis transition is stale or has been edited after derivation",
            ));
        }
        Ok(())
    }
}

#[derive(Clone, Debug, Eq, PartialEq)]
pub struct InquirySaveReceiptV0 {
    pub path: PathBuf,
    pub artifact_digest: String,
    pub bytes_written: u64,
}

pub fn derive_inquiry_frontier_v0(
    calibration: &TraceArithmeticCalibrationV0,
) -> Result<InquiryFrontierV0, InquiryErrorV0> {
    calibration.check()?;
    let frontier = InquiryFrontierV0 {
        schema: INQUIRY_FRONTIER_SCHEMA_V0.to_owned(),
        version: INQUIRY_VERSION_V0,
        interface: InquiryInterfaceV0::canonical(),
        source_calibration_digest: trace_calibration_digest(calibration)?,
        source_calibration: calibration.clone(),
        obligations: obligations_from_calibration(calibration),
        vocabulary: initial_vocabulary(),
        lineage: FrontierLineageV0 {
            sequence: 0,
            parent_frontier_digest: None,
            algorithm_contract_digest: None,
            consumed_resource_digests: Vec::new(),
            retained_hypothesis_digests: Vec::new(),
        },
        pause_reason: FrontierPauseReasonV0::ExternalKnowledgeRequired,
    };
    frontier.check()?;
    Ok(frontier)
}

/// Run one bounded learning edge. This copies one candidate into a proposed
/// hypothesis, but closes no obligation and authenticates no external claim.
pub fn learn_hypothesis_v0(
    frontier: &InquiryFrontierV0,
    contract: &ExplorationContractV0,
    resource: &ResourceSnapshotV0,
) -> Result<HypothesisTransitionV0, InquiryErrorV0> {
    frontier.check()?;
    contract.check()?;
    resource.check()?;
    let subject_digest = frontier.digest()?;
    let method_digest = contract.digest()?;
    let object_digest = resource.digest()?;
    if let Some(expected) = &frontier.lineage.algorithm_contract_digest {
        if expected != &method_digest {
            return Err(InquiryErrorV0::AlgorithmDrift {
                expected: expected.clone(),
                actual: method_digest,
            });
        }
    }
    if frontier
        .lineage
        .consumed_resource_digests
        .contains(&object_digest)
    {
        return Err(InquiryErrorV0::ResourceReplay(object_digest));
    }
    let candidate = resource
        .candidates
        .first()
        .expect("a checked resource has a candidate");
    let obligation_ids = frontier
        .obligations
        .iter()
        .map(|obligation| obligation.id.clone())
        .collect::<Vec<_>>();
    if candidate.addressed_obligations != obligation_ids {
        return Err(InquiryErrorV0::ObligationMismatch);
    }
    let identity_digest = candidate_identity_digest(candidate)?;
    let result = HypothesisV0 {
        identity_digest: identity_digest.clone(),
        local_name: candidate.local_name.clone(),
        state: HypothesisStateV0::Proposed,
        claim: candidate.claim.clone(),
        addressed_obligations: candidate.addressed_obligations.clone(),
        assumptions: candidate.assumptions.clone(),
        required_observations: candidate.required_observations.clone(),
        falsifiers: candidate.falsifiers.clone(),
        parent_frontier_digest: subject_digest.clone(),
        resource_digest: object_digest.clone(),
    };
    let mut vocabulary = frontier.vocabulary.clone();
    insert_vocabulary(
        &mut vocabulary,
        VocabularyEntryV0 {
            local_name: "hypothesis".to_owned(),
            role: VocabularyRoleV0::Hypothesis,
            introduced_at: frontier.lineage.sequence + 1,
            definition:
                "an externally proposed, explicitly falsifiable result that closes no obligation"
                    .to_owned(),
        },
    )?;
    insert_vocabulary(
        &mut vocabulary,
        VocabularyEntryV0 {
            local_name: candidate.local_name.clone(),
            role: VocabularyRoleV0::Candidate,
            introduced_at: frontier.lineage.sequence + 1,
            definition: candidate.claim.clone(),
        },
    )?;
    let mut consumed = frontier.lineage.consumed_resource_digests.clone();
    consumed.push(object_digest.clone());
    let mut retained = frontier.lineage.retained_hypothesis_digests.clone();
    retained.push(identity_digest);
    let next_frontier = InquiryFrontierV0 {
        schema: INQUIRY_FRONTIER_SCHEMA_V0.to_owned(),
        version: INQUIRY_VERSION_V0,
        interface: InquiryInterfaceV0::canonical(),
        source_calibration_digest: frontier.source_calibration_digest.clone(),
        source_calibration: frontier.source_calibration.clone(),
        obligations: frontier.obligations.clone(),
        vocabulary,
        lineage: FrontierLineageV0 {
            sequence: frontier.lineage.sequence + 1,
            parent_frontier_digest: Some(subject_digest.clone()),
            algorithm_contract_digest: Some(method_digest.clone()),
            consumed_resource_digests: consumed,
            retained_hypothesis_digests: retained,
        },
        pause_reason: FrontierPauseReasonV0::ExternalKnowledgeRequired,
    };
    next_frontier.check()?;
    let next_frontier_digest = next_frontier.digest()?;
    let history = InquiryHistoryV0 {
        mechanism: MechanismV0::Learn,
        interface: InquiryInterfaceV0::canonical(),
        subject_frontier_digest: subject_digest,
        method_contract_digest: method_digest.clone(),
        object_resource_digest: object_digest,
        selected_candidate_ordinal: 0,
        entropy: resource.entropy.clone(),
        introduced_words: vec!["hypothesis".to_owned(), candidate.local_name.clone()],
        retained_obligations: obligation_ids,
    };
    Ok(HypothesisTransitionV0 {
        schema: HYPOTHESIS_TRANSITION_SCHEMA_V0.to_owned(),
        version: INQUIRY_VERSION_V0,
        interface: InquiryInterfaceV0::canonical(),
        input: InquiryInputV0 {
            subject: frontier.clone(),
            method: contract.clone(),
            object: resource.clone(),
        },
        output: InquiryOutputV0 {
            history,
            result,
            evidence: ContinuationEvidenceV0 {
                interface: InquiryInterfaceV0::canonical(),
                all_obligations_retained: CheckStatus::Checked,
                external_content_not_truth: CheckStatus::Checked,
                candidate_copied_exactly: CheckStatus::Checked,
                interface_preserved: CheckStatus::Checked,
                next_frontier,
                next_input: NextInquiryInputV0 {
                    subject_frontier_digest: next_frontier_digest,
                    method_contract_digest: method_digest,
                    object_schema: RESOURCE_SNAPSHOT_SCHEMA_V0.to_owned(),
                },
            },
        },
    })
}

pub fn load_inquiry_frontier_v0(
    path: impl AsRef<Path>,
) -> Result<InquiryFrontierV0, InquiryErrorV0> {
    load_checked(path, InquiryFrontierV0::from_json)
}

pub fn load_exploration_contract_v0(
    path: impl AsRef<Path>,
) -> Result<ExplorationContractV0, InquiryErrorV0> {
    load_checked(path, ExplorationContractV0::from_json)
}

pub fn load_resource_snapshot_v0(
    path: impl AsRef<Path>,
) -> Result<ResourceSnapshotV0, InquiryErrorV0> {
    load_checked(path, ResourceSnapshotV0::from_json)
}

pub fn load_hypothesis_transition_v0(
    path: impl AsRef<Path>,
) -> Result<HypothesisTransitionV0, InquiryErrorV0> {
    load_checked(path, HypothesisTransitionV0::from_json)
}

pub fn save_inquiry_frontier_v0(
    path: impl AsRef<Path>,
    frontier: &InquiryFrontierV0,
) -> Result<InquirySaveReceiptV0, InquiryErrorV0> {
    save_checked(path, frontier.to_json()?)
}

pub fn save_hypothesis_transition_v0(
    path: impl AsRef<Path>,
    transition: &HypothesisTransitionV0,
) -> Result<InquirySaveReceiptV0, InquiryErrorV0> {
    save_checked(path, transition.to_json()?)
}

pub fn derive_inquiry_frontier_from_file_v0(
    path: impl AsRef<Path>,
) -> Result<InquiryFrontierV0, InquiryErrorV0> {
    derive_inquiry_frontier_v0(&load_trace_arithmetic_v0(path)?)
}

fn obligations_from_calibration(
    calibration: &TraceArithmeticCalibrationV0,
) -> Vec<InquiryObligationV0> {
    calibration
        .questions
        .iter()
        .map(|question| InquiryObligationV0 {
            id: question.residual.clone(),
            kind: question.kind,
            typed_unit: match question.kind {
                TraceArithmeticQuestionKindV0::TimeCharacteristic => {
                    TypedUnitV0::CharacteristicWitness {
                        target: ObserverDomainV0::Time,
                    }
                }
                TraceArithmeticQuestionKindV0::SpaceCharacteristic => {
                    TypedUnitV0::CharacteristicWitness {
                        target: ObserverDomainV0::Space,
                    }
                }
                TraceArithmeticQuestionKindV0::ConstructionCharacteristic => {
                    TypedUnitV0::CharacteristicWitness {
                        target: ObserverDomainV0::Construction,
                    }
                }
                TraceArithmeticQuestionKindV0::MultiplicativeHolonomy => {
                    TypedUnitV0::MultiplicativeIdentity
                }
                TraceArithmeticQuestionKindV0::CommonTruthCoordinate => {
                    TypedUnitV0::SharedTruthCoordinate
                }
            },
            detail: question.detail.clone(),
            state: InquiryObligationStateV0::Open,
        })
        .collect()
}

fn initial_vocabulary() -> Vec<VocabularyEntryV0> {
    vec![VocabularyEntryV0 {
        local_name: "frontier".to_owned(),
        role: VocabularyRoleV0::Frontier,
        introduced_at: 0,
        definition: "a resumable boundary retaining open obligations and continuation lineage"
            .to_owned(),
    }]
}

fn check_vocabulary(vocabulary: &[VocabularyEntryV0], sequence: u64) -> Result<(), InquiryErrorV0> {
    if vocabulary.is_empty() {
        return Err(InquiryErrorV0::InvalidArtifact(
            "a frontier must retain its vocabulary",
        ));
    }
    let mut names = BTreeSet::new();
    for entry in vocabulary {
        if entry.local_name.trim().is_empty()
            || entry.definition.trim().is_empty()
            || entry.introduced_at > sequence
            || !names.insert(&entry.local_name)
        {
            return Err(InquiryErrorV0::InvalidArtifact(
                "frontier vocabulary entries must be nonempty, unique, and historically placed",
            ));
        }
    }
    if vocabulary[0] != initial_vocabulary()[0] {
        return Err(InquiryErrorV0::InvalidArtifact(
            "frontier must remain the first vocabulary coordinate",
        ));
    }
    Ok(())
}

fn insert_vocabulary(
    vocabulary: &mut Vec<VocabularyEntryV0>,
    entry: VocabularyEntryV0,
) -> Result<(), InquiryErrorV0> {
    if let Some(existing) = vocabulary
        .iter()
        .find(|existing| existing.local_name == entry.local_name)
    {
        if existing.role != entry.role || existing.definition != entry.definition {
            return Err(InquiryErrorV0::VocabularyDrift(entry.local_name));
        }
    } else {
        vocabulary.push(entry);
    }
    Ok(())
}

fn check_candidate(candidate: &HypothesisCandidateV0) -> Result<(), InquiryErrorV0> {
    if candidate.local_name.trim().is_empty()
        || candidate.claim.trim().is_empty()
        || candidate.addressed_obligations.is_empty()
        || candidate.assumptions.is_empty()
        || candidate.required_observations.is_empty()
        || candidate.falsifiers.is_empty()
        || candidate
            .assumptions
            .iter()
            .chain(&candidate.required_observations)
            .chain(&candidate.falsifiers)
            .any(|value| value.trim().is_empty())
    {
        return Err(InquiryErrorV0::InvalidArtifact(
            "a candidate needs a name, claim, obligations, assumptions, observations, and falsifiers",
        ));
    }
    let ids = candidate
        .addressed_obligations
        .iter()
        .map(ArtifactKeyV0::as_str)
        .collect::<BTreeSet<_>>();
    if ids.len() != candidate.addressed_obligations.len() || ids.contains("") {
        return Err(InquiryErrorV0::InvalidArtifact(
            "candidate obligation coordinates must be nonempty and unique",
        ));
    }
    Ok(())
}

#[derive(Serialize)]
struct CandidateIdentity<'a> {
    claim: &'a str,
    addressed_obligations: &'a [ArtifactKeyV0],
    assumptions: &'a [String],
    required_observations: &'a [String],
    falsifiers: &'a [String],
}

fn candidate_identity_digest(candidate: &HypothesisCandidateV0) -> Result<String, InquiryErrorV0> {
    let identity = CandidateIdentity {
        claim: &candidate.claim,
        addressed_obligations: &candidate.addressed_obligations,
        assumptions: &candidate.assumptions,
        required_observations: &candidate.required_observations,
        falsifiers: &candidate.falsifiers,
    };
    let canonical =
        serde_json::to_vec(&identity).map_err(|error| InquiryErrorV0::Json(error.to_string()))?;
    Ok(format!("blake3:{}", blake3::hash(&canonical).to_hex()))
}

fn trace_calibration_digest(
    calibration: &TraceArithmeticCalibrationV0,
) -> Result<String, InquiryErrorV0> {
    digest_checked_json(calibration.to_json()?)
}

fn digest_checked_json(json: String) -> Result<String, InquiryErrorV0> {
    let encoded = format!("{json}\n");
    Ok(format!(
        "blake3:{}",
        blake3::hash(encoded.as_bytes()).to_hex()
    ))
}

fn check_header(
    schema: &str,
    version: u32,
    expected_schema: &str,
    interface: &InquiryInterfaceV0,
) -> Result<(), InquiryErrorV0> {
    if schema != expected_schema
        || version != INQUIRY_VERSION_V0
        || interface != &InquiryInterfaceV0::canonical()
    {
        return Err(InquiryErrorV0::InvalidArtifact(
            "unsupported inquiry schema, version, or three-port interface",
        ));
    }
    Ok(())
}

fn check_digest_list(digests: &[String]) -> Result<(), InquiryErrorV0> {
    let mut unique = BTreeSet::new();
    for digest in digests {
        check_digest(digest)?;
        if !unique.insert(digest) {
            return Err(InquiryErrorV0::InvalidArtifact(
                "lineage digests must be unique",
            ));
        }
    }
    Ok(())
}

fn check_digest(digest: &str) -> Result<(), InquiryErrorV0> {
    let Some(hex) = digest.strip_prefix("blake3:") else {
        return Err(InquiryErrorV0::InvalidArtifact(
            "an inquiry digest must be a BLAKE3 coordinate",
        ));
    };
    if hex.len() != 64
        || !hex
            .bytes()
            .all(|byte| byte.is_ascii_digit() || (b'a'..=b'f').contains(&byte))
    {
        return Err(InquiryErrorV0::InvalidArtifact(
            "an inquiry digest must be a lowercase BLAKE3 coordinate",
        ));
    }
    Ok(())
}

fn load_checked<T>(
    path: impl AsRef<Path>,
    decode: impl FnOnce(&str) -> Result<T, InquiryErrorV0>,
) -> Result<T, InquiryErrorV0> {
    let path = path.as_ref();
    crate::persistence::require_adva_extension(path)
        .map_err(|error| InquiryErrorV0::Persistence(error.to_string()))?;
    let source = fs::read_to_string(path).map_err(|error| InquiryErrorV0::Io {
        path: path.to_path_buf(),
        detail: error.to_string(),
    })?;
    decode(&source)
}

fn save_checked(
    path: impl AsRef<Path>,
    json: String,
) -> Result<InquirySaveReceiptV0, InquiryErrorV0> {
    let path = path.as_ref();
    crate::persistence::require_adva_extension(path)
        .map_err(|error| InquiryErrorV0::Persistence(error.to_string()))?;
    let encoded = format!("{json}\n");
    crate::persistence::write_atomically(path, encoded.as_bytes())
        .map_err(|error| InquiryErrorV0::Persistence(error.to_string()))?;
    Ok(InquirySaveReceiptV0 {
        path: path.to_path_buf(),
        artifact_digest: format!("blake3:{}", blake3::hash(encoded.as_bytes()).to_hex()),
        bytes_written: u64::try_from(encoded.len()).unwrap_or(u64::MAX),
    })
}

#[derive(Clone, Debug, Eq, Error, PartialEq)]
pub enum InquiryErrorV0 {
    #[error("invalid inquiry artifact: {0}")]
    InvalidArtifact(&'static str),
    #[error("algorithm contract drift: expected {expected}, received {actual}")]
    AlgorithmDrift { expected: String, actual: String },
    #[error("resource snapshot has already been consumed: {0}")]
    ResourceReplay(String),
    #[error("the selected candidate does not address the frontier obligations in exact order")]
    ObligationMismatch,
    #[error("vocabulary meaning drift for local name {0:?}")]
    VocabularyDrift(String),
    #[error("inquiry JSON error: {0}")]
    Json(String),
    #[error("inquiry persistence error: {0}")]
    Persistence(String),
    #[error("I/O error at {path:?}: {detail}")]
    Io { path: PathBuf, detail: String },
    #[error(transparent)]
    TraceArithmetic(#[from] TraceArithmeticErrorV0),
}
