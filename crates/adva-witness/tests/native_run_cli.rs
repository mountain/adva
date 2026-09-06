use serde_json::{Value, json};
use std::fs;
use std::io::ErrorKind;
use std::path::{Path, PathBuf};
use std::process::{Command, Output};
use std::sync::atomic::{AtomicU64, Ordering};

const SOURCE: &str = "(module demo (export calc) (def calc (fn ((x Real) (y Real) (z Real)) Real (add (use x) (mul (use y) (use z))))))";
static NEXT_DIRECTORY: AtomicU64 = AtomicU64::new(0);

struct TestDirectory(PathBuf);

impl TestDirectory {
    fn new() -> Self {
        loop {
            let sequence = NEXT_DIRECTORY.fetch_add(1, Ordering::Relaxed);
            let path = std::env::temp_dir().join(format!(
                "adva-native-run-cli-{}-{sequence}",
                std::process::id()
            ));
            match fs::create_dir(&path) {
                Ok(()) => return Self(path),
                Err(error) if error.kind() == ErrorKind::AlreadyExists => continue,
                Err(error) => panic!("cannot create test directory: {error}"),
            }
        }
    }

    fn path(&self, name: &str) -> PathBuf {
        self.0.join(name)
    }

    fn write_program(&self, program: &Value) -> PathBuf {
        let path = self.path("program.adva");
        fs::write(&path, serde_json::to_vec_pretty(program).unwrap()).unwrap();
        path
    }
}

impl Drop for TestDirectory {
    fn drop(&mut self) {
        let _ = fs::remove_dir_all(&self.0);
    }
}

fn program(x: i32, y: i32, z: i32) -> Value {
    json!({
        "schema": "adva.run.program.research",
        "version": 0,
        "source": SOURCE,
        "module": "demo",
        "entry": "calc",
        "inputs": { "x": x, "y": y, "z": z },
        "fuel": 16
    })
}

fn invoke(input: &Path, output: &Path) -> Output {
    Command::new(env!("CARGO_BIN_EXE_adva"))
        .arg("run")
        .arg(input)
        .arg("--output")
        .arg(output)
        .output()
        .expect("native adva CLI must be executable")
}

fn assert_exit(output: &Output, expected: i32) {
    assert_eq!(
        output.status.code(),
        Some(expected),
        "stdout: {}\nstderr: {}",
        String::from_utf8_lossy(&output.stdout),
        String::from_utf8_lossy(&output.stderr)
    );
}

fn read_report(path: &Path) -> Value {
    serde_json::from_slice(&fs::read(path).expect("CLI must save a report"))
        .expect("report must be JSON")
}

fn assert_rejected(output: &Output, report_path: &Path) {
    assert_exit(output, 2);
    let report = read_report(report_path);
    assert_eq!(report["state"], "Rejected");
    assert_eq!(report.get("evaluation"), Some(&Value::Null));
}

#[test]
fn run_executes_the_checked_native_program() {
    let directory = TestDirectory::new();
    let input = directory.write_program(&program(2, 3, 4));
    let report_path = directory.path("result.adva");

    let output = invoke(&input, &report_path);

    assert_exit(&output, 0);
    let report = read_report(&report_path);
    assert_eq!(report["state"], "Completed");
    assert_eq!(report["evaluation"]["values"], json!([14.0]));
}

#[test]
fn the_same_program_runs_with_a_fresh_input_instance() {
    let directory = TestDirectory::new();
    let input = directory.write_program(&program(5, 2, 3));
    let report_path = directory.path("result.adva");

    let output = invoke(&input, &report_path);

    assert_exit(&output, 0);
    let report = read_report(&report_path);
    assert_eq!(report["state"], "Completed");
    assert_eq!(report["evaluation"]["values"], json!([11.0]));
}

#[test]
fn implicit_input_reuse_is_rejected_with_a_report() {
    let directory = TestDirectory::new();
    let mut document = program(2, 3, 4);
    document["source"] = json!(
        "(module demo (export calc) (def calc (fn ((x Real)) Real (add (use x) (use x)))))"
    );
    document["inputs"] = json!({ "x": 2 });
    let input = directory.write_program(&document);
    let report_path = directory.path("result.adva");

    let output = invoke(&input, &report_path);

    assert_rejected(&output, &report_path);
}

#[test]
fn an_unknown_program_schema_is_rejected_with_a_report() {
    let directory = TestDirectory::new();
    let mut document = program(2, 3, 4);
    document["schema"] = json!("adva.unregistered-program.research");
    let input = directory.write_program(&document);
    let report_path = directory.path("result.adva");

    let output = invoke(&input, &report_path);

    assert_rejected(&output, &report_path);
}

#[test]
fn insufficient_fuel_is_rejected_with_a_report() {
    let directory = TestDirectory::new();
    let mut document = program(2, 3, 4);
    document["fuel"] = json!(0);
    let input = directory.write_program(&document);
    let report_path = directory.path("result.adva");

    let output = invoke(&input, &report_path);

    assert_rejected(&output, &report_path);
}

#[test]
fn an_existing_output_is_preserved() {
    let directory = TestDirectory::new();
    let input = directory.write_program(&program(2, 3, 4));
    let input_before = fs::read(&input).unwrap();
    let report_path = directory.path("result.adva");
    let previous_report = b"preexisting evidence must not be overwritten\n";
    fs::write(&report_path, previous_report).unwrap();

    let output = invoke(&input, &report_path);

    assert_exit(&output, 2);
    assert_eq!(fs::read(&report_path).unwrap(), previous_report.to_vec());
    assert_eq!(fs::read(&input).unwrap(), input_before);
}

#[test]
fn using_the_input_as_output_preserves_the_program() {
    let directory = TestDirectory::new();
    let input = directory.write_program(&program(2, 3, 4));
    let input_before = fs::read(&input).unwrap();

    let output = invoke(&input, &input);

    assert_exit(&output, 2);
    assert_eq!(fs::read(&input).unwrap(), input_before);
}
