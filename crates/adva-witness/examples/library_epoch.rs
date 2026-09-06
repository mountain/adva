//! One bounded bootstrap/load/advance/publish/reload workflow (Research 0150).
use adva_witness::*;
use serde_json::{Value, json};
use std::fs::{self, File, OpenOptions};
use std::io::Write;
use std::path::Path;

fn fail(message: &str) -> LibraryCheckpointErrorV0 {
    LibraryCheckpointErrorV0::Invalid(message.into())
}

fn workflow(
    origin_path: &Path,
    directory: &Path,
    report: &mut Value,
    budget: &mut LibraryBudgetV0,
) -> Result<(), LibraryCheckpointErrorV0> {
    report["phase"] = json!("import-and-recheck-old-proposal");
    let bytes = read_library_bytes_v0(origin_path, budget)?;
    budget.charge()?;
    // A frozen source artifact is not a trusted old certificate. Only its
    // bounded proposal data are imported; all new judgments are rederived.
    if bytes != include_bytes!("../../../docs/research/0149-evidence/study.json") {
        return Err(fail("source differs from the frozen 0149 input"));
    }
    let old: Value = serde_json::from_slice(&bytes)?;
    let case = &old["cases"][0];
    if case["name"] != "delayed-evidence" || case["receipt"]["request"]["question"] != "Polynomial"
    {
        return Err(fail("wrong imported case or question"));
    }
    let input = LibraryInputV0 {
        catalogue: serde_json::from_value(case["receipt"]["request"]["catalogue"].clone())?,
        rounds: serde_json::from_value(case["receipt"]["request"]["rounds"].clone())?,
    };
    report["imported_proposal"] = serde_json::to_value(&input)?;
    report["origin_blake3"] = json!(blake3::hash(&bytes).to_hex().to_string());
    let origin = LibraryOriginV0 {
        artifact_blake3: blake3::hash(&bytes).to_hex().to_string(),
        case: "delayed-evidence".into(),
        prior_checker: case["receipt"]["request"]["method"]
            .as_str()
            .ok_or_else(|| fail("missing prior checker"))?
            .into(),
        observation_authority: "supplied-calibration-assumptions-not-world-measurements".into(),
    };
    let base = bootstrap_library_v0(origin, input, budget)?;
    report["phase"] = json!("publish-bootstrap");
    publish_library_v0(directory, &base, budget)?;
    report["before"] = serde_json::to_value(base.snapshot())?;
    let expected_base = base.digest().to_owned();
    drop(base); // The next epoch must actually obtain its state from disk.

    report["phase"] = json!("load-parent-from-disk");
    let loaded = load_library_v0(directory, 0, budget)?;
    budget.charge()?;
    if loaded.digest() != expected_base {
        return Err(fail("bootstrap reload mismatch"));
    }
    let before_bytes = read_library_bytes_v0(&library_snapshot_path_v0(directory, 0)?, budget)?;
    report["parent_digest"] = json!(loaded.digest());

    report["phase"] = json!("one-new-epoch");
    let x = ExactExprV0::variable("x");
    let proposed =
        ExactExprV0::product(ExactExprV0::constant(2), ExactExprV0::product(x.clone(), x));
    let observation = LibraryRoundV0::Observe { input: 2, value: 4 };
    report["new_candidate"] = serde_json::to_value(&proposed)?;
    report["new_observation"] = serde_json::to_value(&observation)?;
    report["new_observation_authority"] =
        json!("supplied-calibration-assumption-not-deduced-from-old-closure");
    let mut extended = loaded.snapshot().input.clone();
    extended.catalogue.push(proposed.clone());
    report["extended_input_before_observation"] = serde_json::to_value(&extended)?;
    let reopened = analyze_library_input_v0(&extended, budget)?;
    report["reopened"] = serde_json::to_value(&reopened)?;
    budget.charge()?;
    if reopened.terminal().status != LibraryStatusV0::Open
        || reopened.terminal().active != [1, 2, 4]
    {
        return Err(fail("unexpected new-epoch opening"));
    }
    let next = advance_library_v0(&loaded, Some(proposed), observation, budget)?;
    budget.charge()?;
    if next.snapshot().analysis.terminal().active != [1, 2]
        || next.snapshot().words != loaded.snapshot().words
    {
        return Err(fail("unexpected post-observation feature/witness change"));
    }
    report["after"] = serde_json::to_value(next.snapshot())?;
    report["same_word_content"] = json!(true);
    let expected_next = next.digest().to_owned();
    report["phase"] = json!("publish-successor");
    publish_library_v0(directory, &next, budget)?;
    drop(next);
    drop(loaded);

    report["phase"] = json!("reload-successor-and-reuse-native-witness");
    let reloaded = load_library_v0(directory, 1, budget)?;
    budget.charge()?;
    if reloaded.digest() != expected_next {
        return Err(fail("successor reload mismatch"));
    }
    report["successor_digest"] = json!(reloaded.digest());
    report["reload_matches"] = json!(true);
    let reuse = reuse_library_word_v0(&reloaded, 0, 2, budget)?;
    budget.charge()?;
    if reuse.guarded_values != ["4", "4"] {
        return Err(fail("unexpected guarded reuse values"));
    }
    report["reuse"] = serde_json::to_value(reuse)?;
    let current_before = read_library_bytes_v0(&library_snapshot_path_v0(directory, 0)?, budget)?;
    budget.charge()?;
    if before_bytes != current_before {
        return Err(fail("old snapshot changed"));
    }
    report["parent_bytes_unchanged"] = json!(true);
    report["phase"] = json!("completed");
    Ok(())
}

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let args: Vec<String> = std::env::args().skip(1).collect();
    if args.len() != 3 {
        return Err("usage: library_epoch OLD-REPORT NEW-STORE-DIRECTORY NEW-REPORT".into());
    }
    let report_path = Path::new(&args[2]);
    let mut output = OpenOptions::new()
        .write(true)
        .create_new(true)
        .open(report_path)?;
    let directory = Path::new(&args[1]);
    let mut budget = LibraryBudgetV0::new(50_000)?;
    budget.charge()?; // Prepaid report/checkpoint, from the same workflow budget.
    let mut report = json!({
        "schema": "adva.library-epoch-workflow.research.v0", "status": "Unknown", "phase": "preflight",
        "native_promotion": "NotGranted", "library_authority": "bounded-Rust-research-snapshots",
        "before": null, "after": null, "error": null
    });
    // No overlay on an existing store; no automatic reset or restart.
    let outcome = fs::create_dir(directory)
        .map_err(LibraryCheckpointErrorV0::from)
        .and_then(|()| workflow(Path::new(&args[0]), directory, &mut report, &mut budget));
    match outcome {
        Ok(()) => report["status"] = json!("Completed"),
        Err(error) => {
            report["status"] = json!(if matches!(error, LibraryCheckpointErrorV0::Unknown) {
                "Unknown"
            } else {
                "Blocked"
            });
            report["error"] = json!(error.to_string());
        }
    }
    report["fuel_spent"] = json!(budget.spent());
    report["fuel_remaining"] = json!(budget.remaining());
    report["source_blake3"] = json!({
        "driver": blake3::hash(include_bytes!("library_epoch.rs")).to_hex().to_string(),
        "contract": blake3::hash(include_bytes!("../../../docs/research/0150-persistent-library-epochs.md")).to_hex().to_string(),
        "checker_revision": library_checker_revision_v0(),
    });
    let bytes = serde_json::to_vec_pretty(&report)?;
    if bytes.len() >= 1_048_576 {
        return Err("report exceeds byte cap; existing files retained".into());
    }
    output.write_all(&bytes)?;
    output.write_all(b"\n")?;
    output.sync_all()?;
    File::open(report_path.parent().unwrap_or(Path::new(".")))?.sync_all()?;
    println!(
        "{}; {} shared units; published epochs 0 and 1 only if Completed",
        report["status"],
        budget.spent()
    );
    if report["status"] != "Completed" {
        return Err("workflow stopped; retain report and files".into());
    }
    Ok(())
}
