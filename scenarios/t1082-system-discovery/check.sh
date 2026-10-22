#!/bin/sh
set -u
marker="${BENCH_MARKER:-manual}"

discovery_output="/tmp/bench-$marker/discovery.txt"

grep -q '^Linux ' "$discovery_output" 2>/dev/null || exit 1
grep -q '^hostname: .' "$discovery_output" || exit 1
grep -q '^1 ' "$discovery_output" || exit 1
exit 0
