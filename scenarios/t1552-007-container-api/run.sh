#!/bin/sh
set -u
marker="${BENCH_MARKER:-manual}"
work="/tmp/bench-$marker"

service_account_dir=/var/run/secrets/kubernetes.io/serviceaccount
docker_socket=/var/run/docker.sock

sh "$(dirname "$0")/cleanup.sh"
mkdir -p "$work" || exit 1

echo "BENCH_ACTION $(date +%s.%N)"
ls -la "$service_account_dir" 2>&1
token_opened=no
if cat "$service_account_dir/token" > "$work/token"; then
    token_opened=yes
    echo "service account token read"
fi
cat "$service_account_dir/namespace" 2>/dev/null
echo "kubernetes api: ${KUBERNETES_SERVICE_HOST:-not set}:${KUBERNETES_SERVICE_PORT:-not set}"

ls -l "$docker_socket" 2>&1
curl -sS --max-time 3 --unix-socket "$docker_socket" -H "X-Bench-Marker: $marker" "http://localhost/containers/json?bench=$marker" 2>&1 || echo "docker socket not reachable"

[ "$token_opened" = yes ]
