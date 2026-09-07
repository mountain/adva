// 最小 GraftTrace 计算驱动（研究本地；不动仓库）。
// 编译含调用的双模块并打印 GraftTrace 结果与证书。
use adva_lisp::{compile_function, link_modules, parse_module};

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let arithmetic = r#"
(module arithmetic
  (export shared-double)
  (def shared-double
    (fn ((x Real)) Real
      (add (copy (use x))))))
"#;
    let client = r#"
(module client
  (import arithmetic shared-double)
  (export quadruple)
  (def quadruple
    (fn ((x Real)) Real
      (call arithmetic/shared-double
        (call arithmetic/shared-double (use x))))))
"#;
    let linked = link_modules(vec![parse_module(arithmetic)?, parse_module(client)?])?;
    let artifact = compile_function(&linked, "client", "quadruple")?;
    println!(
        "certificate.certified: {}",
        artifact.certificate.certified()
    );
    let trace = artifact.graft_trace;
    std::fs::write(
        "graft-result.json",
        serde_json::to_string_pretty(&trace.result)?,
    )?;
    std::fs::write(
        "graft-certificate.json",
        serde_json::to_string_pretty(&trace.certificate)?,
    )?;
    println!(
        "graft_trace: {}",
        serde_json::to_string_pretty(&trace.result)?
    );
    println!(
        "graft_certificate: {}",
        serde_json::to_string_pretty(&trace.certificate)?
    );
    println!("frames: {}", trace.result.frames.len());
    println!("root: {}", trace.result.root .0);
    Ok(())
}
