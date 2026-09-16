//! File boundary for the separate research data-machine profile.
use adva_witness::{
    DATA_MACHINE_MAX_BYTES_V1, DATA_MACHINE_MAX_REPORT_V1, DataMachineProgramV1, DataMachineRunV1,
    DataMachineStatusV1, MachineDataV1, resume_data_machine_v1, run_data_machine_v1,
    verify_data_machine_run_v1,
};
use std::collections::BTreeMap;
use std::error::Error;
use std::fs::{self, File};
use std::io::{self, Read};
use std::path::Path;

fn invalid(message: impl Into<String>) -> io::Error {
    io::Error::new(io::ErrorKind::InvalidInput, message.into())
}

fn read(path: &str, max: usize) -> io::Result<String> {
    let file = File::open(path)?;
    if !file.metadata()?.is_file() {
        return Err(invalid("input must be a regular file"));
    }
    let mut source = String::new();
    file.take((max + 1) as u64).read_to_string(&mut source)?;
    if source.len() > max {
        return Err(invalid("input exceeds byte limit"));
    }
    Ok(source)
}

pub fn run(mut arguments: impl Iterator<Item = String>) -> Result<(), Box<dyn Error>> {
    let program_path = arguments.next().ok_or_else(|| invalid("missing program"))?;
    let mut options = BTreeMap::new();
    while let Some(key) = arguments.next() {
        if ![
            "--input",
            "--fuel",
            "--quantum",
            "--output",
            "--resume",
            "--check",
        ]
        .contains(&key.as_str())
            || options.contains_key(&key)
        {
            return Err(invalid("unknown or duplicate data-run option").into());
        }
        let value = arguments
            .next()
            .ok_or_else(|| invalid("option requires a value"))?;
        options.insert(key, value);
    }
    let required = |key: &str| -> Result<&str, io::Error> {
        options
            .get(key)
            .map(String::as_str)
            .ok_or_else(|| invalid(format!("missing {key}")))
    };
    let output = Path::new(required("--output")?);
    if Path::new(&program_path)
        .extension()
        .and_then(|s| s.to_str())
        != Some("adva")
        || output.extension().and_then(|s| s.to_str()) != Some("adva")
    {
        return Err(invalid("program and output require .adva extensions").into());
    }
    if fs::symlink_metadata(output).is_ok() {
        return Err(invalid("output already exists").into());
    }
    if options.contains_key("--resume") && options.contains_key("--check") {
        return Err(invalid("resume and check are exclusive").into());
    }
    let fuel: u32 = required("--fuel")?.parse()?;
    let quantum: u32 = required("--quantum")?.parse()?;
    let program: DataMachineProgramV1 =
        serde_json::from_str(&read(&program_path, DATA_MACHINE_MAX_BYTES_V1)?)?;
    let input: MachineDataV1 =
        serde_json::from_str(&read(required("--input")?, DATA_MACHINE_MAX_BYTES_V1)?)?;
    let (bytes, rejected, status) = if let Some(path) = options.get("--check") {
        if quantum != 0 {
            return Err(invalid("check requires zero quantum").into());
        }
        let checkpoint: DataMachineRunV1 =
            serde_json::from_str(&read(path, DATA_MACHINE_MAX_REPORT_V1)?)?;
        let reception =
            verify_data_machine_run_v1(&program, &input, fuel, &checkpoint).map_err(invalid)?;
        (
            serde_json::to_vec_pretty(&reception)?,
            false,
            "Verified".to_owned(),
        )
    } else {
        let report = if let Some(path) = options.get("--resume") {
            let checkpoint: DataMachineRunV1 =
                serde_json::from_str(&read(path, DATA_MACHINE_MAX_REPORT_V1)?)?;
            resume_data_machine_v1(&program, &input, fuel, &checkpoint, quantum)
        } else {
            run_data_machine_v1(&program, &input, fuel, quantum)
        }
        .map_err(invalid)?;
        (
            serde_json::to_vec_pretty(&report)?,
            report.status == DataMachineStatusV1::Rejected,
            format!("{:?}", report.status),
        )
    };
    if bytes.len() > DATA_MACHINE_MAX_REPORT_V1 {
        return Err(invalid("report exceeds byte limit").into());
    }
    super::native_run_cli::publish_new(output, &bytes)?;
    println!("status={status}; output={}", output.display());
    if rejected {
        return Err(invalid("data-machine execution rejected; see retained report").into());
    }
    Ok(())
}
