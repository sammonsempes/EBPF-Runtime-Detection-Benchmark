#!/bin/sh
set -u
marker="${BENCH_MARKER:-manual}"

grep -qE 'succeeded|open' "/tmp/bench-$marker/scan.log" 2>/dev/null || exit 1
exit 0
