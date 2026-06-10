# Preprocessing

Le preprocessing est la premiere etape du projet. Avant de calculer une diversite lexicale, des themes, un resume ou une similarite, on transforme le texte brut en texte exploitable.

Le code principal est dans `utils/text_processing.py`.

## Objectif

Les fichiers Project Gutenberg ne contiennent pas seulement le livre. Ils contiennent aussi une en-tete, des informations de licence et parfois un footer. Ces parties ne doivent pas influencer les resultats NLP.

Le preprocessing sert donc a :

- retirer l'en-tete et le footer Gutenberg ;
- nettoyer les espaces et caracteres inutiles ;
- normaliser le texte ;
- decouper le texte en mots ;
- retirer les mots vides quand une commande en a besoin ;
- decouper le texte en phrases ou en sections.

## Nettoyage

La fonction `strip_gutenberg_header_footer(text)` cherche les marqueurs Gutenberg et garde uniquement le contenu du livre.

Sans cette etape, des mots comme `Project`, `Gutenberg`, `license` ou `ebook` pourraient etre comptes comme s'ils faisaient partie de l'histoire.

## Normalisation

La fonction `normalize_text(text)` rend le texte plus regulier.

Elle sert notamment a :

- harmoniser les apostrophes ;
- harmoniser les tirets ;
- remplacer les retours a la ligne multiples ;
- mettre en minuscules si necessaire.

Exemple :

```text
Alice's Adventures
```

peut devenir :

```text
alice's adventures
```

## Tokenisation

La fonction `tokenize(text)` transforme le texte en liste de mots.

Exemple :

```text
Alice follows the White Rabbit.
```

devient :

```python
["alice", "follows", "the", "white", "rabbit"]
```

Cette etape valide le trophee `tokenisation`.

## Mots vides

Les mots vides sont des mots tres frequents qui apportent peu d'information thematique, par exemple `the`, `and`, `of`, `in`.

Pour certaines commandes, on les retire avec :

```python
tokenize(text, remove_stop_words=True)
```

On ne les retire pas toujours. Par exemple, pour `lexdiv`, garder tous les mots permet de mesurer la diversite globale du texte. Pour `topics`, `summarize` et `similar`, les retirer aide a garder les mots les plus utiles.

## Commande de test

```bash
python3 -c "from utils.gutenberg import load_book; from utils.text_processing import tokenize; text = load_book(11); print(tokenize(text)[:30])"
```

## Trophees lies

- nettoyage
- tokenisation
- mots vides
- normalisation
- maintenabilite
