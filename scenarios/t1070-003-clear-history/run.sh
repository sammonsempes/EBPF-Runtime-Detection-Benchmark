#!/bin/sh
set -u
marker="${BENCH_MARKER:-manual}"
work="/tmp/bench-$marker"

history_file=/root/.bash_history
backup="$work/bash_history"

sh "$(dirname "$0")/cleanup.sh"
mkdir -p "$work" || exit 1
if [ -f "$history_file" ] && [ ! -L "$history_file" ]; then
    cp -p "$history_file" "$backup" || exit 1
else
    : > "$work/history.created"
    printf 'echo bench-%s\n' "$marker" > "$history_file"
fi

echo "BENCH_ACTION $(date +%s.%N)"
HISTFILE="$history_file" bash -c 'history -c; history -w' "bench-clear-history-$marker"
truncate -s 0 "$history_file" || exit 1
rm -f "$history_file" || exit 1
ln -s /dev/null "$history_file" || exit 1
ls -l "$history_file"
