#!/bin/sh
set -u
marker="${BENCH_MARKER:-manual}"

discovery_output="/tmp/bench-$marker/discovery.txt"

grep -qE '^[0-9]+:[^:]*:/' "$discovery_output" 2>/dev/null || exit 1
grep -q '^CapEff:' "$discovery_output" || exit 1
exit 0
