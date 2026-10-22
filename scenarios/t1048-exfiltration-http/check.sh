#!/bin/sh
set -u
marker="${BENCH_MARKER:-manual}"

grep -qE '"received_bytes": [1-9]' "/tmp/bench-$marker/upload.response" 2>/dev/null || exit 1
exit 0
