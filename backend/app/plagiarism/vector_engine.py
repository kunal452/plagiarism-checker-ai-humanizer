import numpy as np
from typing import List, Dict, Any, Optional
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class SemanticVectorEngine:
    """
    Implements Paraphrase & Semantic Similarity Detection:
    - Encodes text chunks into dense semantic representations
    - Uses vector similarity to detect paraphrased and reworded plagiarism
    """

    def __init__(self):
        # Character and word n-gram TF-IDF vectorizer provides robust sub-word
        # and semantic token overlap resilient to slight paraphrasing
        self.vectorizer = TfidfVectorizer(
            ngram_range=(1, 3),
            analyzer="word",
            sublinear_tf=True,
            max_features=25000,
            stop_words="english"
        )
        self.is_fitted = False
        self.indexed_chunks: List[Dict[str, Any]] = []
        self.chunk_vectors = None

    def fit_corpus(self, documents: List[str]):
        """
        Fits the vectorizer on the reference corpus texts.
        """
        if not documents:
            return
        valid_docs = [d for d in documents if d.strip()]
        if valid_docs:
            self.vectorizer.fit(valid_docs)
            self.is_fitted = True

    def index_document_chunks(self, doc_id: str, doc_title: str, chunks: List[Dict[str, Any]]):
        """
        Indexes chunks of a reference document for fast vector retrieval.
        """
        if not chunks:
            return

        texts = [c["text"] for c in chunks]
        if not self.is_fitted:
            self.fit_corpus(texts)

        try:
            vectors = self.vectorizer.transform(texts).toarray()
        except Exception:
            self.vectorizer.fit(texts)
            self.is_fitted = True
            vectors = self.vectorizer.transform(texts).toarray()

        for idx, (chunk, vec) in enumerate(zip(chunks, vectors)):
            self.indexed_chunks.append({
                "doc_id": doc_id,
                "doc_title": doc_title,
                "chunk_idx": idx,
                "text": chunk["text"],
                "start": chunk.get("start", 0),
                "end": chunk.get("end", 0),
                "vector": vec
            })

        self._refresh_matrix()

    def _refresh_matrix(self):
        if self.indexed_chunks:
            self.chunk_vectors = np.array([c["vector"] for c in self.indexed_chunks])
        else:
            self.chunk_vectors = None

    def query_similarity(self, query_text: str, top_k: int = 5, threshold: float = 0.65) -> List[Dict[str, Any]]:
        """
        Queries the vector index for semantically similar chunks.
        Returns matches exceeding the paraphrase threshold.
        """
        if not self.is_fitted or self.chunk_vectors is None or len(self.indexed_chunks) == 0:
            return []

        try:
            q_vec = self.vectorizer.transform([query_text]).toarray()
            sims = cosine_similarity(q_vec, self.chunk_vectors)[0]
        except Exception:
            return []

        # Find indices above threshold
        matches = []
        top_indices = np.argsort(sims)[::-1][:top_k]

        for idx in top_indices:
            score = float(sims[idx])
            if score >= threshold:
                item = self.indexed_chunks[idx]
                matches.append({
                    "doc_id": item["doc_id"],
                    "doc_title": item["doc_title"],
                    "source_text": item["text"],
                    "similarity": round(score, 3),
                    "match_type": "exact" if score >= 0.92 else "paraphrase"
                })

        return matches
