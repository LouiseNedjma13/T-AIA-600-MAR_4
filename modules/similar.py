import json
import math
from collections import Counter
from pathlib import Path

from utils.cache import load_cache, save_cache
from utils.gutenberg import load_book
from utils.text_processing import tokenize


DATA_DIR = Path(__file__).resolve().parents[1] / "data"
BOOK_COLLECTION_PATH = DATA_DIR / "book_collection.json"
DEFAULT_TOP_N = 5
DEFAULT_METHOD = "jaccard"
MIN_TOKEN_LENGTH = 3
NARRATIVE_STOP_WORDS = {
    "said", "say", "says", "would", "could", "should", "upon", "one",
    "two", "like", "little", "much", "must", "might", "came", "come",
    "went", "go", "got", "get", "made", "make", "looked", "look",
    "thought", "think", "know", "quite", "thing", "things", "chapter",
}


def find_similar_books(
    book_id: int | str,
    top_n: int = DEFAULT_TOP_N,
    method: str = DEFAULT_METHOD,
    use_cache: bool = True,
) -> list[str]:
    cache_key = f"similar_{book_id}_{method}_top{top_n}"

    if use_cache:
        cached_result = load_cache(cache_key)
        if cached_result is not None:
            return cached_result

    scored_books = score_similar_books(book_id, method=method)
    titles = [book["title"] for book in scored_books[:top_n]]

    if use_cache:
        save_cache(cache_key, titles)

    return titles


def compare_similarity_methods(book_id: int | str, top_n: int = DEFAULT_TOP_N) -> dict[str, list[str]]:
    return {
        "jaccard": find_similar_books(book_id, top_n=top_n, method="jaccard", use_cache=False),
        "frequency": find_similar_books(book_id, top_n=top_n, method="frequency", use_cache=False),
        "tfidf": find_similar_books(book_id, top_n=top_n, method="tfidf", use_cache=False),
    }


def score_similar_books(book_id: int | str, method: str = "tfidf") -> list[dict]:
    books = load_book_collection()
    target_id = str(book_id)
    documents = _load_documents(books)

    if target_id not in documents:
        raise ValueError(f"book id {book_id} is not part of the configured collection")

    if method == "jaccard":
        scores = _score_with_jaccard(target_id, documents)
    elif method == "frequency":
        scores = _score_with_frequency_cosine(target_id, documents)
    elif method == "tfidf":
        scores = _score_with_tfidf_cosine(target_id, documents)
    else:
        raise ValueError("method must be one of: jaccard, frequency, tfidf")

    return _format_scores(scores, books, target_id)


def load_book_collection() -> list[dict]:
    return json.loads(BOOK_COLLECTION_PATH.read_text(encoding="utf-8"))


def _load_documents(books: list[dict]) -> dict[str, list[str]]:
    documents = {}

    for book in books:
        book_id = str(book["id"])
        text = load_book(book_id)
        tokens = tokenize(text, remove_stop_words=True)
        documents[book_id] = [
            token
            for token in tokens
            if (
                len(token) >= MIN_TOKEN_LENGTH
                and token.isalpha()
                and token not in NARRATIVE_STOP_WORDS
            )
        ]

    return documents


def _score_with_jaccard(target_id: str, documents: dict[str, list[str]]) -> dict[str, float]:
    target_words = set(documents[target_id])
    scores = {}

    for book_id, tokens in documents.items():
        if book_id == target_id:
            continue

        compared_words = set(tokens)
        union = target_words | compared_words
        intersection = target_words & compared_words
        scores[book_id] = len(intersection) / len(union) if union else 0.0

    return scores


def _score_with_frequency_cosine(target_id: str, documents: dict[str, list[str]]) -> dict[str, float]:
    vectors = {
        book_id: Counter(tokens)
        for book_id, tokens in documents.items()
    }
    return _score_with_cosine(target_id, vectors)


def _score_with_tfidf_cosine(target_id: str, documents: dict[str, list[str]]) -> dict[str, float]:
    document_count = len(documents)
    document_frequencies = Counter()

    for tokens in documents.values():
        document_frequencies.update(set(tokens))

    vectors = {}
    for book_id, tokens in documents.items():
        token_counts = Counter(tokens)
        total_tokens = len(tokens) or 1
        vector = {}

        for token, count in token_counts.items():
            term_frequency = count / total_tokens
            inverse_document_frequency = math.log(
                (1 + document_count) / (1 + document_frequencies[token])
            ) + 1
            vector[token] = term_frequency * inverse_document_frequency

        vectors[book_id] = vector

    return _score_with_cosine(target_id, vectors)


def _score_with_cosine(target_id: str, vectors: dict[str, dict | Counter]) -> dict[str, float]:
    target_vector = vectors[target_id]
    target_norm = _vector_norm(target_vector)
    scores = {}

    for book_id, vector in vectors.items():
        if book_id == target_id:
            continue

        compared_norm = _vector_norm(vector)
        denominator = target_norm * compared_norm
        scores[book_id] = _dot_product(target_vector, vector) / denominator if denominator else 0.0

    return scores


def _dot_product(left_vector: dict | Counter, right_vector: dict | Counter) -> float:
    if len(left_vector) > len(right_vector):
        left_vector, right_vector = right_vector, left_vector

    return sum(value * right_vector.get(token, 0.0) for token, value in left_vector.items())


def _vector_norm(vector: dict | Counter) -> float:
    return math.sqrt(sum(value * value for value in vector.values()))


def _format_scores(scores: dict[str, float], books: list[dict], target_id: str) -> list[dict]:
    books_by_id = {str(book["id"]): book for book in books}
    ranked_ids = sorted(scores, key=lambda book_id: scores[book_id], reverse=True)

    return [
        {
            "id": int(book_id),
            "title": books_by_id[book_id]["title"],
            "category": books_by_id[book_id]["category"],
            "score": scores[book_id],
        }
        for book_id in ranked_ids
        if book_id != target_id
    ]
