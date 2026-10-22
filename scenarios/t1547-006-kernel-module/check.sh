#!/bin/sh
set -u
marker="${BENCH_MARKER:-manual}"
work="/tmp/bench-$marker"

[ -f "$work/insmod.status" ] || exit 1
[ "$(cat "$work/insmod.status")" = 0 ] && exit 0
grep -q 'could not insert module' "$work/insmod.out" 2>/dev/null || exit 1
grep -q 'Operation not permitted' "$work/insmod.out" && exit 1
exit 0
