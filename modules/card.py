from modules.entities import extract_entities
from modules.lexdiv import compute_lexical_diversity
from modules.similar import find_similar_books, get_book_info
from modules.summarize import summarize_book
from modules.topics import extract_topics
from services.cache import load_cache, save_cache


def build_book_card(book_id: int | str, use_cache: bool = True) -> dict:
    cached = load_cache("card_v4", book_id) if use_cache else None
    if cached is not None:
        cached["topics"] = {int(section): words for section, words in cached["topics"].items()}
        return cached

    card = {
        "info": get_book_info(book_id),
        "lexdiv": compute_lexical_diversity(book_id, use_cache=use_cache),
        "topics": extract_topics(book_id, use_cache=use_cache),
        "entities": extract_entities(book_id, use_cache=use_cache),
        "summary": summarize_book(book_id, use_cache=use_cache),
        "similar": find_similar_books(book_id, use_cache=use_cache),
    }
    return save_cache("card_v4", book_id, card) if use_cache else card
