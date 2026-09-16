//! Bounded timing of the existing checked APIs; no alternate VM or unchecked path.
//! Authored by ChatGPT (OpenAI), through Mingli Yuan's authorized account proxy.
use adva_witness::*;
use serde::Deserialize;
use serde_json::{Value, json};
use std::hint::black_box;
use std::io::Write;
use std::time::Instant;

#[derive(Deserialize)]
struct Case {
    name: String,
    version: u8,
    program: Value,
    input: Value,
    fuel: u32,
    expected: Value,
    iterations: usize,
    samples: usize,
}

enum Prepared {
    V0(DataMachineProgramV0, MachineDataV0),
    V1(DataMachineProgramV1, MachineDataV1),
}

impl Prepared {
    fn checked_observation(&self, fuel: u32) -> Result<Value, String> {
        // First execution and complete native replay are outside the timed region.
        let (record, steps) = match self {
            Self::V0(p, d) => {
                let r = run_data_machine_v0(p, d, fuel, fuel)?;
                let received = verify_data_machine_run_v0(p, d, fuel, &r)?;
                (serde_json::to_value(r).unwrap(), received.verified_steps)
            }
            Self::V1(p, d) => {
                let r = run_data_machine_v1(p, d, fuel, fuel)?;
                let received = verify_data_machine_run_v1(p, d, fuel, &r)?;
                (serde_json::to_value(r).unwrap(), received.verified_steps)
            }
        };
        Ok(json!({
            "observation": {"status": record["status"], "value": record["state"]["phase"]["value"]},
            "phase": record["state"]["phase"], "steps": steps,
            "profile": record["profile"],
            "trace_blake3": blake3::hash(&serde_json::to_vec(&record["trace"]).unwrap()).to_hex().to_string()
        }))
    }

    fn batch(&self, fuel: u32, count: usize) -> Result<f64, String> {
        let start = Instant::now();
        for _ in 0..count {
            match self {
                Self::V0(p, d) => drop(black_box(run_data_machine_v0(
                    black_box(p),
                    black_box(d),
                    fuel,
                    fuel,
                )?)),
                Self::V1(p, d) => drop(black_box(run_data_machine_v1(
                    black_box(p),
                    black_box(d),
                    fuel,
                    fuel,
                )?)),
            }
        }
        Ok(start.elapsed().as_secs_f64() * 1e9 / count as f64)
    }
}

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let path = std::env::args().nth(1).ok_or("expected suite.json")?;
    let cases: Vec<Case> = serde_json::from_slice(&std::fs::read(path)?)?;
    if cases.is_empty() || cases.len() > 100 {
        return Err("suite size exceeds fixed limit".into());
    }
    let mut prepared = Vec::new();
    for c in &cases {
        if !(1..=128).contains(&c.iterations) || !(1..=9).contains(&c.samples) {
            return Err("sample budget exceeds fixed limit".into());
        }
        let p = match c.version {
            0 => Prepared::V0(
                serde_json::from_value(c.program.clone())?,
                serde_json::from_value(c.input.clone())?,
            ),
            1 => Prepared::V1(
                serde_json::from_value(c.program.clone())?,
                serde_json::from_value(c.input.clone())?,
            ),
            _ => return Err("unknown profile".into()),
        };
        let observation = p.checked_observation(c.fuel)?;
        if observation["observation"] != c.expected {
            return Err(format!("{}: observation mismatch", c.name).into());
        }
        println!(
            "{}",
            json!({"kind":"checked", "name":c.name, "result":observation})
        );
        std::io::stdout().flush()?;
        prepared.push(p);
    }
    // Rotate/reverse case order each round so comparison arms are interleaved.
    for round in 0..9 {
        let mut order: Vec<usize> = (0..cases.len()).collect();
        order.rotate_left((round * 17) % cases.len());
        if round % 2 == 1 {
            order.reverse();
        }
        for i in order {
            let c = &cases[i];
            if round >= c.samples {
                continue;
            }
            let ns = prepared[i].batch(c.fuel, c.iterations)?;
            println!(
                "{}",
                json!({"kind":"sample", "name":c.name, "round":round,
                "iterations":c.iterations, "ns_per_run":ns})
            );
            std::io::stdout().flush()?;
        }
    }
    Ok(())
}
