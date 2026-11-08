"""Reproducible in-process Python search comparison with independent verification."""
import pathlib
import platform
import random
import statistics
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'Python/source'))
import algorithms

lines = [
    '# Python search benchmark', '',
    f'Runtime: {platform.python_implementation()} {platform.python_version()}; OS: {platform.platform()}.',
    'Unit: milliseconds per invocation, measured using perf_counter_ns.',
    'Each method/case: 3 untimed warm-ups, then 3 separately timed invocations. Normal GC enabled; no JIT configuration.',
    'Timing includes preprocessing, comparisons and result allocation, excluding input generation, oracle, startup and JSON.',
    'Every result is independently checked before timing; measured results are checked after timing.',
    'Random: random.Random(20261108+n), uniform abcd; pattern=text[n//3:n//3+m].',
    'Repetitive: a^n / a^m. Near-miss: a^n / a^(m-1)b.', '',
    '|Case|n|m|Seed|Algorithm|Run 1 (ms)|Run 2|Run 3|Median (ms)|Verified|',
    '|---|---:|---:|---|---|---:|---:|---:|---:|---|',
]
for kind in ('random', 'repetitive', 'near-miss'):
    for n in (750, 1500, 3000):
        m = n // 4
        seed = 20261108 + n
        rng = random.Random(seed)
        text = ''.join(rng.choice('abcd') for _ in range(n)) if kind == 'random' else 'a' * n
        pattern = text[n // 3:n // 3 + m] if kind == 'random' else 'a' * m if kind == 'repetitive' else 'a' * (m - 1) + 'b'
        request = dict(text=text, pattern=pattern)
        expected = [i for i in range(n + 1) if text.startswith(pattern, i)]
        methods = (algorithms.naive, algorithms.kmp, algorithms.rk)
        for method in methods:
            assert method(request)['positions'] == expected
            for _ in range(3):
                method(request)
        times = {method.__name__: [] for method in methods}
        for round_index in range(3):
            for offset in range(3):
                method = methods[(round_index + offset) % 3]
                start = time.perf_counter_ns()
                result = method(request)
                elapsed = (time.perf_counter_ns() - start) / 1_000_000
                assert result['positions'] == expected
                times[method.__name__].append(elapsed)
        for method in methods:
            values = times[method.__name__]
            row = f'|{kind}|{n}|{m}|{seed if kind == "random" else "n/a"}|{method.__name__}|'
            row += '|'.join(f'{value:.6f}' for value in values + [statistics.median(values)])
            lines.append(row + f'|yes ({len(expected)} starts)|')
output = '\n'.join(lines) + '\n'
(ROOT / 'tests/student/benchmark-results.md').write_text(output, encoding='utf-8')
print(output, end='')
