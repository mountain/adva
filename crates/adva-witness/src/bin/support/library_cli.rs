//! Read-only CLI for the existing bounded epoch loader and guarded word reuse.
//! No document-wide execution, new witness rules, or automatic publication.
use adva_witness::{
    LibraryBudgetV0, LibraryCheckpointErrorV0, library_checker_revision_v0, load_library_v0,
    reuse_library_word_v0,
};
use serde_json::{Value, json};
use std::collections::BTreeMap;
use std::error::Error;
use std::fs::{self, OpenOptions};
use std::io::{self, Write};
use std::path::{Path, PathBuf};
use std::time::Instant;

const MAX_REPORT_BYTES: usize = 2 * 1024 * 1024;

fn invalid(message: impl Into<String>) -> io::Error {
    io::Error::new(io::ErrorKind::InvalidInput, message.into())
}

#[derive(Debug)]
struct Request {
    action: String,
    library: PathBuf,
    epoch: u32,
    word: Option<usize>,
    input: Option<i32>,
    output: PathBuf,
    fuel: u32,
    expected: Option<String>,
}

fn parse(mut arguments: impl Iterator<Item = String>) -> io::Result<Request> {
    let action = arguments
        .next()
        .ok_or_else(|| invalid("missing library action"))?;
    if action != "check" && action != "reuse" {
        return Err(invalid("library action must be check or reuse"));
    }
    let mut options = BTreeMap::new();
    while let Some(key) = arguments.next() {
        if ![
            "--path",
            "--epoch",
            "--word",
            "--input",
            "--output",
            "--fuel",
            "--expect-digest",
        ]
        .contains(&key.as_str())
            || options.contains_key(&key)
        {
            return Err(invalid(format!("unknown or repeated option {key}")));
        }
        let value = arguments
            .next()
            .ok_or_else(|| invalid(format!("missing value for {key}")))?;
        options.insert(key, value);
    }
    let required = |key: &str| {
        options
            .get(key)
            .cloned()
            .ok_or_else(|| invalid(format!("{key} is required")))
    };
    let epoch = required("--epoch")?
        .parse::<u32>()
        .map_err(|_| invalid("invalid epoch"))?;
    let fuel = options
        .get("--fuel")
        .map_or(Ok(50_000), |v| v.parse::<u32>())
        .map_err(|_| invalid("invalid fuel"))?;
    if epoch > 3 || fuel > 50_000 {
        return Err(invalid("epoch must be 0..3; fuel must be 0..50000"));
    }
    let (word, input) = if action == "reuse" {
        (
            Some(
                required("--word")?
                    .parse()
                    .map_err(|_| invalid("invalid word"))?,
            ),
            Some(
                required("--input")?
                    .parse()
                    .map_err(|_| invalid("invalid input"))?,
            ),
        )
    } else {
        if options.contains_key("--word") || options.contains_key("--input") {
            return Err(invalid("check does not accept --word or --input"));
        }
        (None, None)
    };
    let expected = options.get("--expect-digest").cloned();
    if expected
        .as_ref()
        .is_some_and(|v| v.len() != 64 || !v.bytes().all(|b| b.is_ascii_hexdigit()))
    {
        return Err(invalid(
            "expected digest must be 64 hexadecimal BLAKE3 digits",
        ));
    }
    Ok(Request {
        action,
        library: PathBuf::from(required("--path")?),
        epoch,
        word,
        input,
        output: PathBuf::from(required("--output")?),
        fuel,
        expected: expected.map(|v| v.to_ascii_lowercase()),
    })
}

fn inspect(
    request: &Request,
    budget: &mut LibraryBudgetV0,
    report: &mut Value,
) -> Result<(), LibraryCheckpointErrorV0> {
    let loaded = load_library_v0(&request.library.join("stability"), request.epoch, budget)?;
    report["snapshot_digest"] = json!(loaded.digest());
    if let Some(expected) = &request.expected {
        budget.charge()?;
        if loaded.digest() != expected {
            return Err(LibraryCheckpointErrorV0::Invalid(
                "expected snapshot digest differs".into(),
            ));
        }
        report["expected_digest_matched"] = json!(true);
    }
    // Keep the original expressions and scoped witness nodes beside the result.
    report["snapshot"] = serde_json::to_value(loaded.snapshot())?;
    if let (Some(word), Some(input)) = (request.word, request.input) {
        report["reuse"] =
            serde_json::to_value(reuse_library_word_v0(&loaded, word, input, budget)?)?;
        report["status"] = json!("ReuseChecked");
    } else {
        report["status"] = json!("SnapshotChecked");
    }
    Ok(())
}

// Publish a complete report without overwriting another file. Inputs and their
// library directory are never destinations. Hard-link publication is required.
fn publish(output: &Path, bytes: &[u8]) -> io::Result<()> {
    let mut name = output
        .file_name()
        .ok_or_else(|| invalid("output needs a file name"))?
        .to_os_string();
    name.push(format!(".{}.pending", std::process::id()));
    let staged = output.with_file_name(name);
    let mut file = OpenOptions::new()
        .write(true)
        .create_new(true)
        .open(&staged)?;
    let result = (|| {
        file.write_all(bytes)?;
        file.sync_all()?;
        drop(file);
        fs::hard_link(&staged, output)
    })();
    let cleanup = fs::remove_file(staged);
    result?;
    cleanup
}

pub fn run(arguments: impl Iterator<Item = String>) -> Result<(), Box<dyn Error>> {
    let request = parse(arguments)?;
    let started = Instant::now();
    if fs::symlink_metadata(&request.output).is_ok() {
        return Err(invalid("output already exists; choose a fresh path").into());
    }
    let parent = request
        .output
        .parent()
        .filter(|p| !p.as_os_str().is_empty())
        .unwrap_or(Path::new("."));
    let parent = parent.canonicalize()?;
    if request
        .library
        .canonicalize()
        .is_ok_and(|library| parent.starts_with(library))
    {
        return Err(invalid("report must be outside the read-only library").into());
    }
    let mut budget = LibraryBudgetV0::new(request.fuel)?;
    let mut report = json!({
        "schema": "adva.library-cli-report.research.v0",
        "status": "Rejected", "action": request.action,
        "request": {"library_root": request.library, "epoch": request.epoch,
            "word": request.word, "input": request.input, "fuel": request.fuel,
            "expected_snapshot_digest": request.expected},
        "checker_revision": library_checker_revision_v0(),
        "snapshot_digest": null, "expected_digest_matched": null,
        "snapshot": null, "reuse": null, "error": null,
        "scope": "Rust-rechecked bounded research epoch and optional guarded exact-integer reuse; supplied observations remain assumptions",
        "authentication": "not-established", "native_free": "NotGranted",
        "peak_memory_bytes": null,
        "fuel_scope": "Existing shared library logical checks; terminal report I/O and host work are not fuel units"
    });
    let outcome = inspect(&request, &mut budget, &mut report);
    if let Err(error) = &outcome {
        report["status"] = json!(if matches!(error, LibraryCheckpointErrorV0::Unknown) {
            "Unknown"
        } else {
            "Rejected"
        });
        report["error"] = json!(error.to_string());
    }
    report["fuel"] = serde_json::to_value(&budget)?;
    report["wall_seconds_before_serialization"] = json!(started.elapsed().as_secs_f64());
    let mut bytes = serde_json::to_vec_pretty(&report)?;
    bytes.push(b'\n');
    if bytes.len() > MAX_REPORT_BYTES {
        return Err(invalid("report exceeds 2 MiB cap; no report published").into());
    }
    publish(&request.output, &bytes)?;
    println!(
        "status={}; output={}",
        report["status"],
        request.output.display()
    );
    outcome.map_err(Into::into)
}
