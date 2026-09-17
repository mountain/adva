#!/usr/bin/env python3
"""Original finite composition campaign, Unknown v0.3.

ChatGPT (OpenAI), through Mingli Yuan's authorized proxy; not his review.
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
PROFILE = "adva.research.decision-scale-composition.v0"
spec = importlib.util.spec_from_file_location("scale_producer", ROOT.parent / "decision_scale/run.py")
producer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(producer)
rat, put = producer.rat, producer.put


def produce(request):
    first = dict(source=copy.deepcopy(request["source"]), **request["steps"][0])
    middle = producer.target(first)
    second = dict(source=middle, **request["steps"][1])
    final = producer.target(second)
    product = F(*first["factor"]) * F(*second["factor"])
    return {"profile": PROFILE, "request": copy.deepcopy(request),
            "links": [producer.receipt(first), producer.receipt(second)],
            "summary": {"product_factor": rat(product), "final_context": final,
                        "single_step_factor_status": "WithinFactorBound" if max(product.numerator, product.denominator) <= 16 else "OutsideFactorBound"}}


def fixtures():
    f = producer.producer.fixture
    definitions = [
        ("nonidentity", f("nonidentity"), F(3, 2), F(2)),
        ("inverse", f("inverse"), F(3, 2), F(2, 3)),
        ("asymmetric-reuse", f("asymmetric-reuse", prior=(F(2, 3), F(1, 3)), kernel=((F(3, 4), F(1, 4)), (F(1, 2), F(1, 2))), loss=((0, 2), (3, 0)), cost=F(1, 12)), F(2, 3), F(3, 2)),
        ("ties", f("ties", loss=((0, 3), (1, 0)), cost=0), F(1, 2), F(2)),
        ("null-event", f("null-event", kernel=((1, 0), (1, 0)), cost=0), F(2), F(1, 2)),
        ("beyond-single-factor", f("beyond-single-factor"), F(8), F(4)),
    ]
    rows, summaries, requests = [], [], []
    for name, source, a, b in definitions:
        request = {"source": source, "steps": [
            {"factor": rat(a), "target_unit": "declared-middle-unit", "step": name + ":first"},
            {"factor": rat(b), "target_unit": source["loss_unit"], "step": name + ":second"}]}
        requests.append(request); good = produce(request)
        summaries.append({"name": name, "request": request, "summary": good["summary"],
                          "source_claims": good["links"][0]["source_receipt"]["claims"],
                          "final_claims": good["links"][1]["target_receipt"]["claims"]})
        if a*b == 1:
            original = {k:v for k,v in source.items() if k != "history"}
            final = {k:v for k,v in good["summary"]["final_context"].items() if k != "history"}
            assert original == final
        assert good["summary"]["final_context"]["history"] == source["history"] + [s["step"] for s in request["steps"]]
        rows.append((name + "/valid", "composition", request, good, "AcceptedScaleComposition", 2))
        x = copy.deepcopy(good); changed = copy.deepcopy(x["links"][1]["request"])
        changed["source"]["loss_unit"] = "unrequested-middle-unit"
        x["links"][1] = producer.receipt(changed)
        assert x["links"][1]["target_receipt"]["context"] == good["summary"]["final_context"]
        rows.append((name + "/wrong-middle-unit", "composition", request, x, "InvalidEvidence", 2))
        x = copy.deepcopy(good); changed = copy.deepcopy(x["links"][1]["request"])
        changed["source"]["history"][-1] = "unrequested-first-step"
        x["links"][1] = producer.receipt(changed)
        rows.append((name + "/rewritten-middle-history", "composition", request, x, "InvalidEvidence", 2))
        x = copy.deepcopy(good); x["summary"]["product_factor"] = rat(a*b + 1)
        rows.append((name + "/wrong-product", "composition", request, x, "InvalidEvidence", 2))
        x = copy.deepcopy(good); x["links"].reverse()
        rows.append((name + "/reversed-links", "composition", request, x, "InvalidEvidence", 2))
    request = requests[0]; good = produce(request)
    x = copy.deepcopy(good); x["links"].pop()
    rows.append(("extra/missing-link", "composition", request, x, "InvalidEvidence", 0))
    x = copy.deepcopy(good); x["native_free"] = True
    rows.append(("extra/unsupported-free", "composition", request, x, "InvalidEvidence", 0))
    x = copy.deepcopy(good); x["links"][0]["target_receipt"]["claims"]["net_value"] = rat(7)
    rows.append(("extra/wrong-parent-arithmetic", "composition", request, x, "InvalidEvidence", 0))
    x = copy.deepcopy(good); x["summary"]["product_factor"] = [True, 1]
    rows.append(("extra/boolean-product", "composition", request, x, "InvalidEvidence", 2))
    bad = copy.deepcopy(request); bad["steps"][0]["factor"] = [0, 1]
    rows.append(("extra/zero-step", "composition", bad, good, "InvalidContext", 0))
    bad = copy.deepcopy(request); bad["source"]["history"].append("history-at-cap-next")
    rows.append(("extra/history-cap", "composition", bad, good, "InvalidContext", 0))
    bad = copy.deepcopy(request); bad["source"]["loss"][0][1] = rat(8)
    bad["steps"][0]["factor"] = rat(16); bad["steps"][1]["factor"] = rat(F(1,16))
    rows.append(("extra/intermediate-cap", "composition", bad, good, "InvalidContext", 0))
    direct = {"source": requests[-1]["source"], "factor": rat(32), "target_unit": requests[-1]["steps"][1]["target_unit"], "step": "collapsed-one-step"}
    rows.append(("extra/actual-single-step-cap", "scale", direct, producer.receipt(direct), "InvalidContext", 0))
    assert len(rows) == 38
    return rows, summaries


def limits():
    resource.setrlimit(resource.RLIMIT_AS, (128*1024**2,)*2)
    resource.setrlimit(resource.RLIMIT_CPU, (3,3))
    resource.setrlimit(resource.RLIMIT_FSIZE, (262144,262144))


def main(output):
    output.mkdir(parents=True, exist_ok=False)
    (output/"contract.json").write_bytes((ROOT/"contract.json").read_bytes())
    started=time.perf_counter();metrics=[];assertions=0;units=0
    phases={"construction_seconds":0.0,"input_serialization_seconds":0.0,"receiving_seconds":0.0}
    report={"profile":PROFILE,"execution":"ExternalFreshProcessCompositionReceiver","search_candidates":0,"new_vocabulary":0}
    try:
        t=time.perf_counter();rows,summaries=fixtures();phases["construction_seconds"]=time.perf_counter()-t;report["instances"]=summaries
        for name,kind,request,candidate,wanted,checked in rows:
            remaining=30-(time.perf_counter()-started)
            if len(metrics)>=40 or remaining<=0:raise RuntimeError("UnknownBudget")
            folder=output/name;folder.mkdir(parents=True)
            t=time.perf_counter();put(folder/"expected.json",request);put(folder/"candidate.json",candidate);phases["input_serialization_seconds"]+=time.perf_counter()-t
            receiver=ROOT/"receive.py" if kind=="composition" else ROOT.parent/"decision_scale/receive.py"
            t=time.perf_counter()
            with (folder/"stdout.json").open('wb') as out,(folder/"stderr.txt").open('wb') as err:
                p=subprocess.run([sys.executable,'-B','-S',str(receiver),'--expected',str(folder/'expected.json'),'--candidate',str(folder/'candidate.json')],stdout=out,stderr=err,timeout=min(3,remaining),preexec_fn=limits)
            elapsed=time.perf_counter()-t;phases["receiving_seconds"]+=elapsed
            row={"case":name,"receiver":kind,"returncode":p.returncode,"wall_seconds":elapsed};metrics.append(row)
            assert p.returncode==0,row
            r=json.loads((folder/'stdout.json').read_text());units+=r['work_units']
            diag=r['locally_checked_steps'] if kind=='composition' else r['endpoint_arithmetic_checked']
            row.update(outcome=r['outcome'],work_units=r['work_units'],local_checks=diag,reason=r['reason'])
            assert r['outcome']==wanted,(name,r);assertions+=1
            assert r['expected_request']==request;assertions+=1
            assert len(diag)==checked,(name,r);assertions+=1
            assert all(r[k] is False for k in ('native_authority','close_authorized','free_authorized'));assertions+=1
            if wanted!='AcceptedScaleComposition':assert r['semantic_delta']==[];assertions+=1
        report['outcome']='PassedScaleCompositionCampaign'
    except Exception as e:
        report.update(outcome='Failure',failure={'type':type(e).__name__,'message':str(e)})
    report.update(metrics=metrics,assertions=assertions,work_units=units,phases=phases,campaign_wall_seconds=time.perf_counter()-started,peak_children_rss_kib=resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss,peak_supervisor_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,cost_scope='Construction, per-case input serialization, child startup/receiving and all ancestors are included. Reuse included but not separately timed. Final report write, archiving, research and publication excluded.')
    paths=[ROOT/'contract.json',ROOT/'run.py',ROOT/'receive.py']+[ROOT.parent/d/f for d in ('decision_scale','finite_decision','probability_receipt') for f in ('run.py','receive.py')]
    report['source_sha256']={str(p.relative_to(ROOT.parent.parent)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
    put(output/'result.json',report)
    print(json.dumps({k:report[k] for k in ('outcome','assertions','work_units','campaign_wall_seconds','peak_children_rss_kib')}))
    return 0 if report['outcome']=='PassedScaleCompositionCampaign' else 1


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True)
    raise SystemExit(main(p.parse_args().output))
