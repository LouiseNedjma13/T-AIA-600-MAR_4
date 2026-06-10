# Similarity Methods

La commande `--similar` compare un livre avec la collection du projet et retourne les cinq livres les plus proches.

Le code principal est dans `modules/similar.py`.

## Objectif

Le but est de recommander des livres similaires a celui donne en parametre.

Pour le livre `11`, qui correspond a *Alice's Adventures in Wonderland*, le programme compare Alice avec les autres livres de `data/book_collection.json`.

## Methode finale choisie

La methode utilisee par defaut est Jaccard.

Nous avons quand meme teste trois methodes :

- Jaccard ;
- cosine similarity avec frequence de mots ;
- cosine similarity avec TF-IDF.

Cela permet de justifier le choix final au lieu de choisir une methode au hasard.

## 1. Jaccard

Jaccard compare les vocabulaires partages entre deux livres.

Chaque livre est transforme en ensemble de mots uniques.

La formule est :

```text
nombre de mots en commun / nombre total de mots uniques
```

Exemple :

```python
book_a = {"alice", "rabbit", "queen", "garden"}
book_b = {"alice", "rabbit", "cat", "tea"}
```

Mots en commun :

```python
{"alice", "rabbit"}
```

Tous les mots uniques :

```python
{"alice", "rabbit", "queen", "garden", "cat", "tea"}
```

Score :

```text
2 / 6 = 0.33
```

### Pourquoi cette methode est utile

Jaccard est simple, rapide et tres facile a expliquer.

Elle a bien fonctionne pour Alice parce qu'elle retourne des livres proches en univers et en vocabulaire jeunesse/fantastique.

Resultat obtenu pour le livre `11` :

```python
[
    "Through the Looking-Glass",
    "The Wonderful Wizard of Oz",
    "Peter Pan",
    "The Secret Garden",
    "The Jungle Book"
]
```

### Limite

Jaccard regarde seulement si un mot existe ou non. Il ne regarde pas combien de fois le mot apparait.

Un mot present une fois et un mot present cent fois ont donc le meme poids.

## 2. Cosine similarity avec frequence de mots

Cette methode transforme chaque livre en vecteur de frequences.

Au lieu de garder seulement la presence des mots, elle compte combien de fois chaque mot apparait.

Exemple :

```python
book_a = {"alice": 10, "rabbit": 6, "queen": 2}
book_b = {"alice": 3, "rabbit": 1, "cat": 8}
```

Ensuite, le programme compare les vecteurs avec une similarite cosinus.

La question devient :

```text
Est-ce que les deux livres utilisent les memes mots avec des frequences proches ?
```

### Pourquoi on l'a testee

Cette methode est plus fine que Jaccard car elle prend en compte les repetitions.

Si un mot est central dans un livre, il aura plus de poids.

### Resultat sur Alice

```python
[
    "Through the Looking-Glass",
    "Dracula",
    "The Adventures of Sherlock Holmes",
    "The Memoirs of Sherlock Holmes",
    "Treasure Island"
]
```

### Pourquoi on ne l'a pas choisie

Le resultat est moins coherent pour Alice : `Dracula` et `Sherlock Holmes` apparaissent tres haut alors que leur univers est moins proche.

Cette methode peut etre influencee par des mots narratifs frequents, meme apres nettoyage.

## 3. TF-IDF + cosine similarity

TF-IDF signifie `Term Frequency - Inverse Document Frequency`.

Cette methode donne un poids aux mots :

- un mot frequent dans un livre devient important pour ce livre ;
- un mot present dans presque tous les livres perd de l'importance ;
- un mot rare et specifique gagne de l'importance.

Ensuite, les livres sont compares avec une similarite cosinus.

Cette methode correspond au trophee theorique `vectorisation`, car elle transforme un texte en vecteur numerique.

### Pourquoi on l'a testee

TF-IDF est une methode classique et serieuse pour comparer des textes.

Elle est souvent meilleure que la frequence simple car elle reduit le poids des mots trop communs.

### Resultat sur Alice

```python
[
    "Through the Looking-Glass",
    "The Adventures of Sherlock Holmes",
    "Treasure Island",
    "The Memoirs of Sherlock Holmes",
    "The Time Machine"
]
```

### Pourquoi on ne l'a pas choisie par defaut

TF-IDF est interessant en theorie, mais sur notre petit corpus melange, il ne donne pas la liste la plus naturelle pour Alice.

Il retrouve des ressemblances de vocabulaire, mais pas toujours des ressemblances d'univers litteraire.

## Choix final

Nous gardons les trois methodes dans le code pour pouvoir les comparer.

Par defaut, nous utilisons Jaccard parce que c'est la methode qui donne les recommandations les plus coherentes pour Alice dans notre corpus.

## Cache

Le resultat est sauvegarde dans `data/cache` avec une cle du type :

```text
similar_11_jaccard_top5.json
```

## Commande CLI

```bash
python3 bookworm.py --similar 11
```

## Trophees valides

- similaire
- similar_doc
- vectorisation
- justification_outils
