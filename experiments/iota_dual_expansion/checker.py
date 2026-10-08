"""Original finite calibration by ChatGPT (OpenAI), under Unknown v0.3.
Submitted through Mingli Yuan's account proxy; no human verification implied.
These Python objects are external syntax, not native Adva identities.
"""
import argparse
from dataclasses import dataclass
import hashlib
import importlib.util
import json
from pathlib import Path
import resource
import signal
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]

@dataclass(frozen=True)
class Leaf:
    symbol: str
    def __post_init__(self):
        if self.symbol not in ('i', 's', 'k', 'a', 'b', 'c'):
            raise TypeError('external iota leaf required')

@dataclass(frozen=True)
class App:
    function: object
    argument: object
    def __post_init__(self):
        if not all(isinstance(t, (Leaf, App)) for t in (self.function, self.argument)):
            raise TypeError('Iota application operands required')

@dataclass(frozen=True)
class Comb:
    active_slot: int
    chronology: int
    active: object
    constant: str
    def __post_init__(self):
        if self.active_slot not in (1, 2) or self.chronology < 1:
            raise TypeError('comb slot/chronology')
        if not (self.active == 'z' or isinstance(self.active, Comb)):
            raise TypeError('AEG skeleton is not an Iota application')
        if self.constant != 'c' + str(self.chronology):
            raise TypeError('chronological constant required')

I, S, K = Leaf('i'), Leaf('s'), Leaf('k')

def show(t):
    return t.symbol if isinstance(t, Leaf) else '@' + show(t.function) + show(t.argument)

def mirror(t):
    return t if isinstance(t, Leaf) else App(mirror(t.argument), mirror(t.function))

def build(slot, count, seed):
    t = seed
    for _ in range(count):
        t = App(t, I) if slot == 1 else App(I, t)
    return t

def comb(slot, count):
    t = 'z'
    for j in range(1, count + 1):
        t = Comb(slot, j, t, 'c' + str(j))
    return t

def tagged(t):
    if isinstance(t, Leaf):
        return {'type': 'iota-leaf' if t.symbol == 'i' else 'internal-combinator' if t.symbol in 'sk' else 'aperture-leaf', 'symbol': t.symbol}
    if isinstance(t, App):
        return {'type': 'iota-application', 'function': tagged(t.function), 'argument': tagged(t.argument)}
    if isinstance(t, Comb):
        return {'type': 'AEG-comb-skeleton', 'operation': 'omega_' + str(t.chronology), 'slot': t.active_slot, 'active': tagged(t.active), 'constant': t.constant}
    return {'type': 'AEG-hole', 'symbol': t}

def nodes(t):
    return 1 if isinstance(t, Leaf) else 1 + nodes(t.function) + nodes(t.argument)

def root_step(t):
    args = []
    h = t
    while isinstance(h, App):
        args.insert(0, h.argument)
        h = h.function
    if h == I and len(args) == 1:
        return 'i', App(App(args[0], S), K)
    if h == K and len(args) == 2:
        return 'k', args[0]
    if h == S and len(args) == 3:
        x, y, z = args
        return 's', App(App(x, z), App(y, z))
    return None

def step(t, path=()):
    if isinstance(t, Leaf):
        return None
    left = step(t.function, path + (0,))
    if left:
        rule, p, before, after, replacement = left
        return rule, p, before, after, App(replacement, t.argument)
    own = root_step(t)
    if own:
        rule, after = own
        return rule, path, show(t), show(after), after
    right = step(t.argument, path + (1,))
    if right:
        rule, p, before, after, replacement = right
        return rule, p, before, after, App(t.function, replacement)
    return None

def history(t):
    events, states = [], [show(t)]
    for _ in range(65):
        if nodes(t) > 4096:
            raise RuntimeError('Unknown: node budget')
        found = step(t)
        if found is None:
            return {'source': states[0], 'normal_form': show(t), 'events': events, 'schedule_cuts': states}
        if len(events) == 64:
            raise RuntimeError('Unknown: event budget')
        rule, path, before, after, t = found
        events.append({'rule': rule, 'path': list(path), 'before': before, 'after': after})
        states.append(show(t))
    raise RuntimeError('Unknown: event budget')

def run():
    contract = json.loads((HERE / 'contract.json').read_text())
    for relative, expected in contract['pins'].items():
        if hashlib.sha256((ROOT / relative).read_bytes()).hexdigest() != expected:
            raise ValueError('input pin mismatch: ' + relative)
    old_path = ROOT / 'experiments/four_iota_frames/checker.py'
    spec = importlib.util.spec_from_file_location('reference', old_path)
    old = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(old)
    rows = []
    sources = []
    for kind, seed, offset in [('pure', I, -1), ('open', Leaf('a'), 0)]:
        for k in (1, 2, 3):
            n = k + offset
            left, right = build(1, n, seed), build(2, n, seed)
            assert mirror(left) == right and mirror(right) == left
            row = {'family': kind, 'k': k, 'application_nodes': n, 'left_tree': tagged(left), 'right_tree': tagged(right), 'left_comb': tagged(comb(1,n)), 'right_comb': tagged(comb(2,n)), 'left': history(left), 'right': history(right)}
            rows.append(row)
            sources.extend([left, right])
    controls = [I, build(1,2,I), Leaf('a'), App(App(I,I),Leaf('a')), App(I,Leaf('a')), App(Leaf('a'),I), App(App(Leaf('a'),App(I,Leaf('b'))),Leaf('c'))]
    sources.extend(controls)
    agreements = []
    for t in sources:
        ours = history(t)
        theirs = old.reduce_term(show(t), cap=64)
        assert ours['normal_form'] == theirs['normal_form']
        assert ours['events'] == [{k:e[k] for k in ('rule','path','before','after')} for e in theirs['events']]
        agreements.append(show(t))
    h = [history(t) for t in controls]
    assert h[0]['normal_form'] == h[1]['normal_form'] and len(h[0]['events']) != len(h[1]['events'])
    assert h[2]['normal_form'] == h[3]['normal_form'] and len(h[2]['events']) != len(h[3]['events'])
    assert step(controls[4]) is not None and step(mirror(controls[4])) is None
    assert rows[2]['left']['normal_form'] != rows[2]['right']['normal_form']
    return {'status':'ExternalExactPass', 'rows':rows, 'controls':h, 'independent_reducer_agreements':agreements, 'three_role_binding': {'source':show(controls[6]), 'entry_roles':[0,1,2], 'exit_roles':[0,1,2], 'port_leaves':['a','b','c'], 'role_reading':['{}','[]','()'], 'scope':'external declared policy over actual source leaves; not native aperture admission'}, 'pins': {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in [old_path, ROOT/'knowledge/received/iota-process-knowledge-2026-09-17-v1/materials/iota.md', HERE/'contract.json', HERE/'checker.py']}}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    if sys.platform != 'linux':
        raise RuntimeError('Unknown: contracted memory enforcement requires Linux')
    resource.setrlimit(resource.RLIMIT_CPU, (15,15))
    resource.setrlimit(resource.RLIMIT_AS, (268435456,268435456))
    resource.setrlimit(resource.RLIMIT_FSIZE, (1048576,1048576))
    def timeout(*_):
        raise RuntimeError('Unknown: wall budget')
    signal.signal(signal.SIGALRM, timeout)
    signal.alarm(20)
    report = run()
    data = json.dumps(report, ensure_ascii=False, indent=2) + '\n'
    if len(data.encode()) > 1048576:
        raise RuntimeError('Unknown: output budget')
    with Path(args.output).open('x', encoding='utf-8') as f:
        f.write(data)

if __name__ == '__main__':
    main()
