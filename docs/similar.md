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
