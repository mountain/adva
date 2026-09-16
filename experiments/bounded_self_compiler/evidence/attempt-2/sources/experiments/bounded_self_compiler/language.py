"""Research source grammar, explicit wire codec and external stage-0 seed.

The codec only changes representation. It never lowers control or fills targets.
No native semantic identities are created here.
"""
import json

SOURCE = 'adva.structured.program.research.v0'
TARGET = 'adva.data-machine.program.research.v1'
OPS = [
    ('input', 'dst'), ('constant', 'dst value'), ('copy', 'src dst'),
    ('clear', 'stack'), ('push', 'stack src'), ('pop', 'stack dst'),
    ('is_empty', 'stack dst'), ('tag', 'src dst'), ('field', 'src arity index dst'),
    ('as_integer', 'src dst'), ('box_integer', 'src dst'), ('node', 'tag fields dst'),
    ('add', 'left right dst'), ('multiply', 'left right dst'), ('equal', 'left right dst'),
    ('jump', 'target'), ('branch', 'condition yes no'), ('return', 'src'),
    ('reject', 'reason'), ('length', 'src dst'), ('field_dynamic', 'src index dst'),
    ('pack', 'stack tag dst'), ('stack_length', 'stack dst'),
]
TYPES = ['integer', 'boolean', 'data', 'stack']


def integer(n):
    if type(n) is not int or not -(2**63) <= n < 2**63:
        raise ValueError('expected i64')
    return {'kind': 'integer', 'value': n}


def node(tag, fields):
    return {'kind': 'node', 'tag': tag, 'fields': fields}


def text_data(s):
    return node(255, [integer(b) for b in s.encode('utf-8')])


def untext(d):
    if d.get('tag') != 255:
        raise ValueError('expected text encoding')
    return bytes(unint(b) for b in d['fields']).decode('utf-8')


def unint(d):
    if set(d) != {'kind', 'value'} or d['kind'] != 'integer':
        raise ValueError('expected integer data')
    return integer(d['value'])['value']


def instruction_data(i):
    names = [op for op, _ in OPS]
    k = names.index(i['op'])
    keys = OPS[k][1].split()
    if set(i) != {'op', *keys}:
        raise ValueError('instruction fields')
    return node(k, [text_data(i[p]) if p == 'reason' else
                    node(254, [integer(x) for x in i[p]]) if p == 'fields' else
                    integer(i[p]) for p in keys])


def decode_instruction(d):
    if d.get('kind') != 'node' or type(d.get('tag')) is not int or not 0 <= d['tag'] < len(OPS):
        raise ValueError('instruction tag')
    op, params = OPS[d['tag']]
    keys = params.split()
    if len(keys) != len(d['fields']):
        raise ValueError('instruction arity')
    result = {'op': op}
    for p, v in zip(keys, d['fields']):
        if p == 'fields':
            if v.get('tag') != 254:
                raise ValueError('expected field vector')
            result[p] = [unint(x) for x in v['fields']]
        else:
            result[p] = untext(v) if p == 'reason' else unint(v)
    if instruction_data(result) != d:
        raise ValueError('noncanonical instruction')
    return result


def body_data(b, depth=0):
    if depth > 24:
        raise ValueError('source depth')
    kind = b['kind']
    if kind == 'prim' and set(b) == {'kind', 'instruction'}:
        if b['instruction']['op'] in ('jump', 'branch'):
            raise ValueError('unstructured source control')
        return node(0, [instruction_data(b['instruction'])])
    if kind == 'seq' and set(b) == {'kind', 'items'}:
        return node(1, [body_data(x, depth+1) for x in b['items']])
    if kind == 'if' and set(b) == {'kind', 'condition', 'yes', 'no'}:
        return node(2, [integer(b['condition']), body_data(b['yes'], depth+1), body_data(b['no'], depth+1)])
    if kind == 'while' and set(b) == {'kind', 'condition', 'body'}:
        return node(3, [integer(b['condition']), body_data(b['body'], depth+1)])
    raise ValueError('source constructor')


def encode_source(s):
    if set(s) != {'schema', 'name', 'registers', 'body'} or s['schema'] != SOURCE:
        raise ValueError('source schema')
    regs = []
    for r in s['registers']:
        if set(r) != {'name', 'kind'}:
            raise ValueError('register schema')
        regs.append(node(TYPES.index(r['kind']), [text_data(r['name'])]))
    result = node(240, [text_data(s['name']), node(254, regs), body_data(s['body'])])
    if len(canonical(result)) > 524288:
        raise ValueError('source encoding capacity')
    return result


def decode_target(d):
    if d.get('tag') != 241 or len(d['fields']) != 3:
        raise ValueError('target module encoding')
    name, registers, code = d['fields']
    if registers.get('tag') != 254 or code.get('tag') != 250:
        raise ValueError('target vector encoding')
    regs = []
    for r in registers['fields']:
        if r.get('kind') != 'node' or not 0 <= r['tag'] < len(TYPES) or len(r['fields']) != 1:
            raise ValueError('register encoding')
        regs.append({'name': untext(r['fields'][0]), 'kind': TYPES[r['tag']]})
    return {'schema': TARGET, 'name': untext(name), 'registers': regs,
            'code': [decode_instruction(i) for i in code['fields']]}


def seed_compile(s):
    """External seed: forward emission plus patching, not the Adva algorithm."""
    encode_source(s)
    code = []
    def emit(b):
        kind = b['kind']
        if kind == 'prim':
            code.append(dict(b['instruction']))
        elif kind == 'seq':
            for x in b['items']:
                emit(x)
        elif kind == 'if':
            start = len(code)
            code.append({'op': 'branch', 'condition': b['condition'], 'yes': start+1, 'no': None})
            emit(b['yes'])
            end_jump = len(code)
            code.append({'op': 'jump', 'target': None})
            code[start]['no'] = len(code)
            emit(b['no'])
            code[end_jump]['target'] = len(code)
        elif kind == 'while':
            start = len(code)
            code.append({'op': 'branch', 'condition': b['condition'], 'yes': start+1, 'no': None})
            emit(b['body'])
            code.append({'op': 'jump', 'target': start})
            code[start]['no'] = len(code)
    emit(s['body'])
    return {'schema': TARGET, 'name': s['name'], 'registers': s['registers'], 'code': code}


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=True).encode()


def prim(op, **params):
    return {'kind': 'prim', 'instruction': {'op': op, **params}}


def seq(*items):
    return {'kind': 'seq', 'items': list(items)}


def if_(condition, yes, no=None):
    return {'kind': 'if', 'condition': condition, 'yes': yes, 'no': seq() if no is None else no}


def while_(condition, body):
    return {'kind': 'while', 'condition': condition, 'body': body}
