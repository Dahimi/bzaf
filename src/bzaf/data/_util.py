from __future__ import annotations

import os
import random
import shutil
import urllib.request
from pathlib import Path

CACHE = Path(os.environ.get("BZAF_RAW", "data/raw"))  # on Modal: a volume, so large files download once


def fetch(url: str, name: str, cache: Path | None = None) -> Path:
    """Download `url` once into <cache>/<name> (streamed, so large files do not sit in memory) and return the path."""
    path = (cache or CACHE) / name
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(path.suffix + ".part")
        with urllib.request.urlopen(url, timeout=300) as r, tmp.open("wb") as f:
            shutil.copyfileobj(r, f, 1 << 20)
        tmp.rename(path)
    return path


def sample(items: list, limit: int | None, seed: int) -> list:
    """A fixed random subset (order preserved), so every model sees the same items."""
    if limit is None or limit >= len(items):
        return items
    keep = set(random.Random(seed).sample(range(len(items)), limit))
    return [x for i, x in enumerate(items) if i in keep]
