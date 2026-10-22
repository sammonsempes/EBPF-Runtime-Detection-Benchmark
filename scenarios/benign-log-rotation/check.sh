#!/bin/sh
set -u
marker="${BENCH_MARKER:-manual}"
log_dir="/var/log/benchapp-$marker"

[ -f "$log_dir/app.log" ] || exit 1
gzip -t "$log_dir/app.log.1.gz" "$log_dir/worker.log.1.gz" 2>/dev/null || exit 1
exit 0
