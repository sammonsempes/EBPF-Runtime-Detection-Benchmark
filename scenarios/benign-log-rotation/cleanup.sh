#!/bin/sh
set -u
marker="${BENCH_MARKER:-manual}"

rm -rf "/var/log/benchapp-$marker" "/tmp/bench-logrotate-$marker"
exit 0
