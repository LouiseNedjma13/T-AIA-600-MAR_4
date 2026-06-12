# Resume extractif : le programme ne cree pas de nouvelles phrases,
# il selectionne les phrases les plus representatives du livre.

import re
from collections import Counter
from math import ceil

from utils.cache import load_cache, save_cache
from utils.gutenberg import load_book
from utils.text_processing import normalize_text, split_into_sentences, tokenize


DEFAULT_SENTENCE_COUNT = 8
DEFAULT_SECTION_COUNT = 4
MIN_SECTION_TOKENS = 100
MIN_SENTENCE_TOKENS = 5
MAX_SENTENCE_TOKENS = 45
CHAPTER_PATTERN = re.compile(r"(?im)^\s*chapter\s+[ivxlcdm0-9]+\.?.*$")
CHAPTER_TITLE_PATTERN = re.compile(r"(?im)^\s*chapter\s+[ivxlcdm0-9]+\.?\s*$\n?\s*[^\n.!?]{0,80}$")
ROMAN_TITLE_PATTERN = re.compile(r"(?im)^\s*[ivxlcdm]+\.\s+[^\n.!?]{1,80}$")


def summarize_book(
    book_id: int | str,
    sentence_count: int = DEFAULT_SENTENCE_COUNT,
    use_cache: bool = True,
) -> str:
    cache_key = f"summary_v8_{book_id}_sentences{sentence_count}"

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
    sections = _select_summary_sections(text, max_sections=DEFAULT_SECTION_COUNT)

    if not sections:
        return _summarize_section(text, sentence_count)

    sentences_per_section = max(1, ceil(sentence_count / len(sections)))
    selected_sentences = []

    for section_index, section_text in sections.items():
        section_sentences = _summarize_section_candidates(
            section_text,
            sentence_count=sentences_per_section,
            section_index=section_index,
        )
        selected_sentences.extend(section_sentences)

    selected_sentences = sorted(selected_sentences, key=lambda item: (item["section"], item["index"]))
    selected_sentences = selected_sentences[:sentence_count]

    return " ".join(item["sentence"] for item in selected_sentences)


def _summarize_section(text: str, sentence_count: int) -> str:
    selected_sentences = _summarize_section_candidates(
        text,
        sentence_count=sentence_count,
        section_index=1,
    )
    selected_sentences = sorted(selected_sentences, key=lambda item: item["index"])
    return " ".join(item["sentence"] for item in selected_sentences)


def _select_summary_sections(text: str, max_sections: int) -> dict[int, str]:
    normalized_text = normalize_text(text, lowercase=False)
    matches = list(CHAPTER_PATTERN.finditer(normalized_text))
    chapters = []

    for index, match in enumerate(matches):
        start = match.start()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(normalized_text)
        chapter = normalized_text[start:end].strip()
        cleaned_chapter = _remove_chapter_headings(chapter)

        if len(tokenize(cleaned_chapter, remove_stop_words=True)) >= MIN_SECTION_TOKENS:
            chapters.append(chapter)

    if not chapters:
        return {1: normalized_text}

    return _merge_chapters(chapters, max_sections=max_sections)


def _merge_chapters(chapters: list[str], max_sections: int) -> dict[int, str]:
    grouped_sections = {}
    chapter_count = len(chapters)

    for index in range(max_sections):
        start = round(index * chapter_count / max_sections)
        end = round((index + 1) * chapter_count / max_sections)
        section_text = "\n\n".join(chapters[start:end]).strip()

        if section_text:
            grouped_sections[index + 1] = section_text

    return grouped_sections


def _summarize_section_candidates(
    section_text: str,
    sentence_count: int,
    section_index: int,
) -> list[dict]:
    cleaned_section = _remove_chapter_headings(section_text)
    sentences = split_into_sentences(cleaned_section)
    candidates = _build_sentence_candidates(sentences, section_index=section_index)

    if not candidates:
        return []

    word_scores = _compute_word_scores(candidates)
    ranked_sentences = _rank_sentences(candidates, word_scores)
    return sorted(ranked_sentences[:sentence_count], key=lambda item: item["index"])


def _build_sentence_candidates(sentences: list[str], section_index: int) -> list[dict]:
    candidates = []

    for index, sentence in enumerate(sentences):
        tokens = tokenize(sentence, remove_stop_words=True)
        tokens = [token for token in tokens if token.isalpha()]

        if _is_valid_candidate(sentence, tokens):
            candidates.append({
                "section": section_index,
                "index": index,
                "sentence": sentence,
                "tokens": tokens,
            })

    return candidates


def _is_valid_candidate(sentence: str, tokens: list[str]) -> bool:
    if _looks_like_heading(sentence):
        return False

    if not MIN_SENTENCE_TOKENS <= len(tokens) <= MAX_SENTENCE_TOKENS:
        return False

    if _looks_like_dialogue(sentence):
        return False

    if _looks_too_repetitive(tokens):
        return False

    if "_" in sentence:
        return False

    return True


def _remove_chapter_headings(text: str) -> str:
    text = CHAPTER_TITLE_PATTERN.sub("", text)
    return ROMAN_TITLE_PATTERN.sub("", text)


def _looks_like_heading(sentence: str) -> bool:
    lowered_sentence = sentence.lower().strip()
    return lowered_sentence.startswith("chapter ") or "\nchapter " in lowered_sentence


def _looks_like_dialogue(sentence: str) -> bool:
    lowered_sentence = sentence.lower()
    return '"' in sentence or " said " in lowered_sentence or lowered_sentence.startswith("said ")


def _looks_too_repetitive(tokens: list[str]) -> bool:
    if len(tokens) < 6:
        return False

    unique_ratio = len(set(tokens)) / len(tokens)
    return unique_ratio < 0.6


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

        position_bonus = 1 / (1 + candidate["index"] / 80)
        normalized_score = (normalized_score * 0.9) + (position_bonus * 0.1)

        ranked_sentences.append({
            "section": candidate["section"],
            "index": candidate["index"],
            "sentence": candidate["sentence"],
            "score": normalized_score,
        })

    return sorted(ranked_sentences, key=lambda item: item["score"], reverse=True)
