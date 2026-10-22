#!/bin/sh
set -u
marker="${BENCH_MARKER:-manual}"
work="/tmp/bench-$marker"

port=18080
site_dir="/tmp/bench-site-$marker"

sh "$(dirname "$0")/cleanup.sh"
mkdir -p "$site_dir" "$work" || exit 1
printf '<html><body>bench %s</body></html>\n' "$marker" > "$site_dir/index.html"

echo "BENCH_ACTION $(date +%s.%N)"
python3 -m http.server "$port" --bind 127.0.0.1 --directory "$site_dir" > /dev/null 2>&1 &
server_pid=$!
echo "$server_pid" > "$work/server.pid"

attempt=0
until curl -fsS --max-time 2 -o /dev/null "http://127.0.0.1:$port/"; do
    attempt=$((attempt + 1))
    [ "$attempt" -ge 50 ] && exit 1
    sleep 0.2
done

curl -fsS --max-time 5 -o "$work/index.html" "http://127.0.0.1:$port/index.html" || exit 1
kill "$server_pid" 2>/dev/null
wait "$server_pid" 2>/dev/null
grep -F "bench $marker" "$work/index.html"
