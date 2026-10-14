//! Codex (OpenAI), project-original contribution under Unknown v0.3.
//! Research-local comparison; native identities and steps enter through Rust.
use adva_ir::{NodeId, SharedProgramDiagram};
use adva_lisp::{
    advance_causal_cut, compile_function, import_diagram_json, link_modules, parse_module,
};
use serde_json::{Value, json};
use std::{
    collections::{BTreeMap, BTreeSet, VecDeque},
    fs,
    time::Instant,
};

#[derive(Default)]
struct Cost {
    probes: usize,
    prefixes: usize,
    permutations: usize,
}
impl Cost {
    fn value(&self) -> Value {
        json!({"native_advance_attempts":self.probes,"prefix_records":self.prefixes,"permutations":self.permutations,"counted_units":self.probes+self.prefixes+self.permutations})
    }
}
fn load(path: &str) -> Result<Value, String> {
    if fs::metadata(path).map_err(|e| e.to_string())?.len() > 1_048_576 {
        return Err("UnknownBudget: input bytes".into());
    }
    serde_json::from_slice(&fs::read(path).map_err(|e| e.to_string())?).map_err(|e| e.to_string())
}
fn ids(d: &SharedProgramDiagram) -> Vec<NodeId> {
    d.nodes.iter().map(|n| n.id).collect()
}
fn imported(input: &Value) -> Result<SharedProgramDiagram, String> {
    let raw = input["diagram"].as_str().ok_or("InvalidContext: diagram")?;
    if input["diagram_hash"] != blake3::hash(raw.as_bytes()).to_hex().as_str() {
        return Err("InvalidContext: diagram binding".into());
    }
    let d = import_diagram_json(raw).map_err(|e| e.to_string())?.result;
    if d.nodes.is_empty() || d.nodes.len() > 4 {
        return Err("UnknownScope: events".into());
    }
    Ok(d)
}
fn expand(
    d: &SharedProgramDiagram,
    word: &[NodeId],
    cut: &[NodeId],
    cost: &mut Cost,
) -> Vec<(NodeId, Vec<NodeId>, Value)> {
    let mut children = Vec::new();
    for event in ids(d) {
        if word.contains(&event) {
            continue;
        }
        cost.probes += 1;
        if let Ok(step) = advance_causal_cut(d, cut, event) {
            assert!(step.certificate.certified());
            children.push((
                event,
                step.result.after.completed.clone(),
                serde_json::to_value(step).unwrap(),
            ));
        }
    }
    children
}
fn dfs(
    d: &SharedProgramDiagram,
    word: Vec<NodeId>,
    cut: Vec<NodeId>,
    records: &mut Vec<Value>,
    cost: &mut Cost,
) {
    cost.prefixes += 1;
    let children = expand(d, &word, &cut, cost);
    let edges: Vec<_> = children
        .iter()
        .map(|(event, _, step)| json!({"event":event,"step":step}))
        .collect();
    records.push(json!({"word":word,"cut":cut,"edges":edges}));
    for (event, next, _) in children {
        let mut child = word.clone();
        child.push(event);
        dfs(d, child, next, records, cost);
    }
}
fn produce(input: &Value) -> Result<Value, String> {
    let start = Instant::now();
    let d = imported(input)?;
    let mut cost = Cost::default();
    let mut records = Vec::new();
    dfs(&d, vec![], vec![], &mut records, &mut cost);
    Ok(
        json!({"schema":"enabled-prefix-tree.v0","diagram_hash":input["diagram_hash"],"records":records,"cost":cost.value(),"construction_ns":start.elapsed().as_nanos()}),
    )
}
fn permutations(prefix: &mut Vec<NodeId>, remaining: Vec<NodeId>, out: &mut Vec<Vec<NodeId>>) {
    if remaining.is_empty() {
        out.push(prefix.clone());
        return;
    }
    for i in 0..remaining.len() {
        let mut tail = remaining.clone();
        prefix.push(tail.remove(i));
        permutations(prefix, tail, out);
        prefix.pop();
    }
}
fn baseline(d: &SharedProgramDiagram) -> (BTreeSet<Vec<NodeId>>, Cost) {
    let mut all = Vec::new();
    permutations(&mut Vec::new(), ids(d), &mut all);
    let mut cost = Cost::default();
    let mut legal = BTreeSet::new();
    for word in all {
        cost.permutations += 1;
        let mut cut = Vec::new();
        let mut valid = true;
        for event in &word {
            cost.probes += 1;
            match advance_causal_cut(d, &cut, *event) {
                Ok(s) => cut = s.result.after.completed,
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
    (legal, cost)
}
fn reject(kind: &str, residual: Value, cost: &Cost) -> Value {
    json!({"outcome":kind,"residual":residual,"verification_cost":cost.value()})
}
fn verify(input: &Value, tree: &Value) -> Result<Value, String> {
    let start = Instant::now();
    let d = imported(input)?;
    let mut cost = Cost::default();
    if tree["schema"] != "enabled-prefix-tree.v0" || tree["diagram_hash"] != input["diagram_hash"] {
        return Ok(reject("InvalidContext", json!("tree binding"), &cost));
    }
    let records = tree["records"]
        .as_array()
        .ok_or("InvalidEvidence: records")?;
    if records.len() > 65 {
        return Ok(reject("UnknownBudget", json!("record count"), &cost));
    }
    let mut lookup = BTreeMap::new();
    for record in records {
        let word: Vec<NodeId> =
            serde_json::from_value(record["word"].clone()).map_err(|e| e.to_string())?;
        if lookup.insert(word, record).is_some() {
            return Ok(reject("InvalidEvidence", json!("duplicate prefix"), &cost));
        }
    }
    let mut queue = VecDeque::from([(Vec::new(), Vec::new())]);
    let mut seen = BTreeSet::new();
    let mut leaves = BTreeSet::new();
    while let Some((word, cut)) = queue.pop_front() {
        cost.prefixes += 1;
        seen.insert(word.clone());
        let Some(record) = lookup.get(&word) else {
            return Ok(reject(
                "UnknownCoverage",
                json!({"missing_prefix":word}),
                &cost,
            ));
        };
        if record["cut"] != serde_json::to_value(&cut).unwrap() {
            return Ok(reject(
                "InvalidEvidence",
                json!({"wrong_cut_at":word}),
                &cost,
            ));
        }
        let children = expand(&d, &word, &cut, &mut cost);
        let expected: Vec<_> = children
            .iter()
            .map(|(e, _, s)| json!({"event":e,"step":s}))
            .collect();
        let supplied = record["edges"].as_array().ok_or("InvalidEvidence: edges")?;
        if supplied.len() != expected.len() {
            return Ok(reject(
                "UnknownCoverage",
                json!({"prefix":word,"expected_children":expected.iter().map(|e|e["event"].clone()).collect::<Vec<_>>()}),
                &cost,
            ));
        }
        if *supplied != expected {
            return Ok(reject(
                "InvalidEvidence",
                json!({"wrong_edges_at":word}),
                &cost,
            ));
        }
        if word.len() == d.nodes.len() {
            leaves.insert(word.clone());
        }
        for (event, next, _) in children {
            let mut child = word.clone();
            child.push(event);
            queue.push_back((child, next));
        }
    }
    if seen.len() != records.len() {
        return Ok(reject(
            "InvalidEvidence",
            json!("unreachable record"),
            &cost,
        ));
    }
    let prefix_ns = start.elapsed().as_nanos();
    let baseline_start = Instant::now();
    let (reference, reference_cost) = baseline(&d);
    let baseline_ns = baseline_start.elapsed().as_nanos();
    if leaves != reference {
        return Ok(reject(
            "ImplementationDisagreement",
            json!({"prefix":leaves,"permutation":reference}),
            &cost,
        ));
    }
    let first = ids(&d)[0];
    let yes = leaves.iter().find(|w| w[0] == first);
    let no = leaves.iter().find(|w| w[0] != first);
    let first_query = match (yes, no) {
        (Some(a), Some(b)) => json!({"outcome":"NonSaturated","left":a,"right":b}),
        _ => json!({"outcome":"Descends"}),
    };
    // Intentionally lossy control: retain one record per completed cut.
    let mut cuts = BTreeSet::new();
    let mut naive_leaves = Vec::new();
    for record in records {
        let cut: Vec<NodeId> = serde_json::from_value(record["cut"].clone()).unwrap();
        let word: Vec<NodeId> = serde_json::from_value(record["word"].clone()).unwrap();
        if cuts.insert(cut) && word.len() == d.nodes.len() {
            naive_leaves.push(word);
        }
    }
    Ok(
        json!({"outcome":"Verified","legal_words":leaves,"whole_query":"Descends","first_query":first_query,"verification_cost":cost.value(),"baseline_cost":reference_cost.value(),"prefix_verify_ns":prefix_ns,"baseline_ns":baseline_ns,"naive_cut_dedup":{"retained_leaves":naive_leaves,"lost_histories":reference.len()-naive_leaves.len(),"singleton_only_query_would_descend":true}}),
    )
}
fn fresh() -> Value {
    let m=parse_module("(module chains (export pair) (def pair (fn ((x Real) (y Real)) (outputs Real Real) (frontier (neg (neg (use x))) (id (neg (use y)))))))").unwrap();
    let linked = link_modules(vec![m]).unwrap();
    let d = compile_function(&linked, "chains", "pair")
        .unwrap()
        .result
        .to_json()
        .unwrap();
    json!({"diagram_hash":blake3::hash(d.as_bytes()).to_hex().to_string(),"diagram":d})
}
fn main() {
    let started = Instant::now();
    let args: Vec<_> = std::env::args().collect();
    let result = (|| -> Result<Value, String> {
        match args.get(1).map(String::as_str) {
            Some("fresh") => Ok(fresh()),
            Some("produce") if args.len() == 3 => produce(&load(&args[2])?),
            Some("verify") if args.len() == 4 => verify(&load(&args[2])?, &load(&args[3])?),
            _ => Err("InvalidRequest".into()),
        }
    })();
    let mut result = result.unwrap_or_else(|e| json!({"outcome":"InvalidEvidence","error":e}));
    let rss = fs::read_to_string("/proc/self/status").ok().and_then(|s| {
        s.lines()
            .find(|l| l.starts_with("VmHWM:"))
            .map(str::to_owned)
    });
    result["telemetry"] = json!({"total_ns":started.elapsed().as_nanos(),"linux_vm_hwm":rss});
    println!("{result}");
}
