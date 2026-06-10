from modules.entities import extract_entities
from modules.lexdiv import compute_lexdiv
from modules.similar import find_similar_books, load_book_collection
from modules.summarize import summarize_book
from modules.topics import extract_topics_for_book
from utils.cache import load_cache, save_cache
from utils.gutenberg import load_book


UNKNOWN_VALUE = "unknown"


def build_book_card(book_id: int | str, use_cache: bool = True) -> dict:
    normalized_id = str(book_id)
    cache_key = f"card_{normalized_id}"

    if use_cache:
        cached_card = load_cache(cache_key)
        if cached_card is not None:
            return cached_card

    text = load_book(normalized_id)
    card = {
        "info": get_book_info(normalized_id),
        "lexdiv": compute_lexdiv(text),
        "topics": extract_topics_for_book(normalized_id),
        "entities": extract_entities(text),
        "summary": summarize_book(normalized_id),
        "similar": find_similar_books(normalized_id),
    }

    if use_cache:
        save_cache(cache_key, card)

    return card


def get_book_info(book_id: int | str) -> dict:
    normalized_id = str(book_id)
    collection = load_book_collection()

    for book in collection:
        if str(book["id"]) == normalized_id:
            return {
                "id": normalized_id,
                "authors": book.get("author", UNKNOWN_VALUE),
                "bookshelves": book.get("category", UNKNOWN_VALUE),
            }

    return {
        "id": normalized_id,
        "authors": UNKNOWN_VALUE,
        "bookshelves": UNKNOWN_VALUE,
    }
