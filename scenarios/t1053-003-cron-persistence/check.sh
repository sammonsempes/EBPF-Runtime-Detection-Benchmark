#!/bin/sh
set -u
marker="${BENCH_MARKER:-manual}"

grep -qF "bench-cron-$marker" "/etc/cron.d/bench-$marker" 2>/dev/null || exit 1
exit 0
