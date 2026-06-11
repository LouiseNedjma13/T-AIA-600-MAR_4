import re
from collections import Counter

from services.cache import load_cache, save_cache
from services.gutenberg import load_book
from utils.text_processing import normalize_text


ENTITY_PATTERN = re.compile(
    r"\b(?:[A-Z][a-z]+(?:'s)?)(?:\s+(?:[A-Z][a-z]+(?:'s)?))*\b"
)
LOCATION_CONTEXT_PATTERN = re.compile(
    r"\b(?:in|at|to|from|near|towards|toward|through|under|over|inside)\s+"
    r"([A-Z][A-Za-z]+(?:\s+[A-Z][A-Za-z]+)*)"
)
TITLE_WORDS = {"Mr", "Mrs", "Miss", "Ms", "Dr", "Sir", "Lady", "Professor"}
ENTITIES_CACHE_NAMESPACE = "entities_v2"
ENTITY_STOPLIST = {
    "A", "About", "After", "And", "Author", "Before", "Book", "Chapter",
    "Contents", "Copyright", "English", "Every", "First", "For", "Gutenberg",
    "If", "Illustration", "Illustrations", "In", "It", "Language", "Last",
    "License", "Produced", "Project", "Release", "The", "This", "Title",
    "Transcriber", "Updated",
    "Am", "Are", "As", "At", "But", "Can", "Could", "Did", "Do", "Does",
    "Had", "Has", "Have", "He", "Her", "Here", "Hers", "Him", "His",
    "How", "I", "Is", "It", "It's", "Me", "My", "No", "Not", "Oh",
    "She", "So", "That", "There", "They", "Then", "These", "Those",
    "Was", "We", "Well", "Were", "What", "When", "Where", "Which",
    "Who", "Why", "With", "Would", "Yes", "You",
    "All", "Bill", "Coils", "Come", "Don", "France Then", "However",
    "Just", "Let", "Looking", "Majesty", "March", "Now", "Off", "One",
    "Soup", "That's", "Two",
}
KNOWN_LOCATIONS = {
    "Africa", "America", "Asia", "Australia", "Baker Street", "Boston",
    "Castle", "China", "England", "Europe", "France", "India", "Ireland",
    "Island", "London", "New York", "Paris", "Rome", "Scotland", "Sea",
    "Spain", "Wonderland",
}


def extract_entities(book_id: int | str, use_cache: bool = True) -> dict[str, list[str]]:
    cached = load_cache(ENTITIES_CACHE_NAMESPACE, book_id) if use_cache else None
    if cached is not None:
        return cached

    text = normalize_text(load_book(book_id), lowercase=False)
    candidates = [_clean_entity(match.group()) for match in ENTITY_PATTERN.finditer(text)]
    candidates = [candidate for candidate in candidates if _is_entity_candidate(candidate)]

    name_counter = Counter(candidates)
    location_counter = Counter(_extract_context_locations(text))
    locations = _rank_locations(location_counter, name_counter)
    location_set = set(locations)
    characters = [
        name
        for name, count in name_counter.most_common()
        if count >= 2 and name not in location_set and name not in KNOWN_LOCATIONS
    ][:20]

    result = {"characters": characters, "locations": locations[:20]}
    return save_cache(ENTITIES_CACHE_NAMESPACE, book_id, result) if use_cache else result


def _clean_entity(entity: str) -> str:
    words = [word.strip("'") for word in entity.split()]
    words = [word[:-2] if word.endswith("'s") else word for word in words]
    words = [word for word in words if word not in TITLE_WORDS]
    if words and words[0] == "The":
        words = words[1:]
    return " ".join(words).strip()


def _is_entity_candidate(entity: str) -> bool:
    if not entity or entity in ENTITY_STOPLIST:
        return False
    if len(entity) <= 2:
        return False
    return not entity.lower().startswith("chapter ")


def _extract_context_locations(text: str) -> list[str]:
    locations = []
    for match in LOCATION_CONTEXT_PATTERN.finditer(text):
        location = _clean_entity(match.group(1))
        if _is_entity_candidate(location):
            locations.append(location)
    return locations


def _rank_locations(location_counter: Counter, name_counter: Counter) -> list[str]:
    for location in KNOWN_LOCATIONS:
        if location in name_counter:
            location_counter[location] += name_counter[location]

    return [
        location
        for location, count in location_counter.most_common()
        if count >= 1 and _is_location_candidate(location)
    ]


def _is_location_candidate(location: str) -> bool:
    if not _is_entity_candidate(location):
        return False
    if location in KNOWN_LOCATIONS:
        return True
    return any(
        location.endswith(suffix)
        for suffix in (" Street", " Island", " Sea", " Castle", " House")
    )
