use crate::{
    ArtifactKeyV0, InputLabelV0, InquiryErrorV0, InquiryFrontierV0, InquiryInterfaceV0,
    InquirySaveReceiptV0, MechanismV0, ObserverDomainV0, OutputLabelV0, TypedUnitV0,
};
use adva_ir::CheckStatus;
use serde::{Deserialize, Serialize};
use std::collections::{BTreeMap, BTreeSet};
use std::fs;
use std::path::{Path, PathBuf};
use thiserror::Error;

pub const VERIFICATION_CONTRACT_SCHEMA_V0: &str = "adva.verification-contract.research";
pub const VERIFICATION_PACKET_SCHEMA_V0: &str = "adva.verification-packet.research";
pub const VERIFICATION_FRONTIER_SCHEMA_V0: &str = "adva.verification-frontier.research";
pub const VERIFICATION_TRANSITION_SCHEMA_V0: &str = "adva.verification-transition.research";
pub const VERIFICATION_VERSION_V0: u32 = 0;

const FIRST_VERIFICATION_NAME: &str = "first:verifier:refinement-without-discharge";

#[derive(Clone, Copy, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum DischargePolicyV0 {
    TypedPredicateRequiredButUnavailable,
}

/// The verifier is a persistent method carrier. Its digest, rather than the
/// currently installed CLI binary, fixes the interpretation of one edge.
#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct VerificationContractV0 {
    pub schema: String,
    pub version: u32,
    pub interface: InquiryInterfaceV0,
    pub name: String,
    pub mechanism: MechanismV0,
    pub accepted_subject_schemas: [String; 2],
    pub object_schema: String,
    pub output_schema: String,
    pub discharge_policy: DischargePolicyV0,
}

impl VerificationContractV0 {
    #[must_use]
    pub fn first_refinement() -> Self {
        Self {
            schema: VERIFICATION_CONTRACT_SCHEMA_V0.to_owned(),
            version: VERIFICATION_VERSION_V0,
            interface: InquiryInterfaceV0::canonical(),
            name: FIRST_VERIFICATION_NAME.to_owned(),
            mechanism: MechanismV0::Verify,
            accepted_subject_schemas: [
                crate::INQUIRY_FRONTIER_SCHEMA_V0.to_owned(),
                VERIFICATION_FRONTIER_SCHEMA_V0.to_owned(),
            ],
            object_schema: VERIFICATION_PACKET_SCHEMA_V0.to_owned(),
            output_schema: VERIFICATION_TRANSITION_SCHEMA_V0.to_owned(),
            discharge_policy: DischargePolicyV0::TypedPredicateRequiredButUnavailable,
        }
    }

    pub fn from_json(source: &str) -> Result<Self, VerificationErrorV0> {
        let artifact: Self = serde_json::from_str(source)
            .map_err(|error| VerificationErrorV0::Json(error.to_string()))?;
        artifact.check()?;
        Ok(artifact)
    }

    pub fn to_json(&self) -> Result<String, VerificationErrorV0> {
        self.check()?;
        pretty_json(self)
    }

    pub fn digest(&self) -> Result<String, VerificationErrorV0> {
        digest_json(self.to_json()?)
    }

    pub fn check(&self) -> Result<(), VerificationErrorV0> {
        if self != &Self::first_refinement() {
            return Err(VerificationErrorV0::InvalidArtifact(
                "the version-zero verification contract is not the frozen first verifier",
            ));
        }
        Ok(())
    }
}

#[derive(Clone, Copy, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(tag = "kind", rename_all = "snake_case")]
pub enum VerificationUnitV0 {
    CharacteristicWitness { target: ObserverDomainV0 },
    MultiplicativeIdentity,
    SharedTruthCoordinate,
    ExternalCoordinate,
    IndependentMeasurement,
    OrderedHolonomyReplay,
    SharedCoordinateTransport,
    CustodyRecovery,
}

impl From<TypedUnitV0> for VerificationUnitV0 {
    fn from(value: TypedUnitV0) -> Self {
        match value {
            TypedUnitV0::CharacteristicWitness { target } => Self::CharacteristicWitness { target },
            TypedUnitV0::MultiplicativeIdentity => Self::MultiplicativeIdentity,
            TypedUnitV0::SharedTruthCoordinate => Self::SharedTruthCoordinate,
        }
    }
}

#[derive(Clone, Copy, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum VerificationObligationRoleV0 {
    SemanticClosure,
    Custody,
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(tag = "state", rename_all = "snake_case")]
pub enum VerificationObligationStateV0 {
    Open,
    Refined {
        children: Vec<ArtifactKeyV0>,
        basis_digest: String,
    },
    Discharged {
        witness_digest: String,
        verifier_digest: String,
        scope_digest: String,
    },
    Reopened {
        prior_witness_digest: String,
        counterevidence_digest: String,
    },
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct VerificationObligationV0 {
    pub id: ArtifactKeyV0,
    pub role: VerificationObligationRoleV0,
    pub unit: VerificationUnitV0,
    pub detail: String,
    pub parents: Vec<ArtifactKeyV0>,
    pub introduced_at: u64,
    pub state: VerificationObligationStateV0,
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct RefinementObligationV0 {
    pub id: ArtifactKeyV0,
    pub role: VerificationObligationRoleV0,
    pub unit: VerificationUnitV0,
    pub detail: String,
    pub parents: Vec<ArtifactKeyV0>,
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct UnresolvedForkV0 {
    pub id: ArtifactKeyV0,
    pub left_digest: String,
    pub right_digest: String,
    pub detail: String,
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(tag = "action", rename_all = "snake_case")]
pub enum VerificationActionV0 {
    Refine {
        children: Vec<RefinementObligationV0>,
    },
    Discharge {
        obligation_id: ArtifactKeyV0,
        witness_digest: String,
        scope_digest: String,
    },
    Reopen {
        obligation_id: ArtifactKeyV0,
        prior_witness_digest: String,
        counterevidence_digest: String,
    },
    RegisterFork {
        fork: UnresolvedForkV0,
    },
}

/// An object carrier asks the fixed verifier to update a finite obligation
/// boundary. A packet may request discharge, but version zero records a
/// refusal because it has no typed semantic predicate for doing so.
#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct VerificationPacketV0 {
    pub schema: String,
    pub version: u32,
    pub interface: InquiryInterfaceV0,
    pub packet_coordinate: String,
    pub basis_hypothesis_digest: String,
    pub actions: Vec<VerificationActionV0>,
}

impl VerificationPacketV0 {
    pub fn from_json(source: &str) -> Result<Self, VerificationErrorV0> {
        let artifact: Self = serde_json::from_str(source)
            .map_err(|error| VerificationErrorV0::Json(error.to_string()))?;
        artifact.check()?;
        Ok(artifact)
    }

    pub fn to_json(&self) -> Result<String, VerificationErrorV0> {
        self.check()?;
        pretty_json(self)
    }

    pub fn digest(&self) -> Result<String, VerificationErrorV0> {
        digest_json(self.to_json()?)
    }

    pub fn check(&self) -> Result<(), VerificationErrorV0> {
        check_header(
            &self.schema,
            self.version,
            VERIFICATION_PACKET_SCHEMA_V0,
            &self.interface,
        )?;
        if self.packet_coordinate.trim().is_empty() || self.actions.is_empty() {
            return Err(VerificationErrorV0::InvalidArtifact(
                "a verification packet needs a coordinate and at least one action",
            ));
        }
        check_digest(&self.basis_hypothesis_digest)?;
        let mut introduced = BTreeSet::new();
        let mut acted = BTreeSet::new();
        let mut forks = BTreeSet::new();
        for action in &self.actions {
            match action {
                VerificationActionV0::Refine { children } => {
                    if children.is_empty() {
                        return Err(VerificationErrorV0::InvalidArtifact(
                            "a refinement action must introduce at least one obligation",
                        ));
                    }
                    for child in children {
                        check_refinement_child(child)?;
                        if !introduced.insert(child.id.as_str()) {
                            return Err(VerificationErrorV0::InvalidArtifact(
                                "refinement child identifiers must be unique within a packet",
                            ));
                        }
                    }
                }
                VerificationActionV0::Discharge {
                    obligation_id,
                    witness_digest,
                    scope_digest,
                } => {
                    if !acted.insert(obligation_id.as_str()) {
                        return Err(VerificationErrorV0::InvalidArtifact(
                            "one packet cannot act twice on the same obligation",
                        ));
                    }
                    check_digest(witness_digest)?;
                    check_digest(scope_digest)?;
                }
                VerificationActionV0::Reopen {
                    obligation_id,
                    prior_witness_digest,
                    counterevidence_digest,
                } => {
                    if !acted.insert(obligation_id.as_str()) {
                        return Err(VerificationErrorV0::InvalidArtifact(
                            "one packet cannot act twice on the same obligation",
                        ));
                    }
                    check_digest(prior_witness_digest)?;
                    check_digest(counterevidence_digest)?;
                }
                VerificationActionV0::RegisterFork { fork } => {
                    check_fork(fork)?;
                    if !forks.insert(fork.id.as_str()) {
                        return Err(VerificationErrorV0::InvalidArtifact(
                            "fork identifiers must be unique within a packet",
                        ));
                    }
                }
            }
        }
        Ok(())
    }
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(tag = "kind", content = "artifact", rename_all = "snake_case")]
pub enum VerificationSubjectV0 {
    InquiryFrontier(Box<InquiryFrontierV0>),
    VerificationFrontier(Box<VerificationFrontierV0>),
}

impl VerificationSubjectV0 {
    fn check(&self) -> Result<(), VerificationErrorV0> {
        match self {
            Self::InquiryFrontier(frontier) => frontier.check().map_err(Into::into),
            Self::VerificationFrontier(frontier) => frontier.check(),
        }
    }

    fn digest(&self) -> Result<String, VerificationErrorV0> {
        match self {
            Self::InquiryFrontier(frontier) => Ok(frontier.digest()?),
            Self::VerificationFrontier(frontier) => frontier.digest(),
        }
    }
}

#[derive(Clone, Copy, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum VerificationFrontierStateV0 {
    Open,
    ScopedClosed,
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct VerificationLineageV0 {
    pub sequence: u64,
    pub parent_subject_digest: String,
    pub method_contract_digest: String,
    pub consumed_packet_digests: Vec<String>,
}

/// A new layer over an immutable inquiry frontier. The embedded origin makes
/// every root coordinate independently checkable without rewriting its v0
/// bytes or digest.
#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct VerificationFrontierV0 {
    pub schema: String,
    pub version: u32,
    pub interface: InquiryInterfaceV0,
    pub origin_inquiry_frontier_digest: String,
    pub origin_inquiry_frontier: InquiryFrontierV0,
    pub obligations: Vec<VerificationObligationV0>,
    pub unresolved_forks: Vec<UnresolvedForkV0>,
    pub lineage: VerificationLineageV0,
    pub state: VerificationFrontierStateV0,
}

impl VerificationFrontierV0 {
    pub fn from_json(source: &str) -> Result<Self, VerificationErrorV0> {
        let artifact: Self = serde_json::from_str(source)
            .map_err(|error| VerificationErrorV0::Json(error.to_string()))?;
        artifact.check()?;
        Ok(artifact)
    }

    pub fn to_json(&self) -> Result<String, VerificationErrorV0> {
        self.check()?;
        pretty_json(self)
    }

    pub fn digest(&self) -> Result<String, VerificationErrorV0> {
        digest_json(self.to_json()?)
    }

    pub fn open_semantic_leaves(&self) -> usize {
        self.obligations
            .iter()
            .filter(|obligation| {
                obligation.role == VerificationObligationRoleV0::SemanticClosure
                    && is_open_leaf(&obligation.state)
            })
            .count()
    }

    pub fn open_custody_leaves(&self) -> usize {
        self.obligations
            .iter()
            .filter(|obligation| {
                obligation.role == VerificationObligationRoleV0::Custody
                    && is_open_leaf(&obligation.state)
            })
            .count()
    }

    pub fn check(&self) -> Result<(), VerificationErrorV0> {
        check_header(
            &self.schema,
            self.version,
            VERIFICATION_FRONTIER_SCHEMA_V0,
            &self.interface,
        )?;
        self.origin_inquiry_frontier.check()?;
        if self.origin_inquiry_frontier_digest != self.origin_inquiry_frontier.digest()? {
            return Err(VerificationErrorV0::InvalidArtifact(
                "the embedded origin inquiry frontier digest is stale",
            ));
        }
        if self.lineage.sequence == 0
            || usize::try_from(self.lineage.sequence).ok()
                != Some(self.lineage.consumed_packet_digests.len())
        {
            return Err(VerificationErrorV0::InvalidArtifact(
                "verification lineage must count every consumed packet",
            ));
        }
        check_digest(&self.lineage.parent_subject_digest)?;
        check_digest(&self.lineage.method_contract_digest)?;
        check_digest_list(&self.lineage.consumed_packet_digests)?;
        check_obligation_graph(self)?;
        let mut fork_ids = BTreeSet::new();
        for fork in &self.unresolved_forks {
            check_fork(fork)?;
            if !fork_ids.insert(fork.id.as_str()) {
                return Err(VerificationErrorV0::InvalidArtifact(
                    "unresolved fork identifiers must be unique",
                ));
            }
        }
        if self.state != derived_frontier_state(self) {
            return Err(VerificationErrorV0::InvalidArtifact(
                "verification frontier state does not match its open leaves and forks",
            ));
        }
        Ok(())
    }
}

#[derive(Clone, Copy, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum VerificationDecisionV0 {
    Refined,
    Reopened,
    ForkRecorded,
    Rejected,
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct VerificationActionOutcomeV0 {
    pub action_ordinal: u32,
    pub decision: VerificationDecisionV0,
    pub obligations: Vec<ArtifactKeyV0>,
    pub detail: String,
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct VerificationLeafDeltaV0 {
    pub semantic_before: u32,
    pub semantic_after: u32,
    pub custody_before: u32,
    pub custody_after: u32,
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct VerificationHistoryV0 {
    pub mechanism: MechanismV0,
    pub interface: InquiryInterfaceV0,
    pub subject_digest: String,
    pub method_contract_digest: String,
    pub object_packet_digest: String,
    pub outcomes: Vec<VerificationActionOutcomeV0>,
    pub leaf_delta: VerificationLeafDeltaV0,
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct ScopedCertificateV0 {
    pub scope_digest: String,
    pub verifier_digest: String,
    pub witness_digests: Vec<String>,
    pub statement: String,
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct VerificationResultV0 {
    pub state: VerificationFrontierStateV0,
    pub open_semantic_leaves: u32,
    pub open_custody_leaves: u32,
    pub unresolved_forks: u32,
    pub certificate: Option<ScopedCertificateV0>,
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct NextVerificationInputV0 {
    pub subject_frontier_digest: String,
    pub method_contract_digest: String,
    pub object_schema: String,
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct VerificationEvidenceV0 {
    pub interface: InquiryInterfaceV0,
    pub origin_unchanged: CheckStatus,
    pub method_content_addressed: CheckStatus,
    pub unsupported_discharge_refused: CheckStatus,
    pub interface_preserved: CheckStatus,
    pub residual_frontier: VerificationFrontierV0,
    pub next_input: NextVerificationInputV0,
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct VerificationInputV0 {
    pub subject: VerificationSubjectV0,
    pub method: VerificationContractV0,
    pub object: VerificationPacketV0,
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct VerificationOutputV0 {
    pub history: VerificationHistoryV0,
    pub result: VerificationResultV0,
    pub evidence: VerificationEvidenceV0,
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct VerificationTransitionV0 {
    pub schema: String,
    pub version: u32,
    pub interface: InquiryInterfaceV0,
    pub input: VerificationInputV0,
    pub output: VerificationOutputV0,
}

impl VerificationTransitionV0 {
    pub fn from_json(source: &str) -> Result<Self, VerificationErrorV0> {
        let artifact: Self = serde_json::from_str(source)
            .map_err(|error| VerificationErrorV0::Json(error.to_string()))?;
        artifact.check()?;
        Ok(artifact)
    }

    pub fn to_json(&self) -> Result<String, VerificationErrorV0> {
        self.check()?;
        pretty_json(self)
    }

    pub fn digest(&self) -> Result<String, VerificationErrorV0> {
        digest_json(self.to_json()?)
    }

    pub fn check(&self) -> Result<(), VerificationErrorV0> {
        check_header(
            &self.schema,
            self.version,
            VERIFICATION_TRANSITION_SCHEMA_V0,
            &self.interface,
        )?;
        let expected =
            verify_obligations_v0(&self.input.subject, &self.input.method, &self.input.object)?;
        if self != &expected {
            return Err(VerificationErrorV0::InvalidArtifact(
                "the verification transition is stale or was edited after derivation",
            ));
        }
        Ok(())
    }
}

/// Apply one bounded verification edge. Refinement and reopening are state
/// changes; an unsupported discharge request is retained as a rejected
/// outcome, never promoted to a certificate.
pub fn verify_obligations_v0(
    subject: &VerificationSubjectV0,
    contract: &VerificationContractV0,
    packet: &VerificationPacketV0,
) -> Result<VerificationTransitionV0, VerificationErrorV0> {
    subject.check()?;
    contract.check()?;
    packet.check()?;
    let subject_digest = subject.digest()?;
    let method_digest = contract.digest()?;
    let object_digest = packet.digest()?;
    let mut frontier = seed_or_continue_frontier(subject, &method_digest)?;
    if !frontier
        .origin_inquiry_frontier
        .lineage
        .retained_hypothesis_digests
        .contains(&packet.basis_hypothesis_digest)
    {
        return Err(VerificationErrorV0::UnknownBasis(
            packet.basis_hypothesis_digest.clone(),
        ));
    }
    if frontier
        .lineage
        .consumed_packet_digests
        .contains(&object_digest)
    {
        return Err(VerificationErrorV0::PacketReplay(object_digest));
    }
    let semantic_before = count_open(&frontier, VerificationObligationRoleV0::SemanticClosure);
    let custody_before = count_open(&frontier, VerificationObligationRoleV0::Custody);
    let sequence = frontier.lineage.sequence + 1;
    let mut outcomes = Vec::new();
    let mut touched_parents = BTreeSet::new();
    for (ordinal, action) in packet.actions.iter().enumerate() {
        let action_ordinal = u32::try_from(ordinal).map_err(|_| {
            VerificationErrorV0::InvalidArtifact("verification action count exceeds u32")
        })?;
        match action {
            VerificationActionV0::Refine { children } => {
                let outcome = apply_refinement(
                    &mut frontier,
                    children,
                    sequence,
                    &object_digest,
                    &mut touched_parents,
                    action_ordinal,
                )?;
                outcomes.push(outcome);
            }
            VerificationActionV0::Discharge { obligation_id, .. } => {
                require_obligation(&frontier, obligation_id)?;
                outcomes.push(VerificationActionOutcomeV0 {
                    action_ordinal,
                    decision: VerificationDecisionV0::Rejected,
                    obligations: vec![obligation_id.clone()],
                    detail: "the frozen version-zero verifier has no typed discharge predicate; a digest reference alone cannot close a hole".to_owned(),
                });
            }
            VerificationActionV0::Reopen {
                obligation_id,
                prior_witness_digest,
                counterevidence_digest,
            } => {
                let obligation = require_obligation_mut(&mut frontier, obligation_id)?;
                let VerificationObligationStateV0::Discharged { witness_digest, .. } =
                    &obligation.state
                else {
                    outcomes.push(VerificationActionOutcomeV0 {
                        action_ordinal,
                        decision: VerificationDecisionV0::Rejected,
                        obligations: vec![obligation_id.clone()],
                        detail: "only a discharged obligation can be reopened".to_owned(),
                    });
                    continue;
                };
                if witness_digest != prior_witness_digest {
                    outcomes.push(VerificationActionOutcomeV0 {
                        action_ordinal,
                        decision: VerificationDecisionV0::Rejected,
                        obligations: vec![obligation_id.clone()],
                        detail:
                            "the reopening request does not name the recorded discharge witness"
                                .to_owned(),
                    });
                    continue;
                }
                obligation.state = VerificationObligationStateV0::Reopened {
                    prior_witness_digest: prior_witness_digest.clone(),
                    counterevidence_digest: counterevidence_digest.clone(),
                };
                outcomes.push(VerificationActionOutcomeV0 {
                    action_ordinal,
                    decision: VerificationDecisionV0::Reopened,
                    obligations: vec![obligation_id.clone()],
                    detail: "counterevidence reopened the finite scoped obligation".to_owned(),
                });
            }
            VerificationActionV0::RegisterFork { fork } => {
                if frontier
                    .unresolved_forks
                    .iter()
                    .any(|existing| existing.id == fork.id)
                {
                    return Err(VerificationErrorV0::InvalidArtifact(
                        "a fork coordinate cannot be registered twice",
                    ));
                }
                frontier.unresolved_forks.push(fork.clone());
                outcomes.push(VerificationActionOutcomeV0 {
                    action_ordinal,
                    decision: VerificationDecisionV0::ForkRecorded,
                    obligations: Vec::new(),
                    detail:
                        "both conflicting branches remain visible; no branch was selected as truth"
                            .to_owned(),
                });
            }
        }
    }
    let unsupported_discharge_refused =
        packet.actions.iter().enumerate().all(|(ordinal, action)| {
            !matches!(action, VerificationActionV0::Discharge { .. })
                || outcomes.get(ordinal).is_some_and(|outcome| {
                    outcome.decision == VerificationDecisionV0::Rejected
                        && outcome.detail.contains("no typed discharge predicate")
                })
        });
    frontier.lineage.sequence = sequence;
    frontier.lineage.parent_subject_digest = subject_digest.clone();
    frontier
        .lineage
        .consumed_packet_digests
        .push(object_digest.clone());
    frontier.state = derived_frontier_state(&frontier);
    frontier.check()?;
    let next_frontier_digest = frontier.digest()?;
    let semantic_after = count_open(&frontier, VerificationObligationRoleV0::SemanticClosure);
    let custody_after = count_open(&frontier, VerificationObligationRoleV0::Custody);
    let certificate = derive_certificate(&frontier, &method_digest)?;
    let result = VerificationResultV0 {
        state: frontier.state,
        open_semantic_leaves: checked_u32(semantic_after, "semantic leaf count")?,
        open_custody_leaves: checked_u32(custody_after, "custody leaf count")?,
        unresolved_forks: checked_u32(frontier.unresolved_forks.len(), "fork count")?,
        certificate,
    };
    Ok(VerificationTransitionV0 {
        schema: VERIFICATION_TRANSITION_SCHEMA_V0.to_owned(),
        version: VERIFICATION_VERSION_V0,
        interface: InquiryInterfaceV0::canonical(),
        input: VerificationInputV0 {
            subject: subject.clone(),
            method: contract.clone(),
            object: packet.clone(),
        },
        output: VerificationOutputV0 {
            history: VerificationHistoryV0 {
                mechanism: MechanismV0::Verify,
                interface: InquiryInterfaceV0::canonical(),
                subject_digest,
                method_contract_digest: method_digest.clone(),
                object_packet_digest: object_digest,
                outcomes,
                leaf_delta: VerificationLeafDeltaV0 {
                    semantic_before: checked_u32(semantic_before, "semantic leaf count")?,
                    semantic_after: checked_u32(semantic_after, "semantic leaf count")?,
                    custody_before: checked_u32(custody_before, "custody leaf count")?,
                    custody_after: checked_u32(custody_after, "custody leaf count")?,
                },
            },
            result,
            evidence: VerificationEvidenceV0 {
                interface: InquiryInterfaceV0::canonical(),
                origin_unchanged: CheckStatus::Checked,
                method_content_addressed: CheckStatus::Checked,
                unsupported_discharge_refused: if unsupported_discharge_refused {
                    CheckStatus::Checked
                } else {
                    CheckStatus::Unchecked
                },
                interface_preserved: CheckStatus::Checked,
                residual_frontier: frontier,
                next_input: NextVerificationInputV0 {
                    subject_frontier_digest: next_frontier_digest,
                    method_contract_digest: method_digest,
                    object_schema: VERIFICATION_PACKET_SCHEMA_V0.to_owned(),
                },
            },
        },
    })
}

fn seed_or_continue_frontier(
    subject: &VerificationSubjectV0,
    method_digest: &str,
) -> Result<VerificationFrontierV0, VerificationErrorV0> {
    match subject {
        VerificationSubjectV0::InquiryFrontier(origin) => Ok(VerificationFrontierV0 {
            schema: VERIFICATION_FRONTIER_SCHEMA_V0.to_owned(),
            version: VERIFICATION_VERSION_V0,
            interface: InquiryInterfaceV0::canonical(),
            origin_inquiry_frontier_digest: origin.digest()?,
            origin_inquiry_frontier: origin.as_ref().clone(),
            obligations: root_obligations(origin),
            unresolved_forks: Vec::new(),
            lineage: VerificationLineageV0 {
                sequence: 0,
                parent_subject_digest: origin.digest()?,
                method_contract_digest: method_digest.to_owned(),
                consumed_packet_digests: Vec::new(),
            },
            state: VerificationFrontierStateV0::Open,
        }),
        VerificationSubjectV0::VerificationFrontier(frontier) => {
            if frontier.lineage.method_contract_digest != method_digest {
                return Err(VerificationErrorV0::MethodDrift {
                    expected: frontier.lineage.method_contract_digest.clone(),
                    actual: method_digest.to_owned(),
                });
            }
            Ok(frontier.as_ref().clone())
        }
    }
}

fn apply_refinement(
    frontier: &mut VerificationFrontierV0,
    children: &[RefinementObligationV0],
    sequence: u64,
    basis_digest: &str,
    touched_parents: &mut BTreeSet<ArtifactKeyV0>,
    action_ordinal: u32,
) -> Result<VerificationActionOutcomeV0, VerificationErrorV0> {
    let existing = frontier
        .obligations
        .iter()
        .map(|obligation| obligation.id.clone())
        .collect::<BTreeSet<_>>();
    if children.iter().any(|child| existing.contains(&child.id)) {
        return Err(VerificationErrorV0::InvalidArtifact(
            "a refinement cannot reuse an existing obligation coordinate",
        ));
    }
    let mut parent_children: BTreeMap<ArtifactKeyV0, Vec<ArtifactKeyV0>> = BTreeMap::new();
    for child in children {
        for parent_id in &child.parents {
            let parent = require_obligation(frontier, parent_id)?;
            if parent.role != VerificationObligationRoleV0::SemanticClosure
                || parent.state != VerificationObligationStateV0::Open
            {
                return Err(VerificationErrorV0::InvalidArtifact(
                    "refinement parents must be distinct open semantic obligations",
                ));
            }
            parent_children
                .entry(parent_id.clone())
                .or_default()
                .push(child.id.clone());
        }
    }
    if parent_children.is_empty()
        || parent_children.keys().any(|parent| {
            !children
                .iter()
                .any(|child| child.parents.iter().any(|candidate| candidate == parent))
        })
    {
        return Err(VerificationErrorV0::InvalidArtifact(
            "a refinement must refine at least one semantic parent",
        ));
    }
    for parent_id in parent_children.keys() {
        if !touched_parents.insert(parent_id.clone()) {
            return Err(VerificationErrorV0::InvalidArtifact(
                "one packet cannot refine the same parent twice",
            ));
        }
    }
    for (parent_id, child_ids) in &parent_children {
        let parent = require_obligation_mut(frontier, parent_id)?;
        parent.state = VerificationObligationStateV0::Refined {
            children: child_ids.clone(),
            basis_digest: basis_digest.to_owned(),
        };
    }
    frontier
        .obligations
        .extend(children.iter().map(|child| VerificationObligationV0 {
            id: child.id.clone(),
            role: child.role,
            unit: child.unit,
            detail: child.detail.clone(),
            parents: child.parents.clone(),
            introduced_at: sequence,
            state: VerificationObligationStateV0::Open,
        }));
    let parent_ids = parent_children.into_keys().collect::<Vec<_>>();
    let child_count = children.len();
    Ok(VerificationActionOutcomeV0 {
        action_ordinal,
        decision: VerificationDecisionV0::Refined,
        obligations: parent_ids,
        detail: format!(
            "refined the selected parents into {child_count} typed leaves; no leaf was discharged"
        ),
    })
}

fn root_obligations(origin: &InquiryFrontierV0) -> Vec<VerificationObligationV0> {
    origin
        .obligations
        .iter()
        .map(|obligation| VerificationObligationV0 {
            id: obligation.id.clone(),
            role: VerificationObligationRoleV0::SemanticClosure,
            unit: obligation.typed_unit.into(),
            detail: obligation.detail.clone(),
            parents: Vec::new(),
            introduced_at: 0,
            state: VerificationObligationStateV0::Open,
        })
        .collect()
}

fn check_obligation_graph(frontier: &VerificationFrontierV0) -> Result<(), VerificationErrorV0> {
    let roots = root_obligations(&frontier.origin_inquiry_frontier);
    if frontier.obligations.len() < roots.len()
        || frontier.obligations[..roots.len()]
            .iter()
            .zip(&roots)
            .any(|(actual, root)| {
                actual.id != root.id
                    || actual.role != root.role
                    || actual.unit != root.unit
                    || actual.detail != root.detail
                    || actual.parents != root.parents
                    || actual.introduced_at != 0
            })
    {
        return Err(VerificationErrorV0::InvalidArtifact(
            "verification roots must exactly retain the immutable inquiry obligations",
        ));
    }
    let mut seen = BTreeSet::new();
    for (index, obligation) in frontier.obligations.iter().enumerate() {
        if obligation.id.as_str().is_empty()
            || obligation.detail.trim().is_empty()
            || obligation.introduced_at > frontier.lineage.sequence
            || !seen.insert(obligation.id.clone())
        {
            return Err(VerificationErrorV0::InvalidArtifact(
                "verification obligations need unique coordinates, details, and valid sequence positions",
            ));
        }
        if index >= roots.len()
            && (obligation.introduced_at == 0
                || (obligation.role == VerificationObligationRoleV0::SemanticClosure
                    && obligation.parents.is_empty())
                || (obligation.role == VerificationObligationRoleV0::Custody
                    && !obligation.parents.is_empty()))
        {
            return Err(VerificationErrorV0::InvalidArtifact(
                "new semantic leaves need parents while custody leaves remain orthogonal",
            ));
        }
        let parents = obligation.parents.iter().collect::<BTreeSet<_>>();
        if parents.len() != obligation.parents.len()
            || obligation
                .parents
                .iter()
                .any(|parent| parent == &obligation.id || !seen.contains(parent))
        {
            return Err(VerificationErrorV0::InvalidArtifact(
                "the obligation graph must be an ordered acyclic parent relation",
            ));
        }
        check_state_digests(&obligation.state)?;
    }
    for obligation in &frontier.obligations {
        let actual_children = frontier
            .obligations
            .iter()
            .filter(|candidate| candidate.parents.contains(&obligation.id))
            .map(|candidate| candidate.id.clone())
            .collect::<Vec<_>>();
        match &obligation.state {
            VerificationObligationStateV0::Refined { children, .. }
                if children == &actual_children && !children.is_empty() => {}
            VerificationObligationStateV0::Refined { .. } => {
                return Err(VerificationErrorV0::InvalidArtifact(
                    "a refined state must name exactly its ordered child obligations",
                ));
            }
            _ if !actual_children.is_empty() => {
                return Err(VerificationErrorV0::InvalidArtifact(
                    "an obligation with children must retain its refined state",
                ));
            }
            _ => {}
        }
    }
    Ok(())
}

fn check_refinement_child(child: &RefinementObligationV0) -> Result<(), VerificationErrorV0> {
    if child.id.as_str().is_empty() || child.detail.trim().is_empty() {
        return Err(VerificationErrorV0::InvalidArtifact(
            "a refinement child needs a coordinate and detail",
        ));
    }
    let parents = child.parents.iter().collect::<BTreeSet<_>>();
    if parents.len() != child.parents.len()
        || (child.role == VerificationObligationRoleV0::SemanticClosure && child.parents.is_empty())
        || (child.role == VerificationObligationRoleV0::Custody && !child.parents.is_empty())
    {
        return Err(VerificationErrorV0::InvalidArtifact(
            "semantic children need unique parents while custody children remain orthogonal",
        ));
    }
    Ok(())
}

fn check_state_digests(state: &VerificationObligationStateV0) -> Result<(), VerificationErrorV0> {
    match state {
        VerificationObligationStateV0::Open => Ok(()),
        VerificationObligationStateV0::Refined { basis_digest, .. } => check_digest(basis_digest),
        VerificationObligationStateV0::Discharged {
            witness_digest,
            verifier_digest,
            scope_digest,
        } => {
            check_digest(witness_digest)?;
            check_digest(verifier_digest)?;
            check_digest(scope_digest)
        }
        VerificationObligationStateV0::Reopened {
            prior_witness_digest,
            counterevidence_digest,
        } => {
            check_digest(prior_witness_digest)?;
            check_digest(counterevidence_digest)
        }
    }
}

fn check_fork(fork: &UnresolvedForkV0) -> Result<(), VerificationErrorV0> {
    if fork.id.as_str().is_empty()
        || fork.detail.trim().is_empty()
        || fork.left_digest == fork.right_digest
    {
        return Err(VerificationErrorV0::InvalidArtifact(
            "a fork needs a coordinate, two distinct branches, and a detail",
        ));
    }
    check_digest(&fork.left_digest)?;
    check_digest(&fork.right_digest)
}

fn require_obligation<'a>(
    frontier: &'a VerificationFrontierV0,
    id: &ArtifactKeyV0,
) -> Result<&'a VerificationObligationV0, VerificationErrorV0> {
    frontier
        .obligations
        .iter()
        .find(|obligation| obligation.id == *id)
        .ok_or_else(|| VerificationErrorV0::UnknownObligation(id.as_str().to_owned()))
}

fn require_obligation_mut<'a>(
    frontier: &'a mut VerificationFrontierV0,
    id: &ArtifactKeyV0,
) -> Result<&'a mut VerificationObligationV0, VerificationErrorV0> {
    frontier
        .obligations
        .iter_mut()
        .find(|obligation| obligation.id == *id)
        .ok_or_else(|| VerificationErrorV0::UnknownObligation(id.as_str().to_owned()))
}

fn count_open(frontier: &VerificationFrontierV0, role: VerificationObligationRoleV0) -> usize {
    frontier
        .obligations
        .iter()
        .filter(|obligation| obligation.role == role && is_open_leaf(&obligation.state))
        .count()
}

const fn is_open_leaf(state: &VerificationObligationStateV0) -> bool {
    matches!(
        state,
        VerificationObligationStateV0::Open | VerificationObligationStateV0::Reopened { .. }
    )
}

fn derived_frontier_state(frontier: &VerificationFrontierV0) -> VerificationFrontierStateV0 {
    if count_open(frontier, VerificationObligationRoleV0::SemanticClosure) == 0
        && frontier.unresolved_forks.is_empty()
    {
        VerificationFrontierStateV0::ScopedClosed
    } else {
        VerificationFrontierStateV0::Open
    }
}

fn derive_certificate(
    frontier: &VerificationFrontierV0,
    method_digest: &str,
) -> Result<Option<ScopedCertificateV0>, VerificationErrorV0> {
    if frontier.state != VerificationFrontierStateV0::ScopedClosed {
        return Ok(None);
    }
    let mut witness_digests = frontier
        .obligations
        .iter()
        .filter_map(|obligation| match &obligation.state {
            VerificationObligationStateV0::Discharged { witness_digest, .. } => {
                Some(witness_digest.clone())
            }
            _ => None,
        })
        .collect::<Vec<_>>();
    witness_digests.sort();
    witness_digests.dedup();
    let statement = "all semantic leaves in the embedded inquiry scope are discharged by typed witnesses and no unresolved fork remains".to_owned();
    #[derive(Serialize)]
    struct ScopeIdentity<'a> {
        origin: &'a str,
        statement: &'a str,
    }
    let scope_digest = digest_json(pretty_json(&ScopeIdentity {
        origin: &frontier.origin_inquiry_frontier_digest,
        statement: &statement,
    })?)?;
    Ok(Some(ScopedCertificateV0 {
        scope_digest,
        verifier_digest: method_digest.to_owned(),
        witness_digests,
        statement,
    }))
}

pub fn load_verification_subject_v0(
    path: impl AsRef<Path>,
) -> Result<VerificationSubjectV0, VerificationErrorV0> {
    let path = path.as_ref();
    require_adva(path)?;
    let source = read_source(path)?;
    let value: serde_json::Value = serde_json::from_str(&source)
        .map_err(|error| VerificationErrorV0::Json(error.to_string()))?;
    match value.get("schema").and_then(serde_json::Value::as_str) {
        Some(crate::INQUIRY_FRONTIER_SCHEMA_V0) => Ok(VerificationSubjectV0::InquiryFrontier(
            Box::new(InquiryFrontierV0::from_json(&source)?),
        )),
        Some(VERIFICATION_FRONTIER_SCHEMA_V0) => Ok(VerificationSubjectV0::VerificationFrontier(
            Box::new(VerificationFrontierV0::from_json(&source)?),
        )),
        _ => Err(VerificationErrorV0::InvalidArtifact(
            "verify subject must be an inquiry or verification frontier",
        )),
    }
}

pub fn load_verification_contract_v0(
    path: impl AsRef<Path>,
) -> Result<VerificationContractV0, VerificationErrorV0> {
    load_checked(path, VerificationContractV0::from_json)
}

pub fn load_verification_packet_v0(
    path: impl AsRef<Path>,
) -> Result<VerificationPacketV0, VerificationErrorV0> {
    load_checked(path, VerificationPacketV0::from_json)
}

pub fn load_verification_frontier_v0(
    path: impl AsRef<Path>,
) -> Result<VerificationFrontierV0, VerificationErrorV0> {
    load_checked(path, VerificationFrontierV0::from_json)
}

pub fn load_verification_transition_v0(
    path: impl AsRef<Path>,
) -> Result<VerificationTransitionV0, VerificationErrorV0> {
    load_checked(path, VerificationTransitionV0::from_json)
}

pub fn save_verification_frontier_v0(
    path: impl AsRef<Path>,
    frontier: &VerificationFrontierV0,
) -> Result<InquirySaveReceiptV0, VerificationErrorV0> {
    save_checked(path, frontier.to_json()?)
}

pub fn save_verification_transition_v0(
    path: impl AsRef<Path>,
    transition: &VerificationTransitionV0,
) -> Result<InquirySaveReceiptV0, VerificationErrorV0> {
    save_checked(path, transition.to_json()?)
}

fn check_header(
    schema: &str,
    version: u32,
    expected_schema: &str,
    interface: &InquiryInterfaceV0,
) -> Result<(), VerificationErrorV0> {
    if schema != expected_schema
        || version != VERIFICATION_VERSION_V0
        || interface != &InquiryInterfaceV0::canonical()
        || interface.inputs != InputLabelV0::ALL
        || interface.outputs != OutputLabelV0::ALL
    {
        return Err(VerificationErrorV0::InvalidArtifact(
            "unsupported verification schema, version, or three-port interface",
        ));
    }
    Ok(())
}

fn pretty_json<T: Serialize>(value: &T) -> Result<String, VerificationErrorV0> {
    serde_json::to_string_pretty(value)
        .map_err(|error| VerificationErrorV0::Json(error.to_string()))
}

fn digest_json(json: String) -> Result<String, VerificationErrorV0> {
    let encoded = format!("{json}\n");
    Ok(format!(
        "blake3:{}",
        blake3::hash(encoded.as_bytes()).to_hex()
    ))
}

fn check_digest_list(digests: &[String]) -> Result<(), VerificationErrorV0> {
    let mut unique = BTreeSet::new();
    for digest in digests {
        check_digest(digest)?;
        if !unique.insert(digest) {
            return Err(VerificationErrorV0::InvalidArtifact(
                "verification lineage digests must be unique",
            ));
        }
    }
    Ok(())
}

fn check_digest(digest: &str) -> Result<(), VerificationErrorV0> {
    let Some(hex) = digest.strip_prefix("blake3:") else {
        return Err(VerificationErrorV0::InvalidArtifact(
            "a verification digest must be a BLAKE3 coordinate",
        ));
    };
    if hex.len() != 64
        || !hex
            .bytes()
            .all(|byte| byte.is_ascii_digit() || (b'a'..=b'f').contains(&byte))
    {
        return Err(VerificationErrorV0::InvalidArtifact(
            "a verification digest must be a lowercase BLAKE3 coordinate",
        ));
    }
    Ok(())
}

fn checked_u32(value: usize, label: &'static str) -> Result<u32, VerificationErrorV0> {
    u32::try_from(value).map_err(|_| VerificationErrorV0::CountOverflow(label))
}

fn require_adva(path: &Path) -> Result<(), VerificationErrorV0> {
    crate::persistence::require_adva_extension(path)
        .map_err(|error| VerificationErrorV0::Persistence(error.to_string()))
}

fn read_source(path: &Path) -> Result<String, VerificationErrorV0> {
    fs::read_to_string(path).map_err(|error| VerificationErrorV0::Io {
        path: path.to_path_buf(),
        detail: error.to_string(),
    })
}

fn load_checked<T>(
    path: impl AsRef<Path>,
    decode: impl FnOnce(&str) -> Result<T, VerificationErrorV0>,
) -> Result<T, VerificationErrorV0> {
    let path = path.as_ref();
    require_adva(path)?;
    decode(&read_source(path)?)
}

fn save_checked(
    path: impl AsRef<Path>,
    json: String,
) -> Result<InquirySaveReceiptV0, VerificationErrorV0> {
    let path = path.as_ref();
    require_adva(path)?;
    let encoded = format!("{json}\n");
    crate::persistence::write_atomically(path, encoded.as_bytes())
        .map_err(|error| VerificationErrorV0::Persistence(error.to_string()))?;
    Ok(InquirySaveReceiptV0 {
        path: path.to_path_buf(),
        artifact_digest: format!("blake3:{}", blake3::hash(encoded.as_bytes()).to_hex()),
        bytes_written: u64::try_from(encoded.len()).unwrap_or(u64::MAX),
    })
}

#[derive(Clone, Debug, Eq, Error, PartialEq)]
pub enum VerificationErrorV0 {
    #[error("invalid verification artifact: {0}")]
    InvalidArtifact(&'static str),
    #[error("verification method drift: expected {expected}, received {actual}")]
    MethodDrift { expected: String, actual: String },
    #[error("verification packet has already been consumed: {0}")]
    PacketReplay(String),
    #[error("verification packet refers to an unretained hypothesis: {0}")]
    UnknownBasis(String),
    #[error("unknown verification obligation: {0}")]
    UnknownObligation(String),
    #[error("verification {0} exceeds u32")]
    CountOverflow(&'static str),
    #[error("verification JSON error: {0}")]
    Json(String),
    #[error("verification persistence error: {0}")]
    Persistence(String),
    #[error("I/O error at {path:?}: {detail}")]
    Io { path: PathBuf, detail: String },
    #[error(transparent)]
    Inquiry(#[from] InquiryErrorV0),
}
