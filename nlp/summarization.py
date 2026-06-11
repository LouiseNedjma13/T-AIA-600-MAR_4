from collections import Counter

from nlp.entities import extract_entities
from nlp.topics import extract_topics
from services.cache import load_cache, save_cache
from services.gutenberg import load_book
from utils.text_processing import split_into_sentences, tokenize


def summarize_book(
    book_id: int | str, sentence_count: int = 4, use_cache: bool = True
) -> str:
    cached = load_cache("summary_v3", book_id) if use_cache else None
    if cached is not None:
        return cached

    text = load_book(book_id)
    entities = extract_entities(book_id, use_cache=use_cache)
    topics = extract_topics(book_id, use_cache=use_cache)
    important_terms = _important_terms(entities, topics)
    sentences = _candidate_sentences(split_into_sentences(text))
    if not sentences:
        return ""

    frequencies = Counter(tokenize(" ".join(sentences), remove_stop_words=True))
    if not frequencies:
        summary = " ".join(sentences[:sentence_count])
        return save_cache("summary_v3", book_id, summary) if use_cache else summary

    max_frequency = max(frequencies.values())
    normalized = {word: count / max_frequency for word, count in frequencies.items()}
    scored_sentences = []

    for index, sentence in enumerate(sentences):
        tokens = tokenize(sentence, remove_stop_words=True)
        if not tokens:
            continue
        score = sum(normalized.get(token, 0.0) for token in tokens) / len(tokens)
        score += _entity_topic_bonus(sentence, tokens, important_terms)
        score += _position_bonus(index, len(sentences))
        scored_sentences.append((score, index, sentence))

    selected = sorted(scored_sentences, reverse=True)[:sentence_count]
    extractive_summary = " ".join(
        sentence for _, _, sentence in sorted(selected, key=lambda item: item[1])
    )
    structured_intro = _structured_intro(entities, topics)
    summary = " ".join(part for part in [structured_intro, extractive_summary] if part)
    return save_cache("summary_v3", book_id, summary) if use_cache else summary


def _important_terms(
    entities: dict[str, list[str]], topics: dict[int, list[str]]
) -> set[str]:
    terms = set()
    for entity in entities.get("characters", [])[:5] + entities.get("locations", [])[:5]:
        terms.update(tokenize(entity, remove_stop_words=True))
    for section_words in topics.values():
        terms.update(section_words[:5])
    return terms


def _entity_topic_bonus(sentence: str, tokens: list[str], important_terms: set[str]) -> float:
    token_hits = len(set(tokens) & important_terms)
    lower_sentence = sentence.lower()
    phrase_hits = sum(1 for term in important_terms if " " in term and term in lower_sentence)
    return min(0.35, (token_hits * 0.04) + (phrase_hits * 0.08))


def _structured_intro(entities: dict[str, list[str]], topics: dict[int, list[str]]) -> str:
    characters = entities.get("characters", [])[:3]
    locations = entities.get("locations", [])[:2]
    topic_words = _top_topic_words(topics, limit=5)

    parts = []
    if characters:
        parts.append(f"The book highlights characters such as {_join_words(characters)}")
    if locations:
        parts.append(f"with important places such as {_join_words(locations)}")
    if topic_words:
        parts.append(f"and recurring themes around {_join_words(topic_words)}")

    if not parts:
        return ""

    return " ".join(parts) + "."


def _top_topic_words(topics: dict[int, list[str]], limit: int) -> list[str]:
    words = []
    seen = set()
    for section_words in topics.values():
        for word in section_words:
            if word not in seen:
                seen.add(word)
                words.append(word)
            if len(words) == limit:
                return words
    return words


def _join_words(words: list[str]) -> str:
    if len(words) == 1:
        return words[0]
    return ", ".join(words[:-1]) + f" and {words[-1]}"


def _candidate_sentences(sentences: list[str]) -> list[str]:
    candidates = []
    for sentence in sentences:
        normalized_sentence = sentence.replace("\n", " ")
        lower_sentence = normalized_sentence.lower()
        word_count = len(tokenize(sentence))
        if not 8 <= word_count <= 45:
            continue
        if "_" in normalized_sentence:
            continue
        if "chapter" in lower_sentence:
            continue
        if "illustration" in lower_sentence:
            continue
        if "dramatis person" in lower_sentence:
            continue
        if "edition" in lower_sentence:
            continue
        if "by lewis carroll" in lower_sentence:
            continue
        if normalized_sentence.lstrip().startswith(('"', "'")):
            continue
        if " said " in lower_sentence or lower_sentence.startswith("said "):
            continue
        if " growled " in lower_sentence or " cried " in lower_sentence:
            continue
        if normalized_sentence.count('"') > 2:
            continue
        candidates.append(normalized_sentence)
    return candidates


def _position_bonus(index: int, total: int) -> float:
    if total <= 1:
        return 0.0
    if index < total * 0.08:
        return 0.15
    if index > total * 0.92:
        return 0.05
    return 0.0
