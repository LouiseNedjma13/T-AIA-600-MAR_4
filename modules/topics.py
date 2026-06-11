import json
import re
from collections import Counter
from pathlib import Path

from utils.cache import load_cache, save_cache
from utils.gutenberg import load_book
from utils.text_processing import normalize_text, split_into_sections, tokenize


DATA_DIR = Path(__file__).resolve().parents[1] / "data"
TOPIC_KEYWORDS_PATH = DATA_DIR / "topic_keywords.json"


# Lightweight keyword-based topic extraction. This replaces heavier topic models
# like LDA/LSA with transparent theme vocabularies that are easy to explain.
MIN_WORD_LENGTH = 3
MIN_SECTION_TOKENS = 100
CHAPTER_PATTERN = re.compile(
    r"(?im)^\s*(chapter\s+[ivxlcdm0-9]+\.?.*)\s*$"
)


def _load_theme_keywords() -> dict[str, set[str]]:
    with TOPIC_KEYWORDS_PATH.open(encoding="utf-8") as keywords_file:
        raw_keywords = json.load(keywords_file)

    return {
        theme: set(words)
        for theme, words in raw_keywords.items()
    }


THEME_KEYWORDS = _load_theme_keywords()


def extract_topics_for_book(
    book_id: int | str,
    top_n: int = 10,
    max_sections: int = 4,
    use_cache: bool = True,
) -> dict[int, list[str]]:
    cache_key = f"topics_v2_{book_id}_top{top_n}_sections{max_sections}"

    if use_cache:
        cached_topics = load_cache(cache_key)
        if cached_topics is not None:
            return _restore_topic_keys(cached_topics)

    text = load_book(book_id)
    topics = extract_topics(text, top_n=top_n, max_sections=max_sections)

    if use_cache:
        save_cache(cache_key, topics)

    return topics


def extract_topics(text: str, top_n: int = 10, max_sections: int = 4) -> dict[int, list[str]]:
    sections = _select_topic_sections(text, max_sections=max_sections)
    return {
        section_number: extract_section_topics(section_text, top_n=top_n)
        for section_number, section_text in sections.items()
    }


def extract_section_topics(section_text: str, top_n: int = 10) -> list[str]:
    tokens = tokenize(section_text, remove_stop_words=True)
    tokens = [token for token in tokens if len(token) >= MIN_WORD_LENGTH]

    if not tokens:
        return []

    counts = Counter(tokens)
    theme_words = _matching_theme_words(counts)

    if len(theme_words) >= top_n:
        return theme_words[:top_n]

    fallback_words = [
        word
        for word, _count in counts.most_common()
        if word not in theme_words
    ]
    return (theme_words + fallback_words)[:top_n]


def score_themes(section_text: str) -> dict[str, int]:
    tokens = tokenize(section_text, remove_stop_words=True)
    counts = Counter(tokens)

    return {
        theme: sum(counts[word] for word in keywords if word in counts)
        for theme, keywords in THEME_KEYWORDS.items()
    }


def _matching_theme_words(counts: Counter[str]) -> list[str]:
    keyword_scores = {}

    for keywords in THEME_KEYWORDS.values():
        for keyword in keywords:
            if keyword in counts:
                keyword_scores[keyword] = counts[keyword]

    return sorted(keyword_scores, key=lambda word: (-keyword_scores[word], word))


def _select_topic_sections(text: str, max_sections: int) -> dict[int, str]:
    normalized_text = normalize_text(text, lowercase=False)
    matches = list(CHAPTER_PATTERN.finditer(normalized_text))
    real_sections = []

    for index, match in enumerate(matches):
        start = match.start()
        if index + 1 < len(matches):
            end = matches[index + 1].start()
        else:
            end = len(normalized_text)

        section = normalized_text[start:end].strip()
        token_count = len(tokenize(section, remove_stop_words=True))

        if token_count >= MIN_SECTION_TOKENS:
            real_sections.append(section)

    if not real_sections:
        return split_into_sections(text, max_sections=max_sections)

    return _merge_sections(real_sections, max_sections)


def _merge_sections(sections: list[str], max_sections: int) -> dict[int, str]:
    grouped_sections = {}
    section_count = len(sections)

    for index in range(max_sections):
        start = round(index * section_count / max_sections)
        end = round((index + 1) * section_count / max_sections)
        section = "\n\n".join(sections[start:end]).strip()
        if section:
            grouped_sections[index + 1] = section

    return grouped_sections


def _restore_topic_keys(topics: dict[str, list[str]]) -> dict[int, list[str]]:
    return {int(section): words for section, words in topics.items()}
