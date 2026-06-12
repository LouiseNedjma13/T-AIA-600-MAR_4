# utilisation de tokenize(text) pour le nettoyage et la tokenisation du texte, 
#puis calcul de différentes mesures de diversité lexicale
# calcule le voc du livre, nb de mot, mot differents, utilisé une fois, richess lexicale, longueur moyenne des mots, fréquence moyenne des mots

{
    "tok": int,
    "typ": int,
    "hap": int,
    "ttr": float,
    "mwl": float,
    "mwf": float,
}
from collections import Counter #outil python qui sert a commpter les éléments d'une liste et à créer un dictionnaire avec les éléments uniques comme clés et leur nombre d'occurrences comme valeurs

from utils.text_processing import tokenize


def compute_lexdiv(text: str) -> dict:
    tokens = tokenize(text)
    return compute_lexdiv_from_tokens(tokens)


def compute_lexdiv_from_tokens(tokens: list[str]) -> dict:
    counts = Counter(tokens)

    tok = len(tokens)
    typ = len(counts)
    hap = sum(1 for count in counts.values() if count == 1)

    if tok == 0 or typ == 0:
        return {
            "tok": 0,
            "typ": 0,
            "hap": 0,
            "ttr": 0.0,
            "mwl": 0.0,
            "mwf": 0.0,
        }

    return {
        "tok": tok,
        "typ": typ,
        "hap": hap,
        "ttr": typ / tok,
        "mwl": sum(len(token) for token in tokens) / tok,
        "mwf": tok / typ,
    }