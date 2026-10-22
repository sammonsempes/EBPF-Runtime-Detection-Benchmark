#!/bin/sh
set -u
marker="${BENCH_MARKER:-manual}"
work="/tmp/bench-$marker"

if [ -r "$work/server.pid" ]; then
    server_pid=$(cat "$work/server.pid")
    if [ -n "$server_pid" ] && grep -q 'http.server' "/proc/$server_pid/cmdline" 2>/dev/null; then
        kill "$server_pid" 2>/dev/null
    fi
fi
rm -rf "/tmp/bench-site-$marker" "$work"
exit 0
