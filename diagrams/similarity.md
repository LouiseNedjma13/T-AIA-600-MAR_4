# Similarity pipeline

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
