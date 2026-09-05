use adva_witness::{derive_trace_projection_witness_pair_v0, load_trace_arithmetic_v0};
use std::error::Error;
use std::io::{self, Write};
use std::time::Instant;

fn main() -> Result<(), Box<dyn Error>> {
    let mut args = std::env::args_os().skip(1);
    let path = args.next().ok_or("expected a trace-arithmetic .adva path")?;
    if args.next().is_some() {
        return Err("expected exactly one trace-arithmetic .adva path".into());
    }
    let started = Instant::now();
    let calibration = load_trace_arithmetic_v0(path)?;
    let loaded = started.elapsed();
    let witness = derive_trace_projection_witness_pair_v0(&calibration)?;
    let derived = started.elapsed();
    let json = format!("{}\n", witness.to_json()?);
    let encoded = started.elapsed();
    io::stdout().lock().write_all(json.as_bytes())?;
    eprintln!(
        "temporal_count_witnesses=2 construction_recovery=refuted source_questions={} bytes={}",
        witness.source_calibration.questions.len(),
        json.len()
    );
    eprintln!(
        "load_check_us={} derive_check_us={} recheck_encode_us={} peak_memory=unmeasured",
        loaded.as_micros(),
        (derived - loaded).as_micros(),
        (encoded - derived).as_micros()
    );
    Ok(())
}
