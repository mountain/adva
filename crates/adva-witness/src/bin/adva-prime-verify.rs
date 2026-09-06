//! Bounded file interface for the Research 0148 exact prime checker.

use std::env;
use std::ffi::OsString;
use std::fs::{self, File, OpenOptions};
use std::io::{self, Read, Write};
use std::path::{Path, PathBuf};
use std::process::ExitCode;

use adva_witness::{
    PrimeExtensionRequestV0, PrimeExtensionResultV0, reject_prime_extension_input_v0,
    verify_prime_extension_v0,
};

const INPUT_LIMIT: u64 = 16 * 1024;
const OUTPUT_LIMIT: usize = 256 * 1024;

#[derive(Debug)]
struct TemporaryOutput(PathBuf);

impl Drop for TemporaryOutput {
    fn drop(&mut self) {
        let _ = fs::remove_file(&self.0);
    }
}

fn write_new(path: &Path, result: &PrimeExtensionResultV0) -> io::Result<()> {
    let mut bytes = serde_json::to_vec_pretty(result).map_err(io::Error::other)?;
    bytes.push(b'\n');
    if bytes.len() > OUTPUT_LIMIT {
        return Err(io::Error::other("result exceeds 262144 bytes"));
    }
    let name = path
        .file_name()
        .ok_or_else(|| io::Error::other("output needs a filename"))?;
    let mut temporary_name = OsString::from(".");
    temporary_name.push(name);
    temporary_name.push(format!(".{}.prime.tmp", std::process::id()));
    let temporary_path = path.with_file_name(temporary_name);
    let mut file = OpenOptions::new()
        .create_new(true)
        .write(true)
        .open(&temporary_path)?;
    let temporary = TemporaryOutput(temporary_path);
    file.write_all(&bytes)?;
    file.sync_all()?;
    drop(file);
    // An existing output is never replaced; no rename-overwrite fallback.
    fs::hard_link(&temporary.0, path)?;
    Ok(())
}

fn load_request(path: &Path) -> io::Result<PrimeExtensionResultV0> {
    let mut bytes = Vec::new();
    File::open(path)?
        .take(INPUT_LIMIT + 1)
        .read_to_end(&mut bytes)?;
    if bytes.len() as u64 > INPUT_LIMIT {
        return Ok(reject_prime_extension_input_v0("input exceeds 16384 bytes"));
    }
    let result = match serde_json::from_slice::<PrimeExtensionRequestV0>(&bytes) {
        Ok(request) => verify_prime_extension_v0(request),
        Err(_) => reject_prime_extension_input_v0("input is not a strict prime-extension request"),
    };
    Ok(result)
}

fn run() -> io::Result<u8> {
    let mut args = env::args_os().skip(1);
    let usage = || io::Error::other("usage: adva-prime-verify INPUT --output NEW");
    let input = args.next().ok_or_else(usage)?;
    if args.next().as_deref() != Some(std::ffi::OsStr::new("--output")) {
        return Err(usage());
    }
    let output = args.next().ok_or_else(usage)?;
    if args.next().is_some() {
        return Err(usage());
    }
    let result = load_request(Path::new(&input))?;
    write_new(Path::new(&output), &result)?;
    println!("{}", result.status);
    Ok(match result.status.as_str() {
        "FiniteExtensionVerified" => 0,
        "Unknown" => 3,
        _ => 2,
    })
}

fn main() -> ExitCode {
    match run() {
        Ok(code) => ExitCode::from(code),
        Err(error) => {
            eprintln!("adva-prime-verify: {error}");
            ExitCode::from(2)
        }
    }
}
