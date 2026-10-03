"""Minimal client for TypeSafe-compatible decision servers (POST /v1/systemone).

Kev, Imajev, JevK5, Decision 2.0 and most open decision models serve this wire format. We never call TypeSafe's
own endpoint (see docs/decisions.md, D4).
"""
from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from typing import Any


class DecisionClient:
    def __init__(self, base_url: str, model: str = "default", api_key: str | None = None, timeout: float = 300.0, retries: int = 3):
        self.url = base_url.rstrip("/") + "/v1/systemone"
        self.model = model
        self.api_key = api_key if api_key is not None else os.environ.get("BZAF_API_KEY")
        self.timeout = timeout
        self.retries = retries

    def decide(self, state: Any, questions: dict[str, dict]) -> dict:
        """Send one request; return the response body ({"answers": {...}, ...})."""
        body = json.dumps({"state": state, "model": self.model, "questions": questions}).encode()
        headers = {"content-type": "application/json"}
        if self.api_key:
            headers["authorization"] = f"Bearer {self.api_key}"
        for attempt in range(self.retries + 1):
            try:
                req = urllib.request.Request(self.url, data=body, headers=headers, method="POST")
                with urllib.request.urlopen(req, timeout=self.timeout) as r:
                    return json.loads(r.read())
            except urllib.error.HTTPError as e:
                if e.code < 500 or attempt == self.retries:  # 4xx (e.g. 422 too long) will not fix itself
                    raise RuntimeError(f"HTTP {e.code}: {e.read()[:500]!r}") from e
            except (urllib.error.URLError, TimeoutError, ConnectionError):
                if attempt == self.retries:
                    raise
            time.sleep(2 ** attempt)
        raise AssertionError("unreachable")
