#!/bin/sh
set -u
marker="${BENCH_MARKER:-manual}"
work="/tmp/bench-$marker"

suid_binary="/tmp/bench-suid-$marker"

sh "$(dirname "$0")/cleanup.sh"
mkdir -p "$work" || exit 1

echo "BENCH_ACTION $(date +%s.%N)"
cp /usr/bin/id "$suid_binary" || exit 1
chmod u+s "$suid_binary" || exit 1
[ -u "$suid_binary" ] || exit 1
ls -l "$suid_binary"
setpriv --reuid=65534 --regid=65534 --clear-groups "$suid_binary" > "$work/suid.out" || true
cat "$work/suid.out"
