import json
from pathlib import Path
from typing import Any


CACHE_DIR = Path(__file__).resolve().parents[1] / "data" / "cache"


def get_cache_path(namespace: str, book_id: int | str) -> Path:
    safe_namespace = "".join(
        char for char in namespace.lower() if char.isalnum() or char in "-_"
    )
    return CACHE_DIR / f"{safe_namespace}_{book_id}.json"


def load_cache(namespace: str, book_id: int | str) -> Any | None:
    path = get_cache_path(namespace, book_id)

    if not path.exists():
        return None

    try:
        with path.open("r", encoding="utf-8") as file:
            return json.load(file)
    except json.JSONDecodeError:
        return None


def save_cache(namespace: str, book_id: int | str, data: Any) -> Any:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    path = get_cache_path(namespace, book_id)

    with path.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=2, ensure_ascii=False)

    return data
