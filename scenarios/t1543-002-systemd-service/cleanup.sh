#!/bin/sh
set -u
marker="${BENCH_MARKER:-manual}"

rm -f "/etc/systemd/system/multi-user.target.wants/bench-$marker.service" "/etc/systemd/system/bench-$marker.service"
exit 0
