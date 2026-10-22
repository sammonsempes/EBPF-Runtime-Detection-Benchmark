#!/bin/sh
set -u
marker="${BENCH_MARKER:-manual}"

unit_file="/etc/systemd/system/bench-$marker.service"
wants_link="/etc/systemd/system/multi-user.target.wants/bench-$marker.service"

grep -qxF "Description=bench persistence $marker" "$unit_file" 2>/dev/null || exit 1
[ -L "$wants_link" ] || exit 1
exit 0
