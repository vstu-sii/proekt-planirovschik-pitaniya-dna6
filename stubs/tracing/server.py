import json
import os
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

trace_path = Path(os.getenv("TRACE_PATH", "/data/traces.jsonl"))
trace_path.parent.mkdir(parents=True, exist_ok=True)
lock = threading.Lock()


class Handler(BaseHTTPRequestHandler):
    def send_json(self, status: int, payload: dict | list) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802
        if self.path == "/health":
            self.send_json(200, {"status": "ok"})
            return
        if self.path == "/traces":
            lines = trace_path.read_text(encoding="utf-8").splitlines() if trace_path.exists() else []
            self.send_json(200, [json.loads(line) for line in lines[-100:]])
            return
        self.send_json(404, {"error": "not_found"})

    def do_POST(self) -> None:  # noqa: N802
        if self.path != "/v1/traces":
            self.send_json(404, {"error": "not_found"})
            return
        length = int(self.headers.get("Content-Length", "0"))
        event = json.loads(self.rfile.read(length) or b"{}")
        with lock, trace_path.open("a", encoding="utf-8") as file:
            file.write(json.dumps(event, ensure_ascii=False) + "\n")
        self.send_json(202, {"accepted": True})

    def log_message(self, format: str, *args: object) -> None:
        return


ThreadingHTTPServer(("0.0.0.0", 9411), Handler).serve_forever()
