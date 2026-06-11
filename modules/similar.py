import math
from collections import Counter

from services.cache import load_cache, save_cache
from services.gutenberg import GutenbergError, load_book
from utils.text_processing import tokenize


BOOK_COLLECTION = {
    "11": {"title": "Alice's Adventures in Wonderland", "authors": "Lewis Carroll", "bookshelves": "Children / Young Adult"},
    "12": {"title": "Through the Looking-Glass", "authors": "Lewis Carroll", "bookshelves": "Children / Young Adult"},
    "16": {"title": "Peter Pan", "authors": "J. M. Barrie", "bookshelves": "Children / Young Adult"},
    "55": {"title": "The Wonderful Wizard of Oz", "authors": "L. Frank Baum", "bookshelves": "Children / Young Adult"},
    "113": {"title": "The Secret Garden", "authors": "Frances Hodgson Burnett", "bookshelves": "Children / Young Adult"},
    "120": {"title": "Treasure Island", "authors": "Robert Louis Stevenson", "bookshelves": "Children / Young Adult"},
    "236": {"title": "The Jungle Book", "authors": "Rudyard Kipling", "bookshelves": "Children / Young Adult"},
    "108": {"title": "The Return of Sherlock Holmes", "authors": "Arthur Conan Doyle", "bookshelves": "Crime, Mystery & Thriller"},
    "834": {"title": "The Memoirs of Sherlock Holmes", "authors": "Arthur Conan Doyle", "bookshelves": "Crime, Mystery & Thriller"},
    "863": {"title": "The Mysterious Affair at Styles", "authors": "Agatha Christie", "bookshelves": "Crime, Mystery & Thriller"},
    "1661": {"title": "The Adventures of Sherlock Holmes", "authors": "Arthur Conan Doyle", "bookshelves": "Crime, Mystery & Thriller"},
    "61262": {"title": "Poirot Investigates", "authors": "Agatha Christie", "bookshelves": "Crime, Mystery & Thriller"},
    "69087": {"title": "The murder of Roger Ackroyd", "authors": "Agatha Christie", "bookshelves": "Crime, Mystery & Thriller"},
    "70114": {"title": "The Big Four", "authors": "Agatha Christie", "bookshelves": "Crime, Mystery & Thriller"},
    "35": {"title": "The Time Machine", "authors": "H. G. Wells", "bookshelves": "Science-Fiction & Fantasy"},
    "36": {"title": "The War of the Worlds", "authors": "H. G. Wells", "bookshelves": "Science-Fiction & Fantasy"},
    "84": {"title": "Frankenstein; Or, The Modern Prometheus", "authors": "Mary Wollstonecraft Shelley", "bookshelves": "Science-Fiction & Fantasy"},
    "159": {"title": "The island of Doctor Moreau", "authors": "H. G. Wells", "bookshelves": "Science-Fiction & Fantasy"},
    "164": {"title": "Twenty Thousand Leagues under the Sea", "authors": "Jules Verne", "bookshelves": "Science-Fiction & Fantasy"},
    "345": {"title": "Dracula", "authors": "Bram Stoker", "bookshelves": "Science-Fiction & Fantasy"},
    "68283": {"title": "The call of Cthulhu", "authors": "H. P. Lovecraft", "bookshelves": "Science-Fiction & Fantasy"},
}
CATEGORY_BONUS = 0.04
AUTHOR_BONUS = 0.03


def find_similar_books(book_id: int | str, use_cache: bool = True) -> list[dict[str, str | float]]:
    normalized_id = str(book_id).strip()
    cached = load_cache("similar_v5", normalized_id) if use_cache else None
    if cached is not None:
        return cached

    vectors = _build_collection_vectors()
    if normalized_id not in vectors:
        fallback = _metadata_fallback(normalized_id)
        return save_cache("similar_v5", normalized_id, fallback) if use_cache else fallback

    source_vector = vectors[normalized_id]
    source_metadata = BOOK_COLLECTION[normalized_id]
    similarities = []
    for other_id, vector in vectors.items():
        if other_id == normalized_id:
            continue
        text_score = _cosine(source_vector, vector)
        score = text_score
        other_metadata = BOOK_COLLECTION[other_id]
        if other_metadata["bookshelves"] == source_metadata["bookshelves"]:
            score += CATEGORY_BONUS
        if other_metadata["authors"] == source_metadata["authors"]:
            score += AUTHOR_BONUS
        similarities.append((score, text_score, other_id))

    recommendations = [
        _recommendation_payload(normalized_id, other_id, score, text_score)
        for score, text_score, other_id in sorted(similarities, reverse=True)[:5]
    ]
    if len(recommendations) < 5:
        known_titles = {item["title"] for item in recommendations}
        for item in _metadata_fallback(normalized_id):
            if item["title"] not in known_titles:
                recommendations.append(item)
            if len(recommendations) == 5:
                break

    return save_cache("similar_v5", normalized_id, recommendations) if use_cache else recommendations


def get_book_info(book_id: int | str) -> dict[str, str]:
    normalized_id = str(book_id).strip()
    metadata = BOOK_COLLECTION.get(normalized_id, {})
    return {
        "id": normalized_id,
        "authors": metadata.get("authors", "unknown"),
        "bookshelves": metadata.get("bookshelves", "unknown"),
    }


def _build_collection_vectors() -> dict[str, Counter]:
    documents = {}
    for book_id in BOOK_COLLECTION:
        try:
            tokens = tokenize(load_book(book_id), remove_stop_words=True)
        except GutenbergError:
            continue
        documents[book_id] = Counter(token for token in tokens if len(token) >= 3)

    document_frequency = Counter()
    for frequencies in documents.values():
        document_frequency.update(frequencies.keys())

    total_documents = len(documents)
    vectors = {}
    for book_id, frequencies in documents.items():
        vector = Counter()
        for token, count in frequencies.items():
            idf = math.log((total_documents + 1) / (document_frequency[token] + 1)) + 1
            vector[token] = count * idf
        vectors[book_id] = vector

    return vectors


def _cosine(left: Counter, right: Counter) -> float:
    shared_words = set(left) & set(right)
    numerator = sum(left[word] * right[word] for word in shared_words)
    left_norm = math.sqrt(sum(value * value for value in left.values()))
    right_norm = math.sqrt(sum(value * value for value in right.values()))

    if not left_norm or not right_norm:
        return 0.0

    return numerator / (left_norm * right_norm)


def _metadata_fallback(book_id: str) -> list[dict[str, str | float]]:
    source = BOOK_COLLECTION.get(book_id)
    if source is None:
        raise ValueError(f"book {book_id} is not available for similarity comparison")

    same_category = [
        _fallback_payload(metadata["title"], CATEGORY_BONUS, "same editorial category")
        for other_id, metadata in BOOK_COLLECTION.items()
        if other_id != book_id and metadata["bookshelves"] == source["bookshelves"]
    ]
    same_category_titles = {item["title"] for item in same_category}
    remaining = [
        _fallback_payload(metadata["title"], 0.0, "available in the comparison collection")
        for other_id, metadata in BOOK_COLLECTION.items()
        if other_id != book_id and metadata["title"] not in same_category_titles
    ]
    return (same_category + remaining)[:5]


def _recommendation_payload(
    source_id: str, other_id: str, score: float, text_score: float
) -> dict[str, str | float]:
    source = BOOK_COLLECTION[source_id]
    other = BOOK_COLLECTION[other_id]
    return {
        "title": other["title"],
        "score": round(score, 4),
        "reason": _recommendation_reason(source, other, text_score),
    }


def _recommendation_reason(source: dict[str, str], other: dict[str, str], text_score: float) -> str:
    reasons = []
    if source["authors"] == other["authors"]:
        reasons.append("same author")
    if source["bookshelves"] == other["bookshelves"]:
        reasons.append("same editorial category")
    if text_score > 0:
        reasons.append("similar TF-IDF vocabulary")
    return ", ".join(reasons) if reasons else "closest available TF-IDF match"


def _fallback_payload(title: str, score: float, reason: str) -> dict[str, str | float]:
    return {"title": title, "score": round(score, 4), "reason": reason}
