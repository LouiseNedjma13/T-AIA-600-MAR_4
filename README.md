# Bookworm

Bookworm is a lightweight NLP prototype for Project Gutenberg books. It turns
raw literary texts into structured "book cards" with lexical metrics, topics,
entities, summaries and recommendations.

The required CLI entry point is:

```bash
python3 bookworm.py --lexdiv 11
python3 bookworm.py --topics 11
python3 bookworm.py --entities 11
python3 bookworm.py --summarize 11
python3 bookworm.py --similar 11
python3 bookworm.py --card 11
```

## Architecture

```text
bookworm.py
nlp/
  lexical_diversity.py
  topics.py
  entities.py
  summarization.py
  similarity.py
  card.py
services/
  gutenberg.py
  cache.py
utils/
  text_processing.py
data/
  books/
  cache/
diagrams/
requirements.txt
```

`bookworm.py` is the CLI orchestrator. It reads the user command and calls the
right NLP function.

`nlp/` contains the text analysis features required by the subject.

`services/` contains reusable project services: Project Gutenberg access and
cache management.

`utils/` contains low-level text processing helpers: Gutenberg cleanup,
normalization, tokenization, stop-word removal, sentence splitting and section
splitting.

`data/books/` stores downloaded `.txt` books. `data/cache/` stores cached
results. Generated data files are ignored by Git.

## Methods

### Lexical diversity

The program tokenizes the text and computes:

- `tok`: total word tokens
- `typ`: unique word tokens
- `hap`: words occurring once
- `ttr`: type-token ratio
- `mwl`: mean word length
- `mwf`: mean word frequency

### Topics

The book is split into four sections. For each section, the program removes
stop words and computes TF-IDF scores. Important keywords are then mapped to
broader theme families such as animals, authority, adventure, fantasy,
mirror world or mystery.

The returned list starts with the most present broad themes and is completed
with representative keywords. This follows the idea that topics should describe
general themes, not only raw frequent words. It is fast and explainable, but it
depends on the quality of the handcrafted theme vocabulary.

### Entities

The prototype uses capitalization and context heuristics to find likely
characters and locations. It is lightweight and easy to explain, but less
accurate than a trained NER model.

### Summarization

The summary uses a lightweight hybrid method. First, the program extracts
characters, locations and broad topics. These structured signals are used to
build a short introductory sentence and to give a bonus to important sentences.
Then the program applies extractive summarization: sentences are scored with
word frequencies and returned in original order.

This follows the teacher's guidance: the summary is not only a list of frequent
sentences, it is guided by information extracted from the text. The limitation
is that the template sentence can be less natural for some books, so the method
keeps extractive sentences as a robust fallback.

### Similarity

The program vectorizes the required book collection with TF-IDF and compares
books using cosine similarity. A small editorial category bonus is added so
books from the same audience/genre group are ranked more naturally. It returns
the five closest titles.

## Cache

Some operations can be expensive, so results are cached in `data/cache/`.

For example:

```text
data/cache/topics_11.json
data/cache/summary_11.json
data/cache/similar_11.json
```

Use `--no-cache` to force recomputation:

```bash
python3 bookworm.py --topics 11 --no-cache
```

## Diagrams

Pipeline diagrams are included below for quick review. The same diagrams are
also available as separate files in `diagrams/`.

### Lexical Diversity Pipeline

```mermaid
flowchart LR
    A[Book ID] --> B[Load Gutenberg text]
    B --> C[Strip Gutenberg metadata]
    C --> D[Normalize text]
    D --> E[Tokenize words]
    E --> F[Count tokens, types and hapax]
    F --> G[Compute TTR, MWL and MWF]
    G --> H[Cache and return dictionary]
```

### Topics Pipeline

```mermaid
flowchart LR
    A[Book ID] --> B[Load Gutenberg text]
    B --> C[Normalize and split into 4 sections]
    C --> D[Tokenize each section]
    D --> E[Remove stop words]
    E --> F[Compute section TF-IDF scores]
    F --> G[Score broad theme families]
    G --> H[Rank recurring themes]
    F --> I[Keep representative keywords]
    H --> J[Return themes then keywords]
    I --> J
    J --> K[Cache and return dictionary]
```

### Entities Pipeline

```mermaid
flowchart LR
    A[Book ID] --> B[Load Gutenberg text]
    B --> C[Keep capitalization]
    C --> D[Find capitalized name candidates]
    C --> E[Find location context patterns]
    D --> F[Filter metadata and false positives]
    E --> G[Rank likely locations]
    F --> H[Rank repeated character names]
    G --> I[Cache and return entities]
    H --> I
```

### Summarization Pipeline

```mermaid
flowchart LR
    A[Book ID] --> B[Load Gutenberg text]
    A --> C[Extract entities]
    A --> D[Extract topics]
    B --> E[Split into sentences]
    E --> F[Filter very short and very long sentences]
    C --> G[Build important terms]
    D --> G
    F --> H[Score sentences with word frequencies]
    G --> I[Add entity and topic bonus]
    H --> J[Select best sentences]
    I --> J
    J --> K[Add structured intro]
    K --> L[Cache summary string]
```

### Similarity Pipeline

```mermaid
flowchart LR
    A[Target book ID] --> B[Load required collection]
    B --> C[Tokenize without stop words]
    C --> D[Build TF-IDF vectors]
    D --> E[Compute cosine similarity]
    E --> F[Add editorial category bonus]
    F --> G[Sort by decreasing score]
    G --> H[Return top 5 titles]
```

### Book Card Pipeline

```mermaid
flowchart LR
    A[Book ID] --> B[Metadata]
    A --> C[Lexical diversity]
    A --> D[Topics]
    A --> E[Entities]
    A --> F[Summary]
    A --> G[Similar books]
    B --> H[Assemble dictionary]
    C --> H
    D --> H
    E --> H
    F --> H
    G --> H
    H --> I[Cache and return card]
```

## Notes For Presentation

The project avoids large transformers, LLMs and APIs. The goal is not perfect
NLP quality, but a clear, reproducible and defensible methodology.
