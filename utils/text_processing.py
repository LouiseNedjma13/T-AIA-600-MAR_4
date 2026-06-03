import re


GUTENBERG_START_PATTERN = re.compile(
    r"\*\*\*\s*START OF (?:THE|THIS)?\s*PROJECT GUTENBERG EBOOK.*?\*\*\*",
    re.IGNORECASE | re.DOTALL,
)
GUTENBERG_END_PATTERN = re.compile(
    r"\*\*\*\s*END OF (?:THE|THIS)?\s*PROJECT GUTENBERG EBOOK.*?\*\*\*",
    re.IGNORECASE | re.DOTALL,
)
CHAPTER_PATTERN = re.compile(
    r"(?im)^\s*(chapter\s+[ivxlcdm0-9]+\.?.*|[ivxlcdm]+\.\s+.+)\s*$"
)
WORD_PATTERN = re.compile(r"[a-z]+(?:'[a-z]+)?")
SENTENCE_PATTERN = re.compile(r"(?<=[.!?])\s+")

STOP_WORDS = {
    "a", "about", "above", "after", "again", "against", "all", "am",
    "an", "and", "any", "are", "as", "at", "be", "because", "been",
    "before", "being", "below", "between", "both", "but", "by", "can",
    "did", "do", "does", "doing", "don", "down", "during", "each", "few",
    "for", "from", "further", "had", "has", "have", "having", "he", "her",
    "here", "hers", "herself", "him", "himself", "his", "how", "i", "if",
    "in", "into", "is", "it", "its", "itself", "just", "me", "more",
    "most", "my", "myself", "no", "nor", "not", "now", "of", "off", "on",
    "once", "only", "or", "other", "our", "ours", "ourselves", "out",
    "over", "own", "s", "same", "she", "should", "so", "some", "such",
    "t", "than", "that", "the", "their", "theirs", "them", "themselves",
    "then", "there", "these", "they", "this", "those", "through", "to",
    "too", "under", "until", "up", "very", "was", "we", "were", "what",
    "when", "where", "which", "while", "who", "whom", "why", "will", "with",
    "you", "your", "yours", "yourself", "yourselves",
}


def strip_gutenberg_header_footer(text: str) -> str:
    """Return only the book content, without Gutenberg license metadata."""
    start_match = GUTENBERG_START_PATTERN.search(text)
    end_match = GUTENBERG_END_PATTERN.search(text)

    start_index = start_match.end() if start_match else 0
    end_index = end_match.start() if end_match else len(text)

    if start_index >= end_index:
        return text.strip()

    return text[start_index:end_index].strip()


def normalize_text(text: str, lowercase: bool = True) -> str:
    """Normalize common typography and whitespace."""
    text = strip_gutenberg_header_footer(text)
    text = text.replace("\ufeff", "")
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = text.replace("\u2019", "'").replace("\u2018", "'").replace("`", "'")
    text = text.replace("\u201c", '"').replace("\u201d", '"')
    text = text.replace("\u2014", " ").replace("\u2013", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)

    if lowercase:
        text = text.lower()

    return text.strip()


def clean_text(text: str) -> str:
    """Return normalized text containing only letters, apostrophes and spaces."""
    text = normalize_text(text, lowercase=True)
    text = re.sub(r"[^a-z'\s]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def tokenize(text: str, remove_stop_words: bool = False) -> list[str]:
    """Tokenize text into normalized word tokens."""
    normalized_text = normalize_text(text, lowercase=True)
    tokens = [
        _normalize_token(match.group())
        for match in WORD_PATTERN.finditer(normalized_text)
    ]
    tokens = [token for token in tokens if token]

    if remove_stop_words:
        return remove_stopwords(tokens)

    return tokens


def remove_stopwords(tokens: list[str]) -> list[str]:
    """Remove common English stop words from a token list."""
    return [token for token in tokens if token not in STOP_WORDS]


def split_into_sentences(text: str) -> list[str]:
    """Split text into simple sentence candidates."""
    normalized_text = normalize_text(text, lowercase=False)
    sentences = SENTENCE_PATTERN.split(normalized_text)
    return [sentence.strip() for sentence in sentences if sentence.strip()]


def split_into_sections(text: str, max_sections: int = 4) -> dict[int, str]:
    """Split a book into chapter-like sections, falling back to equal chunks."""
    normalized_text = normalize_text(text, lowercase=False)
    matches = list(CHAPTER_PATTERN.finditer(normalized_text))

    if len(matches) >= max_sections:
        sections = []
        for index, match in enumerate(matches):
            start = match.start()
            if index + 1 < len(matches):
                end = matches[index + 1].start()
            else:
                end = len(normalized_text)
            section = normalized_text[start:end].strip()
            if section:
                sections.append(section)
        return _limit_sections(sections, max_sections)

    return _split_equal_chunks(normalized_text, max_sections)


def _normalize_token(token: str) -> str:
    token = token.strip("'")

    if token.endswith("'s"):
        token = token[:-2]

    return token


def _limit_sections(sections: list[str], max_sections: int) -> dict[int, str]:
    selected_sections = sections[:max_sections]
    return {index + 1: section for index, section in enumerate(selected_sections)}


def _split_equal_chunks(text: str, max_sections: int) -> dict[int, str]:
    words = text.split()

    if not words:
        return {}

    chunk_size = max(1, len(words) // max_sections)
    sections = {}

    for index in range(max_sections):
        start = index * chunk_size
        if index + 1 < max_sections:
            end = (index + 1) * chunk_size
        else:
            end = len(words)
        chunk = " ".join(words[start:end]).strip()

        if chunk:
            sections[index + 1] = chunk

    return sections
