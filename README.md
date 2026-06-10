# Bookworm - Alice's Adventures in Wonderland

Bookworm est un prototype de moteur NLP qui analyse des livres provenant de Project Gutenberg.
Le but est de transformer un texte brut en informations structurees pour produire une fiche de livre.

Le point d'entree du projet est `bookworm.py`.

## Installation

Le projet utilise uniquement la bibliotheque standard Python.

Version conseillee : Python 3.10 ou plus.

```bash
python3 --version
```

Aucune dependance externe n'est necessaire pour lancer les commandes actuelles.

## Structure

```text
T-AIA-600-MAR_4/
├── bookworm.py
├── modules/
│   ├── lexdiv.py
│   ├── entities.py
│   ├── card.py
│   ├── topics.py
│   ├── similar.py
│   └── summarize.py
├── utils/
│   ├── gutenberg.py
│   ├── cache.py
│   └── text_processing.py
├── data/
│   ├── book_collection.json
│   ├── topic_keywords.json
│   ├── books/
│   └── cache/
├── diagrams/
├── docs/
├── requirements.txt
├── .gitignore
└── README.md
```

## Role des dossiers

`bookworm.py` est le script principal. Il gere les arguments CLI et appelle la bonne commande.

`modules/` contient les commandes NLP demandees par le sujet : diversite lexicale, entites, topics, resume, similarite et fiche finale.

`utils/` contient les outils communs utilises par plusieurs commandes : telechargement Gutenberg, cache JSON et preprocessing du texte.

`data/book_collection.json` contient la liste des livres utilises pour la similarite.

`data/topic_keywords.json` contient le dictionnaire de themes utilise par `--topics`.

`data/books/` contient les livres telecharges depuis Project Gutenberg. Les fichiers `.txt` sont generes automatiquement et ne sont pas versionnes.

`data/cache/` contient les resultats sauvegardes pour eviter de recalculer les memes analyses. Les fichiers de cache ne sont pas versionnes.

`diagrams/` contient les schemas PNG demandes pour expliquer les pipelines.

`docs/` contient la documentation detaillee des methodes.

## Recuperer les livres

Les livres sont telecharges automatiquement en local avec `utils/gutenberg.py`.

Exemple pour telecharger Alice, ID Gutenberg `11` :

```bash
python3 -c "from utils.gutenberg import download_book; print(download_book(11))"
```

Le fichier est cree ici :

```text
data/books/11.txt
```

Les livres complets restent en local et ne sont pas pushes sur GitHub pour garder un depot propre.

## Commandes CLI

```bash
python3 bookworm.py --lexdiv 11
python3 bookworm.py --topics 11
python3 bookworm.py --entities 11
python3 bookworm.py --summarize 11
python3 bookworm.py --similar 11
python3 bookworm.py --card 11
```

L'ID `11` correspond a *Alice's Adventures in Wonderland*.

## Exemples d'utilisation

Calculer la diversite lexicale :

```bash
python3 bookworm.py --lexdiv 11
```

Extraire les themes par section :

```bash
python3 bookworm.py --topics 11
```

Extraire les personnages et lieux :

```bash
python3 bookworm.py --entities 11
```

Generer un resume :

```bash
python3 bookworm.py --summarize 11
```

Trouver des livres similaires :

```bash
python3 bookworm.py --similar 11
```

Generer la fiche complete :

```bash
python3 bookworm.py --card 11
```

## Cache

Les commandes couteuses sauvegardent leur resultat dans `data/cache`.

Cela concerne notamment :

- `--topics` ;
- `--summarize` ;
- `--similar` ;
- `--card`.

Avant de recalculer, le programme verifie si un resultat existe deja dans le cache.

## Tests rapides

Verifier que la CLI fonctionne :

```bash
python3 bookworm.py --lexdiv 11
```

Verifier la similarite :

```bash
python3 bookworm.py --similar 11
```

Verifier la gestion des collisions :

```bash
python3 bookworm.py --lexdiv 11 --topics 11
```

Cette derniere commande doit afficher une erreur, car le sujet demande qu'une seule option soit executee a la fois.

## Documentation des methodes

- [Preprocessing](docs/preprocessing.md)
- [Lexical Diversity](docs/lexdiv.md)
- [Topics](docs/topics.md)
- [Entities](docs/entities.md)
- [Summarize](docs/summarize.md)
- [Similarity Methods](docs/similar.md)
- [Book Card](docs/card.md)
- [CLI](docs/cli.md)

## Diagrammes

- `diagrams/diagram_lexdiv.png`
- `diagrams/diagram_topics.png`
- `diagrams/diagram_entities.png`
- `diagrams/diagram_summarize.png`
- `diagrams/diagram_similar.png`
- `diagrams/diagram_card.png`

## Trophees couverts par le projet

Fonctionnalites codees :

- nettoyage
- tokenisation
- collision
- lexdiv
- sujets
- entites
- resume
- similaire
- fiche de livre
- nomenclature
- robustesse
- maintenabilite
- portabilite
- clean_repo
- Bases du versionnage

Documentation et oral :

- mots vides
- normalisation
- vectorisation
- topics-doc
- entities_doc
- summarize_doc
- similar_doc
- doc_basic
- justification_outils
- presentation
- argumentation

## Choix techniques

- Telechargement des livres : `requests` n'est pas necessaire, le projet utilise `urllib` via la bibliotheque standard Python.
- Preprocessing : nettoyage Gutenberg, normalisation, tokenisation et mots vides.
- Topics : dictionnaire de themes pour garder une methode transparente et explicable.
- Resume : resume extractif par frequence de mots.
- Similarite : Jaccard par defaut, avec comparaison possible avec frequence cosinus et TF-IDF cosinus.
- Cache : fichiers JSON dans `data/cache` pour eviter les recalculs.

## Versioning

Les commits suivent le format :

```text
type(scope): message en minuscules
```

Exemples :

```text
feat(gutenberg): add project gutenberg downloader
feat(text-processing): add text cleaning and tokenization
docs(readme): update project documentation
```
