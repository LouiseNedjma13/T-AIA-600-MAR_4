# Summarize

La commande `--summarize` resume un livre en quelques phrases.

Le code principal est dans `modules/summarize.py`.

## Diagramme

![Pipeline resume](../diagrams/diagram_summarize.png)

## Objectif

Le but est de produire un resume extractif. Cela veut dire que le programme ne cree pas de nouvelles phrases : il selectionne des phrases existantes du livre.

## Methode choisie

Nous utilisons une methode par frequence de mots.

L'idee est simple : si une phrase contient beaucoup de mots importants du livre, elle a plus de chances d'etre utile pour le resume.

## Etapes

1. Le livre est decoupe en phrases avec `split_into_sentences`.
2. Les phrases trop courtes ou trop longues sont ignorees.
3. Les dialogues sont filtres pour eviter un resume compose seulement de repliques.
4. Chaque phrase est tokenisee.
5. Les mots vides sont retires.
6. Le programme calcule les mots les plus frequents.
7. Chaque phrase recoit un score.
8. Les meilleures phrases sont selectionnees.
9. Les phrases choisies sont remises dans leur ordre original.
10. Le resultat est sauvegarde dans `data/cache`.

## Pourquoi remettre les phrases dans l'ordre

Le score sert a trouver les phrases importantes, mais le resume doit rester lisible. Une fois les phrases choisies, on les remet dans l'ordre du livre pour garder une progression logique.

## Pourquoi cette methode

Elle est simple, rapide, portable et ne depend pas d'un modele externe lourd.

Elle est moins intelligente qu'un modele generatif, mais elle respecte bien le cadre du projet : resumer un livre en quelques phrases avec une methode explicable.

## Cache

Le resultat est sauvegarde avec une cle du type :

```text
summary_11_sentences5.json
```

## Commande CLI

```bash
python3 bookworm.py --summarize 11
```

## Trophees valides

- resume
- summarize_doc
