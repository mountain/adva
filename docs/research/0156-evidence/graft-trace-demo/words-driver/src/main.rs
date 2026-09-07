// programs/self-boundary/words.lisp 的 GraftTrace 计算（研究本地；不动仓库）。
use adva_lisp::{compile_function, link_modules, parse_module};

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let source = include_str!("/Users/mingli/Adva/adva/programs/self-boundary/words.lisp");
    let linked = link_modules(vec![parse_module(source)?])?;
    let artifact = compile_function(&linked, "self-boundary", "learn")?;
    println!("certificate.certified: {}", artifact.certificate.certified());
    let trace = artifact.graft_trace;
    std::fs::write("graft-words-result.json",
                   serde_json::to_string_pretty(&trace.result)?)?;
    std::fs::write("graft-words-certificate.json",
                   serde_json::to_string_pretty(&trace.certificate)?)?;
    println!("frames: {}", trace.result.frames.len());
    println!("root: {}", trace.result.root .0);
    for frame in &trace.result.frames {
        println!("  {}: {} -> {} (kind {:?})",
                 frame.id.0, frame.caller.function.0, frame.callee.function.0, frame.kind);
    }
    Ok(())
}
