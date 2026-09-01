use adva_labs_search::{
    LabsError, LabsResult, ProgramKind, RunReport, SearchConfig, SearchEngine, exhaustive_optimum,
    read_run_report, run_parallel, write_json,
};
use std::collections::{BTreeMap, HashSet};
use std::env;
use std::path::{Path, PathBuf};
use std::process::ExitCode;

#[derive(Debug)]
struct ParsedArgs {
    values: BTreeMap<String, String>,
    switches: HashSet<String>,
    positionals: Vec<String>,
}

impl ParsedArgs {
    fn parse(arguments: impl Iterator<Item = String>) -> LabsResult<Self> {
        let mut values = BTreeMap::new();
        let mut switches = HashSet::new();
        let mut positionals = Vec::new();
        let mut arguments = arguments.peekable();

        while let Some(argument) = arguments.next() {
            if !argument.starts_with("--") {
                positionals.push(argument);
                continue;
            }
            let key = argument.trim_start_matches("--").to_owned();
            if key == "help" || key == "quiet" {
                switches.insert(key);
                continue;
            }
            let value = arguments.next().ok_or_else(|| {
                LabsError::InvalidConfig(format!("option --{key} requires a value"))
            })?;
            if value.starts_with("--") {
                return Err(LabsError::InvalidConfig(format!(
                    "option --{key} requires a value; found {value}"
                )));
            }
            if values.insert(key.clone(), value).is_some() {
                return Err(LabsError::InvalidConfig(format!(
                    "option --{key} was supplied more than once"
                )));
            }
        }

        Ok(Self {
            values,
            switches,
            positionals,
        })
    }

    fn has(&self, key: &str) -> bool {
        self.switches.contains(key)
    }

    fn string(&self, key: &str) -> Option<&str> {
        self.values.get(key).map(String::as_str)
    }

    fn parse_value<T>(&self, key: &str, default: T) -> LabsResult<T>
    where
        T: std::str::FromStr,
        T::Err: std::fmt::Display,
    {
        match self.string(key) {
            Some(value) => value.parse().map_err(|error| {
                LabsError::InvalidConfig(format!("could not parse --{key}={value:?}: {error}"))
            }),
            None => Ok(default),
        }
    }

    fn required_value<T>(&self, key: &str) -> LabsResult<T>
    where
        T: std::str::FromStr,
        T::Err: std::fmt::Display,
    {
        let value = self.string(key).ok_or_else(|| {
            LabsError::InvalidConfig(format!("required option --{key} is missing"))
        })?;
        value.parse().map_err(|error| {
            LabsError::InvalidConfig(format!("could not parse --{key}={value:?}: {error}"))
        })
    }
}

fn parse_programs(value: Option<&str>) -> LabsResult<Vec<ProgramKind>> {
    match value {
        None => Ok(ProgramKind::ALL.to_vec()),
        Some(names) => {
            let programs: Vec<ProgramKind> = names
                .split(',')
                .map(ProgramKind::parse)
                .collect::<LabsResult<_>>()?;
            if programs.is_empty() {
                return Err(LabsError::InvalidConfig(
                    "--programs must name at least one program".to_owned(),
                ));
            }
            Ok(programs)
        }
    }
}

fn configure_search(arguments: &ParsedArgs) -> LabsResult<SearchConfig> {
    let length = arguments.required_value("length")?;
    let seed = arguments.parse_value("seed", 1_u64)?;
    let mut config = SearchConfig::for_length(length, seed);
    config.enabled_programs = parse_programs(arguments.string("programs"))?;
    config.initial_population =
        arguments.parse_value("initial-population", config.initial_population)?;
    config.move_samples = arguments.parse_value("move-samples", config.move_samples)?;
    config.temporal_top_k = arguments.parse_value("temporal-top-k", config.temporal_top_k)?;
    config.spatial_lags = arguments.parse_value("spatial-lags", config.spatial_lags)?;
    config.construction_trials =
        arguments.parse_value("construction-trials", config.construction_trials)?;
    config.construction_mutations =
        arguments.parse_value("construction-mutations", config.construction_mutations)?;
    config.construction_interval =
        arguments.parse_value("construction-interval", config.construction_interval)?;
    config.archive_size = arguments.parse_value("archive-size", config.archive_size)?;
    config.recent_flip_window =
        arguments.parse_value("recent-flip-window", config.recent_flip_window)?;
    config.restart_after = arguments.parse_value("restart-after", config.restart_after)?;
    config.scheduler_exploration =
        arguments.parse_value("scheduler-exploration", config.scheduler_exploration)?;
    config.trace_stride = arguments.parse_value("trace-stride", config.trace_stride)?;
    config.max_trace_events = arguments.parse_value("max-trace-events", config.max_trace_events)?;
    config.validate()?;
    Ok(config)
}

fn write_or_print_report(report: &RunReport, output: Option<&str>) -> LabsResult<()> {
    if let Some(path) = output {
        write_json(path, report)?;
    } else {
        serde_json::to_writer_pretty(std::io::stdout().lock(), report)?;
        println!();
    }
    Ok(())
}

fn run_single_with_checkpoints(
    mut engine: SearchEngine,
    additional_iterations: u64,
    checkpoint: Option<&Path>,
    checkpoint_every: u64,
    quiet: bool,
) -> LabsResult<RunReport> {
    let mut remaining = additional_iterations;
    while remaining > 0 {
        let chunk = if checkpoint_every == 0 {
            remaining
        } else {
            remaining.min(checkpoint_every)
        };
        engine.run_steps(chunk)?;
        remaining -= chunk;
        if let Some(path) = checkpoint {
            engine.save_checkpoint(path)?;
        }
        if !quiet {
            eprintln!(
                "iteration={} best_energy={} remaining={remaining}",
                engine.iteration(),
                engine.best_energy()
            );
        }
    }
    engine.report()
}

fn search_command(arguments: ParsedArgs) -> LabsResult<()> {
    if arguments.has("help") {
        print_search_help();
        return Ok(());
    }
    let iterations = arguments.parse_value("iterations", 100_000_u64)?;
    let workers = arguments.parse_value("workers", 1_usize)?;
    let output = arguments.string("output");
    let checkpoint = arguments.string("checkpoint").map(PathBuf::from);
    let checkpoint_every = arguments.parse_value("checkpoint-every", 100_000_u64)?;
    let quiet = arguments.has("quiet");

    let report = if let Some(resume_path) = arguments.string("resume") {
        if workers != 1 {
            return Err(LabsError::InvalidConfig(
                "checkpoint resume currently requires --workers 1".to_owned(),
            ));
        }
        let engine = SearchEngine::load_checkpoint(resume_path)?;
        run_single_with_checkpoints(
            engine,
            iterations,
            checkpoint
                .as_deref()
                .or_else(|| Some(Path::new(resume_path))),
            checkpoint_every,
            quiet,
        )?
    } else {
        let config = configure_search(&arguments)?;
        if workers == 1 {
            run_single_with_checkpoints(
                SearchEngine::new(config)?,
                iterations,
                checkpoint.as_deref(),
                checkpoint_every,
                quiet,
            )?
        } else {
            if checkpoint.is_some() {
                return Err(LabsError::InvalidConfig(
                    "periodic checkpoints are currently supported only with --workers 1".to_owned(),
                ));
            }
            run_parallel(config, iterations, workers)?
        }
    };

    report.verify()?;
    if !quiet {
        eprintln!(
            "verified length={} energy={} merit_factor={:.12} worker={}",
            report.best.length, report.best.energy, report.best.merit_factor, report.best_worker
        );
    }
    write_or_print_report(&report, output)
}

fn verify_command(arguments: ParsedArgs) -> LabsResult<()> {
    if arguments.has("help") {
        eprintln!("Usage: adva-labs-search verify <run-report.json>");
        return Ok(());
    }
    let path = arguments
        .positionals
        .first()
        .ok_or_else(|| LabsError::InvalidConfig("verify requires a JSON path".to_owned()))?;
    let report = read_run_report(path)?;
    let evaluation = report.verify()?;
    println!(
        "verified length={} energy={} correlations={:?} merit_factor={:.12}",
        report.best.length, evaluation.energy, evaluation.correlations, report.best.merit_factor
    );
    Ok(())
}

fn exhaustive_command(arguments: ParsedArgs) -> LabsResult<()> {
    if arguments.has("help") {
        eprintln!("Usage: adva-labs-search exhaustive --length N [--output exact-N.json]");
        return Ok(());
    }
    let length = arguments.required_value("length")?;
    let report = exhaustive_optimum(length)?;
    if let Some(path) = arguments.string("output") {
        write_json(path, &report)?;
    } else {
        serde_json::to_writer_pretty(std::io::stdout().lock(), &report)?;
        println!();
    }
    Ok(())
}

fn print_search_help() {
    eprintln!(
        r#"Usage:
  adva-labs-search search --length N [options]
  adva-labs-search search --resume checkpoint.json [options]

Core options:
  --iterations N                steps per worker, or additional resume steps
  --workers N                   independent deterministic workers
  --seed N                      base SplitMix64 seed
  --programs LIST               comma-separated temporal,spatial,constructive
  --output PATH                 write a verified run report
  --checkpoint PATH             save deterministic single-worker state
  --checkpoint-every N          checkpoint interval
  --resume PATH                 resume a single-worker checkpoint
  --quiet                       suppress progress lines

Search controls:
  --initial-population N
  --move-samples N
  --temporal-top-k N
  --spatial-lags N
  --construction-trials N
  --construction-mutations N
  --construction-interval N
  --archive-size N
  --recent-flip-window N
  --restart-after N
  --scheduler-exploration X
  --trace-stride N
  --max-trace-events N

Example:
  cargo run --release -p adva-labs-search -- search \
    --length 64 --iterations 5000000 --workers 16 \
    --output labs-64.json
"#
    );
}

fn print_help() {
    eprintln!(
        r#"Adva bounded triadic LABS experiment

Commands:
  search       run the three-program search or an ablation
  verify       independently recompute a Rust run report
  exhaustive   compute an exact small-length optimum (N <= 25)

Use '<command> --help' for command-specific options.
"#
    );
}

fn run() -> LabsResult<()> {
    let mut arguments = env::args().skip(1);
    let Some(command) = arguments.next() else {
        print_help();
        return Ok(());
    };
    let parsed = ParsedArgs::parse(arguments)?;
    match command.as_str() {
        "search" => search_command(parsed),
        "verify" => verify_command(parsed),
        "exhaustive" => exhaustive_command(parsed),
        "help" | "--help" | "-h" => {
            print_help();
            Ok(())
        }
        other => Err(LabsError::InvalidConfig(format!(
            "unknown command {other:?}"
        ))),
    }
}

fn main() -> ExitCode {
    match run() {
        Ok(()) => ExitCode::SUCCESS,
        Err(error) => {
            eprintln!("error: {error}");
            ExitCode::FAILURE
        }
    }
}
