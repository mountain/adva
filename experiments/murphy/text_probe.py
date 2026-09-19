"""The declared Kip Thorne opaque-character probe, not a string decoder.

Authored by ChatGPT (OpenAI), project-original under Unknown v0.3.
Usage: python3 text_probe.py --output FRESH_DIRECTORY
"""
import argparse
import json
from pathlib import Path
import lambda_ref as l
from research import reduce_comb, digest

HERE = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    out = parser.parse_args().output
    out.mkdir(parents=True, exist_ok=False)
    result = {'schema': 'adva.murphy.text-probe.v1', 'input': 'Kip Thorne',
              'representation': 'left-associated iota application to ten opaque character atoms, no terminator',
              'native_runs': 0, 'printer_invocations': 0,
              'is_string_decoder': False, 'cases': [],
              'limits': {'max_contractions_per_case': 20000, 'max_tree_nodes': 200000,
                         'wall_seconds_per_combinator_case': 30,
                         'lambda_work': 4000000, 'lambda_wall_seconds': 30}}
    try:
        chars = list(result['input'])
        names = ['char'+str(k) for k in range(len(chars))]
        vs = list(map(l.V, names))
        data = l.apps(l.j, *vs)
        p = l.decode((HERE/'murphy.iota').read_text().strip())
        c = l.decode((HERE/'evidence/C.iota').read_text().strip())
        tree = json.loads((HERE/'inputs/P-tree.json').read_text())
        left_d = l.closure(tree[1])
        inner = l.left(left_d)
        w = l.L('r', l.A(left_d, l.A(inner, l.V('r'))))
        f = l.lams('p q r s k', l.apps(l.V('k'), *map(l.V, ['p','q','s','r'])))
        def nf(t):
            return l.normal(l.db(l.lams(' '.join(names), t)))
        cases = [('murphy', l.A(p, data), [inner], ['A']),
                 ('murphy murphy', l.A(l.A(p,p), data), [w], ['B']),
                 ('C', l.A(c,data), [f], ['F']),
                 ('C twice', l.A(c,l.A(c,data)), [f,f], ['F','F'])]
        for name, term, tail, labels in cases:
            value, stats = reduce_comb(term, name+' applied to Kip Thorne')
            expected = l.apps(vs[0], l.C('S'), l.C('K'), *vs[1:], *tail)
            if nf(value) != nf(expected):
                raise AssertionError(name+' symbolic result disagrees')
            args, head = [], value
            while head[0] == 'a':
                args.append(head[2]); head = head[1]
            args.reverse()
            if head != vs[0] or args[:2] != [l.C('S'),l.C('K')] or args[2:11] != vs[1:]:
                raise AssertionError(name+' opaque characters not preserved')
            result['cases'].append({'program': name, 'contractions': stats['contractions'],
                'rules': stats['rules'], 'peak_nodes': stats['peak_nodes'],
                'head_character': chars[0], 'prefix_arguments': ['S_comb','K_comb']+chars[1:],
                'attached_values': labels, 'result_sha256': digest(value),
                'all_ten_characters_preserved_in_order': True, 'matches_symbolic_derivation': True})
        result['C_twice_equals_input'] = nf(l.A(c,l.A(c,data))) == nf(data)
        if result['C_twice_equals_input']:
            raise AssertionError('Expected coordinate-domain counterexample disappeared')
        result['status'] = 'CheckedWithinDeclaredScope'
    except (TimeoutError, RecursionError) as error:
        result.update(status='Unknown', reason=str(error))
    except Exception as error:
        result.update(status='Failed', reason=repr(error))
    (out/'result.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps({'status': result['status'], 'cases': len(result['cases']),
                      'native_runs': 0, 'reason': result.get('reason')}))
    return 0 if result['status'] == 'CheckedWithinDeclaredScope' else 1


if __name__ == '__main__':
    raise SystemExit(main())
