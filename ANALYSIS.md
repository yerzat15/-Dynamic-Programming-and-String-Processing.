# Assignment 4 — Python analysis

## Environment and execution

The selected language is **Python**, as recorded in `submission.json`. The implementation uses Python 3.12+ and only standard-library modules (`array`, `collections`, JSON transport). No algorithm library or built-in substring search replaces a required algorithm.

Measurements were collected on 8 November 2026 using CPython 3.12.14, Windows 11 build 26200, AMD Ryzen 7 5800H with Radeon Graphics, and 16,473,034,752 bytes of physical memory (15.34 GiB). Full runtime evidence is in [environment.txt](tests/student/environment.txt). These are local Windows measurements, not official container results. The solution is single-threaded; local runs do not enforce the official total-memory cap.

Commands from the repository root:

```sh
python tools/run.py --setup
python tools/run.py --check
python tools/run.py --input examples/lcs.jsonl
python tests/student/test_solution.py
python tests/student/benchmark.py
python tests/student/environment.py
```

No compilation step is required. For direct JSON Lines execution use `python Python/source/main.py`. On this machine, commands used `C:/Users/rusla/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe` because the system Python shortcut is unavailable; see README for PowerShell commands. A normal Python 3.12+ installation works elsewhere.

Every input line produces one output object. State is local to a request. All positions are zero-based, strings use the published printable-ASCII domain, and Python integers preserve exact costs and counts without 32-bit overflow. Complexity bounds below count bounded-domain arithmetic as constant-time and separate auxiliary memory from input/output storage.

## Algorithm explanations

### LCS

`dp[i][j]` is the length of a longest common subsequence of prefixes `a[:i]` and `b[:j]`. The zero row and column represent empty prefixes. When final characters agree, the value is `dp[i-1][j-1]+1`; otherwise it is `max(dp[i-1][j], dp[i][j-1])`. Increasing row/column order makes all dependencies available.

If the final characters differ, a common subsequence must omit at least one of their positions. If they agree, an optimum can be chosen to use that common last character after an optimum of the shorter prefixes. These cases prove the recurrence by induction.

Reconstruction moves backwards from `(n,m)`: equal characters give a diagonal step and append one character; a mismatch moves to a predecessor with the same optimum. On ties the upper cell is selected. Reversing the result preserves original order in both strings and gives exactly the stored optimum length. Empty input yields an empty sequence.

Time and auxiliary space: `O((n+1)(m+1))`, with `O(n+m)` reconstruction time. The table is a list of independent row lists. Input uses `O(n+m)` space; output uses `O(length+1)`. `tea_time` / `team` tests subsequence rather than contiguous substring behavior; `ab` / `ba` checks alternative optimal answers.

### Ordered adjacent-block merging

`dp[l][r]` is the minimum cost to merge the closed original interval `[l,r]`. A singleton costs zero. Prefix sums provide the interval weight in constant time. Considering the last split gives:

`dp[l][r] = min(dp[l][k] + dp[k+1][r]) + prefix[r+1] - prefix[l]`, for `l<=k<r`.

Intervals are processed in increasing length. Every legal last operation joins two adjacent intervals; its children can be independently replaced by cheaper plans. Conversely, optimal child plans followed by their merge are legal. Minimizing all last splits therefore gives an optimum. Python tuple ordering chooses the smallest `k` on ties, and `split[l][r]` stores it.

An explicit stack reconstructs in postorder: emit left child operations, right child operations, then `[l,k,r]`. Thus both referenced blocks exist when the merge is emitted. For `n>1`, exactly `n-1` merges are returned. For zero or one block, return zero cost and an empty plan.

Time is `O(n^3)`, auxiliary space `O(n^2)`, and input/output space `O(n+1)`; empty input costs `O(1)`. The generator passed to `min` is consumed incrementally, not stored as a cubic collection. `[1,100,1]` costs 203 under adjacency, whereas illegally combining the outside blocks would give 104. Three billion-sized blocks cost 5,000,000,000, testing exact integer arithmetic.

### Tree independent set

Build adjacency lists and an iterative parent-before-child order rooted at vertex 0. In Python, iterating over `order` visits appended children as well; the tree contract guarantees that excluding the parent visits each vertex exactly once. Reverse that order for bottom-up processing.

`take[u]` is the best subtree weight if `u` is selected; `skip[u]` is the best weight if it is omitted. Initially `take[u]=weight[u]` and `skip[u]=0`. Each child `v` contributes `skip[v]` to `take[u]` and `max(take[v],skip[v])` to `skip[u]`. Subtrees have no cross edges, so these independent choices are exhaustive and compatible. Induction from leaves proves both values, and the root optimum is their maximum.

During reconstruction, select `u` only if its parent is omitted and `take[u]>skip[u]`. Ties are skipped. This enforces independence, visits each vertex once, and attains the optimum. All-negative trees return the empty set with weight zero; an empty tree is handled explicitly. Random relabelling tests that changing the effective root does not affect the optimum.

Time and auxiliary memory are `O(n+1)`; input adjacency/weights and output also use `O(n+1)`. The copy `order[1:]` remains linear space. No recursive call is used, including on a 100,000-vertex chain. Large sums are Python integers. Small subset enumeration checks values and reconstruction independently.

### Naive exact search

Try every start in `range(n-m+1)`, comparing characters from left to right. After `j` successful comparisons, exactly the first `j` pattern characters agree with that window. Output the start iff `j=m`. Increasing starts give sorted positions and retain overlaps. An empty pattern succeeds at every boundary `0..n`; a longer pattern has no candidate start.

Time is `O(n*m+n+1)` including output. Auxiliary space is `O(1)`; the result list requires `O(z+1)` for `z` matches, and the input requires `O(n+m)`. The `a b` / empty-pattern fixture expects `[0,1,2,3]`, catching omission of the last boundary.

### KMP

`pi[i]` is the length of the longest proper prefix of `pattern[:i+1]` that is also its suffix. During construction, a mismatch falls back from border length `j` to `pi[j-1]`; a match extends the border. The failure chain enumerates the remaining possible borders, so no valid one is skipped.

During scanning, `j` describes the pattern prefix matching the suffix of text consumed so far. Applying the same fallback rule preserves all possible continuation matches. A full match ends at `i`, so its start is `i-m+1`. Falling back to `pi[m-1]` after reporting retains overlaps; `abababa` / `aba` gives `[0,2,4]`. The empty pattern returns all boundaries before accessing any pattern character.

Every increase in `j` is at most one per processed character; each fallback decreases it. This amortization gives `O(n+m+z+1)` time, `O(m+1)` auxiliary memory for the prefix list, `O(z+1)` output memory and `O(n+m)` input memory.

### Exact Rabin–Karp

Hashes use ASCII codes, base 31 and modulus 101, with the highest power on the left. Build the target and first window by repeated multiplication/addition. Let `P=31^(m-1) mod 101`; the rolling update is:

`((window - ord(outgoing)*P)*31 + ord(incoming)) % 101`.

Subtracting the outgoing term, shifting powers and appending the new character preserves the polynomial hash. Python's remainder with positive divisor 101 is always nonnegative, including negative intermediates. Empty or overlong patterns are handled before constructing a window.

Different hashes reject a window; equal hashes trigger actual character comparisons. Therefore collisions cannot produce false positives. `ab` and `dj` both hash to 75, but `abdj` / `ab` reports only start 0. `zab` / `ab` tests a negative rolling intermediate and must report start 1. Overlaps and empty boundaries match the other search methods.

For `1<=m<=n`, time is `O(n+m+c*m)` for `c` equal-hash candidates, including modular-power setup within this bound. The general bound is `O(n*m+n+m+1)`; it is not deterministic linear worst-case time. Scalar rolling state gives `O(1)` auxiliary space in the bounded arithmetic model, besides `O(z+1)` output and `O(n+m)` input. The deliberately small modulus makes collision checking important.

### Prefix-doubling suffix array and Kasai LCP

Initially ranks are character codes. For width `w`, a suffix key is `(rank[i], rank[i+w])`, with `-1` if the second block is missing. Sorting pairs orders prefixes of length `2w`. Equal keys receive equal new ranks; distinct keys receive consecutive ranks. Induction on the doubled width proves this invariant. Stop once all ranks are distinct or the width covers the text. Missing second blocks sort before real characters, preserving shorter-prefix ordering.

The implementation uses Python's comparison-based list sort with precomputed constant-size tuple keys. It does not materialize suffix strings. There are `O(log(n+1))` rounds, each costing `O(n log(n+1))`, so construction takes `O(n log^2(n+1))` time and `O(n+1)` auxiliary space, including sorting workspace, tuples and rank lists. Only nonempty suffix starts are emitted; there is no sentinel in the output.

Kasai constructs the inverse suffix order. For each original start, compare it to its lexicographic predecessor and store the common length in the corresponding LCP entry. On the next original start, at least `common-1` characters can be reused: removing one shared character leaves that common prefix, and the next predecessor cannot be worse than the guaranteed candidate. For rank zero, reset to zero because no predecessor exists. The common length decreases at most once per iteration; total increases are linear. Kasai therefore costs `O(n)` time and auxiliary space, with `lcp[0]=0`.

Suffixes sharing a prefix form a contiguous sorted interval. Hence every repeated substring is represented by an adjacent common prefix somewhere in that interval, and `max(lcp)` is the longest repeated-substring length. The first strictly longer candidate encountered in original-start order is retained; any optimal tie is allowed. Return just that one slice of the input. `banana` gives `ana`, with overlapping occurrences. Empty input gives empty arrays and string; a singleton gives `[0]`, `[0]`, and an empty string.

Overall auxiliary and output memory are `O(n+1)` and input memory is `O(n)`. Empty input takes constant time. Direct small suffix sorting, ties, distinct characters and 50,000-character repetitive inputs test the complete output, not only the longest repeat.

### Aho–Corasick

Insert patterns into a trie; retain one terminal index per original dictionary position. Duplicate strings share states but retain separate result columns. Each actual state has a packed `array('i')` of 95 transitions rather than 95 independent Python integer objects. Root index zero also represents initially missing edges.

Breadth-first construction sets failure links to the longest proper suffix represented by a trie state. Root children fail to root. For a child edge `(u,c)->v`, set `failure[v]=go[failure[u]][c]`; missing edges inherit `go[failure[u]][c]`. Shallower failure rows are completed first, so all fallback dependencies are available. There are no copied inherited output lists.

During a text scan, the state is the longest trie prefix that is a suffix of the consumed text. Increment its visit count once per character. In reverse breadth-first order, add each state's visits to its failure parent. Every suffix-pattern match lies on this failure chain, so propagation counts suffixes and overlaps without enumerating each individual occurrence. Read each dictionary terminal's total in original order, including duplicate columns.

Each text has a fresh visits list and starts at root. Every request builds a fresh automaton. An empty dictionary yields an empty row per text; no texts yields no rows; empty texts yield zero counts. `he,she,he` with two copies of `sheshe` and an empty text checks duplicates, suffix matches and reset.

Let `L` be total pattern length, `p` dictionary size, `S` actual states and `q` text count. Construction costs `O(L+95*S+p)` time and `O(95*S+p)` auxiliary space. Only actual states receive rows, so duplicates do not allocate unused rows. Per text, scanning, initialization, reverse propagation and extraction cost `O(|text|+S+p)`. Input takes `O(L+totalTextLength+p+q)` and output takes `O(q*(p+1)+1)` space. Counts are exact Python integers. Packed signed state indices fit because there are at most 100,001 states.

## Independent tests and actual results

The test driver uses seed **20261107**. Expected LCS values come from enumerating subsequences; merge optima come from enumerating legal adjacent-merge histories; tree optima come from subset enumeration; search/count results use independent `startswith` calls; small suffix outputs use direct suffix-string sorting and character-by-character LCP. These built-ins and deliberately slow methods occur only in verification code.

The supplied validator checks complete schemas and semantic witnesses. There are **12 named fixtures, 4,064 generated small cases repeated twice, and 20 domain-limit cases: 8,160 checked responses**. Binary texts through length 5 and patterns through length 3 are exhaustively paired for each search method. Mixed requests run in one persistent process to detect stale state. Actual fixture inputs, expected outputs and answers are retained in [fixture-results.json](tests/student/fixture-results.json).

|Command|Input / fixture|Expected|Actual result and defect checked|
|---|---|---|---|
|LCS|`tea_time` / `team`; `ab` / `ba`|4 and `team`; optimum 1|PASS: subsequence and alternative witness|
|LCS|either/both empty; 1000-character alternating strings|0; length 999|PASS: boundaries and maximum product|
|Merge|`[1,100,1]`; three billion-sized blocks|203; 5,000,000,000|PASS: adjacency, chronology, large cost|
|Merge|200 equal billion-sized blocks; 200 zeros|1,544,000,000,000; 0|PASS: 199 legal operations and maximum size|
|Tree|`[4,9,6]` chain; all-negative/zero/empty|10 with `[0,2]`; zero where appropriate|PASS: witness, ties and empty set|
|Tree|100,000-vertex positive chain and star|50,000,000,000,000; 99,999,000,000,000|PASS: no recursion failure, exact sums|
|Naive|`a b` / empty|`[0,1,2,3]`|PASS: final boundary|
|KMP|`abababa` / `aba`|`[0,2,4]`|PASS: overlapping fallback|
|RK|`abdj` / `ab`; `zab` / `ab`|`[0]`; `[1]`|PASS: collision verification and negative intermediate|
|All searches|empty text, overlong pattern, punctuation/case, maximum dense/empty-pattern inputs|Independent oracle/formula|PASS: contracts and full result lists|
|Suffix|`banana`|SA `[5,3,1,0,4,2]`, LCP `[0,1,3,0,0,2]`, `ana`|PASS: full order and overlapping repeat|
|Suffix|empty/single/distinct/tied; 50,000 equal/alternating chars|Exact SA/LCP; longest repeats 49,999 / 49,998|PASS: sentinel omission, Kasai and scale|
|Aho|`he,she,he`; `sheshe,sheshe,empty`|`[[2,2,2],[2,2,2],[0,0,0]]`|PASS: duplicate columns, suffixes, reset|
|Aho|10,000 copies of `a`; text length 200,000|200,000 per column|PASS: dense duplicate aggregation|
|Aho|`a^1` through `a^446`, text `a^200000`|`200001-length` per column|PASS: dense suffix matches|
|Aho|pattern length 100,000 and 100 short texts|100 zero rows|PASS: maximum depth and text count|
|Aho|10,000 patterns and 100 texts|1,000,000 values equal to 2000|PASS: maximum output dimensions|

For 200 equal merge blocks, the optimal full binary tree has leaf depths 7 and 8: `200*9-256=1544` units, giving an independent large-case cost oracle. Large repetitive suffix expectations are derived directly from suffix lengths and first-character groups. Tree expected sums follow chain/star structure.

All **44 public cases** and the repeated **88-request public batch** passed. All student checks passed. Logs: [public-results.txt](tests/student/public-results.txt), [test-results.txt](tests/student/test-results.txt), [setup-results.txt](tests/student/setup-results.txt). Each domain-limit batch finished within the launcher's 20-second timeout; the largest observed group time was 3.491 seconds for Aho, including process startup and transport but excluding oracle validation. These results do not assign an official grade or claim success on unseen tests.

## Reproducible search comparison

Run `python tests/student/benchmark.py`. It generates identical inputs for all three methods at `(n,m)=(750,187),(1500,375),(3000,750)`, within their common domain. Random inputs use `random.Random(20261108+n)` over uniformly selected `abcd` characters; the pattern is the slice starting at `n//3`, ensuring a match. Repetitive inputs use `a^n` / `a^m`; an extra near-miss family uses `a^n` / `a^(m-1)b`.

Every method is checked against a separate `startswith` oracle before timing. Each method/pair has three untimed warm-ups and three individually measured invocations. Method order rotates across rounds. `perf_counter_ns` measures the method call including preprocessing, comparisons and result allocation; input generation, validation, printing, interpreter startup and JSON transport are excluded. Results from timed calls are validated after stopping the timer. Normal garbage collection remains enabled. The tested CPython 3.12 runtime has no JIT warm-up; the untimed calls reduce first-use effects. The output variables retain results so the work is not discarded.

Units are **milliseconds per invocation**. Raw times and medians below come from the Python run and are also saved in [benchmark-results.md](tests/student/benchmark-results.md).

|Case|n|m|Seed|Algorithm|Run 1 (ms)|Run 2|Run 3|Median (ms)|Verified|
|---|---:|---:|---|---|---:|---:|---:|---:|---|
|random|750|187|20261858|naive|0.143800|0.142200|0.140900|0.142200|yes (1 starts)|
|random|750|187|20261858|kmp|0.170200|0.165600|0.166100|0.166100|yes (1 starts)|
|random|750|187|20261858|rk|0.287400|0.301500|0.285300|0.287400|yes (1 starts)|
|random|1500|375|20262608|naive|0.294200|0.500200|0.493200|0.493200|yes (1 starts)|
|random|1500|375|20262608|kmp|0.340700|0.340200|0.558400|0.340700|yes (1 starts)|
|random|1500|375|20262608|rk|0.580600|1.018600|1.046700|1.018600|yes (1 starts)|
|random|3000|750|20264108|naive|0.579200|0.578400|0.574100|0.578400|yes (1 starts)|
|random|3000|750|20264108|kmp|0.685600|0.661700|0.654800|0.661700|yes (1 starts)|
|random|3000|750|20264108|rk|1.167800|1.166100|1.179500|1.167800|yes (1 starts)|
|repetitive|750|187|n/a|naive|12.903800|13.428700|13.000600|13.000600|yes (564 starts)|
|repetitive|750|187|n/a|kmp|0.273100|0.253600|0.296100|0.273100|yes (564 starts)|
|repetitive|750|187|n/a|rk|14.406500|13.298600|13.002800|13.298600|yes (564 starts)|
|repetitive|1500|375|n/a|naive|57.063500|54.966100|55.524100|55.524100|yes (1126 starts)|
|repetitive|1500|375|n/a|kmp|0.569800|0.539300|0.530100|0.539300|yes (1126 starts)|
|repetitive|1500|375|n/a|rk|58.183300|55.679500|55.513600|55.679500|yes (1126 starts)|
|repetitive|3000|750|n/a|naive|266.497600|268.408000|262.158500|266.497600|yes (2251 starts)|
|repetitive|3000|750|n/a|kmp|2.286100|1.070000|1.776000|1.776000|yes (2251 starts)|
|repetitive|3000|750|n/a|rk|261.045700|261.787800|287.800700|261.787800|yes (2251 starts)|
|near-miss|750|187|n/a|naive|12.942500|15.028300|15.476600|15.028300|yes (0 starts)|
|near-miss|750|187|n/a|kmp|0.244800|0.235400|0.455400|0.244800|yes (0 starts)|
|near-miss|750|187|n/a|rk|0.281400|0.267000|0.277300|0.277300|yes (0 starts)|
|near-miss|1500|375|n/a|naive|56.355300|61.174400|67.085400|61.174400|yes (0 starts)|
|near-miss|1500|375|n/a|kmp|0.531400|0.513800|0.532500|0.531400|yes (0 starts)|
|near-miss|1500|375|n/a|rk|0.549300|0.512400|0.501300|0.512400|yes (0 starts)|
|near-miss|3000|750|n/a|naive|232.373400|247.929700|242.127800|242.127800|yes (0 starts)|
|near-miss|3000|750|n/a|kmp|1.078500|1.076200|1.069100|1.076200|yes (0 starts)|
|near-miss|3000|750|n/a|rk|1.082000|1.043300|1.048600|1.048600|yes (0 starts)|

Random inputs usually mismatch early, making naive search competitive despite its worst-case bound. On dense repetitive inputs every candidate is a real match: naive and exact RK compare the long pattern repeatedly, whereas KMP reuses the matched prefix and performs linear amortized work. For near misses, naive compares almost the whole pattern at every start; RK rejects these windows by their different hashes, while KMP uses prefix fallback.

The small modulus 101 admits many accidental hash candidates. Verification preserves exactness but adds comparison work, and dense genuine matches cannot be rejected by any hash. The results should not be generalized to every production rolling-hash design. Three observations per row are enough for the requested classroom comparison but remain sensitive to scheduling, allocation and interpreter overhead; empirical timings are not proofs of asymptotic complexity.

## Sources, AI assistance and verification

- [Course template](https://github.com/RZhaniya/daa-assignment-4-archive), including the JSON transport, launcher, validator, public cases, assignment specification and examples.
- Local [contracts](docs/guide/CONTRACTS.md), [rubric](docs/guide/RUBRIC.md), [testing requirements](docs/guide/TESTING.md) and [full specification](docs/Assignment_4_EN.md) define the required algorithms and interfaces.
- This Python project was prepared with OpenAI Codex assistance and follows the same algorithm designs as the Java solution prepared earlier in this workspace. The student test suite was reused and adapted to launch Python; its expected-value oracles remain independent of both submitted implementations. This is not represented as independently authored work by a different person.
- Codex wrote/adapted the Python implementations, test and benchmark drivers, and this analysis, and executed the reported local checks and measurements. No third-party algorithm implementation was imported. Verification includes independent small oracles, semantic witness checks, collisions and boundary cases, persistent mixed requests and full-domain stress cases.
- The student's own manual review and defence preparation are not claimed to have happened. Review the implementation and report before submission; the assessed defence is individual and must be taken without AI assistance.

## Submission status

Local files, tests and evidence are prepared. No personal GitHub repository, pushed submission commit, hosted Actions result or Moodle submission is claimed. Publish to the student's own repository and submit the exact commit URL as required by the course.
