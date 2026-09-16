"""Independent recursive prefix receiver; no call to the Adva mix or its author.

This checks a complete syntactic input-binding/relocation relation. It is an
external research receipt, not a native certificate or semantic identity.
"""
from copy import deepcopy
import hashlib
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from experiments.bounded_self_compiler.language import TYPES, TARGET, canonical, instruction_data, node, text_data


def wire(program):
    if program['schema'] != TARGET:
        raise ValueError('expected unchanged v1 program')
    return node(241,[text_data(program['name']),
        node(254,[node(TYPES.index(r['kind']),[text_data(r['name'])]) for r in program['registers']]),
        node(250,[instruction_data(i) for i in program['code']])])


def binding(program,static):
    """Direct recursive specification used only by the external receiver."""
    n=len(program['registers'])
    if not 1 <= n <= 48 or any(r['name'].startswith('mix_') for r in program['registers']):
        raise ValueError('source register capacity or reserved namespace')
    dyn,bound,integer,data=n,n+1,n+2,n+3
    base=n+4
    code=[{'op':'input','dst':dyn},{'op':'clear','stack':base}]
    def literal(value,depth):
        if value['kind']=='integer':
            code.extend([{'op':'constant','dst':integer,'value':value['value']},
                         {'op':'box_integer','src':integer,'dst':data}])
        elif value['kind']=='node':
            if depth+1 >= 12:
                raise ValueError('mix static literal depth')
            code.append({'op':'clear','stack':base+depth+1})
            for child in value['fields']:
                literal(child,depth+1)
            code.append({'op':'pack','stack':base+depth+1,'tag':value['tag'],'dst':data})
        else:
            raise ValueError('unknown data constructor')
        code.append({'op':'push','stack':base+depth,'src':data})
    literal(static,0)
    code.extend([{'op':'pop','stack':base,'dst':data},
                 {'op':'node','tag':42,'fields':[data,dyn],'dst':bound}])
    offset=len(code)
    for original in program['code']:
        i=deepcopy(original)
        if i['op']=='input':
            i={'op':'copy','src':bound,'dst':i['dst']}
        elif i['op']=='jump':
            i['target']+=offset
        elif i['op']=='branch':
            i['yes']+=offset
            i['no']+=offset
        code.append(i)
    regs=deepcopy(program['registers'])+[
        {'name':'mix_'+chr(65+i),'kind':kind}
        for i,kind in enumerate(['data','data','integer','data']+['stack']*12)]
    return {**deepcopy(program),'registers':regs,'code':code},offset


def receive(program,static,residual):
    expected,offset=binding(program,static)
    if canonical(expected) != canonical(residual):
        raise ValueError('input-binding or body-relocation correspondence mismatch')
    return {'schema':'adva.mix-binding.receipt.research.v0',
            'source_sha256':hashlib.sha256(canonical(program)).hexdigest(),
            'static_sha256':hashlib.sha256(canonical(static)).hexdigest(),
            'residual_sha256':hashlib.sha256(canonical(residual)).hexdigest(),
            'prefix_instructions':offset,'body_instructions':len(program['code']),
            'pc_correspondence':[[pc,offset+pc] for pc in range(len(program['code']))],
            'bound_input_tag':42,'additional_registers':16,
            'retained':['all original body operations','ordered branch targets','dynamic control','refusals'],
            'residual':['capacity and fuel costs differ','no constant folding or interpreter elimination',
                        'external source admission and wire loader','no native identities or stable transformation certificate']}
