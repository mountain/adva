use adva_witness::{AdvaDocumentV0, M6NamingPlanV0, run_m6_reveal_v0, save_reveal_witness_v0};
use std::env;
use std::error::Error;
use std::fs;
use std::io::{self, ErrorKind};
use std::path::PathBuf;

const USAGE: &str =
    "usage: adva reveal <program.adva> --output <witness.adva> [--fuel N] [--print]";

#[derive(Debug)]
struct RevealArgs {
    program: PathBuf,
    output: PathBuf,
    fuel: u64,
    print: bool,
}

fn main() {
    if let Err(error) = run() {
        eprintln!("adva: {error}");
        eprintln!("{USAGE}");
        std::process::exit(2);
    }
}

fn run() -> Result<(), Box<dyn Error>> {
    let mut arguments = env::args().skip(1);
    let command = arguments
        .next()
        .ok_or_else(|| invalid_input("missing command"))?;
    if command != "reveal" {
        return Err(invalid_input(format!("unknown command {command:?}")).into());
    }
    let parsed = parse_reveal_args(arguments)?;
    let source = fs::read_to_string(&parsed.program)?;
    let document = AdvaDocumentV0::from_json(&source)?;
    let witness = run_m6_reveal_v0(&document, M6NamingPlanV0::first_calibration(), parsed.fuel)?;
    let receipt = save_reveal_witness_v0(&parsed.output, &witness)?;

    println!("state={:?}", witness.state);
    println!("fuel={}/{}", witness.fuel_used, witness.fuel_requested);
    println!("questions={}", witness.questions.len());
    println!("source={}", witness.source_document_digest);
    println!("witness={}", receipt.witness_digest);
    println!("output={}", receipt.path.display());
    if parsed.print {
        println!("FIRST_REVEAL_WITNESS_BEGIN");
        println!("{}", witness.to_json()?);
        println!("FIRST_REVEAL_WITNESS_END");
    }
    Ok(())
}

fn parse_reveal_args(arguments: impl IntoIterator<Item = String>) -> io::Result<RevealArgs> {
    let mut arguments = arguments.into_iter();
    let program = arguments
        .next()
        .map(PathBuf::from)
        .ok_or_else(|| invalid_input("missing reveal program"))?;
    let mut output = None;
    let mut fuel = 6;
    let mut print = false;
    while let Some(argument) = arguments.next() {
        match argument.as_str() {
            "--output" => {
                let value = arguments
                    .next()
                    .ok_or_else(|| invalid_input("--output requires a path"))?;
                output = Some(PathBuf::from(value));
            }
            "--fuel" => {
                let value = arguments
                    .next()
                    .ok_or_else(|| invalid_input("--fuel requires an integer"))?;
                fuel = value
                    .parse::<u64>()
                    .map_err(|_| invalid_input("--fuel must be a nonnegative integer"))?;
            }
            "--print" => print = true,
            _ => return Err(invalid_input(format!("unknown argument {argument:?}"))),
        }
    }
    let output = output.ok_or_else(|| invalid_input("--output is required"))?;
    Ok(RevealArgs {
        program,
        output,
        fuel,
        print,
    })
}

fn invalid_input(detail: impl Into<String>) -> io::Error {
    io::Error::new(ErrorKind::InvalidInput, detail.into())
}
