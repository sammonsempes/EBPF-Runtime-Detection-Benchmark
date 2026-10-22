#!/bin/sh
set -u
marker="${BENCH_MARKER:-manual}"

rm -f "/etc/cron.d/bench-$marker"
exit 0
