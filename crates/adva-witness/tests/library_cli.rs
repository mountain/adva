//! CLI boundary tests use a synthetic epoch, independent of private submodule access.
use adva_witness::*;
use serde_json::{Value, json};
use std::fs;
use std::path::PathBuf;
use std::process::Command;
use std::sync::atomic::{AtomicU64, Ordering};

static NEXT: AtomicU64 = AtomicU64::new(0);

struct Fixture {
    root: PathBuf,
    digest: String,
}

impl Fixture {
    fn new() -> Self {
        let root = std::env::temp_dir().join(format!(
            "adva-library-cli-{}-{}",
            std::process::id(),
            NEXT.fetch_add(1, Ordering::Relaxed)
        ));
        fs::create_dir(&root).unwrap();
        fs::create_dir_all(root.join("library/stability")).unwrap();
        let x = ExactExprV0::variable("x");
        let mut budget = LibraryBudgetV0::new(50_000).unwrap();
        let epoch = bootstrap_library_v0(
            LibraryOriginV0 {
                artifact_blake3: "0".repeat(64),
                case: "cli-test".into(),
                prior_checker: "supplied-test".into(),
                observation_authority: "supplied-calibration-assumptions-not-world-measurements"
                    .into(),
            },
            LibraryInputV0 {
                catalogue: vec![
                    ExactExprV0::product(ExactExprV0::constant(2), x.clone()),
                    ExactExprV0::sum(x.clone(), x),
                ],
                rounds: vec![],
            },
            &mut budget,
        )
        .unwrap();
        publish_library_v0(&root.join("library/stability"), &epoch, &mut budget).unwrap();
        Self {
            root,
            digest: epoch.digest().into(),
        }
    }

    fn command(&self, action: &str, name: &str, extra: &[&str]) -> std::process::Output {
        Command::new(env!("CARGO_BIN_EXE_adva"))
            .current_dir(&self.root)
            .args([
                "library", action, "--path", "library", "--epoch", "0", "--output", name,
            ])
            .args(extra)
            .output()
            .unwrap()
    }

    fn report(&self, name: &str) -> Value {
        serde_json::from_slice(&fs::read(self.root.join(name)).unwrap()).unwrap()
    }
}

impl Drop for Fixture {
    fn drop(&mut self) {
        fs::remove_dir_all(&self.root).unwrap();
    }
}

#[test]
fn exact_reuse_relocates_and_keeps_snapshot() {
    let f = Fixture::new();
    let before = fs::read(f.root.join("library/stability/epoch-0000.json")).unwrap();
    assert!(
        f.command("check", "check.json", &["--expect-digest", &f.digest])
            .status
            .success()
    );
    assert_eq!(f.report("check.json")["status"], "SnapshotChecked");
    for (i, input, value) in [(0, "2", "4"), (1, "-3", "-6"), (2, "8", "16")] {
        let name = format!("reuse-{i}.json");
        assert!(
            f.command(
                "reuse",
                &name,
                &[
                    "--word",
                    "0",
                    "--input",
                    input,
                    "--expect-digest",
                    &f.digest
                ]
            )
            .status
            .success()
        );
        let r = f.report(&name);
        assert_eq!(r["status"], "ReuseChecked");
        assert_eq!(r["reuse"]["guarded_values"], json!([value, value]));
        assert_eq!(r["expected_digest_matched"], true);
        assert_eq!(r["snapshot"]["words"].as_array().unwrap().len(), 1);
    }
    assert_eq!(
        before,
        fs::read(f.root.join("library/stability/epoch-0000.json")).unwrap()
    );
}

#[test]
fn guard_scope_digest_and_fuel_remain_distinct() {
    let f = Fixture::new();
    for (name, extra, status) in [
        ("zero.json", vec!["--word", "0", "--input", "0"], "Rejected"),
        (
            "outside.json",
            vec!["--word", "0", "--input", "9"],
            "Rejected",
        ),
        (
            "word.json",
            vec!["--word", "999", "--input", "2"],
            "Rejected",
        ),
        (
            "fuel.json",
            vec!["--word", "0", "--input", "2", "--fuel", "0"],
            "Unknown",
        ),
        (
            "mid-fuel.json",
            vec!["--word", "0", "--input", "2", "--fuel", "5"],
            "Unknown",
        ),
    ] {
        assert!(!f.command("reuse", name, &extra).status.success());
        assert_eq!(f.report(name)["status"], status);
        assert!(f.report(name)["reuse"].is_null());
    }
    assert!(
        !f.command(
            "check",
            "digest.json",
            &["--expect-digest", &"f".repeat(64)]
        )
        .status
        .success()
    );
    assert_eq!(f.report("digest.json")["status"], "Rejected");
}

#[test]
fn forged_snapshot_and_unrecognized_schema_are_not_admitted() {
    for schema in [false, true] {
        let f = Fixture::new();
        let path = f.root.join("library/stability/epoch-0000.json");
        let mut data: Value = serde_json::from_slice(&fs::read(&path).unwrap()).unwrap();
        if schema {
            data["schema"] = json!("adva.run.program.research");
        } else {
            data["analysis"]["readings"][0]["active"] = json!([]);
        }
        fs::write(&path, serde_json::to_vec(&data).unwrap()).unwrap();
        assert!(!f.command("check", "bad.json", &[]).status.success());
        assert_eq!(f.report("bad.json")["status"], "Rejected");
    }
}

#[test]
fn outputs_are_fresh_outside_library_and_options_are_unambiguous() {
    let f = Fixture::new();
    fs::write(f.root.join("occupied.json"), b"retain me").unwrap();
    assert!(!f.command("check", "occupied.json", &[]).status.success());
    assert_eq!(
        fs::read(f.root.join("occupied.json")).unwrap(),
        b"retain me"
    );
    assert!(!f.command("check", "library/new.json", &[]).status.success());
    assert!(!f.root.join("library/new.json").exists());
    for (name, args) in [
        ("repeat.json", vec!["--epoch", "0"]),
        ("extra.json", vec!["--input", "2"]),
        ("limit.json", vec!["--fuel", "50001"]),
    ] {
        assert!(!f.command("check", name, &args).status.success());
        assert!(!f.root.join(name).exists());
    }
}

#[test]
fn missing_epoch_keeps_a_rejection_report() {
    let f = Fixture::new();
    fs::remove_file(f.root.join("library/stability/epoch-0000.json")).unwrap();
    assert!(!f.command("check", "missing.json", &[]).status.success());
    assert_eq!(f.report("missing.json")["status"], "Rejected");
}
