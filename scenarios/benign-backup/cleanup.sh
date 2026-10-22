#!/bin/sh
set -u
marker="${BENCH_MARKER:-manual}"

rm -rf "/srv/bench-data-$marker"
rm -f "/backup/data-$marker.tar.gz"
exit 0
