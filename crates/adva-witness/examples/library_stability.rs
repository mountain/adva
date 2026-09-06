//! Research 0149: finite, immutable library epochs; no stable semantic API.
//!
//! Run with a NEW output path. All fixtures, replay and checkpoint charges
//! share one account. This is not a native learner or an implementation of
//! inverse program execution; see the frozen research contract.

use adva_witness::{ExactExprV0, PolynomialV0};
use num_bigint::BigInt;
use serde::{Deserialize, Serialize};
use std::collections::BTreeMap;
use std::fs::OpenOptions;
use std::io::Write;

const METHOD: &str = "adva.library-stability.polynomial-shadow.research.v0";
const STUDY_FUEL: u32 = 50_000;

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
enum Question {
    Point(i32),
    Polynomial,
    Syntax,
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
enum Round {
    Observe { input: i32, value: i32 },
    Revisit,
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
struct Request {
    method: String,
    kernel_revision: String,
    // Ordered, retained syntax: equal shadows never deduplicate this list.
    catalogue: Vec<ExactExprV0>,
    question: Question,
    rounds: Vec<Round>,
    work_cap: u32,
}

#[derive(Clone, Copy, Debug, Eq, PartialEq, Serialize, Deserialize)]
enum Status {
    FeatureClosed,
    Open,
    ModelGap,
    Unknown,
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
struct Comparison {
    candidate: usize,
    input: i32,
    expected: i32,
    predicted: String,
    agrees: bool,
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
struct Feature {
    candidate: usize,
    value: String,
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
struct Checkpoint {
    active: Vec<usize>,
    features: Vec<Feature>,
    status: Status,
    // Least retained ordinal, not a new semantic identity or a syntax quotient.
    representative: Option<usize>,
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
struct RoundCertificate {
    ordinal: usize,
    before: Vec<usize>,
    comparisons: Vec<Comparison>,
    after: Checkpoint,
    strict_progress: bool,
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
struct Receipt {
    request: Request,
    // Integrity coordinate only. Replay compares full content, not this alone.
    request_digest: String,
    status: Status,
    initial: Option<Checkpoint>,
    history: Vec<RoundCertificate>,
    // Tentative checks are retained but do not commit a partial round.
    pending_checks: Vec<Comparison>,
    pending_rounds: Vec<Round>,
    spent: u32,
    remaining_cap: u32,
    native_promotion: String,
}

#[derive(Debug)]
enum Stop {
    Fuel,
    Invalid(String),
}

type Checked<T> = Result<T, Stop>;

struct Account {
    spent: u32,
    limit: u32,
}

impl Account {
    fn charge(&mut self) -> Checked<()> {
        if self.spent >= self.limit {
            return Err(Stop::Fuel);
        }
        self.spent += 1;
        Ok(())
    }
}

struct Work<'a> {
    account: &'a mut Account,
    spent: u32,
    cap: u32,
}

impl Work<'_> {
    fn charge(&mut self) -> Checked<()> {
        if self.spent >= self.cap {
            return Err(Stop::Fuel);
        }
        self.account.charge()?;
        self.spent += 1;
        Ok(())
    }
}

fn invalid(message: &str) -> Stop {
    Stop::Invalid(message.into())
}

fn digest<T: Serialize>(value: &T) -> String {
    blake3::hash(&serde_json::to_vec(value).expect("research serialization"))
        .to_hex()
        .to_string()
}

fn kernel_revision() -> String {
    digest(&[
        blake3::hash(include_bytes!("library_stability.rs"))
            .to_hex()
            .to_string(),
        blake3::hash(include_bytes!("../src/arithmetic.rs"))
            .to_hex()
            .to_string(),
        blake3::hash(include_bytes!("../../../Cargo.lock"))
            .to_hex()
            .to_string(),
    ])
}

fn admit_expression(expression: &ExactExprV0, work: &mut Work<'_>) -> Checked<()> {
    let mut stack = vec![(expression, 1)];
    let mut count = 0;
    while let Some((node, depth)) = stack.pop() {
        work.charge()?;
        count += 1;
        if count > 31 || depth > 8 {
            return Err(invalid("expression node/depth bound"));
        }
        match node {
            ExactExprV0::Constant { value } => {
                if value < &BigInt::from(-16) || value > &BigInt::from(16) {
                    return Err(invalid("constant bound"));
                }
            }
            ExactExprV0::Variable { name } if name == "x" => {}
            ExactExprV0::Variable { .. } => return Err(invalid("only x is admitted")),
            ExactExprV0::Add { left, right } | ExactExprV0::Multiply { left, right } => {
                stack.push((right, depth + 1));
                stack.push((left, depth + 1));
            }
        }
    }
    Ok(())
}

fn point(polynomial: &PolynomialV0, input: i32) -> Checked<BigInt> {
    polynomial
        .evaluate(&BTreeMap::from([("x".into(), BigInt::from(input))]))
        .map_err(|error| invalid(&error.to_string()))
}

fn checkpoint(
    request: &Request,
    polynomials: &[PolynomialV0],
    active: Vec<usize>,
    work: &mut Work<'_>,
) -> Checked<Checkpoint> {
    let mut features = Vec::new();
    for &candidate in &active {
        work.charge()?;
        let value = match request.question {
            Question::Point(input) => point(&polynomials[candidate], input)?.to_string(),
            Question::Polynomial => serde_json::to_string(&polynomials[candidate])
                .map_err(|error| invalid(&error.to_string()))?,
            Question::Syntax => request.catalogue[candidate].surface(),
        };
        features.push(Feature { candidate, value });
    }
    let mut same = true;
    for feature in features.iter().skip(1) {
        work.charge()?;
        same &= feature.value == features[0].value;
    }
    work.charge()?;
    let status = if active.is_empty() {
        Status::ModelGap
    } else if same {
        Status::FeatureClosed
    } else {
        Status::Open
    };
    Ok(Checkpoint {
        representative: active.first().copied(),
        active,
        features,
        status,
    })
}

fn run(request: &Request, account: &mut Account) -> Checked<Receipt> {
    // The example has no untrusted input decoder. These constant-time gates
    // still precede cloning, traversal and normalization of proposed data.
    if request.catalogue.is_empty()
        || request.catalogue.len() > 8
        || request.rounds.len() > 16
        || request.method.len() > 128
        || request.kernel_revision.len() > 128
        || request.work_cap > STUDY_FUEL
    {
        return Err(invalid("request shape bound"));
    }
    let mut work = Work {
        account,
        spent: 0,
        cap: request.work_cap,
    };
    // Validate the bounded syntax BEFORE cloning/serializing candidate trees.
    let preparation = (|| {
        work.charge()?;
        if request.method != METHOD || request.kernel_revision != kernel_revision() {
            return Err(invalid("checker revision mismatch"));
        }
        if matches!(request.question, Question::Point(x) if !(-8..=8).contains(&x)) {
            return Err(invalid("question point bound"));
        }
        for round in &request.rounds {
            work.charge()?;
            if matches!(round, Round::Observe { input, value }
                if !(-8..=8).contains(input) || !(-1_000_000..=1_000_000).contains(value))
            {
                return Err(invalid("observation bound"));
            }
        }
        for expression in &request.catalogue {
            admit_expression(expression, &mut work)?;
        }
        Ok(())
    })();
    if let Err(Stop::Invalid(message)) = preparation {
        return Err(Stop::Invalid(message));
    }
    // Only frozen, in-process fixtures are used. Fuel suspension during
    // admission retains those inputs, but issues no initial certificate.
    let mut receipt = Receipt {
        request: request.clone(),
        request_digest: digest(request),
        status: Status::Unknown,
        initial: None,
        history: Vec::new(),
        pending_checks: Vec::new(),
        pending_rounds: request.rounds.clone(),
        spent: 0,
        remaining_cap: request.work_cap,
        native_promotion: "NotGranted".into(),
    };
    if preparation.is_ok() {
        let execution = (|| {
            let mut polynomials = Vec::new();
            for expression in &request.catalogue {
                work.charge()?;
                polynomials.push(
                    expression
                        .normalize()
                        .map_err(|e| invalid(&e.to_string()))?,
                );
            }
            let mut current = checkpoint(
                request,
                &polynomials,
                (0..request.catalogue.len()).collect(),
                &mut work,
            )?;
            receipt.initial = Some(current.clone());
            for (ordinal, round) in request.rounds.iter().enumerate() {
                work.charge()?;
                let mut next = Vec::new();
                for &candidate in &current.active {
                    match *round {
                        Round::Observe { input, value } => {
                            work.charge()?;
                            let predicted = point(&polynomials[candidate], input)?;
                            let agrees = predicted == BigInt::from(value);
                            receipt.pending_checks.push(Comparison {
                                candidate,
                                input,
                                expected: value,
                                predicted: predicted.to_string(),
                                agrees,
                            });
                            if agrees {
                                next.push(candidate);
                            }
                        }
                        Round::Revisit => next.push(candidate),
                    }
                }
                let after = checkpoint(request, &polynomials, next, &mut work)?;
                work.charge()?; // Atomic logical round commit, not a filesystem transaction.
                receipt.history.push(RoundCertificate {
                    ordinal,
                    strict_progress: !after.active.is_empty()
                        && after.active.len() < current.active.len(),
                    before: current.active.clone(),
                    comparisons: std::mem::take(&mut receipt.pending_checks),
                    after: after.clone(),
                });
                current = after;
                receipt.pending_rounds = request.rounds[ordinal + 1..].to_vec();
            }
            work.charge()?; // Final certificate admission.
            receipt.status = current.status;
            Ok(())
        })();
        if let Err(Stop::Invalid(message)) = execution {
            return Err(Stop::Invalid(message));
        }
    }
    receipt.spent = work.spent;
    receipt.remaining_cap = request.work_cap - work.spent;
    Ok(receipt)
}

fn replay(request: &Request, receipt: &Receipt, account: &mut Account) -> Checked<bool> {
    account.charge()?;
    if request != &receipt.request || digest(request) != receipt.request_digest {
        return Ok(false);
    }
    let rederived = run(request, account)?;
    account.charge()?;
    Ok(rederived == *receipt)
}

fn base() -> Request {
    let x = ExactExprV0::variable("x");
    Request {
        method: METHOD.into(),
        kernel_revision: kernel_revision(),
        question: Question::Polynomial,
        catalogue: vec![
            x.clone(),
            ExactExprV0::product(ExactExprV0::constant(2), x.clone()),
            ExactExprV0::sum(x.clone(), x.clone()),
            ExactExprV0::product(x.clone(), x),
        ],
        rounds: Vec::new(),
        work_cap: 2_000,
    }
}

fn frozen_cases() -> Vec<(&'static str, Request, Status)> {
    let mut delayed = base();
    delayed.rounds = vec![
        Round::Observe { input: 0, value: 0 },
        Round::Revisit,
        Round::Revisit,
        Round::Revisit,
        Round::Observe { input: 1, value: 2 },
    ];
    let mut syntax = delayed.clone();
    syntax.question = Question::Syntax;
    let mut coarse = base();
    coarse.question = Question::Point(0);
    let mut revisits = base();
    revisits.rounds = vec![Round::Revisit; 6];
    let mut fresh = base();
    let x = ExactExprV0::variable("x");
    fresh.catalogue[1] = ExactExprV0::product(ExactExprV0::constant(3), x.clone());
    fresh.catalogue[2] = ExactExprV0::sum(x.clone(), ExactExprV0::sum(x.clone(), x));
    fresh.rounds = vec![Round::Observe { input: 1, value: 3 }];
    let mut duplicate = delayed.clone();
    duplicate.rounds.push(Round::Observe { input: 1, value: 2 });
    let mut gap = base();
    gap.rounds = vec![Round::Observe { input: 1, value: 7 }];
    let mut zero = delayed.clone();
    zero.work_cap = 0;
    let mut partial = delayed.clone();
    partial.work_cap = 50;
    vec![
        ("delayed-evidence", delayed, Status::FeatureClosed),
        ("syntax-remains-open", syntax, Status::Open),
        ("coarse-point-closed", coarse, Status::FeatureClosed),
        ("six-pass-no-evidence", revisits, Status::Open),
        ("fresh-coefficient", fresh, Status::FeatureClosed),
        ("duplicate-evidence", duplicate, Status::FeatureClosed),
        ("empty-model", gap, Status::ModelGap),
        ("zero-work", zero, Status::Unknown),
        ("partial-work", partial, Status::Unknown),
    ]
}

#[derive(Serialize)]
struct CaseReport {
    name: String,
    expected: Status,
    receipt: Receipt,
    replay_matches: Option<bool>,
}

#[derive(Serialize)]
struct AuditReport {
    name: String,
    receipt_applicable: Option<bool>,
    old_receipt: Receipt,
    proposed_request: Request,
    proposed_receipt: Receipt,
}

#[derive(Serialize)]
struct Study {
    schema: String,
    method: String,
    source_blake3: BTreeMap<String, String>,
    frozen_requests: Vec<Request>,
    cases: Vec<CaseReport>,
    audits: Vec<AuditReport>,
    status: String,
    failure: Option<String>,
    fuel_spent: u32,
    fuel_remaining: u32,
    native_promotion: String,
}

fn study(account: &mut Account) -> Checked<Study> {
    let mut report = Study {
        schema: "adva.library-stability.study.research.v0".into(),
        method: METHOD.into(),
        source_blake3: BTreeMap::from([
            (
                "example".into(),
                blake3::hash(include_bytes!("library_stability.rs"))
                    .to_hex()
                    .to_string(),
            ),
            (
                "arithmetic".into(),
                blake3::hash(include_bytes!("../src/arithmetic.rs"))
                    .to_hex()
                    .to_string(),
            ),
            (
                "contract".into(),
                blake3::hash(include_bytes!(
                    "../../../docs/research/0149-library-stability-and-zigzag.md"
                ))
                .to_hex()
                .to_string(),
            ),
            (
                "cargo_lock".into(),
                blake3::hash(include_bytes!("../../../Cargo.lock"))
                    .to_hex()
                    .to_string(),
            ),
        ]),
        frozen_requests: frozen_cases()
            .into_iter()
            .map(|(_, request, _)| request)
            .collect(),
        cases: Vec::new(),
        audits: Vec::new(),
        status: "Completed".into(),
        failure: None,
        fuel_spent: 0,
        fuel_remaining: 0,
        native_promotion: "NotGranted".into(),
    };
    account.charge()?; // Reserve checkpoint work from the SAME study account.
    if let Err(error) = execute_study(&mut report, account) {
        report.status = if matches!(error, Stop::Fuel) {
            "Unknown"
        } else {
            "Blocked"
        }
        .into();
        report.failure = Some(format!("{error:?}"));
    }
    report.fuel_spent = account.spent;
    report.fuel_remaining = account.limit - account.spent;
    Ok(report)
}

fn execute_study(report: &mut Study, account: &mut Account) -> Checked<()> {
    for (name, request, expected) in frozen_cases() {
        let receipt = run(&request, account)?;
        report.cases.push(CaseReport {
            name: name.into(),
            expected,
            receipt,
            replay_matches: None,
        });
        let case = report.cases.last_mut().unwrap();
        let replay_matches = replay(&request, &case.receipt, account)?;
        case.replay_matches = Some(replay_matches);
        let matched = case.receipt.status == expected && replay_matches;
        if !matched {
            report.status = "Failed".into();
            report.failure = Some(name.into());
            return Ok(());
        }
    }
    let original = report.cases[0].receipt.clone();
    for name in [
        "tampered-feature",
        "changed-question",
        "changed-catalogue",
        "changed-method",
    ] {
        let mut proposed_request = original.request.clone();
        let mut proposed_receipt = original.clone();
        match name {
            "tampered-feature" => {
                proposed_receipt.history.last_mut().unwrap().after.features[0].value =
                    "forged".into();
            }
            "changed-question" => proposed_request.question = Question::Syntax,
            "changed-catalogue" => proposed_request.catalogue.push(ExactExprV0::constant(2)),
            "changed-method" => proposed_request.method.push_str("-changed"),
            _ => unreachable!(),
        }
        report.audits.push(AuditReport {
            name: name.into(),
            receipt_applicable: None,
            old_receipt: original.clone(),
            proposed_request,
            proposed_receipt,
        });
        let audit = report.audits.last_mut().unwrap();
        let receipt_applicable = replay(&audit.proposed_request, &audit.proposed_receipt, account)?;
        audit.receipt_applicable = Some(receipt_applicable);
        if receipt_applicable {
            report.status = "Failed".into();
            report.failure = Some(name.into());
            return Ok(());
        }
    }
    Ok(())
}

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let mut arguments = std::env::args().skip(1);
    let path = arguments
        .next()
        .ok_or("usage: library_stability NEW-OUTPUT.json")?;
    if arguments.next().is_some() {
        return Err("exactly one new output path is required".into());
    }
    // Refuse overwrite before spending trial fuel.
    let mut file = OpenOptions::new().write(true).create_new(true).open(path)?;
    let mut account = Account {
        spent: 0,
        limit: STUDY_FUEL,
    };
    let report = match study(&mut account) {
        Ok(report) => serde_json::to_value(report)?,
        Err(error) => serde_json::json!({
            "status": if matches!(error, Stop::Fuel) { "Unknown" } else { "Blocked" },
            "reason": format!("{error:?}"), "fuel_spent": account.spent,
            "fuel_remaining": account.limit - account.spent, "native_promotion": "NotGranted"
        }),
    };
    let bytes = serde_json::to_vec_pretty(&report)?;
    if bytes.len() > 1_048_576 {
        return Err("checkpoint exceeds 1 MiB".into());
    }
    file.write_all(&bytes)?;
    file.write_all(b"\n")?;
    file.sync_all()?;
    println!(
        "{}; shared fuel {}/{}; {} bytes",
        report["status"],
        account.spent,
        account.limit,
        bytes.len() + 1
    );
    if report["status"] != "Completed" {
        return Err("trial did not complete; retain report".into());
    }
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    fn account() -> Account {
        Account {
            spent: 0,
            limit: STUDY_FUEL,
        }
    }

    #[test]
    fn frozen_outcomes_and_serialized_replay() {
        let mut ledger = account();
        for (_, request, expected) in frozen_cases() {
            let receipt = run(&request, &mut ledger).unwrap();
            assert_eq!(receipt.status, expected);
            let decoded: Receipt =
                serde_json::from_slice(&serde_json::to_vec(&receipt).unwrap()).unwrap();
            assert!(replay(&request, &decoded, &mut ledger).unwrap());
        }
    }

    #[test]
    fn plateau_is_not_closure_and_evidence_changes_representative() {
        let request = &frozen_cases()[0].1;
        let receipt = run(request, &mut account()).unwrap();
        for round in &receipt.history[..4] {
            assert!(!round.strict_progress);
            assert_eq!(round.after.status, Status::Open);
            assert_eq!(round.after.representative, Some(0));
        }
        let final_round = receipt.history.last().unwrap();
        assert!(final_round.strict_progress);
        assert_eq!(final_round.after.active, [1, 2]);
        assert_eq!(final_round.after.representative, Some(1));
        assert_eq!(
            final_round
                .comparisons
                .iter()
                .map(|c| c.predicted.as_str())
                .collect::<Vec<_>>(),
            ["1", "2", "2", "1"]
        );
        assert_ne!(request.catalogue[1], request.catalogue[2]);
        assert_eq!(receipt.request.catalogue.len(), 4);
    }

    #[test]
    fn six_revisits_and_duplicates_do_not_progress() {
        let receipt = run(&frozen_cases()[3].1, &mut account()).unwrap();
        assert_eq!(receipt.history.len(), 6);
        assert!(
            receipt
                .history
                .iter()
                .all(|r| !r.strict_progress && r.after.active.len() == 4)
        );
        let receipt = run(&frozen_cases()[5].1, &mut account()).unwrap();
        assert!(!receipt.history.last().unwrap().strict_progress);
        assert_eq!(receipt.history.last().unwrap().comparisons.len(), 2);
    }

    #[test]
    fn empty_fibre_and_pending_prefix_never_close() {
        let gap = run(&frozen_cases()[6].1, &mut account()).unwrap();
        let end = &gap.history.last().unwrap().after;
        assert_eq!(end.status, Status::ModelGap);
        assert!(end.active.is_empty() && end.features.is_empty());
        let partial = run(&frozen_cases()[8].1, &mut account()).unwrap();
        assert_eq!(partial.status, Status::Unknown);
        assert!(!partial.history.is_empty());
        assert!(!partial.pending_rounds.is_empty());
        assert_eq!(partial.spent, 50);
    }

    #[test]
    fn changed_epoch_requires_rechecking_and_preserves_old_receipt() {
        let old = run(&frozen_cases()[0].1, &mut account()).unwrap();
        let mut revised = old.request.clone();
        let x = ExactExprV0::variable("x");
        revised.catalogue.push(ExactExprV0::product(
            ExactExprV0::constant(2),
            ExactExprV0::product(x.clone(), x),
        ));
        assert!(!replay(&revised, &old, &mut account()).unwrap());
        // Keep ALL previous evidence. The new 2*x*x agrees at 0 and 1 but
        // disagrees as a polynomial: extension is not nonempty refinement.
        let new = run(&revised, &mut account()).unwrap();
        assert_eq!(new.status, Status::Open);
        assert_eq!(old.status, Status::FeatureClosed);
        assert_eq!(old.request.catalogue.len(), 4);
    }

    #[test]
    fn tampered_coverage_history_and_fuel_are_rejected() {
        let request = &frozen_cases()[0].1;
        let receipt = run(request, &mut account()).unwrap();
        for mutation in 0..4 {
            let mut bad = receipt.clone();
            match mutation {
                0 => {
                    bad.history.last_mut().unwrap().after.active.pop();
                }
                1 => {
                    bad.history.remove(0);
                }
                2 => {
                    bad.spent -= 1;
                }
                _ => {
                    bad.history.last_mut().unwrap().comparisons[0].agrees = true;
                }
            }
            assert!(!replay(request, &bad, &mut account()).unwrap());
        }
    }

    #[test]
    fn aggregate_fuel_cannot_be_refilled_by_a_new_run() {
        let mut ledger = Account {
            spent: 0,
            limit: 12,
        };
        let first = run(&base(), &mut ledger).unwrap();
        let second = run(&base(), &mut ledger).unwrap();
        assert_eq!(first.status, Status::Unknown);
        assert_eq!(second.status, Status::Unknown);
        assert_eq!(first.spent, 12);
        assert_eq!(second.spent, 0);
        assert_eq!(ledger.spent, 12);
    }

    #[test]
    fn outside_profile_and_checker_drift_are_blocked() {
        for mutation in 0..7 {
            let mut request = base();
            match mutation {
                0 => request.catalogue.clear(),
                1 => request.catalogue[0] = ExactExprV0::constant(17),
                2 => request.catalogue[0] = ExactExprV0::variable("y"),
                3 => request.question = Question::Point(9),
                4 => request.method.push_str("-changed"),
                5 => request.kernel_revision.push_str("-changed"),
                _ => request.rounds = vec![Round::Revisit; 17],
            }
            assert!(matches!(
                run(&request, &mut account()),
                Err(Stop::Invalid(_))
            ));
        }
    }

    #[test]
    fn whole_study_shares_one_account_and_refuses_four_stale_audits() {
        let mut ledger = account();
        let report = study(&mut ledger).unwrap();
        assert_eq!(report.status, "Completed");
        assert_eq!(report.cases.len(), 9);
        assert_eq!(report.audits.len(), 4);
        assert!(
            report
                .audits
                .iter()
                .all(|a| a.receipt_applicable == Some(false))
        );
        assert_eq!(report.fuel_spent, ledger.spent);
        assert_eq!(report.fuel_spent + report.fuel_remaining, STUDY_FUEL);
    }

    #[test]
    fn study_exhaustion_retains_requests_receipt_and_unfinished_audit() {
        let mut ledger = Account {
            spent: 0,
            limit: 100,
        };
        let report = study(&mut ledger).unwrap();
        assert_eq!(report.status, "Unknown");
        assert_eq!(report.frozen_requests.len(), 9);
        assert_eq!(report.cases.len(), 1);
        assert_eq!(report.cases[0].replay_matches, None);
        assert_eq!(report.fuel_remaining, 0);
        assert_eq!(report.fuel_spent, 100);
    }

    #[test]
    fn unfinished_round_keeps_tentative_comparisons_without_commit() {
        let mut request = frozen_cases()[0].1.clone();
        request.work_cap = 34;
        let receipt = run(&request, &mut account()).unwrap();
        assert_eq!(receipt.status, Status::Unknown);
        assert!(receipt.history.is_empty());
        assert_eq!(receipt.initial.unwrap().active, [0, 1, 2, 3]);
        assert_eq!(receipt.pending_checks.len(), 4);
        assert_eq!(receipt.pending_rounds, request.rounds);
    }
}
