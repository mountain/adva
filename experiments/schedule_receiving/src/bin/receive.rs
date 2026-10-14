//! Rechecks stored candidates using the existing Rust authority; no compiler call.
//! Project-original research by Codex (OpenAI), Unknown v0.3.
use adva_ir::NodeId;
use adva_lisp::{advance_causal_cut, analyze_program_slice, import_diagram_json};
use serde_json::{Value, json};
use std::{collections::BTreeSet, fs};

fn keys(v: &Value, wanted: &[&str]) -> bool {
    v.as_object()
        .is_some_and(|m| m.len() == wanted.len() && wanted.iter().all(|k| m.contains_key(*k)))
}
fn permutations(prefix: &mut Vec<NodeId>, rest: Vec<NodeId>, out: &mut Vec<Vec<NodeId>>) {
    if rest.is_empty() {
        out.push(prefix.clone());
        return;
    }
    for i in 0..rest.len() {
        let mut remaining = rest.clone();
        prefix.push(remaining.remove(i));
        permutations(prefix, remaining, out);
        prefix.pop();
    }
}
fn check(a: &Value, r: &Value, work: &mut usize) -> Result<Value, &'static str> {
    if !keys(a, &["schema", "diagram", "slice", "receipts"])
        || !keys(
            r,
            &["schema", "diagram_hash", "slice_hash", "query", "first"],
        )
        || a["schema"] != "schedule-archive.v0"
        || r["schema"] != "schedule-request.v0"
    {
        return Err("InvalidEvidence");
    }
    let raw = a["diagram"].as_str().ok_or("InvalidEvidence")?;
    if r["diagram_hash"] != blake3::hash(raw.as_bytes()).to_hex().as_str() {
        return Err("InvalidContext");
    }
    let imported = import_diagram_json(raw).map_err(|_| "InvalidEvidence")?;
    let d = imported.result;
    let ids: Vec<_> = d.nodes.iter().map(|n| n.id).collect();
    if ids.is_empty() || ids.len() > 4 {
        return Err("UnknownScope");
    }
    let slice = analyze_program_slice(&d, &[], &ids).map_err(|_| "InvalidEvidence")?;
    let slice_json = serde_json::to_value(slice).map_err(|_| "InvalidEvidence")?;
    if a["slice"] != slice_json
        || r["slice_hash"]
            != blake3::hash(&serde_json::to_vec(&slice_json).unwrap())
                .to_hex()
                .as_str()
    {
        return Err("InvalidContext");
    }
    let first: NodeId =
        serde_json::from_value(r["first"].clone()).map_err(|_| "InvalidEvidence")?;
    if !ids.contains(&first) || (r["query"] != "all" && r["query"] != "first") {
        return Err("InvalidEvidence");
    }
    let receipts = a["receipts"].as_array().ok_or("InvalidEvidence")?;
    if receipts.len() > 24 {
        return Err("UnknownScope");
    }
    let mut words = BTreeSet::new();
    let mut selected = Vec::new();
    for receipt in receipts {
        if !keys(receipt, &["word", "steps", "final_ideal"]) {
            return Err("InvalidEvidence");
        }
        let word: Vec<NodeId> =
            serde_json::from_value(receipt["word"].clone()).map_err(|_| "InvalidEvidence")?;
        if word.len() != ids.len() || !words.insert(word.clone()) {
            return Err("InvalidEvidence");
        }
        let steps = receipt["steps"].as_array().ok_or("InvalidEvidence")?;
        if steps.len() != word.len() {
            return Err("InvalidEvidence");
        }
        let mut cut = Vec::new();
        for (event, stored) in word.iter().zip(steps) {
            *work += 1;
            let actual = advance_causal_cut(&d, &cut, *event).map_err(|_| "InvalidEvidence")?;
            if !actual.certificate.certified() || serde_json::to_value(&actual).unwrap() != *stored
            {
                return Err("InvalidEvidence");
            }
            cut = actual.result.after.completed;
        }
        if cut != ids || receipt["final_ideal"] != serde_json::to_value(&cut).unwrap() {
            return Err("InvalidEvidence");
        }
        selected.push(r["query"] == "all" || word[0] == first);
    }
    let mut candidates = Vec::new();
    permutations(&mut Vec::new(), ids.clone(), &mut candidates);
    let candidate_count = candidates.len();
    let mut legal = BTreeSet::new();
    for word in candidates {
        *work += 1;
        let mut cut = Vec::new();
        let mut valid = true;
        for event in &word {
            *work += 1;
            match advance_causal_cut(&d, &cut, *event) {
                Ok(step) => cut = step.result.after.completed,
                Err(_) => {
                    valid = false;
                    break;
                }
            }
        }
        if valid {
            legal.insert(word);
        }
    }
    if words != legal {
        return Err("UnknownCoverage");
    }
    for i in 0..selected.len() {
        for j in 0..selected.len() {
            *work += 1;
            if selected[i] != selected[j] {
                return Ok(
                    json!({"outcome":"NonSaturated","left":receipts[i],"right":receipts[j],"permutations":candidate_count}),
                );
            }
        }
    }
    Ok(
        json!({"outcome":"Descends","quotient_region":if selected[0] {json!([ids])} else {json!([])},"permutations":candidate_count}),
    )
}
fn main() {
    let start = std::time::Instant::now();
    let args: Vec<_> = std::env::args().collect();
    let mut work = 0;
    let result = (|| {
        if args.len() != 3 {
            return Err("InvalidEvidence");
        }
        let mut values = Vec::new();
        for p in &args[1..] {
            if fs::metadata(p).map_err(|_| "Unavailable")?.len() > 1_048_576 {
                return Err("UnknownScope");
            }
            let raw = fs::read(p).map_err(|_| "Unavailable")?;
            values.push(serde_json::from_slice(&raw).map_err(|_| "InvalidEvidence")?);
        }
        check(&values[0], &values[1], &mut work)
    })();
    let mut result = result.unwrap_or_else(|e| json!({"outcome":e}));
    result["work_units"] = json!(work);
    result["verification_ns"] = json!(start.elapsed().as_nanos());
    println!("{result}");
}
