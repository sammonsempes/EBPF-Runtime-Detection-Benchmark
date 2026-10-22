#!/bin/sh
set -u
marker="${BENCH_MARKER:-manual}"
work="/tmp/bench-$marker"

history_file=/root/.bash_history

if [ -f "$work/bash_history" ]; then
    rm -f "$history_file"
    cp -p "$work/bash_history" "$history_file"
elif [ -f "$work/history.created" ]; then
    rm -f "$history_file"
fi
rm -rf "$work"
exit 0
