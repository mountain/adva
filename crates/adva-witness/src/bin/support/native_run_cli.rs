//! File adapter for the bounded native program envelope.
use adva_witness::run_native_program_v0;
use std::error::Error;
use std::fs::{self, File, OpenOptions};
use std::io::{self, Read, Write};
use std::path::{Path, PathBuf};

const MAX_INPUT_BYTES: u64 = 16 * 1024;
const MAX_REPORT_BYTES: usize = 2 * 1024 * 1024;

fn invalid(message: impl Into<String>) -> io::Error {
    io::Error::new(io::ErrorKind::InvalidInput, message.into())
}

fn check_extension(path: &Path) -> io::Result<()> {
    if path.extension().and_then(|ext| ext.to_str()) != Some("adva") {
        return Err(invalid(
            "native run input and output require .adva extensions",
        ));
    }
    Ok(())
}

pub fn run(arguments: impl Iterator<Item = String>) -> Result<(), Box<dyn Error>> {
    let mut arguments = arguments;
    let input = PathBuf::from(arguments.next().ok_or_else(|| invalid("missing program"))?);
    let mut output = None;
    let mut print = false;
    while let Some(argument) = arguments.next() {
        match argument.as_str() {
            "--output" if output.is_none() => {
                output = Some(PathBuf::from(
                    arguments
                        .next()
                        .ok_or_else(|| invalid("--output requires a path"))?,
                ));
            }
            "--print" if !print => print = true,
            _ => return Err(invalid(format!("unknown or repeated argument {argument:?}")).into()),
        }
    }
    let output = output.ok_or_else(|| invalid("--output is required"))?;
    check_extension(&input)?;
    check_extension(&output)?;
    if fs::symlink_metadata(&output).is_ok() {
        return Err(invalid("output already exists; choose a new path").into());
    }
    let file = File::open(&input)?;
    if !file.metadata()?.is_file() {
        return Err(invalid("program must be a regular file").into());
    }
    let mut source = String::new();
    file.take(MAX_INPUT_BYTES + 1).read_to_string(&mut source)?;
    let report = run_native_program_v0(&source);
    let bytes = serde_json::to_vec_pretty(&report)?;
    if bytes.len() > MAX_REPORT_BYTES {
        return Err(
            invalid("report exceeds the 2 MiB serialization limit; nothing published").into(),
        );
    }
    publish_new(&output, &bytes)?;
    println!("state={}", report.state);
    println!("output={}", output.display());
    if print {
        println!("NATIVE_RUN_REPORT_BEGIN");
        println!("{}", std::str::from_utf8(&bytes)?);
        println!("NATIVE_RUN_REPORT_END");
    }
    if report.state != "Completed" {
        return Err(invalid(
            report
                .error
                .unwrap_or_else(|| "native program rejected".to_owned()),
        )
        .into());
    }
    Ok(())
}

// A same-directory hard link publishes a completely written file without
// replacing an existing target. A failed write never leaves a result document.
fn publish_new(output: &Path, bytes: &[u8]) -> io::Result<()> {
    let name = output
        .file_name()
        .ok_or_else(|| invalid("output needs a file name"))?;
    let mut temporary_name = name.to_os_string();
    temporary_name.push(format!(".{}.tmp", std::process::id()));
    let temporary = output.with_file_name(temporary_name);
    let mut file = OpenOptions::new()
        .write(true)
        .create_new(true)
        .open(&temporary)?;
    let result = (|| {
        file.write_all(bytes)?;
        file.sync_all()?;
        drop(file);
        fs::hard_link(&temporary, output)
    })();
    let cleanup = fs::remove_file(&temporary);
    result?;
    cleanup
}
