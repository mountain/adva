//! Research-only World/open task boundary, using the existing exact Rust kernel.
//! Agreement fixtures are assumptions, not authentication or evidence of real consent.

use adva_witness::{
    ArtifactKeyV0, BoundaryChargeV0, BoundaryCoordinateV0, BoundaryTermV0, ExactExprV0,
    RoleV0, WitnessArtifactV0, WitnessProofV0, WitnessStoreV0,
};
use serde::Serialize;
use serde_json::{Value, json};
use std::collections::BTreeMap;
use std::error::Error;
use std::ffi::OsStr;
use std::fs::OpenOptions;
use std::io::{self, Write};
use std::path::PathBuf;
use std::time::Instant;

type Result<T> = std::result::Result<T, Box<dyn Error>>;
const MAX_BYTES: usize = 128 * 1024;
const EQUATION: &str = "x + 1 = goal";
const ACTION: &str = "review-witness";

#[derive(Debug, Default, Serialize)]
struct Meter {
    candidate_visits: u8,
    native_proof_checks: u8,
}

fn proof_check(meter: &mut Meter) -> Result<()> {
    meter.native_proof_checks += 1;
    require(meter.native_proof_checks <= 16, "native verification budget exceeded")
}

fn require(condition: bool, message: &str) -> Result<()> {
    if !condition {
        return Err(io::Error::new(io::ErrorKind::InvalidData, message).into());
    }
    Ok(())
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize)]
struct TaskSpec {
    task_key: String,
    subject_ref: String,
    machine_ref: String,
    human_ref: String,
    domain: [i32; 3],
    goal: i32,
    fuel: u8,
    acceptance: String,
}

impl TaskSpec {
    fn validate(&self) -> Result<()> {
        require(
            self.domain == [1, 2, 3]
                && [3, 4].contains(&self.goal)
                && (1..=3).contains(&self.fuel)
                && self.acceptance == EQUATION
                && ["main", "short", "reuse"].contains(&self.task_key.as_str())
                && self.subject_ref == "fixture-subject"
                && self.machine_ref == "fixture-machine"
                && self.human_ref == "fixture-human",
            "task exceeds the frozen fixture boundary",
        )
    }
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize)]
struct Task {
    display_name: String,
    spec: TaskSpec,
}

fn task(key: &str, goal: i32, fuel: u8) -> Task {
    Task {
        display_name: format!("seek-{key}"),
        spec: TaskSpec {
            task_key: key.to_owned(),
            subject_ref: "fixture-subject".to_owned(),
            machine_ref: "fixture-machine".to_owned(),
            human_ref: "fixture-human".to_owned(),
            domain: [1, 2, 3],
            goal,
            fuel,
            acceptance: EQUATION.to_owned(),
        },
    }
}

#[derive(Clone, Copy, Debug, Eq, PartialEq, Serialize)]
enum Origin {
    ExternalAssumption,
    MachineProposal,
}

#[derive(Clone, Debug, Serialize)]
struct Agreement {
    origin: Origin,
    task: TaskSpec,
    human_ref: String,
    action: String,
}

fn assumed_agreement(task: &Task) -> Agreement {
    Agreement {
        origin: Origin::ExternalAssumption,
        task: task.spec.clone(),
        human_ref: task.spec.human_ref.clone(),
        action: ACTION.to_owned(),
    }
}

#[derive(Clone, Debug, Serialize)]
struct Trial {
    task: TaskSpec,
    candidate: i32,
    observed: String,
    goal: String,
    artifacts: Vec<WitnessArtifactV0>,
    sealed: Option<ArtifactKeyV0>,
    rejection: Option<String>,
}

fn arithmetic_proof(spec: &TaskSpec, candidate: i32) -> Result<WitnessProofV0> {
    spec.validate()?;
    require(spec.domain.contains(&candidate), "candidate outside domain")?;
    let boundary = BoundaryChargeV0::from_terms(
        [RoleV0::Construction, RoleV0::Space, RoleV0::Time]
            .into_iter()
            .map(|role| BoundaryTermV0::new(BoundaryCoordinateV0::Role { role }, 1)),
    )?;
    Ok(WitnessProofV0::ArithmeticTransition {
        actual_boundary: boundary.clone(),
        declared_boundary: boundary,
        before: ExactExprV0::sum(ExactExprV0::constant(candidate), ExactExprV0::constant(1)),
        after: ExactExprV0::constant(spec.goal),
    })
}

fn trial(spec: &TaskSpec, candidate: i32, meter: &mut Meter) -> Result<Trial> {
    meter.candidate_visits += 1;
    require(meter.candidate_visits <= 6, "candidate budget exceeded")?;
    proof_check(meter)?;
    let mut store = WitnessStoreV0::new();
    let proof = arithmetic_proof(spec, candidate)?;
    let WitnessProofV0::ArithmeticTransition { before, after, .. } = &proof else {
        unreachable!("fixed arithmetic transition");
    };
    let observed = before.evaluate_guarded(&BTreeMap::new())?.to_string();
    let goal = after.evaluate_guarded(&BTreeMap::new())?.to_string();
    let key = store.insert(proof)?;
    let forward = store.artifact(&key).expect("inserted transition").clone();
    require(forward.summary.is_formed(), "unformed arithmetic transition")?;
    let mut artifacts = vec![forward.clone()];
    let (sealed, rejection) = if forward.summary.is_multiplicatively_closed() {
        let key = store.insert(WitnessProofV0::Seal { body: key })?;
        artifacts.push(store.artifact(&key).expect("inserted seal").clone());
        (Some(key), None)
    } else {
        (None, Some("M != 1; candidate does not meet equation".to_owned()))
    };
    Ok(Trial {
        task: spec.clone(),
        candidate,
        observed,
        goal,
        artifacts,
        sealed,
        rejection,
    })
}

#[derive(Clone, Debug, Serialize)]
struct Search {
    task: Task,
    trials: Vec<Trial>,
    remaining: Vec<i32>,
    spent: usize,
    status: String,
    witness: Option<Trial>,
}

fn search(task: Task, meter: &mut Meter) -> Result<Search> {
    task.spec.validate()?;
    let mut trials = Vec::new();
    let mut witness = None;
    for candidate in task.spec.domain.into_iter().take(usize::from(task.spec.fuel)) {
        let record = trial(&task.spec, candidate, meter)?;
        if record.sealed.is_some() {
            witness = Some(record.clone());
        }
        trials.push(record);
        if witness.is_some() {
            break;
        }
    }
    let spent = trials.len();
    let remaining = task.spec.domain[spent..].to_vec();
    let status = if witness.is_some() { "WitnessFound" } else { "Unknown" }.to_owned();
    Ok(Search { task, trials, remaining, spent, status, witness })
}

// Verification replays supplied nodes; it does not enumerate or search candidates.
fn verify(spec: &TaskSpec, record: &Trial, meter: &mut Meter) -> Result<bool> {
    proof_check(meter)?;
    spec.validate()?;
    if record.task != *spec || !(1..=2).contains(&record.artifacts.len()) {
        return Ok(false);
    }
    let expected = arithmetic_proof(spec, record.candidate)?;
    if record.artifacts[0].proof != expected {
        return Ok(false);
    }
    let WitnessProofV0::ArithmeticTransition { before, after, .. } = &expected else {
        unreachable!("fixed arithmetic transition");
    };
    if before.evaluate_guarded(&BTreeMap::new())?.to_string() != record.observed
        || after.evaluate_guarded(&BTreeMap::new())?.to_string() != record.goal
    {
        return Ok(false);
    }
    let mut store = WitnessStoreV0::new();
    for artifact in &record.artifacts {
        let key = store.insert(artifact.proof.clone())?;
        if store.artifact(&key) != Some(artifact) {
            return Ok(false);
        }
        for guard in &artifact.summary.nonzero_obligations {
            guard.evaluate_guarded(&BTreeMap::new())?;
        }
    }
    let Some(sealed) = &record.sealed else {
        return Ok(false);
    };
    let expected_seal = WitnessProofV0::Seal { body: record.artifacts[0].key.clone() };
    Ok(record.artifacts.len() == 2
        && record.artifacts[1].proof == expected_seal
        && &record.artifacts[1].key == sealed
        && record.rejection.is_none()
        && record.observed == record.goal)
}

#[derive(Debug, Eq, PartialEq, Serialize)]
struct Judgment {
    arithmetic: String,
    agreement: String,
    pending_review: bool,
    human_review: String,
    task_closed: bool,
}

fn judge(
    task: &Task,
    witness: Option<&Trial>,
    agreement: Option<&Agreement>,
    meter: &mut Meter,
) -> Result<Judgment> {
    let arithmetic = match witness {
        Some(record) => if verify(&task.spec, record, meter)? { "Verified" } else { "Rejected" },
        None => "Unknown",
    };
    let agreement_status = match agreement {
        None => "Missing",
        Some(a) if a.origin == Origin::MachineProposal => "MachineProposalRejected",
        Some(a) if a.task != task.spec
            || a.human_ref != task.spec.human_ref || a.action != ACTION => "BindingRejected",
        Some(_) => "ConditionallyApplicable",
    };
    let pending_review = arithmetic == "Verified" && agreement_status == "ConditionallyApplicable";
    Ok(Judgment {
        arithmetic: arithmetic.to_owned(),
        agreement: agreement_status.to_owned(),
        pending_review,
        human_review: if pending_review { "Pending" } else { "Unknown" }.to_owned(),
        task_closed: false,
    })
}

fn case(
    name: &str,
    task: &Task,
    witness: Option<&Trial>,
    agreement: Option<&Agreement>,
    meter: &mut Meter,
) -> Result<Value> {
    Ok(json!({ "name": name, "task": task, "witness": witness,
        "agreement_input": agreement, "judgment": judge(task, witness, agreement, meter)? }))
}

fn main() -> Result<()> {
    let mut args = std::env::args_os().skip(1);
    require(args.next().as_deref() == Some(OsStr::new("--output")), "expected --output")?;
    let output = PathBuf::from(args.next().ok_or("missing output path")?);
    require(args.next().is_none(), "unexpected argument")?;
    require(output.file_name() == Some(OsStr::new("world-task.json")), "invalid output basename")?;
    let started = Instant::now();
    let mut meter = Meter::default();
    let main = search(task("main", 3, 2), &mut meter)?;
    let short = search(task("short", 3, 1), &mut meter)?;
    let reuse = search(task("reuse", 4, 3), &mut meter)?;
    let search_ns = started.elapsed().as_nanos();
    require(main.spent + short.spent + reuse.spent == 6, "candidate budget mismatch")?;
    require(short.status == "Unknown" && short.remaining == [2, 3], "short-fuel residual")?;
    let main_witness = main.witness.as_ref().ok_or("missing main witness")?;
    let reuse_witness = reuse.witness.as_ref().ok_or("missing reuse witness")?;
    require(main_witness.candidate == 2 && reuse_witness.candidate == 3, "wrong witness")?;
    let validation = Instant::now();
    let agreement = assumed_agreement(&main.task);
    let reuse_agreement = assumed_agreement(&reuse.task);
    let short_agreement = assumed_agreement(&short.task);
    let mut proposal = agreement.clone();
    proposal.origin = Origin::MachineProposal;
    let mut renamed = main.task.clone();
    renamed.display_name = "World task, renamed display".to_owned();
    let wrong = &main.trials[0];
    proof_check(&mut meter)?;
    let mut refusal_store = WitnessStoreV0::new();
    let wrong_key = refusal_store.insert(wrong.artifacts[0].proof.clone())?;
    let refusal = refusal_store.insert(WitnessProofV0::Seal { body: wrong_key }).err()
        .ok_or("kernel sealed a wrong candidate")?.to_string();
    let cases = vec![
        case("main", &main.task, Some(main_witness), Some(&agreement), &mut meter)?,
        case("short_fuel", &short.task, None, Some(&short_agreement), &mut meter)?,
        case("reuse", &reuse.task, Some(reuse_witness), Some(&reuse_agreement), &mut meter)?,
        case("missing_agreement", &main.task, Some(main_witness), None, &mut meter)?,
        case("machine_proposal", &main.task, Some(main_witness), Some(&proposal), &mut meter)?,
        case("stale_agreement", &reuse.task, Some(reuse_witness), Some(&agreement), &mut meter)?,
        case("display_rename", &renamed, Some(main_witness), Some(&agreement), &mut meter)?,
        case("wrong_candidate", &main.task, Some(wrong), Some(&agreement), &mut meter)?,
    ];
    for (index, expected) in [true, false, true, false, false, false, true, false]
        .into_iter().enumerate()
    {
        require(cases[index]["judgment"]["pending_review"] == expected,
            "unexpected conditional review judgment")?;
        require(cases[index]["judgment"]["task_closed"] == false,
            "task was improperly closed")?;
    }
    require(cases[1]["judgment"]["arithmetic"] == "Unknown", "short run closed")?;
    require(cases[3]["judgment"]["agreement"] == "Missing", "missing agreement accepted")?;
    require(cases[4]["judgment"]["agreement"] == "MachineProposalRejected",
        "proposal accepted as agreement")?;
    require(cases[5]["judgment"]["agreement"] == "BindingRejected", "stale agreement accepted")?;
    require(cases[6]["judgment"] == cases[0]["judgment"], "rename changed judgment")?;
    require(cases[7]["judgment"]["arithmetic"] == "Rejected", "wrong candidate accepted")?;
    let verification_ns = validation.elapsed().as_nanos();
    let evidence = json!({
        "schema": "adva.research.world-task-boundary.v0",
        "name_origin": "user_defined",
        "name": "World",
        "counterpart": "open",
        "operational_status": "Proposed",
        "scope": "One finite existential task and conditional pending review under a fixture agreement",
        "origin_warning": "ExternalAssumption is a fixture tag, not authentication or real consent",
        "role_warning": "Role refs and task keys are fixture labels, not SourceId or semantic identity",
        "residual": "Human review and real-world applicability are unverified; World is not Universe",
        "task_closed": false,
        "searches": [main, short, reuse],
        "cases": cases,
        "wrong_candidate_kernel_refusal": refusal,
        "cost": { "counts": meter, "search_and_construction_ns": search_ns,
            "native_proof_check_unit": "one candidate derivation, saved-witness replay, or seal-refusal check",
            "verification_and_case_recording_ns": verification_ns, "peak_memory": null }
    });
    let serializing = Instant::now();
    let bytes = serde_json::to_vec_pretty(&evidence)?;
    let serialization_ns = serializing.elapsed().as_nanos();
    require(bytes.len() < MAX_BYTES, "evidence exceeds 128 KiB")?;
    let writing = Instant::now();
    let mut file = OpenOptions::new().write(true).create_new(true).open(output)?;
    file.write_all(&bytes)?;
    file.sync_all()?;
    let write_ns = writing.elapsed().as_nanos();
    println!("WORLD_TASK_EVIDENCE_BEGIN");
    println!("{}", std::str::from_utf8(&bytes)?);
    println!("WORLD_TASK_EVIDENCE_END");
    eprintln!("serialization_ns={serialization_ns} write_ns={write_ns} bytes={}", bytes.len());
    Ok(())
}
