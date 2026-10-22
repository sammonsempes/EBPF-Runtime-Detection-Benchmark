#!/bin/sh
set -u
marker="${BENCH_MARKER:-manual}"
work="/tmp/bench-$marker"

hidden_dir="/tmp/.X11-$marker"
fake_sshd="$hidden_dir/sshd"

sh "$(dirname "$0")/cleanup.sh"
mkdir -p "$work" || exit 1

echo "BENCH_ACTION $(date +%s.%N)"
mkdir -p "$hidden_dir" || exit 1
cp /usr/bin/sleep "$fake_sshd" || exit 1
"$fake_sshd" 2 || exit 1
: > "$work/sshd.ran"
echo "ran $fake_sshd"
