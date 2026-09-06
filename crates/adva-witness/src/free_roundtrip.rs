//! Fixed research protocol: six calls, explicit reverse endpoints, retained guards.
//!
//! This is not a learned grammar, a generic inverse, or a definition of `free`.
//! Fuel counts protocol stages. Replay and arithmetic costs are reported separately.

use crate::{
    ArithmeticErrorV0, ArtifactKeyV0, BoundaryChargeV0, BoundaryCoordinateV0, BoundaryTermV0,
    ExactExprV0, RoleV0, TermGlyphV0, WitnessProofV0, WitnessStoreV0,
};
use num_bigint::BigInt;
use serde::{Deserialize, Serialize};
use std::collections::BTreeMap;
use std::error::Error;
use std::fs::{File, OpenOptions};
use std::io::{self, Read, Write};
use std::path::Path;

pub const FREE_ROUNDTRIP_CONTRACT_SCHEMA_V0: &str = "adva.free-roundtrip.contract.v0";
const SUBJECT_SCHEMA: &str = "adva.free-roundtrip.frontier.v0";
const RESOURCE_SCHEMA: &str = "adva.free-roundtrip.resource.v0";
const OUTPUT_SCHEMA: &str = "adva.free-roundtrip.transition.v0";
const MAX_BYTES: usize = 128 * 1024;
type RunResult<T> = Result<T, Box<dyn Error>>;

fn invalid(message: &str) -> Box<dyn Error> {
    io::Error::new(io::ErrorKind::InvalidData, message).into()
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
struct Contract {
    schema: String,
    version: u32,
    max_calls: u8,
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
struct Resource {
    schema: String,
    version: u32,
    account: String,
    total_fuel: u8,
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
struct Subject {
    schema: String,
    version: u32,
    account: String,
    values: [i32; 3],
    history: Vec<StageRecord>,
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(tag = "state", rename_all = "snake_case", deny_unknown_fields)]
enum Guard {
    NotRun,
    Passed { value: String },
    Failed { expression: String },
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
struct StageRecord {
    input_binding: String,
    stage: u8,
    spent: u8,
    remaining: u8,
    action: String,
    artifact: String,
    additive_zero: bool,
    multiplicative_one: bool,
    reverse_requested: bool,
    guard: Guard,
    local_close: bool,
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
struct LocalEvidence {
    local_name: String,
    free_status: String,
    p: String,
    q: String,
    value: String,
    sealed_artifact: String,
    protected_obligations: Vec<String>,
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
struct Transition {
    schema: String,
    version: u32,
    input: Subject,
    output: Subject,
    replayed_prior_stages: usize,
    new_stages: u8,
    evidence: Option<LocalEvidence>,
}

fn expressions() -> (ExactExprV0, ExactExprV0) {
    let p = ExactExprV0::sum(
        ExactExprV0::variable("x"),
        ExactExprV0::product(ExactExprV0::variable("y"), ExactExprV0::variable("z")),
    );
    let q = ExactExprV0::product(ExactExprV0::constant(2), p.clone());
    (p, q)
}

fn common_boundary() -> RunResult<BoundaryChargeV0> {
    Ok(BoundaryChargeV0::from_terms([
        BoundaryTermV0::new(
            BoundaryCoordinateV0::Role {
                role: RoleV0::Construction,
            },
            1,
        ),
        BoundaryTermV0::new(
            BoundaryCoordinateV0::Role {
                role: RoleV0::Space,
            },
            1,
        ),
        BoundaryTermV0::new(BoundaryCoordinateV0::Role { role: RoleV0::Time }, 1),
    ])?)
}

fn matching_reverse(
    before: &ExactExprV0,
    after: &ExactExprV0,
    reverse_before: &ExactExprV0,
    reverse_after: &ExactExprV0,
) -> bool {
    after == reverse_before && before == reverse_after
}

struct Replay {
    store: WitnessStoreV0,
    unit: Option<ArtifactKeyV0>,
    forward: Option<ArtifactKeyV0>,
    reverse: Option<ArtifactKeyV0>,
    composed: Option<ArtifactKeyV0>,
    guard: Guard,
}

impl Replay {
    fn new() -> Self {
        Self {
            store: WitnessStoreV0::new(),
            unit: None,
            forward: None,
            reverse: None,
            composed: None,
            guard: Guard::NotRun,
        }
    }

    fn step(&mut self, stage: u8, values: [i32; 3], account: &str) -> RunResult<StageRecord> {
        let (p, q) = expressions();
        let boundary = common_boundary()?;
        let (action, key) = match stage {
            1 => {
                let key = self.store.insert(WitnessProofV0::Seed {
                    term: TermGlyphV0::Unit,
                })?;
                self.unit = Some(key.clone());
                ("form_common_boundary", key)
            }
            2 => {
                let key = self.store.insert(WitnessProofV0::ArithmeticTransition {
                    actual_boundary: boundary.clone(),
                    declared_boundary: boundary,
                    before: p,
                    after: q,
                })?;
                self.forward = Some(key.clone());
                ("forward_and_request_reverse", key)
            }
            3 => {
                let forward = self
                    .store
                    .artifact(
                        self.forward
                            .as_ref()
                            .ok_or_else(|| invalid("missing forward"))?,
                    )
                    .ok_or_else(|| invalid("missing forward artifact"))?;
                let WitnessProofV0::ArithmeticTransition { before, after, .. } = &forward.proof
                else {
                    return Err(invalid("forward is not an arithmetic transition"));
                };
                if !matching_reverse(before, after, &q, &p) {
                    return Err(invalid("reverse endpoints do not match"));
                }
                let key = self.store.insert(WitnessProofV0::ArithmeticTransition {
                    actual_boundary: boundary.clone(),
                    declared_boundary: boundary,
                    before: q,
                    after: p,
                })?;
                self.reverse = Some(key.clone());
                ("reverse_known_endpoints", key)
            }
            4 => {
                let key = self.store.insert(WitnessProofV0::Compose {
                    left: self
                        .forward
                        .clone()
                        .ok_or_else(|| invalid("missing forward"))?,
                    connector: self.unit.clone().ok_or_else(|| invalid("missing unit"))?,
                    right: self
                        .reverse
                        .clone()
                        .ok_or_else(|| invalid("missing reverse"))?,
                })?;
                self.composed = Some(key.clone());
                ("compose_retaining_guards", key)
            }
            5 => {
                let key = self
                    .composed
                    .clone()
                    .ok_or_else(|| invalid("missing composition"))?;
                let artifact = self
                    .store
                    .artifact(&key)
                    .ok_or_else(|| invalid("missing composition artifact"))?;
                let environment = BTreeMap::from([
                    ("x".to_owned(), BigInt::from(values[0])),
                    ("y".to_owned(), BigInt::from(values[1])),
                    ("z".to_owned(), BigInt::from(values[2])),
                ]);
                self.guard = Guard::NotRun;
                for obligation in &artifact.summary.nonzero_obligations {
                    match obligation.evaluate_guarded(&environment) {
                        Ok(_) => {}
                        Err(ArithmeticErrorV0::ZeroFault { expression }) => {
                            self.guard = Guard::Failed { expression };
                            break;
                        }
                        Err(error) => return Err(error.into()),
                    }
                }
                if !matches!(self.guard, Guard::Failed { .. }) {
                    self.guard = Guard::Passed {
                        value: p.evaluate_guarded(&environment)?.to_string(),
                    };
                }
                ("check_all_retained_nonzero_guards", key)
            }
            6 => {
                if !matches!(self.guard, Guard::Passed { .. }) {
                    return Err(invalid("sealing requires successful concrete guards"));
                }
                let key = self.store.insert(WitnessProofV0::Seal {
                    body: self
                        .composed
                        .clone()
                        .ok_or_else(|| invalid("missing composition"))?,
                })?;
                ("seal_local_roundtrip", key)
            }
            _ => return Err(invalid("stage outside six-call contract")),
        };
        let artifact = self
            .store
            .artifact(&key)
            .ok_or_else(|| invalid("missing generated artifact"))?;
        Ok(StageRecord {
            input_binding: blake3::hash(&serde_json::to_vec(&(SUBJECT_SCHEMA, account, values))?)
                .to_hex()
                .to_string(),
            stage,
            spent: stage,
            remaining: 6 - stage,
            action: action.to_owned(),
            artifact: key.as_str().to_owned(),
            additive_zero: artifact.summary.is_formed(),
            multiplicative_one: artifact.summary.is_multiplicatively_closed(),
            reverse_requested: stage == 2,
            guard: self.guard.clone(),
            local_close: stage == 6,
        })
    }
}

fn advance(subject: &Subject, contract: &Contract, resource: &Resource) -> RunResult<Transition> {
    if contract.schema != FREE_ROUNDTRIP_CONTRACT_SCHEMA_V0
        || contract.version != 0
        || contract.max_calls != 6
    {
        return Err(invalid("unsupported fixed method contract"));
    }
    if resource.schema != RESOURCE_SCHEMA || resource.version != 0 || resource.total_fuel != 6 {
        return Err(invalid(
            "resource contract must retain exactly six total stage fuel",
        ));
    }
    if subject.schema != SUBJECT_SCHEMA
        || subject.version != 0
        || subject.account.is_empty()
        || subject.account.len() > 128
        || subject.account != resource.account
        || subject.history.len() > 6
        || subject
            .values
            .iter()
            .any(|value| !(-16..=16).contains(value))
    {
        return Err(invalid("invalid bounded subject or account"));
    }
    let mut replay = Replay::new();
    for (index, recorded) in subject.history.iter().enumerate() {
        if matches!(replay.guard, Guard::Failed { .. }) {
            return Err(invalid("history continues after a retained guard failure"));
        }
        let stage = u8::try_from(index + 1)?;
        let expected = replay.step(stage, subject.values, &subject.account)?;
        if recorded != &expected {
            return Err(invalid("history differs from native replay"));
        }
    }
    if subject.history.len() == 6 || matches!(replay.guard, Guard::Failed { .. }) {
        return Err(invalid("terminal frontier cannot spend or reset fuel"));
    }
    let stage = u8::try_from(subject.history.len() + 1)?;
    let next = replay.step(stage, subject.values, &subject.account)?;
    let evidence = if stage == 6 {
        let Guard::Passed { value } = &next.guard else {
            return Err(invalid("missing completed guard evidence"));
        };
        let (p, q) = expressions();
        Some(LocalEvidence {
            local_name: "learn".to_owned(),
            free_status: "Proposed".to_owned(),
            p: p.surface(),
            q: q.surface(),
            value: value.clone(),
            sealed_artifact: next.artifact.clone(),
            protected_obligations: vec![
                "free requires a separate task-relative acceptance condition".to_owned(),
                "the six-stage method is supplied, not learned syntax".to_owned(),
                "no source, occurrence, program, or M6 cell identity is inferred".to_owned(),
                "stage fuel is not arithmetic work, wall time, or global anti-replay enforcement"
                    .to_owned(),
            ],
        })
    } else {
        None
    };
    let mut output = subject.clone();
    output.history.push(next);
    Ok(Transition {
        schema: OUTPUT_SCHEMA.to_owned(),
        version: 0,
        input: subject.clone(),
        output,
        replayed_prior_stages: subject.history.len(),
        new_stages: 1,
        evidence,
    })
}

fn load_bounded<T: for<'de> Deserialize<'de>>(path: &Path) -> RunResult<T> {
    let mut bytes = Vec::new();
    File::open(path)?
        .take(u64::try_from(MAX_BYTES + 1)?)
        .read_to_end(&mut bytes)?;
    if bytes.len() > MAX_BYTES {
        return Err(invalid("input exceeds 128 KiB"));
    }
    Ok(serde_json::from_slice(&bytes)?)
}

fn encode_bounded<T: Serialize>(value: &T) -> RunResult<Vec<u8>> {
    let mut bytes = serde_json::to_vec_pretty(value)?;
    bytes.push(b'\n');
    if bytes.len() > MAX_BYTES {
        return Err(invalid("artifact exceeds 128 KiB"));
    }
    Ok(bytes)
}

fn write_new(path: &Path, bytes: &[u8]) -> RunResult<()> {
    let mut file = OpenOptions::new().write(true).create_new(true).open(path)?;
    file.write_all(bytes)?;
    file.sync_all()?;
    Ok(())
}

/// Execute exactly one stage of the fixed research method through `adva learn`.
///
/// # Errors
/// Rejects malformed or oversized inputs, altered history, terminal frontiers,
/// changed resource contracts, and existing output paths. A pair of file saves
/// is not transactional: any save failure is returned explicitly.
pub fn run_free_roundtrip_cli_v0(
    subject: &Path,
    method: &Path,
    resource: &Path,
    output: &Path,
    frontier_output: &Path,
    print: bool,
) -> RunResult<()> {
    if output == frontier_output || output.exists() || frontier_output.exists() {
        return Err(invalid("output paths must be distinct and new"));
    }
    let transition = advance(
        &load_bounded(subject)?,
        &load_bounded(method)?,
        &load_bounded(resource)?,
    )?;
    let result_bytes = encode_bounded(&transition)?;
    let frontier_bytes = encode_bounded(&transition.output)?;
    write_new(output, &result_bytes)?;
    if let Err(error) = write_new(frontier_output, &frontier_bytes) {
        return Err(invalid(&format!(
            "result saved but frontier save failed: {error}"
        )));
    }
    if print {
        io::stdout().write_all(&result_bytes)?;
    }
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    fn initial(values: [i32; 3]) -> (Subject, Contract, Resource) {
        (
            Subject {
                schema: SUBJECT_SCHEMA.to_owned(),
                version: 0,
                account: "fixture-1".to_owned(),
                values,
                history: vec![],
            },
            Contract {
                schema: FREE_ROUNDTRIP_CONTRACT_SCHEMA_V0.to_owned(),
                version: 0,
                max_calls: 6,
            },
            Resource {
                schema: RESOURCE_SCHEMA.to_owned(),
                version: 0,
                account: "fixture-1".to_owned(),
                total_fuel: 6,
            },
        )
    }

    fn finish(values: [i32; 3]) -> Transition {
        let (mut subject, contract, resource) = initial(values);
        for _ in 0..5 {
            subject = advance(&subject, &contract, &resource).unwrap().output;
        }
        advance(&subject, &contract, &resource).unwrap()
    }

    #[test]
    fn six_steps_produce_only_local_evidence() {
        let result = finish([2, 3, 4]);
        let evidence = result.evidence.unwrap();
        assert_eq!(evidence.value, "14");
        assert_eq!(evidence.local_name, "learn");
        assert_eq!(evidence.free_status, "Proposed");
        assert!(result.output.history[5].local_close);

        // Validate the actual persisted CLI transition, including its input
        // history and output fields, with the same bounded native replay.
        let saved_bytes = include_str!("../../../programs/bootstrap-0/learn.adva");
        let persisted: Transition = serde_json::from_str(saved_bytes).unwrap();
        let (_, contract, mut resource) = initial(persisted.input.values);
        resource.account.clone_from(&persisted.input.account);
        assert_eq!(
            advance(&persisted.input, &contract, &resource).unwrap(),
            persisted
        );
    }

    #[test]
    fn replay_rejects_modified_history_and_schema() {
        let (subject, contract, resource) = initial([2, 3, 4]);
        let mut next = advance(&subject, &contract, &resource).unwrap().output;
        next.history[0].spent = 0;
        assert!(advance(&next, &contract, &resource).is_err());
        let mut changed_values = advance(&subject, &contract, &resource).unwrap().output;
        changed_values.values[0] = 5;
        assert!(advance(&changed_values, &contract, &resource).is_err());
        assert!(serde_json::from_str::<Contract>(r#"{"schema":"adva.free-roundtrip.contract.v0","version":0,"max_calls":6,"extra":true}"#).is_err());
    }

    #[test]
    fn cumulative_stage_fuel_cannot_reset() {
        let result = finish([2, 3, 4]);
        let (_, contract, mut resource) = initial([2, 3, 4]);
        assert_eq!(result.output.history[5].remaining, 0);
        assert!(advance(&result.output, &contract, &resource).is_err());
        resource.total_fuel = 7;
        assert!(advance(&result.input, &contract, &resource).is_err());
    }

    #[test]
    fn additive_formation_does_not_seal_forward_transport() {
        let mut replay = Replay::new();
        replay.step(1, [2, 3, 4], "fixture-1").unwrap();
        let row = replay.step(2, [2, 3, 4], "fixture-1").unwrap();
        assert!(row.additive_zero && !row.multiplicative_one && !row.local_close);
        assert!(
            replay
                .store
                .insert(WitnessProofV0::Seal {
                    body: replay.forward.unwrap(),
                })
                .is_err()
        );
    }

    #[test]
    fn reverse_retains_zero_fault_and_remaining_fuel() {
        let (mut subject, contract, resource) = initial([2, -1, 2]);
        for _ in 0..5 {
            subject = advance(&subject, &contract, &resource).unwrap().output;
        }
        let row = &subject.history[4];
        assert!(matches!(row.guard, Guard::Failed { .. }));
        assert_eq!(row.remaining, 1);
        assert!(!row.local_close);
        assert!(advance(&subject, &contract, &resource).is_err());
    }

    #[test]
    fn unrelated_ratios_do_not_authorize_reverse_endpoints() {
        let p = ExactExprV0::constant(1);
        let q = ExactExprV0::constant(2);
        let other_before = ExactExprV0::constant(6);
        let other_after = ExactExprV0::constant(3);
        let a = crate::MultiplicativeResidualV0::from_transition(&p, &q).unwrap();
        let b =
            crate::MultiplicativeResidualV0::from_transition(&other_before, &other_after).unwrap();
        assert!(a.checked_multiply(&b).unwrap().is_one());
        assert!(!matching_reverse(&p, &q, &other_before, &other_after));
    }

    #[test]
    fn second_environment_reuses_fixed_method() {
        assert_eq!(finish([5, 2, 3]).evidence.unwrap().value, "11");
    }
}
