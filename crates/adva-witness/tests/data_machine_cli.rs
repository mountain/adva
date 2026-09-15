use adva_witness::{DataMachineRunV0, DataMachineStatusV0, MachineDataV0, MachinePhaseV0};
use std::fs;
use std::path::PathBuf;
use std::process::{Command, Output};
use std::sync::atomic::{AtomicUsize, Ordering};

static NEXT: AtomicUsize = AtomicUsize::new(0);
struct Fixture(PathBuf);
impl Fixture {
    fn new() -> Self {
        let path = std::env::temp_dir().join(format!(
            "adva-data-cli-{}-{}",
            std::process::id(),
            NEXT.fetch_add(1, Ordering::Relaxed)
        ));
        fs::create_dir(&path).unwrap();
        fs::write(
            path.join("interpreter.adva"),
            include_str!("../../../programs/bounded-interpreter/interpreter.adva"),
        )
        .unwrap();
        fs::write(
            path.join("input.json"),
            include_str!("../../../programs/bounded-interpreter/input.json"),
        )
        .unwrap();
        Self(path)
    }
    fn run(&self, name: &str, fuel: u32, quantum: u32, extra: &[&str]) -> Output {
        Command::new(env!("CARGO_BIN_EXE_adva"))
            .current_dir(&self.0)
            .args([
                "data-run",
                "interpreter.adva",
                "--input",
                "input.json",
                "--fuel",
                &fuel.to_string(),
                "--quantum",
                &quantum.to_string(),
                "--output",
                name,
            ])
            .args(extra)
            .output()
            .unwrap()
    }
    fn read(&self, name: &str) -> DataMachineRunV0 {
        serde_json::from_slice(&fs::read(self.0.join(name)).unwrap()).unwrap()
    }
}
impl Drop for Fixture {
    fn drop(&mut self) {
        fs::remove_dir_all(&self.0).unwrap();
    }
}

#[test]
fn actual_cli_runs_checks_and_refuses_overwrite() {
    let f = Fixture::new();
    assert!(f.run("run.adva", 2048, 2048, &[]).status.success());
    assert_eq!(
        f.read("run.adva").state.phase,
        MachinePhaseV0::Returned {
            value: MachineDataV0::Integer { value: 14 }
        }
    );
    assert!(
        f.run("check.adva", 2048, 0, &["--check", "run.adva"])
            .status
            .success()
    );
    let before = fs::read(f.0.join("run.adva")).unwrap();
    assert!(!f.run("run.adva", 2048, 2048, &[]).status.success());
    assert_eq!(fs::read(f.0.join("run.adva")).unwrap(), before);
}

#[test]
fn actual_cli_resumes_without_changing_original_budget() {
    let f = Fixture::new();
    assert!(f.run("prefix.adva", 2048, 17, &[]).status.success());
    assert!(
        f.run("end.adva", 2048, 2048, &["--resume", "prefix.adva"])
            .status
            .success()
    );
    assert_eq!(f.read("end.adva").status, DataMachineStatusV0::Returned);
    assert!(f.run("empty.adva", 0, 100, &[]).status.success());
    assert!(
        !f.run("refill.adva", 1, 1, &["--resume", "empty.adva"])
            .status
            .success()
    );
    assert!(!f.0.join("refill.adva").exists());
}

#[test]
fn actual_cli_rejects_mutated_state_and_boolean_integer() {
    let f = Fixture::new();
    assert!(f.run("prefix.adva", 2048, 17, &[]).status.success());
    let mut report = f.read("prefix.adva");
    report.state.spent = 0;
    fs::write(
        f.0.join("tampered.adva"),
        serde_json::to_vec(&report).unwrap(),
    )
    .unwrap();
    assert!(
        !f.run("bad.adva", 2048, 1, &["--resume", "tampered.adva"])
            .status
            .success()
    );
    fs::write(f.0.join("input.json"), r#"{"kind":"integer","value":true}"#).unwrap();
    assert!(!f.run("boolean.adva", 2048, 1, &[]).status.success());
    assert!(!f.0.join("boolean.adva").exists());
}

#[test]
fn actual_cli_rejects_duplicate_options_and_oversized_input() {
    let f = Fixture::new();
    assert!(
        !f.run("duplicate.adva", 10, 10, &["--fuel", "20"])
            .status
            .success()
    );
    fs::write(f.0.join("input.json"), vec![b' '; 32769]).unwrap();
    assert!(!f.run("large.adva", 10, 10, &[]).status.success());
    assert!(!f.0.join("large.adva").exists());
}
