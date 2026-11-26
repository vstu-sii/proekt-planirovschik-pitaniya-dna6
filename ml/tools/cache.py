"""SQLite TTL cache. Key includes model and prompt version; no credentials in key."""
from __future__ import annotations
import hashlib, json, sqlite3, time
from pathlib import Path
from typing import Any

class ResponseCache:
    def __init__(self, path: str | Path = "artifacts/llm_cache.sqlite3", ttl_sec: int = 86400):
        self.path = str(path); self.ttl_sec = max(0, int(ttl_sec))
        Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.path) as db:
            db.execute("CREATE TABLE IF NOT EXISTS cache (key TEXT PRIMARY KEY, value TEXT NOT NULL, created REAL NOT NULL)")

    @staticmethod
    def key(request: dict[str, Any], *, model: str, prompt_version: str) -> str:
        payload = json.dumps({"request": request, "model": model, "prompt_version": prompt_version},
                             ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def get(self, key: str) -> Any | None:
        now = time.time()
        with sqlite3.connect(self.path) as db:
            row = db.execute("SELECT value, created FROM cache WHERE key=?", (key,)).fetchone()
            if not row: return None
            if now - row[1] > self.ttl_sec:
                db.execute("DELETE FROM cache WHERE key=?", (key,)); return None
            return json.loads(row[0])

    def set(self, key: str, value: Any) -> None:
        raw = json.dumps(value, ensure_ascii=False, sort_keys=True)
        with sqlite3.connect(self.path) as db:
            db.execute("INSERT OR REPLACE INTO cache(key,value,created) VALUES(?,?,?)", (key, raw, time.time()))
