"""Independent receiving of exact block partitions, not a call to the seed.

Target addresses determine candidate partitions; source structure then checks
all their boundaries and primitive leaves. These are external research
certificates, never native GraftTrace, SourceId or OccurrenceId evidence.
"""
import hashlib
from language import SOURCE, TARGET, canonical


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def receive_compilation(source, target, budget):
    if source['schema'] != SOURCE or target['schema'] != TARGET:
        raise ValueError('compilation schemas')
    if source['name'] != target['name'] or source['registers'] != target['registers']:
        raise ValueError('module header changed')
    code = target['code']
    leaves, blocks = {}, []
    def at(pc, op):
        if not 0 <= pc < len(code) or code[pc]['op'] != op:
            raise ValueError('target instruction shape')
        return code[pc]
    def visit(b, start, path):
        budget.tick()
        kind = b['kind']
        end = start
        if kind == 'prim':
            if not start < len(code) or code[start] != b['instruction']:
                raise ValueError('primitive correspondence')
            if code[start]['op'] in ('jump', 'branch'):
                raise ValueError('source contains target-only control')
            leaves[start] = path
            end = start+1
        elif kind == 'seq':
            for i, x in enumerate(b['items']):
                end = visit(x, end, path + ['items',i])
        elif kind == 'if':
            branch = at(start,'branch')
            if branch != {'op':'branch','condition':b['condition'],'yes':start+1,'no':branch['no']}:
                raise ValueError('if entry')
            split = visit(b['yes'], start+1, path+['yes'])
            jump = at(split,'jump')
            if branch['no'] != split+1:
                raise ValueError('if alternative entry')
            end = visit(b['no'], split+1, path+['no'])
            if jump != {'op':'jump','target':end}:
                raise ValueError('if exit')
        elif kind == 'while':
            branch = at(start,'branch')
            split = visit(b['body'], start+1, path+['body'])
            if at(split,'jump') != {'op':'jump','target':start}:
                raise ValueError('loop back edge')
            end = split+1
            if branch != {'op':'branch','condition':b['condition'],'yes':start+1,'no':end}:
                raise ValueError('loop entry or exit')
        else:
            raise ValueError('source constructor')
        blocks.append({'path':path,'kind':kind,'start':start,'end':end})
        return end
    if visit(source['body'],0,[]) != len(code):
        raise ValueError('unclaimed target suffix')
    return {'schema':'adva.structured-compilation.receipt.research.v0',
            'source_sha256':digest(source),'target_sha256':digest(target),
            'observer':'terminal data/rejection and ordered primitive events; control/fuel costs separate',
            'blocks':blocks,'primitive_paths':{str(k):v for k,v in leaves.items()},
            'residual':['External structural receiver; Rust target admission is separate',
                        'No native source/occurrence or GraftTrace correspondence',
                        'Finite resource exhaustion is not source/target equivalence failure']}
