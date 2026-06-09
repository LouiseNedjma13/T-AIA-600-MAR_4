# classement des entités nommées par personnages/lieux : filtre le texte avec 
# majuscules en début de mot/personnages et lieux connus
# Pour entities on utilise le nettoyage normalize_text(text, lowercase=False) (enleve header, nettoie espace garde majuscule)
from utils.text_processing import normalize_text


KNOWN_CHARACTERS = {
    "Alice",
    "White Rabbit",
    "Mouse",
    "Dodo",
    "Lory",
    "Eaglet",
    "Duck",
    "Caterpillar",
    "Duchess",
    "Cheshire Cat",
    "Hatter",
    "March Hare",
    "Dormouse",
    "Queen",
    "King",
    "Knave",
    "Gryphon",
    "Mock Turtle",
}

KNOWN_LOCATIONS = {
    "Wonderland",
    "Rabbit-Hole",
    "Pool of Tears",
    "Hall",
    "Garden",
    "Court",
}


def extract_entities(text: str) -> dict:
    normalized_text = normalize_text(text, lowercase=False)

    characters = find_known_entities(normalized_text, KNOWN_CHARACTERS)
    locations = find_known_entities(normalized_text, KNOWN_LOCATIONS)

    return {
        "characters": characters,
        "locations": locations,
    }


def find_known_entities(text: str, known_entities: set[str]) -> list[str]:
    found_entities = []

    for entity in known_entities:
        if entity.lower() in text.lower():
            found_entities.append(entity)

    return sorted(found_entities)