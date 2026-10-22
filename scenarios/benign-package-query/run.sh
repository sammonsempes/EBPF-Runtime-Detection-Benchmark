#!/bin/sh
set -u
marker="${BENCH_MARKER:-manual}"
work="/tmp/bench-$marker"

sh "$(dirname "$0")/cleanup.sh"
mkdir -p "$work" || exit 1

echo "BENCH_ACTION $(date +%s.%N)"
dpkg -l > "$work/dpkg-list.out" || exit 1
dpkg -s coreutils > "$work/dpkg-status.out" || exit 1
dpkg -L bash > "$work/dpkg-files.out"
apt-cache policy bash python3 > "$work/apt-policy.out" || exit 1
head -n 20 "$work/dpkg-list.out"
cat "$work/apt-policy.out"
