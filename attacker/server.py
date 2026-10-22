import json
import logging
import socket
import socketserver
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HTTP_PORT = 8080
REVERSE_SHELL_PORT = 4444
STRATUM_PORT = 3333
SESSION_TIMEOUT_SECONDS = 10
MAX_UPLOAD_CHUNK = 65536

PAYLOAD_SCRIPT = b"""#!/bin/sh
echo "bench payload executed as $(id -un) on $(hostname)"
uname -a
exit 0
"""

REVERSE_SHELL_COMMANDS = b"id\nuname -a\nhostname\necho bench-reverse-shell-done\nexit\n"

log = logging.getLogger("attacker")


class PayloadHandler(BaseHTTPRequestHandler):
    server_version = "bench-attacker/1.0"

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/x-shellscript")
        self.send_header("Content-Length", str(len(PAYLOAD_SCRIPT)))
        self.end_headers()
        self.wfile.write(PAYLOAD_SCRIPT)

    def do_POST(self):
        remaining = int(self.headers.get("Content-Length") or 0)
        received = 0
        while remaining > 0:
            chunk = self.rfile.read(min(remaining, MAX_UPLOAD_CHUNK))
            if not chunk:
                break
            received += len(chunk)
            remaining -= len(chunk)
        body = json.dumps({"received_bytes": received, "path": self.path}).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        log.info("http %s %s", self.client_address[0], format % args)


class ReverseShellSink(socketserver.BaseRequestHandler):
    def handle(self):
        self.request.settimeout(SESSION_TIMEOUT_SECONDS)
        log.info("reverse shell connected from %s", self.client_address[0])
        received = 0
        try:
            self.request.sendall(REVERSE_SHELL_COMMANDS)
            while chunk := self.request.recv(4096):
                received += len(chunk)
        except (socket.timeout, ConnectionError):
            pass
        log.info("reverse shell from %s closed after %d bytes", self.client_address[0], received)


class StratumSink(socketserver.StreamRequestHandler):
    def setup(self):
        super().setup()
        self.connection.settimeout(SESSION_TIMEOUT_SECONDS)

    def handle(self):
        log.info("stratum client connected from %s", self.client_address[0])
        try:
            for line in self.rfile:
                reply = self.reply_to(line)
                if reply is None:
                    break
                self.wfile.write(json.dumps(reply).encode() + b"\n")
                self.wfile.flush()
        except (socket.timeout, ConnectionError):
            pass
        log.info("stratum client %s disconnected", self.client_address[0])

    @staticmethod
    def reply_to(line):
        try:
            request = json.loads(line)
        except ValueError:
            return None
        request_id = request.get("id")
        if request.get("method") == "login":
            job = {"blob": "0" * 152, "job_id": "bench-job-1", "target": "ffffff00", "algo": "rx/0"}
            result = {"id": "bench-session", "job": job, "status": "OK"}
        else:
            result = {"status": "OK"}
        return {"id": request_id, "jsonrpc": "2.0", "error": None, "result": result}


class ThreadingTCPServer(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True


def serve_in_background(server):
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return thread


def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
    ThreadingHTTPServer.allow_reuse_address = True
    ThreadingHTTPServer.daemon_threads = True
    servers = [
        ThreadingHTTPServer(("0.0.0.0", HTTP_PORT), PayloadHandler),
        ThreadingTCPServer(("0.0.0.0", REVERSE_SHELL_PORT), ReverseShellSink),
        ThreadingTCPServer(("0.0.0.0", STRATUM_PORT), StratumSink),
    ]
    threads = [serve_in_background(server) for server in servers]
    log.info("attacker listening on %d (http), %d (reverse shell), %d (stratum)", HTTP_PORT, REVERSE_SHELL_PORT, STRATUM_PORT)
    for thread in threads:
        thread.join()


if __name__ == "__main__":
    main()
