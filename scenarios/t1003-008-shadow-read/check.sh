#!/bin/sh
set -u
marker="${BENCH_MARKER:-manual}"

grep -q '^root:' "/tmp/bench-shadow-$marker" 2>/dev/null || exit 1
exit 0
