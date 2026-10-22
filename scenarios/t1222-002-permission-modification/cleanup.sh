#!/bin/sh
set -u
marker="${BENCH_MARKER:-manual}"
work="/tmp/bench-$marker"

mode_file="$work/shadow.mode"

if [ -s "$mode_file" ]; then
    chmod "$(cat "$mode_file")" /etc/shadow
fi
rm -rf "$work"
exit 0
