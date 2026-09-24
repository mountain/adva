"""One declared direct-sum witness, without adaptive search; Unknown v0.3."""
import itertools


def run(contract, input_root):
    n, u, v = (contract[k] for k in ['length', 'U', 'V'])
    a = sorted({(x+y) % n for x in u for y in v})
    b = sorted({(x-y) % n for x in u for y in v})
    assert len(a) == len(b) == len(u)*len(v)
    def corr(s):
        return [sum((x+d) % n in s for x in s) for d in range(n)]
    ca, cb = corr(a), corr(b)
    equivalent = any(sorted((sign*x+t) % n for x in a) == b
                     for sign in [-1, 1] for t in range(n))
    assert ca == cb
    witness = None
    count = 0
    for i, j in itertools.combinations(range(1, n), 2):
        count += 1
        x = sum((t+i) % n in a and (t+j) % n in a for t in a)
        y = sum((t+i) % n in b and (t+j) % n in b for t in b)
        if x != y and witness is None:
            witness = {'offsets':[0, i, j], 'counts':[x, y]}
    return {'first_set':a, 'second_set':b, 'exact_autocorrelation':ca,
            'equal_power_by_cyclic_Wiener_Khinchin':True,
            'translation_or_reflection_equivalent':equivalent,
            'triple_offsets_checked':count, 'triple_witness':witness,
            'scope':'One finite binary-word pair. No geometric contact rules or tile existence established.'}
