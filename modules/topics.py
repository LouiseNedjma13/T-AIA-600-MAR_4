import re
import math
from collections import Counter

from services.cache import load_cache, save_cache
from services.gutenberg import load_book
from utils.text_processing import split_into_sections, tokenize


MIN_TOPIC_WORD_LENGTH = 3
TOPICS_CACHE_NAMESPACE = "topics_v4"
ROMAN_NUMERAL_PATTERN = re.compile(r"^[ivxlcdm]+$")
EXCLUDED_TOPIC_WORDS = {
    "chapter", "chapters", "book", "volume", "contents", "illustration",
    "illustrations", "said", "say", "says", "little",
    "alice", "thing", "things", "time", "long", "quite", "rather", "looked",
    "went", "came", "come", "got", "get", "made", "make", "thought", "think",
    "sends", "sent", "bill", "one", "two", "three", "way",
    "like", "know", "see", "i'm", "i'll", "i've", "would", "could", "should",
    "much", "well", "began", "must", "don't",
}
THEME_KEYWORDS = {
    "animals": {
        "animal", "animals", "bird", "birds", "cat", "dog", "fish", "horse",
        "mouse", "rabbit", "rabbits", "tiger", "wolf",
    },
    "authority": {
        "court", "judge", "king", "law", "order", "orders", "power", "queen",
        "rule", "rules", "trial",
    },
    "adventure": {
        "adventure", "away", "door", "escape", "followed", "found", "journey",
        "road", "ran", "travel", "walked", "went",
    },
    "childhood": {
        "boy", "child", "children", "girl", "lesson", "school", "sister",
        "youth",
    },
    "dreams_and_time": {
        "dream", "dreamed", "dreams", "sleep", "time", "watch", "woke",
    },
    "emotions": {
        "anger", "angry", "cry", "cried", "fear", "happy", "sad", "tears",
        "weep", "wept",
    },
    "fantasy": {
        "curious", "magic", "magical", "strange", "wonder", "wonderland",
        "world",
    },
    "games_and_nonsense": {
        "caucus", "game", "games", "nonsense", "race", "riddle", "tale",
        "tea", "tweedledee", "tweedledum",
    },
    "mirror_world": {
        "glass", "house", "looking", "mirror", "mirrors", "reflection",
        "reflections",
    },
    "fear_and_danger": {
        "afraid", "blood", "danger", "dark", "dead", "death", "fear",
        "frightened", "horror", "murder",
    },
    "nature": {
        "flower", "forest", "garden", "grass", "pool", "river", "sea",
        "tree", "water", "wood",
    },
    "mystery": {
        "case", "clue", "crime", "detective", "evidence", "murder",
        "mystery", "secret", "suspect",
    },
    "science": {
        "experiment", "machine", "science", "scientific", "strange", "world",
    },
}


def extract_topics(book_id: int | str, use_cache: bool = True) -> dict[int, list[str]]:
    cached = load_cache(TOPICS_CACHE_NAMESPACE, book_id) if use_cache else None
    if cached is not None:
        return {int(section): words for section, words in cached.items()}

    text = load_book(book_id)
    sections = split_into_sections(text, max_sections=4)
    section_frequencies = {}
    for section_number, section_text in sections.items():
        section_frequencies[section_number] = Counter(
            token
            for token in tokenize(section_text, remove_stop_words=True)
            if _is_topic_token(token)
        )

    document_frequency = Counter()
    for frequencies in section_frequencies.values():
        document_frequency.update(frequencies.keys())

    topics = {}

    for section_number, frequencies in section_frequencies.items():
        tfidf_scores = _tfidf_scores(frequencies, document_frequency, len(sections))
        topics[section_number] = _section_topics(tfidf_scores)

    return save_cache(TOPICS_CACHE_NAMESPACE, book_id, topics) if use_cache else topics


def _is_topic_token(token: str) -> bool:
    if len(token) < MIN_TOPIC_WORD_LENGTH:
        return False
    if token in EXCLUDED_TOPIC_WORDS:
        return False
    return ROMAN_NUMERAL_PATTERN.fullmatch(token) is None


def _tfidf_scores(
    frequencies: Counter, document_frequency: Counter, section_count: int
) -> dict[str, float]:
    total_tokens = sum(frequencies.values())
    if total_tokens == 0:
        return {}

    scores = {}
    for word, count in frequencies.items():
        tf = count / total_tokens
        idf = math.log((section_count + 1) / (document_frequency[word] + 1)) + 1
        scores[word] = tf * idf
    return scores


def _section_topics(scores: dict[str, float]) -> list[str]:
    theme_scores = Counter()
    for theme, keywords in THEME_KEYWORDS.items():
        theme_scores[theme] = sum(scores.get(word, 0.0) for word in keywords)

    selected = [
        theme.replace("_", " ")
        for theme, score in theme_scores.most_common()
        if score > 0
    ][:5]

    for word, _ in sorted(scores.items(), key=lambda item: item[1], reverse=True):
        if word not in selected:
            selected.append(word)
        if len(selected) == 10:
            break

    return selected
