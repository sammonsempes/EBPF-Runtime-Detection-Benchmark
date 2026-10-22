#!/bin/sh
set -u
marker="${BENCH_MARKER:-manual}"
work="/tmp/bench-$marker"

grep -qE '^ii +coreutils ' "$work/dpkg-list.out" 2>/dev/null || exit 1
grep -q '^Status: install ok installed' "$work/dpkg-status.out" 2>/dev/null || exit 1
grep -q 'bin/bash$' "$work/dpkg-files.out" 2>/dev/null || exit 1
grep -q '^bash:' "$work/apt-policy.out" 2>/dev/null || exit 1
exit 0
