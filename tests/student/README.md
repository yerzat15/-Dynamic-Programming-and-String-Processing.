# Student tests — Python

Run `python tests/student/test_solution.py` from the repository root. It uses only the standard library and the supplied JSON Lines launcher/validator.

The suite verifies 12 named fixtures, 4,064 independent small cases twice in a persistent mixed-request process, and 20 domain-limit cases: **8,160 checked responses**. Random seed: 20261107. Each execution batch has the supplied 20-second timeout. Expected values come from exhaustive small oracles, independent built-in string operations in tests, and closed-form large-case expectations. The submitted algorithms do not use built-in substring search.

|File|Purpose|
|---|---|
|`fixtures.json`|Named inputs and expected results|
|`fixture-results.json`|Actual Python answers and semantic pass flags|
|`test-results.txt`|Actual student test run|
|`public-results.txt`|44 public tests and repeated batch|
|`setup-results.txt`|Startup check|
|`benchmark.py`|Three search methods, three sizes, random/repetitive/near-miss cases|
|`benchmark-results.md`|Three raw measurements per case/method and median|
|`environment.py`, `environment.txt`|Runtime and hardware evidence|

`python tests/student/benchmark.py` regenerates the benchmark table. It checks correctness before timing, uses three untimed warm-ups and three measured invocations, rotates method order, and excludes JSON/process startup. Timing units are milliseconds per invocation. Update the table and observations in `ANALYSIS.md` if rerunning measurements.

To capture fresh test logs in PowerShell:

```powershell
python tools/run.py --setup 2>&1 | Tee-Object tests/student/setup-results.txt
python tools/run.py --check 2>&1 | Tee-Object tests/student/public-results.txt
python tests/student/test_solution.py 2>&1 | Tee-Object tests/student/test-results.txt
```

Check the exit code as well as the log. No test driver or benchmark is imported by the submitted entry point.
