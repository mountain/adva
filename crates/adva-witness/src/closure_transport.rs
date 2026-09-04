use crate::{
    ArtifactKeyV0, BoundaryChargeV0, ExactExprV0, InputLabelV0, InquiryInterfaceV0,
    InquirySaveReceiptV0, MechanismV0, OutputLabelV0, PolynomialV0, WitnessArtifactV0,
    WitnessErrorV0, WitnessProofV0, WitnessStoreV0,
};
use adva_ir::CheckStatus;
use serde::{Deserialize, Serialize};
use std::collections::{BTreeMap, BTreeSet};
use std::fs;
use std::path::{Path, PathBuf};
use thiserror::Error;

pub const LOCAL_CLOSURE_CANDIDATE_SCHEMA_V0: &str = "adva.local-closure-candidate.research";
pub const CLOSURE_TRANSPORT_CONTRACT_SCHEMA_V0: &str = "adva.closure-transport-contract.research";
pub const CLOSURE_TRANSPORT_PLAN_SCHEMA_V0: &str = "adva.closure-transport-plan.research";
pub const POLYNOMIAL_CLOSURE_CERTIFICATE_SCHEMA_V0: &str =
    "adva.polynomial-closure-certificate.research";
pub const POLYNOMIAL_SEPARATION_CERTIFICATE_SCHEMA_V0: &str =
    "adva.polynomial-separation-certificate.research";
pub const CLOSURE_TRANSPORT_FRONTIER_SCHEMA_V0: &str = "adva.closure-transport-frontier.research";
pub const CLOSURE_TRANSPORT_TRANSITION_SCHEMA_V0: &str =
    "adva.closure-transport-transition.research";
pub const CLOSURE_TRANSPORT_VERSION_V0: u32 = 0;

const SLOT_VARIABLE: &str = "__adva_scope_slot__";
const FIRST_CONTRACT_NAME: &str = "first:exact-polynomial-local-closure-transport";
const FIRST_CANDIDATE_NAME: &str = "first:distributivity-local-closure";
const M6_VERIFICATION_FRONTIER_DIGEST: &str =
    "blake3:bf0bfc721c7beea6e20d240846f390404ca9b4dc26158027cd95aa9d3484db91";

#[derive(Clone, Copy, Debug, Eq, Ord, PartialEq, PartialOrd, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum ClosureUnitV0 {
    ExactPolynomialIdentity,
    OrderedHolonomyReplay,
    SharedTruthCoordinate,
}

/// Epistemic names are outcomes of checks, not synonyms for truth values.
/// `Absurdity` is reserved for a future same-scope proof of contradiction and
/// is intentionally never emitted by the first experiment.
#[derive(Clone, Copy, Debug, Eq, Ord, PartialEq, PartialOrd, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum ClosureFindingClassV0 {
    Identity,
    Separation,
    Incommensurate,
    Challenge,
    Absurdity,
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct LocalClosureCandidateV0 {
    pub schema: String,
    pub version: u32,
    pub interface: InquiryInterfaceV0,
    pub name: String,
    pub unit: ClosureUnitV0,
    pub before: ExactExprV0,
    pub after: ExactExprV0,
}

impl LocalClosureCandidateV0 {
    #[must_use]
    pub fn first_distributivity() -> Self {
        let a = ExactExprV0::variable("a");
        let x = ExactExprV0::variable("x");
        let y = ExactExprV0::variable("y");
        Self {
            schema: LOCAL_CLOSURE_CANDIDATE_SCHEMA_V0.to_owned(),
            version: CLOSURE_TRANSPORT_VERSION_V0,
            interface: InquiryInterfaceV0::canonical(),
            name: FIRST_CANDIDATE_NAME.to_owned(),
            unit: ClosureUnitV0::ExactPolynomialIdentity,
            before: ExactExprV0::product(a.clone(), ExactExprV0::sum(x.clone(), y.clone())),
            after: ExactExprV0::sum(
                ExactExprV0::product(a.clone(), x),
                ExactExprV0::product(a, y),
            ),
        }
    }

    pub fn from_json(source: &str) -> Result<Self, ClosureTransportErrorV0> {
        let artifact: Self = serde_json::from_str(source)
            .map_err(|error| ClosureTransportErrorV0::Json(error.to_string()))?;
        artifact.check()?;
        Ok(artifact)
    }

    pub fn to_json(&self) -> Result<String, ClosureTransportErrorV0> {
        self.check()?;
        pretty_json(self)
    }

    pub fn digest(&self) -> Result<String, ClosureTransportErrorV0> {
        digest_serialized(self)
    }

    pub fn check(&self) -> Result<(), ClosureTransportErrorV0> {
        check_header(
            &self.schema,
            self.version,
            LOCAL_CLOSURE_CANDIDATE_SCHEMA_V0,
            &self.interface,
        )?;
        if self != &Self::first_distributivity() {
            return Err(invalid(
                "the version-zero local candidate is not the frozen distributivity identity",
            ));
        }
        Ok(())
    }
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct ClosureTransportContractV0 {
    pub schema: String,
    pub version: u32,
    pub interface: InquiryInterfaceV0,
    pub name: String,
    pub mechanism: MechanismV0,
    pub subject_schema: String,
    pub object_schema: String,
    pub output_schema: String,
    pub supported_unit: ClosureUnitV0,
}

impl ClosureTransportContractV0 {
    #[must_use]
    pub fn first_exact_polynomial() -> Self {
        Self {
            schema: CLOSURE_TRANSPORT_CONTRACT_SCHEMA_V0.to_owned(),
            version: CLOSURE_TRANSPORT_VERSION_V0,
            interface: InquiryInterfaceV0::canonical(),
            name: FIRST_CONTRACT_NAME.to_owned(),
            mechanism: MechanismV0::Verify,
            subject_schema: LOCAL_CLOSURE_CANDIDATE_SCHEMA_V0.to_owned(),
            object_schema: CLOSURE_TRANSPORT_PLAN_SCHEMA_V0.to_owned(),
            output_schema: CLOSURE_TRANSPORT_TRANSITION_SCHEMA_V0.to_owned(),
            supported_unit: ClosureUnitV0::ExactPolynomialIdentity,
        }
    }

    pub fn from_json(source: &str) -> Result<Self, ClosureTransportErrorV0> {
        let artifact: Self = serde_json::from_str(source)
            .map_err(|error| ClosureTransportErrorV0::Json(error.to_string()))?;
        artifact.check()?;
        Ok(artifact)
    }

    pub fn to_json(&self) -> Result<String, ClosureTransportErrorV0> {
        self.check()?;
        pretty_json(self)
    }

    pub fn digest(&self) -> Result<String, ClosureTransportErrorV0> {
        digest_serialized(self)
    }

    pub fn check(&self) -> Result<(), ClosureTransportErrorV0> {
        if self != &Self::first_exact_polynomial() {
            return Err(invalid(
                "the version-zero closure contract is not the frozen exact verifier",
            ));
        }
        Ok(())
    }
}

#[derive(Clone, Debug, Eq, Ord, PartialEq, PartialOrd, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct ClosureScopeV0 {
    pub coordinate: ArtifactKeyV0,
    pub occurrence: ArtifactKeyV0,
    pub unit: ClosureUnitV0,
}

impl ClosureScopeV0 {
    fn first(label: &str) -> Self {
        Self {
            coordinate: key(format!("experiment:0118:scope-{label}")),
            occurrence: key(format!("experiment:0118:occurrence-{label}")),
            unit: ClosureUnitV0::ExactPolynomialIdentity,
        }
    }

    fn check(&self) -> Result<(), ClosureTransportErrorV0> {
        if self.unit != ClosureUnitV0::ExactPolynomialIdentity {
            return Err(invalid("a closure scope has the wrong typed unit"));
        }
        Ok(())
    }
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct ScopeMapV0 {
    pub coordinate: ArtifactKeyV0,
    pub source: ClosureScopeV0,
    pub target: ClosureScopeV0,
    pub context: ExactExprV0,
}

impl ScopeMapV0 {
    fn check(&self) -> Result<(), ClosureTransportErrorV0> {
        self.source.check()?;
        self.target.check()?;
        if self.source.coordinate == self.target.coordinate
            || self.source.occurrence == self.target.occurrence
        {
            return Err(invalid(
                "scope transport must bind a distinct target scope and occurrence",
            ));
        }
        let occurrences = self.context.variable_occurrences();
        if occurrences.get(SLOT_VARIABLE) != Some(&1) {
            return Err(invalid(
                "a scope map must contain exactly one distinguished input slot",
            ));
        }
        Ok(())
    }

    fn digest(&self) -> Result<String, ClosureTransportErrorV0> {
        self.check()?;
        digest_serialized(self)
    }
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct NegativeImportTargetV0 {
    pub coordinate: ArtifactKeyV0,
    pub target_digest: String,
    pub required_unit: ClosureUnitV0,
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct CounterevidenceNoticeV0 {
    pub coordinate: ArtifactKeyV0,
    pub challenged_scope: ArtifactKeyV0,
    pub detail: String,
}

impl CounterevidenceNoticeV0 {
    fn digest(&self) -> Result<String, ClosureTransportErrorV0> {
        digest_serialized(self)
    }
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct ClosureTransportPlanV0 {
    pub schema: String,
    pub version: u32,
    pub interface: InquiryInterfaceV0,
    pub local_scope: ClosureScopeV0,
    pub stage_one: ScopeMapV0,
    pub stage_two: ScopeMapV0,
    pub direct: ScopeMapV0,
    pub negative_targets: [NegativeImportTargetV0; 2],
    pub counterevidence: CounterevidenceNoticeV0,
}

impl ClosureTransportPlanV0 {
    #[must_use]
    pub fn first_experiment() -> Self {
        let scope_a = ClosureScopeV0::first("a");
        let scope_b = ClosureScopeV0::first("b");
        let scope_c = ClosureScopeV0::first("c");
        let slot = ExactExprV0::variable(SLOT_VARIABLE);
        let z = ExactExprV0::variable("z");
        let b = ExactExprV0::variable("b");
        Self {
            schema: CLOSURE_TRANSPORT_PLAN_SCHEMA_V0.to_owned(),
            version: CLOSURE_TRANSPORT_VERSION_V0,
            interface: InquiryInterfaceV0::canonical(),
            local_scope: scope_a.clone(),
            stage_one: ScopeMapV0 {
                coordinate: key("experiment:0118:map-a-b"),
                source: scope_a.clone(),
                target: scope_b.clone(),
                context: ExactExprV0::sum(z.clone(), slot.clone()),
            },
            stage_two: ScopeMapV0 {
                coordinate: key("experiment:0118:map-b-c"),
                source: scope_b,
                target: scope_c.clone(),
                context: ExactExprV0::product(b.clone(), slot.clone()),
            },
            direct: ScopeMapV0 {
                coordinate: key("experiment:0118:map-a-c"),
                source: scope_a.clone(),
                target: scope_c,
                context: ExactExprV0::product(b, ExactExprV0::sum(z, slot)),
            },
            negative_targets: [
                NegativeImportTargetV0 {
                    coordinate: key("experiment:0118:negative:m6-ordered-holonomy"),
                    target_digest: M6_VERIFICATION_FRONTIER_DIGEST.to_owned(),
                    required_unit: ClosureUnitV0::OrderedHolonomyReplay,
                },
                NegativeImportTargetV0 {
                    coordinate: key("experiment:0118:negative:shared-truth-coordinate"),
                    target_digest: M6_VERIFICATION_FRONTIER_DIGEST.to_owned(),
                    required_unit: ClosureUnitV0::SharedTruthCoordinate,
                },
            ],
            counterevidence: CounterevidenceNoticeV0 {
                coordinate: key("experiment:0118:counterevidence-notice-1"),
                challenged_scope: scope_a.coordinate,
                detail: "admit a challenge without treating it as proof of falsity".to_owned(),
            },
        }
    }

    pub fn from_json(source: &str) -> Result<Self, ClosureTransportErrorV0> {
        let artifact: Self = serde_json::from_str(source)
            .map_err(|error| ClosureTransportErrorV0::Json(error.to_string()))?;
        artifact.check()?;
        Ok(artifact)
    }

    pub fn to_json(&self) -> Result<String, ClosureTransportErrorV0> {
        self.check()?;
        pretty_json(self)
    }

    pub fn digest(&self) -> Result<String, ClosureTransportErrorV0> {
        digest_serialized(self)
    }

    pub fn check(&self) -> Result<(), ClosureTransportErrorV0> {
        check_header(
            &self.schema,
            self.version,
            CLOSURE_TRANSPORT_PLAN_SCHEMA_V0,
            &self.interface,
        )?;
        if self != &Self::first_experiment() {
            return Err(invalid(
                "the version-zero transport plan is not the frozen first experiment",
            ));
        }
        self.stage_one.check()?;
        self.stage_two.check()?;
        self.direct.check()?;
        Ok(())
    }
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct PolynomialClosureContentV0 {
    pub name: String,
    pub class: ClosureFindingClassV0,
    pub scope: ClosureScopeV0,
    pub unit: ClosureUnitV0,
    pub before: ExactExprV0,
    pub after: ExactExprV0,
    pub normal_form: PolynomialV0,
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct PolynomialClosureCertificateV0 {
    pub schema: String,
    pub version: u32,
    pub interface: InquiryInterfaceV0,
    pub content: PolynomialClosureContentV0,
    pub witness_graph: Vec<WitnessArtifactV0>,
    pub sealed_witness: ArtifactKeyV0,
}

impl PolynomialClosureCertificateV0 {
    pub fn content_digest(&self) -> Result<String, ClosureTransportErrorV0> {
        self.check()?;
        digest_serialized(&self.content)
    }

    pub fn digest(&self) -> Result<String, ClosureTransportErrorV0> {
        self.check()?;
        digest_serialized(self)
    }

    pub fn check(&self) -> Result<(), ClosureTransportErrorV0> {
        check_header(
            &self.schema,
            self.version,
            POLYNOMIAL_CLOSURE_CERTIFICATE_SCHEMA_V0,
            &self.interface,
        )?;
        self.content.scope.check()?;
        if self.content.class != ClosureFindingClassV0::Identity
            || self.content.name.is_empty()
            || self.content.unit != ClosureUnitV0::ExactPolynomialIdentity
            || self.content.scope.unit != self.content.unit
        {
            return Err(invalid("closure certificate typed units do not agree"));
        }
        let before = self.content.before.normalize()?;
        let after = self.content.after.normalize()?;
        if before != after || before != self.content.normal_form {
            return Err(invalid(
                "closure certificate expressions do not share one exact normal form",
            ));
        }
        if self.witness_graph.len() != 2 {
            return Err(invalid(
                "a version-zero closure certificate must retain transition and seal nodes",
            ));
        }
        let mut store = WitnessStoreV0::new();
        for recorded in &self.witness_graph {
            let key = store.insert(recorded.proof.clone())?;
            if key != recorded.key || store.artifact(&key) != Some(recorded) {
                return Err(invalid(
                    "the embedded witness graph does not replay exactly",
                ));
            }
        }
        let sealed = store
            .artifact(&self.sealed_witness)
            .ok_or_else(|| invalid("the closure certificate seal is absent"))?;
        if !matches!(&sealed.proof, WitnessProofV0::Seal { .. })
            || !sealed.summary.is_formed()
            || !sealed.summary.is_multiplicatively_closed()
        {
            return Err(invalid(
                "the retained witness is not additively and multiplicatively closed",
            ));
        }
        Ok(())
    }
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct TransportReceiptV0 {
    pub map_coordinate: ArtifactKeyV0,
    pub map_digest: String,
    pub source_scope: ArtifactKeyV0,
    pub target_scope: ArtifactKeyV0,
    pub source_occurrence: ArtifactKeyV0,
    pub target_occurrence: ArtifactKeyV0,
    pub source_certificate_digest: String,
    pub result_certificate_digest: String,
    pub result_content_digest: String,
}

impl TransportReceiptV0 {
    fn digest(&self) -> Result<String, ClosureTransportErrorV0> {
        digest_serialized(self)
    }
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct ClosureTransportHistoryV0 {
    pub mechanism: MechanismV0,
    pub subject_digest: String,
    pub method_digest: String,
    pub object_digest: String,
    pub local_certificate_digest: String,
    pub stage_one: TransportReceiptV0,
    pub stage_two: TransportReceiptV0,
    pub direct: TransportReceiptV0,
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct TransportCoherenceV0 {
    pub local_closure: CheckStatus,
    pub composed_scope_map: CheckStatus,
    pub direct_equals_staged: CheckStatus,
    pub distinct_histories_retained: CheckStatus,
    pub common_result_content_digest: String,
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct NegativeImportOutcomeV0 {
    pub class: ClosureFindingClassV0,
    pub target: NegativeImportTargetV0,
    pub supplied_unit: ClosureUnitV0,
    pub accepted: bool,
    pub residual: RejectionResidualV0,
    pub reason: String,
}

#[derive(Clone, Copy, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum RejectionResidualV0 {
    TargetHolePreserved,
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct ExactVariableValueV0 {
    pub variable: String,
    pub value: num_bigint::BigInt,
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct PolynomialSeparationCertificateV0 {
    pub schema: String,
    pub version: u32,
    pub interface: InquiryInterfaceV0,
    pub name: String,
    pub class: ClosureFindingClassV0,
    pub unit: ClosureUnitV0,
    pub before: ExactExprV0,
    pub after: ExactExprV0,
    pub before_normal_form: PolynomialV0,
    pub after_normal_form: PolynomialV0,
    pub counterexample: Vec<ExactVariableValueV0>,
    pub before_value: num_bigint::BigInt,
    pub after_value: num_bigint::BigInt,
}

impl PolynomialSeparationCertificateV0 {
    pub fn check(&self) -> Result<(), ClosureTransportErrorV0> {
        check_header(
            &self.schema,
            self.version,
            POLYNOMIAL_SEPARATION_CERTIFICATE_SCHEMA_V0,
            &self.interface,
        )?;
        if self.name != "separation:omitted-y-factor"
            || self.class != ClosureFindingClassV0::Separation
            || self.unit != ClosureUnitV0::ExactPolynomialIdentity
        {
            return Err(invalid(
                "the arithmetic negative has an invalid epistemic name",
            ));
        }
        if self.before.normalize()? != self.before_normal_form
            || self.after.normalize()? != self.after_normal_form
            || self.before_normal_form == self.after_normal_form
        {
            return Err(invalid(
                "a separation certificate must retain distinct exact normal forms",
            ));
        }
        let environment = self
            .counterexample
            .iter()
            .map(|binding| (binding.variable.clone(), binding.value.clone()))
            .collect::<BTreeMap<_, _>>();
        let variables = self
            .before
            .variable_occurrences()
            .into_keys()
            .chain(self.after.variable_occurrences().into_keys())
            .collect::<BTreeSet<_>>();
        if environment.len() != self.counterexample.len()
            || environment.keys().ne(variables.iter())
            || self.before.evaluate_guarded(&environment)? != self.before_value
            || self.after.evaluate_guarded(&environment)? != self.after_value
            || self.before_value == self.after_value
        {
            return Err(invalid(
                "the retained valuation does not separate both expressions",
            ));
        }
        Ok(())
    }

    pub fn digest(&self) -> Result<String, ClosureTransportErrorV0> {
        self.check()?;
        digest_serialized(self)
    }
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct ClosureTransportResultV0 {
    pub local: PolynomialClosureCertificateV0,
    pub stage_one: PolynomialClosureCertificateV0,
    pub staged: PolynomialClosureCertificateV0,
    pub direct: PolynomialClosureCertificateV0,
    pub coherence: TransportCoherenceV0,
    pub adversarial_separation: PolynomialSeparationCertificateV0,
    pub negative_controls: [NegativeImportOutcomeV0; 2],
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct ClosureDependencyEdgeV0 {
    pub source: ArtifactKeyV0,
    pub target: ArtifactKeyV0,
    pub receipt_digest: String,
}

#[derive(Clone, Copy, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum ClosureFrontierStateV0 {
    Reopened,
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct ClosureTransportFrontierV0 {
    pub schema: String,
    pub version: u32,
    pub interface: InquiryInterfaceV0,
    pub state: ClosureFrontierStateV0,
    pub challenge: CounterevidenceNoticeV0,
    pub challenge_digest: String,
    pub closed_before_challenge: Vec<ArtifactKeyV0>,
    pub reopened_after_challenge: Vec<ArtifactKeyV0>,
    pub dependency_edges: Vec<ClosureDependencyEdgeV0>,
    pub retained_certificate_digests: Vec<String>,
}

impl ClosureTransportFrontierV0 {
    pub fn from_json(source: &str) -> Result<Self, ClosureTransportErrorV0> {
        let artifact: Self = serde_json::from_str(source)
            .map_err(|error| ClosureTransportErrorV0::Json(error.to_string()))?;
        artifact.check()?;
        Ok(artifact)
    }

    pub fn to_json(&self) -> Result<String, ClosureTransportErrorV0> {
        self.check()?;
        pretty_json(self)
    }

    pub fn digest(&self) -> Result<String, ClosureTransportErrorV0> {
        digest_serialized(self)
    }

    pub fn check(&self) -> Result<(), ClosureTransportErrorV0> {
        check_header(
            &self.schema,
            self.version,
            CLOSURE_TRANSPORT_FRONTIER_SCHEMA_V0,
            &self.interface,
        )?;
        if self.challenge_digest != self.challenge.digest()? {
            return Err(invalid("the counterevidence notice digest is stale"));
        }
        check_sorted_unique(&self.closed_before_challenge)?;
        check_sorted_unique(&self.reopened_after_challenge)?;
        if self.closed_before_challenge != self.reopened_after_challenge {
            return Err(invalid(
                "the bounded dependency cone was not reopened without erasing closure history",
            ));
        }
        check_digests(&self.retained_certificate_digests)?;
        if self.dependency_edges.is_empty() {
            return Err(invalid("the reopened frontier has no dependency edges"));
        }
        for edge in &self.dependency_edges {
            check_digest(&edge.receipt_digest)?;
        }
        Ok(())
    }
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct ClosureTransportEvidenceV0 {
    pub residual_frontier: ClosureTransportFrontierV0,
    pub counterevidence_admitted: CheckStatus,
    pub counterevidence_class: ClosureFindingClassV0,
    pub counterevidence_proves_falsity: CheckStatus,
    pub certificates_remain_append_only: CheckStatus,
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct ClosureTransportInputV0 {
    pub subject: LocalClosureCandidateV0,
    pub method: ClosureTransportContractV0,
    pub object: ClosureTransportPlanV0,
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct ClosureTransportOutputV0 {
    pub history: ClosureTransportHistoryV0,
    pub result: ClosureTransportResultV0,
    pub evidence: ClosureTransportEvidenceV0,
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct ClosureTransportTransitionV0 {
    pub schema: String,
    pub version: u32,
    pub interface: InquiryInterfaceV0,
    pub input: ClosureTransportInputV0,
    pub output: ClosureTransportOutputV0,
}

impl ClosureTransportTransitionV0 {
    pub fn from_json(source: &str) -> Result<Self, ClosureTransportErrorV0> {
        let artifact: Self = serde_json::from_str(source)
            .map_err(|error| ClosureTransportErrorV0::Json(error.to_string()))?;
        artifact.check()?;
        Ok(artifact)
    }

    pub fn to_json(&self) -> Result<String, ClosureTransportErrorV0> {
        self.check()?;
        pretty_json(self)
    }

    pub fn digest(&self) -> Result<String, ClosureTransportErrorV0> {
        digest_serialized(self)
    }

    pub fn check(&self) -> Result<(), ClosureTransportErrorV0> {
        check_header(
            &self.schema,
            self.version,
            CLOSURE_TRANSPORT_TRANSITION_SCHEMA_V0,
            &self.interface,
        )?;
        let expected =
            run_closure_transport_v0(&self.input.subject, &self.input.method, &self.input.object)?;
        if self.output != expected.output {
            return Err(invalid(
                "closure transport output does not replay from its three inputs",
            ));
        }
        Ok(())
    }
}

pub fn run_closure_transport_v0(
    subject: &LocalClosureCandidateV0,
    method: &ClosureTransportContractV0,
    object: &ClosureTransportPlanV0,
) -> Result<ClosureTransportTransitionV0, ClosureTransportErrorV0> {
    subject.check()?;
    method.check()?;
    object.check()?;
    if subject.unit != method.supported_unit || object.local_scope.unit != method.supported_unit {
        return Err(invalid(
            "the three input slots do not agree on a typed unit",
        ));
    }

    let local = certify(
        object.local_scope.clone(),
        subject.before.clone(),
        subject.after.clone(),
    )?;
    let (stage_one, stage_one_receipt) = transport(&local, &object.stage_one)?;
    let (staged, stage_two_receipt) = transport(&stage_one, &object.stage_two)?;
    let (direct, direct_receipt) = transport(&local, &object.direct)?;

    let composed = substitute(&object.stage_two.context, &object.stage_one.context);
    if composed != object.direct.context {
        return Err(invalid(
            "the direct scope map is not the exact map composition",
        ));
    }
    if staged != direct {
        return Err(invalid(
            "direct and staged transport do not yield the same scoped certificate",
        ));
    }
    if stage_two_receipt == direct_receipt {
        return Err(invalid(
            "direct and staged transport histories were collapsed",
        ));
    }

    let common_result_content_digest = direct.content_digest()?;
    let adversarial_separation = first_adversarial_separation()?;
    let negative_controls = object
        .negative_targets
        .clone()
        .map(|target| reject_wrong_unit(&local, target));
    if negative_controls.iter().any(|outcome| outcome.accepted) {
        return Err(invalid(
            "a negative import control was unexpectedly admitted",
        ));
    }

    let dependency_edges = vec![
        dependency_edge(&stage_one_receipt)?,
        dependency_edge(&stage_two_receipt)?,
        dependency_edge(&direct_receipt)?,
    ];
    let closed_before_challenge = sorted_scopes([
        object.local_scope.coordinate.clone(),
        object.stage_one.target.coordinate.clone(),
        object.stage_two.target.coordinate.clone(),
    ]);
    let reopened_after_challenge =
        propagate_reopen(&object.counterevidence.challenged_scope, &dependency_edges);
    if reopened_after_challenge != closed_before_challenge {
        return Err(invalid(
            "counterevidence did not reopen the complete bounded dependency cone",
        ));
    }

    let retained_certificate_digests = vec![
        local.digest()?,
        stage_one.digest()?,
        staged.digest()?,
        direct.digest()?,
    ];
    let residual_frontier = ClosureTransportFrontierV0 {
        schema: CLOSURE_TRANSPORT_FRONTIER_SCHEMA_V0.to_owned(),
        version: CLOSURE_TRANSPORT_VERSION_V0,
        interface: InquiryInterfaceV0::canonical(),
        state: ClosureFrontierStateV0::Reopened,
        challenge: object.counterevidence.clone(),
        challenge_digest: object.counterevidence.digest()?,
        closed_before_challenge,
        reopened_after_challenge,
        dependency_edges,
        retained_certificate_digests,
    };
    residual_frontier.check()?;

    let output = ClosureTransportOutputV0 {
        history: ClosureTransportHistoryV0 {
            mechanism: MechanismV0::Verify,
            subject_digest: subject.digest()?,
            method_digest: method.digest()?,
            object_digest: object.digest()?,
            local_certificate_digest: local.digest()?,
            stage_one: stage_one_receipt,
            stage_two: stage_two_receipt,
            direct: direct_receipt,
        },
        result: ClosureTransportResultV0 {
            local,
            stage_one,
            staged,
            direct,
            coherence: TransportCoherenceV0 {
                local_closure: CheckStatus::Checked,
                composed_scope_map: CheckStatus::Checked,
                direct_equals_staged: CheckStatus::Checked,
                distinct_histories_retained: CheckStatus::Checked,
                common_result_content_digest,
            },
            adversarial_separation,
            negative_controls,
        },
        evidence: ClosureTransportEvidenceV0 {
            residual_frontier,
            counterevidence_admitted: CheckStatus::Checked,
            counterevidence_class: ClosureFindingClassV0::Challenge,
            counterevidence_proves_falsity: CheckStatus::Unchecked,
            certificates_remain_append_only: CheckStatus::Checked,
        },
    };
    Ok(ClosureTransportTransitionV0 {
        schema: CLOSURE_TRANSPORT_TRANSITION_SCHEMA_V0.to_owned(),
        version: CLOSURE_TRANSPORT_VERSION_V0,
        interface: InquiryInterfaceV0::canonical(),
        input: ClosureTransportInputV0 {
            subject: subject.clone(),
            method: method.clone(),
            object: object.clone(),
        },
        output,
    })
}

fn certify(
    scope: ClosureScopeV0,
    before: ExactExprV0,
    after: ExactExprV0,
) -> Result<PolynomialClosureCertificateV0, ClosureTransportErrorV0> {
    let before_normal = before.normalize()?;
    let after_normal = after.normalize()?;
    if before_normal != after_normal {
        return Err(invalid(
            "the local candidate does not normalize to equality",
        ));
    }
    let mut store = WitnessStoreV0::new();
    let transition = store.insert(WitnessProofV0::ArithmeticTransition {
        actual_boundary: BoundaryChargeV0::zero(),
        declared_boundary: BoundaryChargeV0::zero(),
        before: before.clone(),
        after: after.clone(),
    })?;
    let sealed_witness = store.insert(WitnessProofV0::Seal {
        body: transition.clone(),
    })?;
    let witness_graph = [transition, sealed_witness.clone()]
        .iter()
        .map(|key| {
            store
                .artifact(key)
                .cloned()
                .ok_or_else(|| invalid("newly constructed witness artifact is absent"))
        })
        .collect::<Result<Vec<_>, _>>()?;
    let certificate = PolynomialClosureCertificateV0 {
        schema: POLYNOMIAL_CLOSURE_CERTIFICATE_SCHEMA_V0.to_owned(),
        version: CLOSURE_TRANSPORT_VERSION_V0,
        interface: InquiryInterfaceV0::canonical(),
        content: PolynomialClosureContentV0 {
            name: format!("identity:{}", scope.coordinate.as_str()),
            class: ClosureFindingClassV0::Identity,
            scope,
            unit: ClosureUnitV0::ExactPolynomialIdentity,
            before,
            after,
            normal_form: before_normal,
        },
        witness_graph,
        sealed_witness,
    };
    certificate.check()?;
    Ok(certificate)
}

fn transport(
    source: &PolynomialClosureCertificateV0,
    map: &ScopeMapV0,
) -> Result<(PolynomialClosureCertificateV0, TransportReceiptV0), ClosureTransportErrorV0> {
    source.check()?;
    map.check()?;
    if source.content.scope != map.source {
        return Err(invalid(
            "scope map source does not match the supplied certificate",
        ));
    }
    let result = certify(
        map.target.clone(),
        substitute(&map.context, &source.content.before),
        substitute(&map.context, &source.content.after),
    )?;
    let receipt = TransportReceiptV0 {
        map_coordinate: map.coordinate.clone(),
        map_digest: map.digest()?,
        source_scope: map.source.coordinate.clone(),
        target_scope: map.target.coordinate.clone(),
        source_occurrence: map.source.occurrence.clone(),
        target_occurrence: map.target.occurrence.clone(),
        source_certificate_digest: source.digest()?,
        result_certificate_digest: result.digest()?,
        result_content_digest: result.content_digest()?,
    };
    Ok((result, receipt))
}

fn substitute(context: &ExactExprV0, replacement: &ExactExprV0) -> ExactExprV0 {
    match context {
        ExactExprV0::Constant { value } => ExactExprV0::constant(value.clone()),
        ExactExprV0::Variable { name } if name == SLOT_VARIABLE => replacement.clone(),
        ExactExprV0::Variable { name } => ExactExprV0::variable(name.clone()),
        ExactExprV0::Add { left, right } => ExactExprV0::sum(
            substitute(left, replacement),
            substitute(right, replacement),
        ),
        ExactExprV0::Multiply { left, right } => ExactExprV0::product(
            substitute(left, replacement),
            substitute(right, replacement),
        ),
    }
}

fn reject_wrong_unit(
    source: &PolynomialClosureCertificateV0,
    target: NegativeImportTargetV0,
) -> NegativeImportOutcomeV0 {
    NegativeImportOutcomeV0 {
        class: ClosureFindingClassV0::Incommensurate,
        supplied_unit: source.content.unit,
        accepted: source.content.unit == target.required_unit,
        residual: RejectionResidualV0::TargetHolePreserved,
        reason: format!(
            "typed import requires {:?}; certificate supplies {:?}",
            target.required_unit, source.content.unit
        ),
        target,
    }
}

fn first_adversarial_separation()
-> Result<PolynomialSeparationCertificateV0, ClosureTransportErrorV0> {
    let a = ExactExprV0::variable("a");
    let x = ExactExprV0::variable("x");
    let y = ExactExprV0::variable("y");
    let before = ExactExprV0::product(a.clone(), ExactExprV0::sum(x.clone(), y.clone()));
    let after = ExactExprV0::sum(ExactExprV0::product(a, x), y);
    let environment: BTreeMap<String, num_bigint::BigInt> = BTreeMap::from([
        ("a".to_owned(), 2.into()),
        ("x".to_owned(), 3.into()),
        ("y".to_owned(), 5.into()),
    ]);
    let certificate = PolynomialSeparationCertificateV0 {
        schema: POLYNOMIAL_SEPARATION_CERTIFICATE_SCHEMA_V0.to_owned(),
        version: CLOSURE_TRANSPORT_VERSION_V0,
        interface: InquiryInterfaceV0::canonical(),
        name: "separation:omitted-y-factor".to_owned(),
        class: ClosureFindingClassV0::Separation,
        unit: ClosureUnitV0::ExactPolynomialIdentity,
        before_normal_form: before.normalize()?,
        after_normal_form: after.normalize()?,
        counterexample: environment
            .iter()
            .map(|(variable, value)| ExactVariableValueV0 {
                variable: variable.clone(),
                value: value.clone(),
            })
            .collect(),
        before_value: before.evaluate_guarded(&environment)?,
        after_value: after.evaluate_guarded(&environment)?,
        before,
        after,
    };
    certificate.check()?;
    Ok(certificate)
}

fn dependency_edge(
    receipt: &TransportReceiptV0,
) -> Result<ClosureDependencyEdgeV0, ClosureTransportErrorV0> {
    Ok(ClosureDependencyEdgeV0 {
        source: receipt.source_scope.clone(),
        target: receipt.target_scope.clone(),
        receipt_digest: receipt.digest()?,
    })
}

fn propagate_reopen(root: &ArtifactKeyV0, edges: &[ClosureDependencyEdgeV0]) -> Vec<ArtifactKeyV0> {
    let mut reopened = BTreeSet::from([root.clone()]);
    loop {
        let next = edges
            .iter()
            .filter(|edge| reopened.contains(&edge.source))
            .map(|edge| edge.target.clone())
            .filter(|target| !reopened.contains(target))
            .collect::<Vec<_>>();
        if next.is_empty() {
            break;
        }
        reopened.extend(next);
    }
    reopened.into_iter().collect()
}

fn sorted_scopes<const N: usize>(scopes: [ArtifactKeyV0; N]) -> Vec<ArtifactKeyV0> {
    scopes
        .into_iter()
        .collect::<BTreeSet<_>>()
        .into_iter()
        .collect()
}

fn check_sorted_unique(values: &[ArtifactKeyV0]) -> Result<(), ClosureTransportErrorV0> {
    let expected = values.iter().cloned().collect::<BTreeSet<_>>();
    if values.iter().ne(expected.iter()) {
        return Err(invalid("scope coordinates must be sorted and unique"));
    }
    Ok(())
}

pub fn load_local_closure_candidate_v0(
    path: impl AsRef<Path>,
) -> Result<LocalClosureCandidateV0, ClosureTransportErrorV0> {
    load_checked(path, LocalClosureCandidateV0::from_json)
}

pub fn load_closure_transport_contract_v0(
    path: impl AsRef<Path>,
) -> Result<ClosureTransportContractV0, ClosureTransportErrorV0> {
    load_checked(path, ClosureTransportContractV0::from_json)
}

pub fn load_closure_transport_plan_v0(
    path: impl AsRef<Path>,
) -> Result<ClosureTransportPlanV0, ClosureTransportErrorV0> {
    load_checked(path, ClosureTransportPlanV0::from_json)
}

pub fn load_closure_transport_frontier_v0(
    path: impl AsRef<Path>,
) -> Result<ClosureTransportFrontierV0, ClosureTransportErrorV0> {
    load_checked(path, ClosureTransportFrontierV0::from_json)
}

pub fn load_closure_transport_transition_v0(
    path: impl AsRef<Path>,
) -> Result<ClosureTransportTransitionV0, ClosureTransportErrorV0> {
    load_checked(path, ClosureTransportTransitionV0::from_json)
}

pub fn save_closure_transport_frontier_v0(
    path: impl AsRef<Path>,
    frontier: &ClosureTransportFrontierV0,
) -> Result<InquirySaveReceiptV0, ClosureTransportErrorV0> {
    save_checked(path, frontier.to_json()?)
}

pub fn save_closure_transport_transition_v0(
    path: impl AsRef<Path>,
    transition: &ClosureTransportTransitionV0,
) -> Result<InquirySaveReceiptV0, ClosureTransportErrorV0> {
    save_checked(path, transition.to_json()?)
}

fn key(value: impl Into<String>) -> ArtifactKeyV0 {
    ArtifactKeyV0::cache_label(value).expect("frozen experiment keys are nonempty")
}

fn check_header(
    schema: &str,
    version: u32,
    expected_schema: &str,
    interface: &InquiryInterfaceV0,
) -> Result<(), ClosureTransportErrorV0> {
    if schema != expected_schema
        || version != CLOSURE_TRANSPORT_VERSION_V0
        || interface != &InquiryInterfaceV0::canonical()
        || interface.inputs != InputLabelV0::ALL
        || interface.outputs != OutputLabelV0::ALL
    {
        return Err(invalid(
            "unsupported closure transport schema, version, or three-port interface",
        ));
    }
    Ok(())
}

fn check_digests(digests: &[String]) -> Result<(), ClosureTransportErrorV0> {
    for digest in digests {
        check_digest(digest)?;
    }
    Ok(())
}

fn check_digest(digest: &str) -> Result<(), ClosureTransportErrorV0> {
    let Some(hex) = digest.strip_prefix("blake3:") else {
        return Err(invalid(
            "a closure transport digest must be a BLAKE3 coordinate",
        ));
    };
    if hex.len() != 64
        || !hex
            .bytes()
            .all(|byte| byte.is_ascii_digit() || (b'a'..=b'f').contains(&byte))
    {
        return Err(invalid(
            "a closure transport digest must be a lowercase BLAKE3 coordinate",
        ));
    }
    Ok(())
}

fn pretty_json<T: Serialize>(value: &T) -> Result<String, ClosureTransportErrorV0> {
    serde_json::to_string_pretty(value)
        .map_err(|error| ClosureTransportErrorV0::Json(error.to_string()))
}

fn digest_serialized<T: Serialize>(value: &T) -> Result<String, ClosureTransportErrorV0> {
    let encoded = format!("{}\n", pretty_json(value)?);
    Ok(format!(
        "blake3:{}",
        blake3::hash(encoded.as_bytes()).to_hex()
    ))
}

fn invalid(detail: impl Into<String>) -> ClosureTransportErrorV0 {
    ClosureTransportErrorV0::InvalidArtifact(detail.into())
}

fn require_adva(path: &Path) -> Result<(), ClosureTransportErrorV0> {
    crate::persistence::require_adva_extension(path)
        .map_err(|error| ClosureTransportErrorV0::Persistence(error.to_string()))
}

fn read_source(path: &Path) -> Result<String, ClosureTransportErrorV0> {
    fs::read_to_string(path).map_err(|error| ClosureTransportErrorV0::Io {
        path: path.to_path_buf(),
        detail: error.to_string(),
    })
}

fn load_checked<T>(
    path: impl AsRef<Path>,
    decode: impl FnOnce(&str) -> Result<T, ClosureTransportErrorV0>,
) -> Result<T, ClosureTransportErrorV0> {
    let path = path.as_ref();
    require_adva(path)?;
    decode(&read_source(path)?)
}

fn save_checked(
    path: impl AsRef<Path>,
    json: String,
) -> Result<InquirySaveReceiptV0, ClosureTransportErrorV0> {
    let path = path.as_ref();
    require_adva(path)?;
    let encoded = format!("{json}\n");
    crate::persistence::write_atomically(path, encoded.as_bytes())
        .map_err(|error| ClosureTransportErrorV0::Persistence(error.to_string()))?;
    Ok(InquirySaveReceiptV0 {
        path: path.to_path_buf(),
        artifact_digest: format!("blake3:{}", blake3::hash(encoded.as_bytes()).to_hex()),
        bytes_written: u64::try_from(encoded.len()).unwrap_or(u64::MAX),
    })
}

#[derive(Debug, Error)]
pub enum ClosureTransportErrorV0 {
    #[error("invalid closure transport artifact: {0}")]
    InvalidArtifact(String),
    #[error("closure transport JSON error: {0}")]
    Json(String),
    #[error("closure transport persistence error: {0}")]
    Persistence(String),
    #[error("I/O error at {path:?}: {detail}")]
    Io { path: PathBuf, detail: String },
    #[error(transparent)]
    Arithmetic(#[from] crate::ArithmeticErrorV0),
    #[error(transparent)]
    Witness(#[from] WitnessErrorV0),
}
