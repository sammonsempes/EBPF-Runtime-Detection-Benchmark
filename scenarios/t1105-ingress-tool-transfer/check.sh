#!/bin/sh
set -u
marker="${BENCH_MARKER:-manual}"

grep -q '^bench payload executed as ' "/tmp/bench-$marker/payload.out" 2>/dev/null || exit 1
exit 0
