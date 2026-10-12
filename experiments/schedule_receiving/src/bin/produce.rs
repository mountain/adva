//! Project-original research by Codex (OpenAI), Unknown v0.3.
use adva_lisp::{
    advance_causal_cut, analyze_program_slice, compile_function, link_modules, parse_module,
};
use serde_json::json;

fn main() {
    let module = parse_module(
        r#"
(module receiving-fixtures
 (export diamond three delayed)
 (def diamond (fn ((x Real) (y Real)) Real
   (add (frontier (neg (use x)) (id (use y))))))
 (def three (fn ((x Real) (y Real) (z Real)) (outputs Real Real Real Real Real)
   (frontier (copy (use x)) (copy (use y)) (id (use z)))))
 (def delayed (fn ((x Real) (y Real)) Real
   (neg (add (frontier (neg (use x)) (id (use y)))))))
)"#,
    )
    .unwrap();
    let linked = link_modules(vec![module]).unwrap();
    let mut cases = Vec::new();
    for name in ["diamond", "three", "delayed"] {
        let start = std::time::Instant::now();
        let artifact = compile_function(&linked, "receiving-fixtures", name).unwrap();
        let d = &artifact.result;
        let ids: Vec<_> = d.nodes.iter().map(|n| n.id).collect();
        let words = match name {
            "diamond" => vec![vec![0, 1, 2], vec![1, 0, 2]],
            "three" => vec![
                vec![0, 1, 2],
                vec![0, 2, 1],
                vec![1, 0, 2],
                vec![1, 2, 0],
                vec![2, 0, 1],
                vec![2, 1, 0],
            ],
            _ => vec![vec![0, 1, 2, 3], vec![1, 0, 2, 3]],
        };
        let slice = analyze_program_slice(d, &[], &ids).unwrap();
        assert!(slice.certificate.certified());
        let mut receipts = Vec::new();
        for indices in words {
            let word: Vec<_> = indices.into_iter().map(|i| ids[i]).collect();
            let mut cut = Vec::new();
            let mut steps = Vec::new();
            for id in &word {
                let step = advance_causal_cut(d, &cut, *id).unwrap();
                assert!(step.certificate.certified());
                cut = step.result.after.completed.clone();
                steps.push(step);
            }
            receipts.push(json!({"word":word,"steps":steps,"final_ideal":cut}));
        }
        let diagram = d.to_json().unwrap();
        let slice = serde_json::to_value(slice).unwrap();
        let slice_hash = blake3::hash(&serde_json::to_vec(&slice).unwrap())
            .to_hex()
            .to_string();
        let request = json!({"schema":"schedule-request.v0", "diagram_hash":blake3::hash(diagram.as_bytes()).to_hex().to_string(), "slice_hash":slice_hash,"query":"all","first":ids[0]});
        let archive = json!({"schema":"schedule-archive.v0","diagram":diagram,"slice":slice,"receipts":receipts});
        cases.push(json!({"name":name,"request":request,"archive":archive,"construction_ns":start.elapsed().as_nanos()}));
    }
    println!("{}", json!({"cases":cases}));
}
