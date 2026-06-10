# Book Card

La commande `--card` genere une fiche complete pour un livre.

Le code principal est dans `modules/card.py`.

## Objectif

La fiche de livre regroupe les resultats des autres commandes dans un seul dictionnaire.

Elle permet d'avoir une vue globale du livre : informations, diversite lexicale, themes, entites, resume et livres similaires.

## Contenu de la fiche

La fiche contient :

- `info` : id, auteur, categorie ;
- `lexdiv` : mesures de diversite lexicale ;
- `topics` : mots importants par section ;
- `entities` : personnages et lieux ;
- `summary` : resume court ;
- `similar` : livres similaires.

## Fonctionnement

Le module `card.py` appelle les autres modules :

```python
compute_lexdiv(text)
extract_topics_for_book(book_id)
extract_entities(text)
summarize_book(book_id)
find_similar_books(book_id)
```

Il recupere aussi les informations du livre depuis `data/book_collection.json`.

## Cache

Comme la fiche appelle plusieurs calculs, elle est sauvegardee dans `data/cache` avec une cle du type :

```text
card_11.json
```

Cela evite de recalculer toute la fiche a chaque execution.

## Commande CLI

```bash
python3 bookworm.py --card 11
```

## Trophee valide

- fiche de livre
