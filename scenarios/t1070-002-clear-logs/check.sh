#!/bin/sh
set -u
marker="${BENCH_MARKER:-manual}"

marker_log="/var/log/bench-$marker.log"

[ -s "/tmp/bench-$marker/logs/_var_log_bench-$marker.log" ] || exit 1
[ -f "$marker_log" ] || exit 1
[ ! -s "$marker_log" ] || exit 1
exit 0
