#!/bin/sh
set -u
marker="${BENCH_MARKER:-manual}"

grep -qF "bench $marker" "/tmp/bench-$marker/index.html" 2>/dev/null || exit 1
exit 0
