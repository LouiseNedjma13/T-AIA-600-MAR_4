# découpage phrase importantes via processing, Nettoyage/tokenization scoring phrases avec mots importants
# selection des meilleures phrases & remise ds l'ordre d'origine, résumé final
# Methode : fréquence de mot : simple rapide pas de modele lourd

from collections import Counter

from utils.cache import load_cache, save_cache
from utils.gutenberg import load_book
from utils.text_processing import split_into_sentences, tokenize


DEFAULT_SENTENCE_COUNT = 5
MIN_SENTENCE_TOKENS = 5
MAX_SENTENCE_TOKENS = 45


def summarize_book(
    book_id: int | str,
    sentence_count: int = DEFAULT_SENTENCE_COUNT,
    use_cache: bool = True,
) -> str:
    cache_key = f"summary_{book_id}_sentences{sentence_count}"

    if use_cache:
        cached_summary = load_cache(cache_key)
        if cached_summary is not None:
            return cached_summary

    text = load_book(book_id)
    summary = summarize_text(text, sentence_count=sentence_count)

    if use_cache:
        save_cache(cache_key, summary)

    return summary


def summarize_text(text: str, sentence_count: int = DEFAULT_SENTENCE_COUNT) -> str:
    sentences = split_into_sentences(text)
    candidates = _build_sentence_candidates(sentences)

    if not candidates:
        return ""

    word_scores = _compute_word_scores(candidates)
    ranked_sentences = _rank_sentences(candidates, word_scores)
    selected_sentences = sorted(ranked_sentences[:sentence_count], key=lambda item: item["index"])

    return " ".join(item["sentence"] for item in selected_sentences)


def _build_sentence_candidates(sentences: list[str]) -> list[dict]:
    candidates = []

    for index, sentence in enumerate(sentences):
        tokens = tokenize(sentence, remove_stop_words=True)
        tokens = [token for token in tokens if token.isalpha()]

        if _is_valid_candidate(sentence, tokens):
            candidates.append({
                "index": index,
                "sentence": sentence,
                "tokens": tokens,
            })

    return candidates


def _is_valid_candidate(sentence: str, tokens: list[str]) -> bool:
    if not MIN_SENTENCE_TOKENS <= len(tokens) <= MAX_SENTENCE_TOKENS:
        return False

    if _looks_like_dialogue(sentence):
        return False

    if "_" in sentence:
        return False

    return True


def _looks_like_dialogue(sentence: str) -> bool:
    lowered_sentence = sentence.lower()
    return '"' in sentence or " said " in lowered_sentence or lowered_sentence.startswith("said ")


def _compute_word_scores(candidates: list[dict]) -> dict[str, float]:
    word_counts = Counter()

    for candidate in candidates:
        word_counts.update(candidate["tokens"])

    if not word_counts:
        return {}

    highest_frequency = max(word_counts.values())
    return {
        word: count / highest_frequency
        for word, count in word_counts.items()
    }


def _rank_sentences(candidates: list[dict], word_scores: dict[str, float]) -> list[dict]:
    ranked_sentences = []

    for candidate in candidates:
        score = sum(word_scores.get(token, 0.0) for token in candidate["tokens"])
        normalized_score = score / len(candidate["tokens"])

        position_bonus = 1 / (1 + candidate["index"] / 250)
        normalized_score = (normalized_score * 0.85) + (position_bonus * 0.15)

        ranked_sentences.append({
            "index": candidate["index"],
            "sentence": candidate["sentence"],
            "score": normalized_score,
        })

    return sorted(ranked_sentences, key=lambda item: item["score"], reverse=True)
