use crate::{ArtifactKeyV0, RoleV0};
use serde::{Deserialize, Serialize};
use std::collections::{BTreeMap, BTreeSet};
use thiserror::Error;

/// Candidate common suffix for neutral Adva carriers.
///
/// This research constant does not change the current Lisp parser or the
/// stable `adva.ir` version-one JSON boundary.
pub const ADVA_FILE_SUFFIX_V0: &str = "adva";

/// The three process labels. They describe edges, not persistent carrier
/// kinds.
#[derive(Clone, Copy, Debug, Eq, Ord, PartialEq, PartialOrd, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum MechanismV0 {
    Compute,
    Verify,
    Learn,
}

impl MechanismV0 {
    pub const ALL: [Self; 3] = [Self::Compute, Self::Verify, Self::Learn];

    #[must_use]
    pub const fn as_str(self) -> &'static str {
        match self {
            Self::Compute => "compute",
            Self::Verify => "verify",
            Self::Learn => "learn",
        }
    }
}

/// The three labels used when a neutral carrier is unpacked for one step.
#[derive(Clone, Copy, Debug, Eq, Ord, PartialEq, PartialOrd, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum InputLabelV0 {
    Subject,
    Method,
    Object,
}

impl InputLabelV0 {
    pub const ALL: [Self; 3] = [Self::Subject, Self::Method, Self::Object];
}

/// The three labels used when one step is packed into neutral carriers.
#[derive(Clone, Copy, Debug, Eq, Ord, PartialEq, PartialOrd, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum OutputLabelV0 {
    History,
    Result,
    Evidence,
}

impl OutputLabelV0 {
    pub const ALL: [Self; 3] = [Self::History, Self::Result, Self::Evidence];
}

/// One research-local coordinate on a carrier's open frontier.
///
/// It is deliberately not an `adva.ir` hole, cut port, logical obligation,
/// or semantic identity. `hole` and `occurrence` retain caller-supplied finite
/// coordinates only.
#[derive(Clone, Debug, Eq, Ord, PartialEq, PartialOrd, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct FrontierSiteV0 {
    pub role: RoleV0,
    pub hole: u8,
    pub occurrence: u32,
}

impl FrontierSiteV0 {
    #[must_use]
    pub const fn new(role: RoleV0, hole: u8, occurrence: u32) -> Self {
        Self {
            role,
            hole,
            occurrence,
        }
    }

    const fn coordinate(&self) -> (u8, u32) {
        (self.hole, self.occurrence)
    }
}

/// Canonical finite set of research-local open-frontier sites.
#[derive(Clone, Debug, Default, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct OpenFrontierV0 {
    sites: Vec<FrontierSiteV0>,
}

impl OpenFrontierV0 {
    #[must_use]
    pub const fn closed() -> Self {
        Self { sites: Vec::new() }
    }

    /// Canonicalize a finite open frontier.
    ///
    /// # Errors
    ///
    /// Rejects two sites that claim the same local hole/occurrence coordinate,
    /// including two different roles at that coordinate.
    pub fn from_sites(
        sites: impl IntoIterator<Item = FrontierSiteV0>,
    ) -> Result<Self, MechanismSyntaxErrorV0> {
        let mut by_coordinate = BTreeMap::new();
        for site in sites {
            let coordinate = site.coordinate();
            if by_coordinate.insert(coordinate, site).is_some() {
                return Err(MechanismSyntaxErrorV0::DuplicateFrontierCoordinate {
                    hole: coordinate.0,
                    occurrence: coordinate.1,
                });
            }
        }
        let mut sites = by_coordinate.into_values().collect::<Vec<_>>();
        sites.sort();
        Ok(Self { sites })
    }

    #[must_use]
    pub fn sites(&self) -> &[FrontierSiteV0] {
        &self.sites
    }

    #[must_use]
    pub fn is_empty(&self) -> bool {
        self.sites.is_empty()
    }

    fn as_set(&self) -> BTreeSet<FrontierSiteV0> {
        self.sites.iter().cloned().collect()
    }

    fn from_set(sites: BTreeSet<FrontierSiteV0>) -> Self {
        Self {
            sites: sites.into_iter().collect(),
        }
    }
}

/// One carrier with neutral content and an explicitly retained open frontier.
///
/// `structure` is a witness-store cache coordinate, not a program, source, or
/// occurrence identity. Program, proof, and model are mechanism-relative
/// readings and therefore do not appear as carrier variants.
#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct NeutralCarrierV0 {
    pub structure: ArtifactKeyV0,
    pub frontier: OpenFrontierV0,
}

/// The fixed three-input outer form shared by all mechanisms.
#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct MechanismInputV0 {
    pub subject: NeutralCarrierV0,
    pub method: NeutralCarrierV0,
    pub object: NeutralCarrierV0,
}

/// The fixed three-output outer form shared by all mechanisms.
///
/// These fields are the candidate persistence labels. The carriers themselves
/// remain neutral and can be relabelled into a later input form only through
/// an explicit substitution record.
#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct MechanismOutputV0 {
    pub history: NeutralCarrierV0,
    pub result: NeutralCarrierV0,
    pub evidence: NeutralCarrierV0,
}

/// An explicit explanation for a declared verification site no longer present
/// on the subject frontier.
#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct DischargeV0 {
    pub site: FrontierSiteV0,
    pub witness: ArtifactKeyV0,
}

/// One proposed replacement for one currently open subject site.
#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct FillAssignmentV0 {
    pub target: FrontierSiteV0,
    pub replacement: NeutralCarrierV0,
    /// Optional candidate evidence. Its presence does not make the proposal a
    /// verified substitution or a semantic certificate.
    pub evidence: Option<ArtifactKeyV0>,
}

/// A finite, possibly partial learning proposal.
#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct FillPlanV0 {
    pub assignments: Vec<FillAssignmentV0>,
}

/// The three mechanism forms checked by this bounded grammar.
#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(tag = "mechanism", rename_all = "snake_case")]
pub enum MechanismFormV0 {
    Compute {
        input: MechanismInputV0,
    },
    Verify {
        input: MechanismInputV0,
        declared_subject: OpenFrontierV0,
        discharges: Vec<DischargeV0>,
    },
    Learn {
        input: MechanismInputV0,
        plan: FillPlanV0,
    },
}

impl MechanismFormV0 {
    #[must_use]
    pub const fn mechanism(&self) -> MechanismV0 {
        match self {
            Self::Compute { .. } => MechanismV0::Compute,
            Self::Verify { .. } => MechanismV0::Verify,
            Self::Learn { .. } => MechanismV0::Learn,
        }
    }

    /// Check one local three-input form without executing, proving, or
    /// synthesizing its contents.
    ///
    /// # Errors
    ///
    /// Computation rejects open subjects and objects. Verification rejects
    /// undeclared, multiply discharged, or unexplained missing sites. Learning
    /// requires a nonempty open subject and a nonempty, collision-free partial
    /// fill plan.
    pub fn check(&self) -> Result<MechanismAdmissionV0, MechanismSyntaxErrorV0> {
        match self {
            Self::Compute { input } => check_compute(input),
            Self::Verify {
                input,
                declared_subject,
                discharges,
            } => check_verify(input, declared_subject, discharges),
            Self::Learn { input, plan } => check_learn(input, plan),
        }
    }
}

/// A successful bounded syntax judgment.
#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(tag = "mechanism", rename_all = "snake_case")]
pub enum MechanismAdmissionV0 {
    Compute {
        /// The method frontier is retained rather than mistaken for a runtime
        /// error. Existing instantiation/execution checks remain authoritative.
        method_frontier: OpenFrontierV0,
    },
    Verify {
        status: VerificationStatusV0,
        remaining_subject: OpenFrontierV0,
    },
    Learn {
        filled_subject: OpenFrontierV0,
        remaining_subject: OpenFrontierV0,
    },
}

#[derive(Clone, Copy, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum VerificationStatusV0 {
    Closed,
    Conditional,
}

fn check_compute(input: &MechanismInputV0) -> Result<MechanismAdmissionV0, MechanismSyntaxErrorV0> {
    if !input.subject.frontier.is_empty() {
        return Err(MechanismSyntaxErrorV0::OpenComputeSubject(
            input.subject.frontier.clone(),
        ));
    }
    if !input.object.frontier.is_empty() {
        return Err(MechanismSyntaxErrorV0::OpenComputeObject(
            input.object.frontier.clone(),
        ));
    }
    Ok(MechanismAdmissionV0::Compute {
        method_frontier: input.method.frontier.clone(),
    })
}

fn check_verify(
    input: &MechanismInputV0,
    declared_subject: &OpenFrontierV0,
    discharges: &[DischargeV0],
) -> Result<MechanismAdmissionV0, MechanismSyntaxErrorV0> {
    let actual = input.subject.frontier.as_set();
    let declared = declared_subject.as_set();
    let extra = actual.difference(&declared).cloned().collect::<Vec<_>>();
    if !extra.is_empty() {
        return Err(MechanismSyntaxErrorV0::UndeclaredVerificationSites(extra));
    }

    let mut discharged = BTreeSet::new();
    for discharge in discharges {
        if !declared.contains(&discharge.site) {
            return Err(MechanismSyntaxErrorV0::UndeclaredDischarge(
                discharge.site.clone(),
            ));
        }
        if actual.contains(&discharge.site) {
            return Err(MechanismSyntaxErrorV0::DischargedOpenSite(
                discharge.site.clone(),
            ));
        }
        if !discharged.insert(discharge.site.clone()) {
            return Err(MechanismSyntaxErrorV0::RepeatedDischarge(
                discharge.site.clone(),
            ));
        }
    }

    let accounted = actual.union(&discharged).cloned().collect::<BTreeSet<_>>();
    let missing = declared.difference(&accounted).cloned().collect::<Vec<_>>();
    if !missing.is_empty() {
        return Err(MechanismSyntaxErrorV0::UnaccountedDeclaredSites(missing));
    }

    Ok(MechanismAdmissionV0::Verify {
        status: if actual.is_empty() {
            VerificationStatusV0::Closed
        } else {
            VerificationStatusV0::Conditional
        },
        remaining_subject: input.subject.frontier.clone(),
    })
}

fn check_learn(
    input: &MechanismInputV0,
    plan: &FillPlanV0,
) -> Result<MechanismAdmissionV0, MechanismSyntaxErrorV0> {
    if input.subject.frontier.is_empty() {
        return Err(MechanismSyntaxErrorV0::ClosedLearningSubject);
    }
    if plan.assignments.is_empty() {
        return Err(MechanismSyntaxErrorV0::EmptyLearningPlan);
    }

    let before = input.subject.frontier.as_set();
    let mut targets = BTreeSet::new();
    for assignment in &plan.assignments {
        if !before.contains(&assignment.target) {
            return Err(MechanismSyntaxErrorV0::UnknownLearningTarget(
                assignment.target.clone(),
            ));
        }
        if !targets.insert(assignment.target.clone()) {
            return Err(MechanismSyntaxErrorV0::RepeatedLearningTarget(
                assignment.target.clone(),
            ));
        }
    }

    let mut remaining = before
        .difference(&targets)
        .cloned()
        .collect::<BTreeSet<_>>();
    let mut remaining_coordinates = remaining
        .iter()
        .map(FrontierSiteV0::coordinate)
        .collect::<BTreeSet<_>>();
    for assignment in &plan.assignments {
        for opened in assignment.replacement.frontier.sites() {
            if !remaining_coordinates.insert(opened.coordinate()) {
                return Err(MechanismSyntaxErrorV0::ReplacementFrontierCollision(
                    opened.clone(),
                ));
            }
            remaining.insert(opened.clone());
        }
    }

    Ok(MechanismAdmissionV0::Learn {
        filled_subject: OpenFrontierV0::from_set(targets),
        remaining_subject: OpenFrontierV0::from_set(remaining),
    })
}

#[derive(Clone, Debug, Eq, Error, PartialEq)]
pub enum MechanismSyntaxErrorV0 {
    #[error("frontier coordinate ({hole}, {occurrence}) occurs more than once")]
    DuplicateFrontierCoordinate { hole: u8, occurrence: u32 },
    #[error("compute subject retains open frontier {0:?}")]
    OpenComputeSubject(OpenFrontierV0),
    #[error("compute object retains open frontier {0:?}")]
    OpenComputeObject(OpenFrontierV0),
    #[error("verification subject has undeclared sites {0:?}")]
    UndeclaredVerificationSites(Vec<FrontierSiteV0>),
    #[error("verification discharges undeclared site {0:?}")]
    UndeclaredDischarge(FrontierSiteV0),
    #[error("verification site is both open and discharged {0:?}")]
    DischargedOpenSite(FrontierSiteV0),
    #[error("verification site is discharged more than once {0:?}")]
    RepeatedDischarge(FrontierSiteV0),
    #[error("declared verification sites are neither open nor discharged {0:?}")]
    UnaccountedDeclaredSites(Vec<FrontierSiteV0>),
    #[error("learning requires an open subject frontier")]
    ClosedLearningSubject,
    #[error("learning requires at least one proposed filling")]
    EmptyLearningPlan,
    #[error("learning plan targets a site outside the subject frontier {0:?}")]
    UnknownLearningTarget(FrontierSiteV0),
    #[error("learning plan targets one site more than once {0:?}")]
    RepeatedLearningTarget(FrontierSiteV0),
    #[error("replacement frontiers collide at {0:?}")]
    ReplacementFrontierCollision(FrontierSiteV0),
}
