# Erz — Assignment 4, Python solution

Complete implementations of `lcs`, `merge`, `tree`, `naive`, `kmp`, `rk`, `suffix` and `aho` in Python 3.12+, using only the standard library.

- [Algorithms](Python/source/algorithms.py)
- [English analysis and measured search comparison](ANALYSIS.md)
- [Tests and evidence](tests/student/README.md)
- [Assignment](docs/Assignment_4_EN.md) / [Russian version](docs/Assignment_4_RU.md)
- [Contracts](docs/guide/CONTRACTS.md) / [Rubric](docs/guide/RUBRIC.md)

## Run

From the `Erz` directory:

```sh
python tools/run.py --setup
python tools/run.py --check
python tools/run.py --input examples/lcs.jsonl
python tests/student/test_solution.py
python tests/student/benchmark.py
```

`submission.json` selects Python. There are no external dependencies and no Java requirement. Direct execution is also supported:

```sh
python Python/source/main.py
```

Enter one JSON request per line, for example:

```json
{"task":"lcs","a":"tea_time","b":"team"}
```

The result is `{"length":4,"sequence":"team"}`. Multiple requests can share one process. Only result JSON is written to standard output.

On the current Windows machine the working interpreter can be selected explicitly:

```powershell
$erzPython = 'C:/Users/rusla/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
& $erzPython tools/run.py --check
& $erzPython tests/student/test_solution.py
& $erzPython tests/student/benchmark.py
```

## Verification and submission

All 44 public cases, the repeated public batch and 8,160 student-test responses passed locally. Logs, named fixtures and actual Python benchmark results are included under `tests/student`. The GitHub workflow runs Python setup, public checks and student tests.

This is a separate Python project; the Java project in `Ass4` remains unchanged. No Git history or remote is copied into this folder. For submission, put these files in your personal repository created from the assignment template, commit and push, verify Actions, and submit the exact commit URL with the full 40-character SHA and language Python in Moodle. Uploading a ZIP is not the specified submission method. Publication and Moodle submission have not been performed.

AI assistance and the shared provenance with the Java version are disclosed in `ANALYSIS.md`. Review the work before submission and prepare independently for the defence.
