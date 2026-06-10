# Similarity Methods

The `similar` feature compares one Gutenberg book with the project book collection and returns the five closest titles.

The final command will be exposed through:

```bash
python3 bookworm.py --similar <ID>
```

Internally, we tested several approaches before choosing the default one.

## Jaccard Similarity

Jaccard similarity compares the vocabulary shared by two books.

Each book is transformed into a set of unique words. The score is computed as:

```text
number of shared words / number of total unique words across both books
```

Example:

```python
book_a = {"alice", "rabbit", "queen", "garden"}
book_b = {"alice", "rabbit", "cat", "tea"}
```

Shared words:

```python
{"alice", "rabbit"}
```

All unique words:

```python
{"alice", "rabbit", "queen", "garden", "cat", "tea"}
```

Score:

```text
2 / 6 = 0.33
```

### Why It Is Useful

Jaccard is simple, fast, and easy to explain. It worked well for `Alice's Adventures in Wonderland` because it returned books with a similar youth/fantasy vocabulary.

Result for book `11`:

```python
[
    "Through the Looking-Glass",
    "The Wonderful Wizard of Oz",
    "Peter Pan",
    "The Secret Garden",
    "The Jungle Book"
]
```

### Limitations

Jaccard only checks whether a word appears or not. It does not consider how many times the word appears.

For example, a word appearing once and a word appearing one hundred times have the same weight.


## Frequency Cosine Similarity

The frequency method represents each book as a word-count vector.

Instead of only checking if a word exists, it counts how many times each word appears.

Example:

```python
book_a = {"alice": 10, "rabbit": 6, "queen": 2}
book_b = {"alice": 3, "rabbit": 1, "cat": 8}
```

The books are compared with cosine similarity. Cosine similarity measures whether two vectors point in a similar direction.

In this project, this means:

```text
Do the books use words with similar frequencies?
```

### Why We Tested It

This method is more precise than Jaccard because it considers word repetition.

If a word is central in a book, it appears many times and receives more importance.

### Result On Alice

For book `11`, this method returned:

```python
[
    "Through the Looking-Glass",
    "Dracula",
    "The Adventures of Sherlock Holmes",
    "The Memoirs of Sherlock Holmes",
    "Treasure Island"
]
```

### Why We Did Not Choose It

The result is less coherent for `Alice's Adventures in Wonderland` because it brings back books such as `Dracula` and `Sherlock Holmes`.

Those books may share narrative vocabulary with Alice, but they are not the closest books in terms of audience or literary universe.

The frequency method can be dominated by repeated narrative words, even after preprocessing.


## TF-IDF Cosine Similarity

TF-IDF means `Term Frequency - Inverse Document Frequency`.

This method gives a weight to each word:

- words that appear often in one book are important for that book;
- words that appear in almost every book become less important;
- rare and specific words receive more weight.

After computing TF-IDF weights, each book becomes a weighted vector of words. The vectors are then compared with cosine similarity.

### Why We Tested It

TF-IDF is a common and serious method for text similarity. It is usually stronger than raw word frequency because it reduces the importance of words that are frequent everywhere.

This is useful when comparing books, because many books share common narrative words.

### Result On Alice

For book `11`, this method returned:

```python
[
    "Through the Looking-Glass",
    "The Adventures of Sherlock Holmes",
    "Treasure Island",
    "The Memoirs of Sherlock Holmes",
    "The Time Machine"
]
```

### Why We Did Not Choose It As Default

TF-IDF is theoretically strong, but on our small and mixed corpus it did not produce the most coherent recommendations for Alice.

After `Through the Looking-Glass`, it returned several books from different categories. These books may share specific vocabulary with Alice, but they are not the most natural recommendations for a youth/fantasy book.

### Final Choice

We kept TF-IDF available for comparison, but chose Jaccard as the default method because it produced the most coherent top 5 recommendations for `Alice's Adventures in Wonderland` in this project corpus.
