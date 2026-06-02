from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import urlopen


BASE_URL = "https://www.gutenberg.org/cache/epub/{book_id}/pg{book_id}.txt"
BOOKS_DIR = Path(__file__).resolve().parents[1] / "data" / "books"
TIMEOUT_SECONDS = 15


class GutenbergError(Exception):
    """Raised when a Project Gutenberg book cannot be retrieved."""


def build_book_url(book_id: int | str) -> str:
    """Build the Project Gutenberg text URL for a book ID."""
    normalized_id = _normalize_book_id(book_id)
    return BASE_URL.format(book_id=normalized_id)


def get_book_path(book_id: int | str) -> Path:
    """Return the local path where a book text file is stored."""
    normalized_id = _normalize_book_id(book_id)
    return BOOKS_DIR / f"{normalized_id}.txt"


def download_book(book_id: int | str, force: bool = False) -> Path:
    """Download a Gutenberg book text file and return its local path."""
    normalized_id = _normalize_book_id(book_id)
    book_path = get_book_path(normalized_id)

    if book_path.exists() and not force:
        return book_path

    BOOKS_DIR.mkdir(parents=True, exist_ok=True)
    url = build_book_url(normalized_id)

    try:
        with urlopen(url, timeout=TIMEOUT_SECONDS) as response:
            raw_content = response.read()
    except HTTPError as error:
        raise GutenbergError(
            f"book {normalized_id} was not found on Project Gutenberg"
        ) from error
    except URLError as error:
        raise GutenbergError(
            f"could not reach Project Gutenberg to download book {normalized_id}"
        ) from error

    text = raw_content.decode("utf-8", errors="replace")
    book_path.write_text(text, encoding="utf-8")
    return book_path


def load_book(book_id: int | str, download_if_missing: bool = True) -> str:
    """Load a book text from disk, downloading it first if needed."""
    book_path = get_book_path(book_id)

    if not book_path.exists():
        if not download_if_missing:
            raise GutenbergError(f"book {book_id} is not available locally")
        book_path = download_book(book_id)

    return book_path.read_text(encoding="utf-8")


def _normalize_book_id(book_id: int | str) -> str:
    normalized_id = str(book_id).strip()

    if not normalized_id.isdigit():
        raise ValueError("book id must be a positive integer")

    if int(normalized_id) <= 0:
        raise ValueError("book id must be a positive integer")

    return normalized_id
