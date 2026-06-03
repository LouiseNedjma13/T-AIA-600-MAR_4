# Bookworm - Alice's Adventures in Wonderland

Bookworm est un prototype de moteur NLP qui analyse des livres provenant de Project Gutenberg.
Le but est de transformer un texte brut en informations structurees pour produire une fiche de livre.

Le script principal attendu par le sujet est `bookworm.py`. Il servira de point d'entree CLI pour lancer les differentes commandes du projet.

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
│   ├── books/
│   └── cache/
├── diagrams/
├── requirements.txt
├── .gitignore
└── README.md
```

## Role des dossiers

`modules/` contient les fonctionnalites NLP demandees par le sujet : diversite lexicale, entites, topics, resume, similarite et fiche finale.

`utils/` contient les outils communs utilisés par plusieurs modules. Ces fichiers preparent les donnees ou evitent de repeter du code.

`data/books/` contient les livres telecharges depuis Project Gutenberg. Les fichiers `.txt` sont generes automatiquement et ne sont pas versionnes.

`data/cache/` servira a stocker les resultats couteux a recalculer.

`diagrams/` contiendra les diagrammes de pipeline demandes dans le sujet.

## `utils/gutenberg.py`

Ce fichier gere la recuperation des livres depuis Project Gutenberg.

Il permet de :

- construire l'URL d'un livre a partir de son ID Gutenberg ;
- telecharger le texte brut du livre ;
- sauvegarder le fichier dans `data/books/` ;
- relire un livre deja telecharge sans refaire une requete reseau ;
- gerer les erreurs avec des messages clairs.

Exemple avec le livre `11`, qui correspond a *Alice's Adventures in Wonderland* :

```python
from utils.gutenberg import download_book, load_book

path = download_book(11)
text = load_book(11)
```

Le livre est sauvegarde ici :

```text
data/books/11.txt
```

## `utils/text_processing.py`

Ce fichier prepare le texte avant les analyses NLP. Il est central, car les modules comme `lexdiv`, `topics`, `similar` ou `summarize` doivent travailler sur un texte propre.

Il permet de :

- enlever l'en-tete et le footer Project Gutenberg ;
- normaliser le texte ;
- nettoyer les caracteres inutiles ;
- tokeniser le texte en mots ;
- retirer les mots vides si necessaire ;
- decouper le texte en phrases ;
- decouper le livre en sections pour les topics.

### Nettoyage Gutenberg

Les fichiers Project Gutenberg contiennent des metadonnees et une licence qui ne font pas partie du livre. Si on garde ces parties, les resultats NLP peuvent etre fausses.

La fonction suivante garde uniquement le contenu reel du livre :

```python
strip_gutenberg_header_footer(text)
```

### Normalisation

La normalisation rend le texte plus regulier. Elle harmonise les apostrophes, les tirets, les retours a la ligne et peut mettre le texte en minuscules.

```python
normalize_text(text)
```

### Tokenisation

La tokenisation transforme un texte en liste de mots.

```python
tokenize(text)
```

Exemple :

```text
Alice's Adventures in Wonderland
```

devient :

```python
["alice", "adventures", "in", "wonderland"]
```

### Mots vides

Les mots vides sont des mots tres frequents qui apportent peu d'information thematique, comme `the`, `a`, `of`, `in`, `and`.

Ils peuvent etre retires avec :

```python
tokenize(text, remove_stop_words=True)
```

## Tests rapides

Telecharger Alice depuis Project Gutenberg :

```bash
python3 -c "from utils.gutenberg import download_book; print(download_book(11))"
```

Afficher les premiers tokens :

```bash
python3 -c "from utils.gutenberg import load_book; from utils.text_processing import tokenize; text = load_book(11); print(tokenize(text)[:30])"
```

Afficher les premiers tokens sans mots vides :

```bash
python3 -c "from utils.gutenberg import load_book; from utils.text_processing import tokenize; text = load_book(11); print(tokenize(text, remove_stop_words=True)[:30])"
```

Afficher le nombre de sections detectees :

```bash
python3 -c "from utils.gutenberg import load_book; from utils.text_processing import split_into_sections; text = load_book(11); print(len(split_into_sections(text)))"
```

## Commandes CLI prevues

Le script `bookworm.py` devra respecter la nomenclature du sujet :

```bash
python3 bookworm.py --lexdiv 11
python3 bookworm.py --topics 11
python3 bookworm.py --entities 11
python3 bookworm.py --summarize 11
python3 bookworm.py --similar 11
python3 bookworm.py --card 11
```

## Versioning

Les commits suivent le format :

```text
type(scope): message en minuscules
```

Exemples :

```text
feat(gutenberg): add project gutenberg downloader
feat(text-processing): add text cleaning and tokenization
docs(readme): add project documentation
```
