#!/usr/bin/env python3
"""Tiny HTTP app for CAP-2931: POST /run {"delay": N} sleeps N seconds, then answers.
Stdlib only, so it runs anywhere python3 does. Logs every request with its timing."""
import json, os, sys, time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

class H(BaseHTTPRequestHandler):
    def _reply(self, code, body):
        data = json.dumps(body).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):  # health probes (/, /healthz, /dapr/config)
        self._reply(200, {"ok": True})

    def do_POST(self):
        n = int(self.headers.get("Content-Length") or 0)
        try:
            delay = float(json.loads(self.rfile.read(n) or b"{}").get("delay", 0))
        except Exception:
            delay = 0
        t0 = time.time()
        time.sleep(delay)
        self._reply(200, {"slept": delay, "answer": "order 42 shipped"})
        print(f"[app] {self.path} delay={delay}s answered 200 after {time.time()-t0:.1f}s", flush=True)

    def log_message(self, *a):
        pass

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8765"))
    print(f"[app] listening on :{port}", flush=True)
    ThreadingHTTPServer(("0.0.0.0", port), H).serve_forever()
