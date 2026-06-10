import json
from pathlib import Path
from typing import Any


CACHE_DIR = Path(__file__).resolve().parents[1] / "data" / "cache"


class CacheError(Exception):
    """Raised when cached data cannot be read or written."""


def get_cache_path(cache_key: str) -> Path:
    safe_key = _sanitize_cache_key(cache_key)
    return CACHE_DIR / f"{safe_key}.json"


def load_cache(cache_key: str) -> Any | None:
    cache_path = get_cache_path(cache_key)

    if not cache_path.exists():
        return None

    try:
        return json.loads(cache_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise CacheError(f"invalid cache file: {cache_path}") from error


def save_cache(cache_key: str, data: Any) -> Path:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache_path = get_cache_path(cache_key)

    try:
        cache_path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    except OSError as error:
        raise CacheError(f"could not write cache file: {cache_path}") from error

    return cache_path


def _sanitize_cache_key(cache_key: str) -> str:
    return "".join(
        character if character.isalnum() or character in {"-", "_"} else "_"
        for character in cache_key.strip()
    )
