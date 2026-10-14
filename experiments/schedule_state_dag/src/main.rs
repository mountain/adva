//! Codex (OpenAI), project-original contribution under Unknown v0.3.
//! Exact-cut transition sharing without erasing labelled incoming paths.
use adva_ir::{NodeId, SharedProgramDiagram};
use adva_lisp::{advance_causal_cut, import_diagram_json};
use serde_json::{Value, json};
use std::{collections::{BTreeMap, BTreeSet, VecDeque}, fs, time::Instant};

#[derive(Default)]
struct Cost { probes: usize, states: usize, path_prefixes: usize }
impl Cost {
    fn value(&self) -> Value { json!({
        "native_advance_attempts":self.probes,
        "state_records":self.states,
        "path_prefixes":self.path_prefixes,
        "counted_units":self.probes+self.states+self.path_prefixes}) }
}
fn load(path: &str) -> Result<Value,String> {
    if fs::metadata(path).map_err(|e|e.to_string())?.len()>1_048_576 { return Err("UnknownBudget: input bytes".into()); }
    serde_json::from_slice(&fs::read(path).map_err(|e|e.to_string())?).map_err(|e|e.to_string())
}
fn imported(input:&Value)->Result<SharedProgramDiagram,String>{
    let raw=input["diagram"].as_str().ok_or("InvalidContext: diagram")?;
    if input["diagram_hash"]!=blake3::hash(raw.as_bytes()).to_hex().as_str(){return Err("InvalidContext: diagram binding".into())}
    let d=import_diagram_json(raw).map_err(|e|e.to_string())?.result;
    if d.nodes.is_empty()||d.nodes.len()>4{return Err("UnknownScope: events".into())} Ok(d)
}
fn ids(d:&SharedProgramDiagram)->Vec<NodeId>{d.nodes.iter().map(|n|n.id).collect()}
fn key(cut:&[NodeId])->Vec<NodeId>{let mut k=cut.to_vec();k.sort();k}
fn expand(d:&SharedProgramDiagram,cut:&[NodeId],cost:&mut Cost)->Vec<(NodeId,Vec<NodeId>,Value)>{
    let mut out=Vec::new();
    for event in ids(d){
        if cut.contains(&event){continue}
        cost.probes+=1;
        if let Ok(step)=advance_causal_cut(d,cut,event){
            assert!(step.certificate.certified());
            let next=key(&step.result.after.completed);
            out.push((event,next,serde_json::to_value(step).unwrap()));
        }
    }
    out
}
fn produce(input:&Value)->Result<Value,String>{
    let started=Instant::now();let d=imported(input)?;let mut cost=Cost::default();
    let mut queue=VecDeque::from([Vec::<NodeId>::new()]);let mut seen=BTreeSet::new();let mut states=Vec::new();
    while let Some(cut)=queue.pop_front(){
        if !seen.insert(cut.clone()){continue} cost.states+=1;
        let children=expand(&d,&cut,&mut cost);
        let edges:Vec<_>=children.iter().map(|(e,n,s)|json!({"event":e,"next_cut":n,"step":s})).collect();
        for (_,next,_) in children{queue.push_back(next)}
        states.push(json!({"cut":cut,"edges":edges}));
    }
    Ok(json!({"schema":"history-preserving-state-dag.v0","diagram_hash":input["diagram_hash"],"states":states,"cost":cost.value(),"construction_ns":started.elapsed().as_nanos()}))
}
fn reject(kind:&str,residual:Value,cost:&Cost)->Value{json!({"outcome":kind,"residual":residual,"verification_cost":cost.value()})}
fn enumerate_paths(edges:&BTreeMap<Vec<NodeId>,Vec<(NodeId,Vec<NodeId>)>>,n:usize,cost:&mut Cost)->Result<BTreeSet<Vec<NodeId>>,String>{
    let mut out=BTreeSet::new();let mut queue=VecDeque::from([(Vec::<NodeId>::new(),Vec::<NodeId>::new())]);
    while let Some((cut,word))=queue.pop_front(){
        cost.path_prefixes+=1;
        if word.len()==n{out.insert(word);continue}
        let next=edges.get(&cut).ok_or("missing checked state")?;
        for (event,next_cut) in next{let mut w=word.clone();w.push(*event);queue.push_back((next_cut.clone(),w));}
    }
    Ok(out)
}
fn verify(input:&Value,dag:&Value)->Result<Value,String>{
    let started=Instant::now();let d=imported(input)?;let mut cost=Cost::default();
    if dag["schema"]!="history-preserving-state-dag.v0"||dag["diagram_hash"]!=input["diagram_hash"]{return Ok(reject("InvalidContext",json!("dag binding"),&cost))}
    let supplied=dag["states"].as_array().ok_or("InvalidEvidence: states")?;
    if supplied.len()>17{return Ok(reject("UnknownBudget",json!("state count"),&cost))}
    let mut lookup=BTreeMap::new();
    for state in supplied{
        let cut:Vec<NodeId>=serde_json::from_value(state["cut"].clone()).map_err(|e|e.to_string())?;
        if cut!=key(&cut){return Ok(reject("InvalidEvidence",json!({"noncanonical_cut":cut}),&cost))}
        if lookup.insert(cut,state).is_some(){return Ok(reject("InvalidEvidence",json!("duplicate state"),&cost))}
    }
    let mut queue=VecDeque::from([Vec::<NodeId>::new()]);let mut seen=BTreeSet::new();let mut checked=BTreeMap::new();
    while let Some(cut)=queue.pop_front(){
        if !seen.insert(cut.clone()){continue} cost.states+=1;
        let Some(state)=lookup.get(&cut) else{return Ok(reject("UnknownCoverage",json!({"missing_state":cut}),&cost))};
        let children=expand(&d,&cut,&mut cost);
        let expected:Vec<_>=children.iter().map(|(e,n,s)|json!({"event":e,"next_cut":n,"step":s})).collect();
        let got=state["edges"].as_array().ok_or("InvalidEvidence: edges")?;
        if got.len()!=expected.len(){return Ok(reject("UnknownCoverage",json!({"cut":cut,"expected_events":expected.iter().map(|x|x["event"].clone()).collect::<Vec<_>>()}),&cost))}
        if *got!=expected{return Ok(reject("InvalidEvidence",json!({"wrong_edges_at":cut}),&cost))}
        let mut compact=Vec::new();for (event,next,_) in children{compact.push((event,next.clone()));queue.push_back(next)}checked.insert(cut,compact);
    }
    if seen.len()!=supplied.len(){return Ok(reject("InvalidEvidence",json!("unreachable state"),&cost))}
    let words=enumerate_paths(&checked,d.nodes.len(),&mut cost)?;
    if words.len()>24{return Ok(reject("UnknownBudget",json!("path count"),&cost))}
    let first=ids(&d)[0];let yes=words.iter().find(|w|w[0]==first);let no=words.iter().find(|w|w[0]!=first);
    let first_query=match(yes,no){(Some(a),Some(b))=>json!({"outcome":"NonSaturated","left":a,"right":b}),_=>json!({"outcome":"Descends"})};
    Ok(json!({"outcome":"Verified","legal_words":words,"whole_query":"Descends","first_query":first_query,"verification_cost":cost.value(),"verification_ns":started.elapsed().as_nanos(),"argument":"All and only checked enabled edges are retained at each reachable exact cut; labelled root-to-terminal paths preserve route multiplicity."}))
}
fn main(){
    let started=Instant::now();let a:Vec<_>=std::env::args().collect();let result=(||->Result<Value,String>{match a.get(1).map(String::as_str){
        Some("produce") if a.len()==3=>produce(&load(&a[2])?),
        Some("verify") if a.len()==4=>verify(&load(&a[2])?,&load(&a[3])?),
        _=>Err("InvalidRequest".into())}})();
    let mut v=result.unwrap_or_else(|e|json!({"outcome":"InvalidEvidence","error":e}));
    let rss=fs::read_to_string("/proc/self/status").ok().and_then(|s|s.lines().find(|l|l.starts_with("VmHWM:")).map(str::to_owned));
    v["telemetry"]=json!({"total_ns":started.elapsed().as_nanos(),"linux_vm_hwm":rss});println!("{v}");
}
