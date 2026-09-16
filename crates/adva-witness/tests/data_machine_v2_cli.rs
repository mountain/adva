use adva_witness::{DataMachineRunV2, MachineDataV2, MachinePhaseV2};
use std::fs;
use std::path::PathBuf;
use std::process::{Command, Output};

struct Fixture(PathBuf);

impl Fixture {
    fn new() -> Self {
        let path = std::env::temp_dir().join(format!("adva-mix-v2-cli-{}", std::process::id()));
        fs::create_dir(&path).unwrap();
        fs::write(
            path.join("residual.adva"),
            include_str!("../../../experiments/bounded_mix/evidence/v2-attempt-01/affine-0-compiled-residual.target.adva"),
        )
        .unwrap();
        fs::write(path.join("input.json"), r#"{"kind":"integer","value":7}"#).unwrap();
        Self(path)
    }

    fn run(&self, output: &str, fuel: &str, quantum: &str, extra: &[&str]) -> Output {
        Command::new(env!("CARGO_BIN_EXE_adva"))
            .current_dir(&self.0)
            .args([
                "data-run-v2",
                "residual.adva",
                "--input",
                "input.json",
                "--fuel",
                fuel,
                "--quantum",
                quantum,
                "--output",
                output,
            ])
            .args(extra)
            .output()
            .unwrap()
    }

    fn read(&self, name: &str) -> DataMachineRunV2 {
        serde_json::from_slice(&fs::read(self.0.join(name)).unwrap()).unwrap()
    }
}

impl Drop for Fixture {
    fn drop(&mut self) {
        fs::remove_dir_all(&self.0).unwrap();
    }
}

#[test]
fn actual_cli_executes_generated_residual_and_keeps_original_checkpoint_budget() {
    let f = Fixture::new();
    assert!(f.run("full.adva", "100", "100", &[]).status.success());
    let full = f.read("full.adva");
    assert_eq!(
        full.state.phase,
        MachinePhaseV2::Returned {
            value: MachineDataV2::Integer { value: 17 }
        }
    );
    assert!(f.run("prefix.adva", "100", "17", &[]).status.success());
    assert!(
        f.run("resumed.adva", "100", "100", &["--resume", "prefix.adva"])
            .status
            .success()
    );
    let resumed = f.read("resumed.adva");
    assert_eq!(resumed.state, full.state);
    assert_eq!(resumed.trace, full.trace);
    assert!(
        f.run("checked.adva", "100", "0", &["--check", "full.adva"])
            .status
            .success()
    );
    assert!(
        !f.run("refuel.adva", "101", "100", &["--resume", "prefix.adva"])
            .status
            .success()
    );
    assert!(!f.0.join("refuel.adva").exists());
    let before = fs::read(f.0.join("full.adva")).unwrap();
    assert!(!f.run("full.adva", "100", "100", &[]).status.success());
    assert_eq!(fs::read(f.0.join("full.adva")).unwrap(), before);
}
