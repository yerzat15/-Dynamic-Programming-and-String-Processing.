# Python search benchmark

Runtime: CPython 3.12.14; OS: Windows-11-10.0.26200-SP0.
Unit: milliseconds per invocation, measured using perf_counter_ns.
Each method/case: 3 untimed warm-ups, then 3 separately timed invocations. Normal GC enabled; no JIT configuration.
Timing includes preprocessing, comparisons and result allocation, excluding input generation, oracle, startup and JSON.
Every result is independently checked before timing; measured results are checked after timing.
Random: random.Random(20261108+n), uniform abcd; pattern=text[n//3:n//3+m].
Repetitive: a^n / a^m. Near-miss: a^n / a^(m-1)b.

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
