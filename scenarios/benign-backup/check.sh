#!/bin/sh
set -u
marker="${BENCH_MARKER:-manual}"
archive="/backup/data-$marker.tar.gz"

[ -s "$archive" ] || exit 1
tar -tzf "$archive" 2>/dev/null | grep -qF "bench-data-$marker/reports/report-10.txt" || exit 1
exit 0
