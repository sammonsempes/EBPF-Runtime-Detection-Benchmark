#!/bin/sh
set -u
marker="${BENCH_MARKER:-manual}"

grep -qxF "bench-python-exec-$marker" "/tmp/bench-$marker/python-exec.proof" 2>/dev/null || exit 1
exit 0
