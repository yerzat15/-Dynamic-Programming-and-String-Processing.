"""Independent small oracles and domain-limit checks; run from repository root."""
import functools
import itertools
import json
import pathlib
import random
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools'))
from run import build, execute
from public_validate import check

SEED = 20261107
rng = random.Random(SEED)
cases = []


def add(name, request, expected):
    cases.append(dict(name=name, input=request, output=expected))


def positions(text, pattern):
    # Library-based oracle is deliberately independent of all three implementations.
    return [i for i in range(len(text) + 1) if text.startswith(pattern, i)]


def lcs_oracle(a, b):
    best = 0
    for mask in range(1 << len(a)):
        candidate = ''.join(c for i, c in enumerate(a) if mask >> i & 1)
        it = iter(b)
        if all(any(c == d for d in it) for c in candidate):
            best = max(best, len(candidate))
    return dict(length=best)


@functools.lru_cache(None)
def merge_oracle(sizes):
    # Enumerate legal chronological choices, rather than using interval DP.
    if len(sizes) < 2:
        return 0
    return min(sizes[i] + sizes[i + 1] + merge_oracle(
        sizes[:i] + (sizes[i] + sizes[i + 1],) + sizes[i + 2:])
        for i in range(len(sizes) - 1))


def tree_oracle(weights, edges):
    return max(sum(w for i, w in enumerate(weights) if mask >> i & 1)
               for mask in range(1 << len(weights))
               if all(not (mask >> u & 1 and mask >> v & 1) for u, v in edges))


def suffix_oracle(text):
    sa = sorted(range(len(text)), key=lambda i: text[i:])
    lcp = [0] * len(text)
    for j in range(1, len(text)):
        a, b = text[sa[j - 1]:], text[sa[j]:]
        for c, d in zip(a, b):
            if c != d:
                break
            lcp[j] += 1
    best = max(range(len(text)), key=lambda j: lcp[j]) if text else 0
    return dict(sa=sa, lcp=lcp, repeated=text[sa[best]:sa[best] + lcp[best]] if text else '')


def word(n, alphabet='ab A!?~'):
    return ''.join(rng.choice(alphabet) for _ in range(n))


def small_cases():
    for a, b in [('', ''), ('', 'a'), ('a', ''), ('tea_time', 'team'),
                 ('aaaa', 'aa'), ('ab', 'ba')] + [(word(rng.randrange(10)), word(rng.randrange(10))) for _ in range(100)]:
        add('lcs exhaustive subsequences', dict(task='lcs', a=a, b=b), lcs_oracle(a, b))
    for sizes in [[], [9], [0, 0, 0], [1, 100, 1], [10**9] * 5] + [
            [rng.randrange(10) for _ in range(rng.randrange(8))] for _ in range(100)]:
        add('merge exhaustive adjacent choices', dict(task='merge', sizes=sizes), dict(cost=merge_oracle(tuple(sizes))))
    trees = [([], []), ([-4], []), ([0], []), ([7], []), ([-2, -3], [[0, 1]]), ([0, 0], [[0, 1]])]
    for _ in range(120):
        n = rng.randrange(1, 12)
        weights = [rng.randrange(-5, 10) for _ in range(n)]
        edges = [[v, rng.randrange(v)] for v in range(1, n)]
        # Relabel the root and shuffle/reverse edges to exercise root invariance.
        permutation = rng.sample(range(n), n)
        shuffled = [0] * n
        for i in range(n): shuffled[permutation[i]] = weights[i]
        edges = [[permutation[v], permutation[u]] for u, v in edges]
        rng.shuffle(edges)
        trees.append((shuffled, edges))
    for weights, edges in trees:
        add('tree exhaustive subsets', dict(task='tree', n=len(weights), weights=weights, edges=edges),
            dict(weight=tree_oracle(weights, edges)))
    pairs = [('', ''), ('abc', ''), ('', 'a'), ('a', 'aa'), ('aaaaa', 'aaa'),
             ('abababa', 'aba'), ('abdj', 'ab'), ('~ ab!ab', 'ab'), ('Aa A! ', 'A'), ('zab', 'ab')]
    pairs += [(word(rng.randrange(65)), word(rng.randrange(15))) for _ in range(200)]
    # Exhaustive binary texts and patterns catch fallback/overlap mistakes.
    binary = [''.join(s) for n in range(6) for s in itertools.product('ab', repeat=n)]
    pairs += [(t, p) for t in binary for p in binary[:15]]
    for t, p in pairs:
        for task in ('naive', 'kmp', 'rk'):
            add('search independent oracle', dict(task=task, text=t, pattern=p), dict(positions=positions(t, p)))
    for t in ['', 'a', 'aaaaaa', 'abcdef', 'banana', 'ababcdcd', ' ~!A a'] + [word(rng.randrange(60)) for _ in range(150)]:
        add('suffix direct sorting and LCP', dict(task='suffix', text=t), suffix_oracle(t))
    dictionaries = [([], ['', 'abc']), (['a'], []), (['a'], ['']),
                    (['he', 'she', 'he'], ['sheshe', 'sheshe', '']),
                    (['a', 'aa', 'aaa', 'a'], ['aaaaa', '', 'aaaaa'])]
    for _ in range(100):
        dictionaries.append(([word(rng.randrange(1, 8)) for _ in range(rng.randrange(12))],
                             [word(rng.randrange(40)) for _ in range(rng.randrange(5))]))
    for patterns, texts in dictionaries:
        add('aho independent occurrence counts', dict(task='aho', patterns=patterns, texts=texts),
            dict(counts=[[len(positions(t, p)) for p in patterns] for t in texts]))


def stress_cases():
    add('lcs maximum product', dict(task='lcs', a='ab' * 500, b='ba' * 500), dict(length=999))
    add('lcs maximum empty side', dict(task='lcs', a='', b='a' * 1000), dict(length=0))
    # Equal leaf weights: optimal ordered full binary tree depths differ by at most 1.
    n = 200
    height = (n - 1).bit_length()
    add('merge 200 large blocks', dict(task='merge', sizes=[10**9] * n),
        dict(cost=(n * (height + 1) - (1 << height)) * 10**9))
    add('merge 200 zero blocks', dict(task='merge', sizes=[0] * n), dict(cost=0))
    n = 100000
    add('tree maximum deep chain', dict(task='tree', n=n, weights=[10**9] * n,
        edges=[[i - 1, i] for i in range(1, n)]), dict(weight=50000 * 10**9))
    add('tree maximum star', dict(task='tree', n=n, weights=[10**9] * n,
        edges=[[0, i] for i in range(1, n)]), dict(weight=(n - 1) * 10**9))
    add('tree maximum negative chain', dict(task='tree', n=n, weights=[-10**9] * n,
        edges=[[i - 1, i] for i in range(1, n)]), dict(weight=0))
    for task, n, m in [('naive', 3000, 1500), ('kmp', 200000, 100000), ('rk', 10000, 2000)]:
        add(task + ' maximum overlap', dict(task=task, text='a' * n, pattern='a' * m),
            dict(positions=list(range(n - m + 1))))
        add(task + ' maximum empty pattern', dict(task=task, text='a' * n, pattern=''),
            dict(positions=list(range(n + 1))))
    add('rk maximum pattern longer than text', dict(task='rk', text='a', pattern='a' * 10000), dict(positions=[]))
    for t in ['a' * 50000, 'ab' * 25000]:
        n = len(t)
        sa = list(range(n - 1, -1, -1)) if t[0] == t[1] else list(range(n - 2, -1, -2)) + list(range(n - 1, -1, -2))
        lcp = [0] + list(range(1, n)) if t[0] == t[1] else [0] + list(range(2, n, 2)) + [0] + list(range(1, n - 1, 2))
        add('suffix maximum repetitive text', dict(task='suffix', text=t), dict(sa=sa, lcp=lcp, repeated=t[:max(lcp)]))
    patterns = ['a'] * 10000
    add('aho maximum duplicates and text', dict(task='aho', patterns=patterns, texts=['a' * 200000]),
        dict(counts=[[200000] * 10000]))
    patterns = ['a' * i for i in range(1, 447)]  # L=99681, dense suffix matches.
    add('aho dense suffixes', dict(task='aho', patterns=patterns, texts=['a' * 200000]),
        dict(counts=[[200001 - len(p) for p in patterns]]))
    add('aho maximum trie depth and 100 texts', dict(task='aho', patterns=['a' * 100000], texts=['a' * 2000] * 100),
        dict(counts=[[0]] * 100))
    add('aho maximum output dimensions', dict(task='aho', patterns=['a'] * 10000, texts=['a' * 2000] * 100),
        dict(counts=[[2000] * 10000 for _ in range(100)]))


def run_batch(command, batch, label):
    start = time.perf_counter()
    answers = execute(command, [c['input'] for c in batch])
    elapsed = time.perf_counter() - start
    for case, answer in zip(batch, answers):
        assert check(case['input'], answer, case['output']), f"FAIL {case['name']}: {str(answer)[:500]}"
    print(f'PASS {label}: {len(batch)} requests, {elapsed:.3f} s (process + transport; validation excluded)')
    return elapsed


def main():
    command = build('Python')
    print(f'Seed: {SEED}; command: {command}')
    fixtures = json.loads((ROOT / 'tests/student/fixtures.json').read_text(encoding='utf-8'))
    answers = execute(command, [case['input'] for case in fixtures])
    for case, answer in zip(fixtures, answers):
        assert check(case['input'], answer, case['output']), case['name']
    (ROOT / 'tests/student/fixture-results.json').write_text(json.dumps([
        dict(name=case['name'], input=case['input'], expected=case['output'], actual=answer, passed=True)
        for case, answer in zip(fixtures, answers)], indent=2), encoding='utf-8')
    print(f'PASS named fixtures: {len(fixtures)}; actual outputs in fixture-results.json')
    small_cases()
    small = cases[:]
    run_batch(command, small + small, 'independent small oracles and repeated mixed batch')
    cases.clear()
    stress_cases()
    for task in ('lcs', 'merge', 'tree', 'naive', 'kmp', 'rk', 'suffix', 'aho'):
        run_batch(command, [c for c in cases if c['input']['task'] == task], f'{task} domain limits')
    print(f'PASS total: {len(fixtures) + 2 * len(small) + len(cases)} checked responses')


if __name__ == '__main__':
    main()
