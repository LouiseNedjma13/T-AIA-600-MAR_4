from collections import Counter

from services.cache import load_cache, save_cache
from services.gutenberg import load_book
from utils.text_processing import tokenize


def compute_lexical_diversity(book_id: int | str, use_cache: bool = True) -> dict:
    cached = load_cache("lexdiv", book_id) if use_cache else None
    if cached is not None:
        return cached

    text = load_book(book_id)
    tokens = tokenize(text)
    frequencies = Counter(tokens)

    token_count = len(tokens)
    type_count = len(frequencies)
    hapax_count = sum(1 for count in frequencies.values() if count == 1)
    mean_word_length = (
        sum(len(token) for token in tokens) / token_count if token_count else 0.0
    )

    result = {
        "tok": token_count,
        "typ": type_count,
        "hap": hapax_count,
        "ttr": round(type_count / token_count, 4) if token_count else 0.0,
        "mwl": round(mean_word_length, 4),
        "mwf": round(token_count / type_count, 4) if type_count else 0.0,
    }
    return save_cache("lexdiv", book_id, result) if use_cache else result
