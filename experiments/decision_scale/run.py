#!/usr/bin/env python3
"""Original bounded scale transport campaign, Unknown v0.3.

ChatGPT (OpenAI), through Mingli Yuan's account proxy; not his review.
"""
import argparse
import copy
from fractions import Fraction as F
import hashlib
import importlib.util
import json
from pathlib import Path
import resource
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parent
PROFILE = "adva.research.decision-scale.v0"
spec = importlib.util.spec_from_file_location("decision_producer", ROOT.parent / "finite_decision/run.py")
producer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(producer)
rat = producer.rat
put = producer.put


def target(request):
    c = copy.deepcopy(request["source"])
    alpha = F(*request["factor"])
    c["loss"] = [[rat(alpha * F(*x)) for x in row] for row in c["loss"]]
    c["observation_cost"] = rat(alpha * F(*c["observation_cost"]))
    c["loss_unit"] = request["target_unit"]
    c["history"].append(request["step"])
    return c


def receipt(request, changed_target=None):
    return {"profile": PROFILE, "request": copy.deepcopy(request),
            "source_receipt": producer.produce(request["source"])[0],
            "target_receipt": producer.produce(target(request) if changed_target is None else changed_target)[0]}


def fixtures():
    c = producer.fixture
    sources = [c("low-cost"), c("high-cost", cost=F(3, 8)),
               c("conditional-tie", loss=((0, 3), (1, 0)), cost=0),
               c("asymmetric-reuse", prior=(F(2, 3), F(1, 3)), kernel=((F(3, 4), F(1, 4)), (F(1, 2), F(1, 2))), loss=((0, 2), (3, 0)), cost=F(1, 12)),
               c("null-event", kernel=((1, 0), (1, 0)), cost=0), c("acquisition-tie", cost=F(1, 4))]
    factors = [F(3, 2), F(2), F(1, 2), F(2, 3), F(3, 2), F(2)]
    reqs = [{"source": s, "factor": rat(a), "target_unit": "declared-loss-subunit", "step": s["question"] + ":scale"} for s, a in zip(sources, factors)]
    reqs.append({"source": target(reqs[0]), "factor": rat(F(2, 3)), "target_unit": sources[0]["loss_unit"], "step": "low-cost:inverse"})
    back = target(reqs[-1]); original = copy.deepcopy(sources[0])
    assert {k:v for k,v in back.items() if k != "history"} == {k:v for k,v in original.items() if k != "history"}
    assert back["history"] == original["history"] + [reqs[0]["step"], reqs[-1]["step"]]
    rows, summaries = [], []
    for i, req in enumerate(reqs):
        name = "inverse" if i == 6 else req["source"]["question"]
        good = receipt(req)
        summaries.append({"name": name, "request": req, "source_claims": good["source_receipt"]["claims"], "target_claims": good["target_receipt"]["claims"], "target_history": good["target_receipt"]["context"]["history"]})
        rows.append((name + "/valid", req, good, "AcceptedDecisionScale", 2))
        other = target(req); other["history"] = copy.deepcopy(req["source"]["history"])
        rows.append((name + "/erased-history", req, receipt(req, other), "InvalidEvidence", 2))
        x = copy.deepcopy(good); x["request"]["factor"] = rat(F(*req["factor"]) + 1)
        rows.append((name + "/changed-request", req, x, "InvalidEvidence", 0))
        x = copy.deepcopy(good); x["target_receipt"]["claims"]["net_value"] = rat(F(*x["target_receipt"]["claims"]["net_value"]) + 1)
        rows.append((name + "/wrong-target-risk", req, x, "InvalidEvidence", 1))
    high = reqs[1]; only_loss = target(high); only_loss["observation_cost"] = copy.deepcopy(high["source"]["observation_cost"])
    low = copy.deepcopy(reqs[0]); low["factor"] = rat(4)
    only_cost = target(low); only_cost["loss"] = copy.deepcopy(low["source"]["loss"])
    for name, req, other in (("loss-only", high, only_loss), ("cost-only", low, only_cost)):
        x = receipt(req, other)
        assert x["source_receipt"]["claims"]["acquisition_minimizers"] != x["target_receipt"]["claims"]["acquisition_minimizers"]
        summaries.append({"name": name, "source_claims": x["source_receipt"]["claims"], "target_claims": x["target_receipt"]["claims"], "interpretation": "Individually valid decision arithmetic; not a common-scale transport"})
        rows.append(("extra/" + name, req, x, "InvalidEvidence", 2))
    req=reqs[0]; other=target(req); other["actions"].reverse()
    rows.append(("extra/action-roles", req, receipt(req, other), "InvalidEvidence", 2))
    req=reqs[2]; x=receipt(req); x["target_receipt"]["claims"]["observations"][1]["minimizers"] = ["a0"]
    rows.append(("extra/missing-tie", req, x, "InvalidEvidence", 1))
    req=reqs[4]; x=receipt(req); x["target_receipt"]["claims"]["observations"][1]["posterior"] = [rat(F(1, 2)), rat(F(1, 2))]
    rows.append(("extra/invented-null-posterior", req, x, "InvalidEvidence", 1))
    req=reqs[0]; x=receipt(req); x["native_free"] = True
    rows.append(("extra/unsupported-free", req, x, "InvalidEvidence", 0))
    for name, factor in (("zero-factor", [0, 1]), ("negative-factor", [-1, 1]), ("boolean-factor", [True, 1]), ("noncanonical-factor", [2, 2])):
        bad=copy.deepcopy(reqs[0]);bad["factor"]=factor
        rows.append(("extra/"+name,bad,receipt(reqs[0]),"InvalidContext",0))
    bad=copy.deepcopy(reqs[0]);bad["source"]["loss"][0][1]=rat(5);bad["factor"]=rat(16)
    rows.append(("extra/target-rational-cap",bad,receipt(reqs[0]),"InvalidContext",0))
    bad=copy.deepcopy(reqs[0]);bad["source"]["history"] += ["step-3", "step-4"]
    rows.append(("extra/target-history-cap",bad,receipt(reqs[0]),"InvalidContext",0))
    assert len(rows)==40
    return rows,summaries


def limits():
    resource.setrlimit(resource.RLIMIT_AS, (128*1024**2,)*2)
    resource.setrlimit(resource.RLIMIT_CPU, (3,3))
    resource.setrlimit(resource.RLIMIT_FSIZE, (262144,262144))


def main(output):
    output.mkdir(parents=True,exist_ok=False)
    (output/"contract.json").write_bytes((ROOT/"contract.json").read_bytes())
    started=time.perf_counter();metrics=[];assertions=0;units=0
    phases={"construction_seconds":0.0,"input_serialization_seconds":0.0,"receiving_seconds":0.0}
    report={"profile":PROFILE,"search_candidates":0,"new_vocabulary":0,"execution":"ExternalFreshProcessScaleReceiver"}
    try:
        t=time.perf_counter();rows,summaries=fixtures();phases["construction_seconds"]=time.perf_counter()-t;report["instances"]=summaries
        for name,req,candidate,wanted,endpoints in rows:
            remaining=30-(time.perf_counter()-started)
            if len(metrics)>=40 or remaining<=0:raise RuntimeError("UnknownBudget")
            folder=output/name;folder.mkdir(parents=True)
            t=time.perf_counter();put(folder/"expected.json",req);put(folder/"candidate.json",candidate);phases["input_serialization_seconds"]+=time.perf_counter()-t
            t=time.perf_counter()
            with (folder/"stdout.json").open('wb') as out,(folder/"stderr.txt").open('wb') as err:
                p=subprocess.run([sys.executable,'-B','-S',str(ROOT/'receive.py'),'--expected',str(folder/'expected.json'),'--candidate',str(folder/'candidate.json')],stdout=out,stderr=err,timeout=min(3,remaining),preexec_fn=limits)
            elapsed=time.perf_counter()-t;phases["receiving_seconds"]+=elapsed
            row={"name":name,"returncode":p.returncode,"wall_seconds":elapsed};metrics.append(row)
            assert p.returncode==0,row
            r=json.loads((folder/'stdout.json').read_text());units+=r['work_units'];row.update(outcome=r['outcome'],work_units=r['work_units'],endpoint_arithmetic_checked=r['endpoint_arithmetic_checked'])
            assert r['outcome']==wanted,(name,r);assertions+=1
            assert r['expected_request']==req;assertions+=1
            assert len(r['endpoint_arithmetic_checked'])==endpoints,(name,r);assertions+=1
            assert all(r[k] is False for k in ('native_authority','free_authorized','close_authorized'));assertions+=1
            if wanted!='AcceptedDecisionScale':assert r['semantic_delta']==[];assertions+=1
        report['outcome']='PassedDecisionScaleCampaign'
    except Exception as e:
        report.update(outcome='Failure',failure={'type':type(e).__name__,'message':str(e)})
    report.update(metrics=metrics,assertions=assertions,work_units=units,phases=phases,campaign_wall_seconds=time.perf_counter()-started,peak_children_rss_kib=resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss,peak_supervisor_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,cost_scope='Includes construction, per-case input serialization, fresh receiving and all parent checks. Reuse included but not separately timed. Final report serialization/write, archiving, research and publication excluded.')
    paths=[ROOT/'contract.json',ROOT/'run.py',ROOT/'receive.py',ROOT.parent/'finite_decision/run.py',ROOT.parent/'finite_decision/receive.py',ROOT.parent/'probability_receipt/run.py',ROOT.parent/'probability_receipt/receive.py']
    report['source_sha256']={str(p.relative_to(ROOT.parent.parent)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
    put(output/'result.json',report)
    print(json.dumps({k:report[k] for k in ('outcome','assertions','work_units','campaign_wall_seconds','peak_children_rss_kib')}))
    return 0 if report['outcome']=='PassedDecisionScaleCampaign' else 1


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True)
    raise SystemExit(main(parser.parse_args().output))
