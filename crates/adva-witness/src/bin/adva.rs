use adva_witness::{
    AdvaDocumentV0, M6NamingPlanV0, calibrate_trace_arithmetic_v0,
    derive_inquiry_frontier_from_file_v0, learn_hypothesis_v0, load_exploration_contract_v0,
    load_inquiry_frontier_v0, load_resource_snapshot_v0, load_reveal_witness_v0,
    load_verification_contract_v0, load_verification_packet_v0, load_verification_subject_v0,
    run_m6_reveal_v0, save_hypothesis_transition_v0, save_inquiry_frontier_v0,
    save_reveal_witness_v0, save_trace_arithmetic_v0, save_verification_frontier_v0,
    save_verification_transition_v0, verify_obligations_v0,
};
use std::env;
use std::error::Error;
use std::fs;
use std::io::{self, ErrorKind};
use std::path::PathBuf;

const USAGE: &str = "usage:
  adva reveal <program.adva> --output <witness.adva> [--fuel N] [--print]
  adva trace-arithmetic <reveal-witness.adva> --output <calibration.adva> [--print]
  adva frontier <calibration.adva> --output <frontier.adva> [--print]
  adva learn <frontier.adva> <contract.adva> <resource.adva> --output <hypothesis.adva> --frontier-output <next-frontier.adva> [--print]
  adva verify <frontier.adva> <verifier.adva> <packet.adva> --output <verification.adva> --frontier-output <verification-frontier.adva> [--print]";

#[derive(Debug)]
struct RevealArgs {
    program: PathBuf,
    output: PathBuf,
    fuel: u64,
    print: bool,
}

#[derive(Debug)]
struct TraceArithmeticArgs {
    witness: PathBuf,
    output: PathBuf,
    print: bool,
}

#[derive(Debug)]
struct FrontierArgs {
    calibration: PathBuf,
    output: PathBuf,
    print: bool,
}

#[derive(Debug)]
struct LearnArgs {
    frontier: PathBuf,
    contract: PathBuf,
    resource: PathBuf,
    output: PathBuf,
    frontier_output: PathBuf,
    print: bool,
}

#[derive(Debug)]
struct VerifyArgs {
    frontier: PathBuf,
    contract: PathBuf,
    packet: PathBuf,
    output: PathBuf,
    frontier_output: PathBuf,
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
    match command.as_str() {
        "reveal" => run_reveal(parse_reveal_args(arguments)?),
        "trace-arithmetic" => run_trace_arithmetic(parse_trace_arithmetic_args(arguments)?),
        "frontier" => run_frontier(parse_frontier_args(arguments)?),
        "learn" => run_learn(parse_learn_args(arguments)?),
        "verify" => run_verify(parse_verify_args(arguments)?),
        _ => Err(invalid_input(format!("unknown command {command:?}")).into()),
    }
}

fn run_frontier(parsed: FrontierArgs) -> Result<(), Box<dyn Error>> {
    let frontier = derive_inquiry_frontier_from_file_v0(&parsed.calibration)?;
    let receipt = save_inquiry_frontier_v0(&parsed.output, &frontier)?;

    println!("sequence={}", frontier.lineage.sequence);
    println!("obligations={}", frontier.obligations.len());
    println!("pause={:?}", frontier.pause_reason);
    println!("source={}", frontier.source_calibration_digest);
    println!("frontier={}", receipt.artifact_digest);
    println!("output={}", receipt.path.display());
    if parsed.print {
        println!("INQUIRY_FRONTIER_BEGIN");
        println!("{}", frontier.to_json()?);
        println!("INQUIRY_FRONTIER_END");
    }
    Ok(())
}

fn run_learn(parsed: LearnArgs) -> Result<(), Box<dyn Error>> {
    let frontier = load_inquiry_frontier_v0(&parsed.frontier)?;
    let contract = load_exploration_contract_v0(&parsed.contract)?;
    let resource = load_resource_snapshot_v0(&parsed.resource)?;
    let transition = learn_hypothesis_v0(&frontier, &contract, &resource)?;
    let transition_receipt = save_hypothesis_transition_v0(&parsed.output, &transition)?;
    let next_frontier = &transition.output.evidence.next_frontier;
    let frontier_receipt = save_inquiry_frontier_v0(&parsed.frontier_output, next_frontier)?;

    println!("mechanism={:?}", transition.output.history.mechanism);
    println!("hypothesis={}", transition.output.result.local_name);
    println!("state={:?}", transition.output.result.state);
    println!("obligations={}", next_frontier.obligations.len());
    println!("next_sequence={}", next_frontier.lineage.sequence);
    println!(
        "new_words={}",
        transition.output.history.introduced_words.join(",")
    );
    println!("resource={}", transition.output.result.resource_digest);
    println!("transition={}", transition_receipt.artifact_digest);
    println!("next_frontier={}", frontier_receipt.artifact_digest);
    println!("output={}", transition_receipt.path.display());
    println!("frontier_output={}", frontier_receipt.path.display());
    if parsed.print {
        println!("HYPOTHESIS_TRANSITION_BEGIN");
        println!("{}", transition.to_json()?);
        println!("HYPOTHESIS_TRANSITION_END");
        println!("NEXT_INQUIRY_FRONTIER_BEGIN");
        println!("{}", next_frontier.to_json()?);
        println!("NEXT_INQUIRY_FRONTIER_END");
    }
    Ok(())
}

fn run_verify(parsed: VerifyArgs) -> Result<(), Box<dyn Error>> {
    let subject = load_verification_subject_v0(&parsed.frontier)?;
    let contract = load_verification_contract_v0(&parsed.contract)?;
    let packet = load_verification_packet_v0(&parsed.packet)?;
    let transition = verify_obligations_v0(&subject, &contract, &packet)?;
    let transition_receipt = save_verification_transition_v0(&parsed.output, &transition)?;
    let next_frontier = &transition.output.evidence.residual_frontier;
    let frontier_receipt = save_verification_frontier_v0(&parsed.frontier_output, next_frontier)?;

    println!("mechanism={:?}", transition.output.history.mechanism);
    println!("state={:?}", transition.output.result.state);
    println!(
        "semantic_leaves={}->{}",
        transition.output.history.leaf_delta.semantic_before,
        transition.output.history.leaf_delta.semantic_after
    );
    println!(
        "custody_leaves={}->{}",
        transition.output.history.leaf_delta.custody_before,
        transition.output.history.leaf_delta.custody_after
    );
    println!("forks={}", transition.output.result.unresolved_forks);
    println!(
        "certificate={}",
        transition.output.result.certificate.is_some()
    );
    println!("transition={}", transition_receipt.artifact_digest);
    println!("next_frontier={}", frontier_receipt.artifact_digest);
    println!("output={}", transition_receipt.path.display());
    println!("frontier_output={}", frontier_receipt.path.display());
    if parsed.print {
        println!("VERIFICATION_TRANSITION_BEGIN");
        println!("{}", transition.to_json()?);
        println!("VERIFICATION_TRANSITION_END");
        println!("VERIFICATION_FRONTIER_BEGIN");
        println!("{}", next_frontier.to_json()?);
        println!("VERIFICATION_FRONTIER_END");
    }
    Ok(())
}

fn run_reveal(parsed: RevealArgs) -> Result<(), Box<dyn Error>> {
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

fn run_trace_arithmetic(parsed: TraceArithmeticArgs) -> Result<(), Box<dyn Error>> {
    let witness = load_reveal_witness_v0(&parsed.witness)?;
    let calibration = calibrate_trace_arithmetic_v0(&witness)?;
    let receipt = save_trace_arithmetic_v0(&parsed.output, &calibration)?;

    println!("time={:?}", calibration.alignment.time);
    println!("space={:?}", calibration.alignment.space);
    println!("construction={:?}", calibration.alignment.construction);
    println!(
        "holonomy_one={}",
        calibration.commutative_holonomy.right_over_left.is_one()
    );
    println!("truth_fiber={:?}", calibration.truth_fiber.state);
    println!("questions={}", calibration.questions.len());
    println!("source={}", calibration.source_witness_digest);
    println!("calibration={}", receipt.calibration_digest);
    println!("output={}", receipt.path.display());
    if parsed.print {
        println!("TRACE_ARITHMETIC_CALIBRATION_BEGIN");
        println!("{}", calibration.to_json()?);
        println!("TRACE_ARITHMETIC_CALIBRATION_END");
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

fn parse_trace_arithmetic_args(
    arguments: impl IntoIterator<Item = String>,
) -> io::Result<TraceArithmeticArgs> {
    let mut arguments = arguments.into_iter();
    let witness = arguments
        .next()
        .map(PathBuf::from)
        .ok_or_else(|| invalid_input("missing reveal witness"))?;
    let mut output = None;
    let mut print = false;
    while let Some(argument) = arguments.next() {
        match argument.as_str() {
            "--output" => {
                let value = arguments
                    .next()
                    .ok_or_else(|| invalid_input("--output requires a path"))?;
                output = Some(PathBuf::from(value));
            }
            "--print" => print = true,
            _ => return Err(invalid_input(format!("unknown argument {argument:?}"))),
        }
    }
    let output = output.ok_or_else(|| invalid_input("--output is required"))?;
    Ok(TraceArithmeticArgs {
        witness,
        output,
        print,
    })
}

fn parse_frontier_args(arguments: impl IntoIterator<Item = String>) -> io::Result<FrontierArgs> {
    let mut arguments = arguments.into_iter();
    let calibration = arguments
        .next()
        .map(PathBuf::from)
        .ok_or_else(|| invalid_input("missing trace-arithmetic calibration"))?;
    let mut output = None;
    let mut print = false;
    while let Some(argument) = arguments.next() {
        match argument.as_str() {
            "--output" => {
                let value = arguments
                    .next()
                    .ok_or_else(|| invalid_input("--output requires a path"))?;
                output = Some(PathBuf::from(value));
            }
            "--print" => print = true,
            _ => return Err(invalid_input(format!("unknown argument {argument:?}"))),
        }
    }
    Ok(FrontierArgs {
        calibration,
        output: output.ok_or_else(|| invalid_input("--output is required"))?,
        print,
    })
}

fn parse_learn_args(arguments: impl IntoIterator<Item = String>) -> io::Result<LearnArgs> {
    let mut arguments = arguments.into_iter();
    let frontier = arguments
        .next()
        .map(PathBuf::from)
        .ok_or_else(|| invalid_input("missing inquiry frontier"))?;
    let contract = arguments
        .next()
        .map(PathBuf::from)
        .ok_or_else(|| invalid_input("missing exploration contract"))?;
    let resource = arguments
        .next()
        .map(PathBuf::from)
        .ok_or_else(|| invalid_input("missing resource snapshot"))?;
    let mut output = None;
    let mut frontier_output = None;
    let mut print = false;
    while let Some(argument) = arguments.next() {
        match argument.as_str() {
            "--output" => {
                let value = arguments
                    .next()
                    .ok_or_else(|| invalid_input("--output requires a path"))?;
                output = Some(PathBuf::from(value));
            }
            "--frontier-output" => {
                let value = arguments
                    .next()
                    .ok_or_else(|| invalid_input("--frontier-output requires a path"))?;
                frontier_output = Some(PathBuf::from(value));
            }
            "--print" => print = true,
            _ => return Err(invalid_input(format!("unknown argument {argument:?}"))),
        }
    }
    Ok(LearnArgs {
        frontier,
        contract,
        resource,
        output: output.ok_or_else(|| invalid_input("--output is required"))?,
        frontier_output: frontier_output
            .ok_or_else(|| invalid_input("--frontier-output is required"))?,
        print,
    })
}

fn parse_verify_args(arguments: impl IntoIterator<Item = String>) -> io::Result<VerifyArgs> {
    let mut arguments = arguments.into_iter();
    let frontier = arguments
        .next()
        .map(PathBuf::from)
        .ok_or_else(|| invalid_input("missing verification frontier"))?;
    let contract = arguments
        .next()
        .map(PathBuf::from)
        .ok_or_else(|| invalid_input("missing verification contract"))?;
    let packet = arguments
        .next()
        .map(PathBuf::from)
        .ok_or_else(|| invalid_input("missing verification packet"))?;
    let mut output = None;
    let mut frontier_output = None;
    let mut print = false;
    while let Some(argument) = arguments.next() {
        match argument.as_str() {
            "--output" => {
                let value = arguments
                    .next()
                    .ok_or_else(|| invalid_input("--output requires a path"))?;
                output = Some(PathBuf::from(value));
            }
            "--frontier-output" => {
                let value = arguments
                    .next()
                    .ok_or_else(|| invalid_input("--frontier-output requires a path"))?;
                frontier_output = Some(PathBuf::from(value));
            }
            "--print" => print = true,
            _ => return Err(invalid_input(format!("unknown argument {argument:?}"))),
        }
    }
    Ok(VerifyArgs {
        frontier,
        contract,
        packet,
        output: output.ok_or_else(|| invalid_input("--output is required"))?,
        frontier_output: frontier_output
            .ok_or_else(|| invalid_input("--frontier-output is required"))?,
        print,
    })
}

fn invalid_input(detail: impl Into<String>) -> io::Error {
    io::Error::new(ErrorKind::InvalidInput, detail.into())
}
