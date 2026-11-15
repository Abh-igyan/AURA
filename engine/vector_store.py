"""
AURA Vector Search Engine
High-fidelity vector embeddings and cosine similarity search over NASA spaceflight medical protocols.
Optimized for 8GB RAM edge environments:
- Zero heavy dependencies required (pure-math subword cosine vector space model).
- Automatically upgrades to sentence-transformers / PyTorch embeddings if available in environment.
- Returns similarity scores, ranked protocols, and exact NASA citations.
"""

from __future__ import annotations
import json
import math
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


class VectorStore:
    """
    In-memory vector database for NASA Space Medicine protocols.
    Computes dense vector representations and cosine similarity.
    """

    def __init__(self, guidelines_path: Path | str):
        self.guidelines_path = Path(guidelines_path)
        with open(self.guidelines_path, "r", encoding="utf-8") as f:
            self.corpus: List[Dict[str, Any]] = json.load(f)

        self.chunks: List[Dict[str, Any]] = []
        self.vocabulary: Dict[str, int] = {}
        self.idf: Dict[str, float] = {}
        self.chunk_vectors: List[List[float]] = []
        self.use_transformer: bool = False
        self.embed_model = None

        self._try_load_transformer()
        self._build_index()

    def _try_load_transformer(self) -> None:
        """Attempts to load lightweight sentence-transformers if present."""
        try:
            from sentence_transformers import SentenceTransformer  # type: ignore
            # all-MiniLM-L6-v2 is ultra-lightweight (80MB, fast CPU inference)
            self.embed_model = SentenceTransformer("all-MiniLM-L6-v2")
            self.use_transformer = True
        except Exception:
            # Fallback to internal high-performance subword vector space engine
            self.use_transformer = False
            self.embed_model = None

    def _tokenize(self, text: str) -> List[str]:
        """Subword and word n-gram tokenizer for spaceflight terminology."""
        text = text.lower()
        # Clean special characters while retaining numbers & medical abbreviations
        clean = re.sub(r"[^a-z0-9_\-\s]", " ", text)
        words = [w for w in clean.split() if len(w) > 1]
        
        # Generate word tokens + character n-grams (3-4 chars) for robust typo & inflection handling
        tokens = list(words)
        for w in words:
            if len(w) >= 4:
                tokens.append(w[:3])
                tokens.append(w[:4])
        return tokens

    def _build_index(self) -> None:
        """Chunks documents and calculates vector space index."""
        self.chunks = []
        for doc in self.corpus:
            doc_id = doc.get("id", "UNKNOWN")
            doc_name = doc.get("document", "NASA Medical Manual")
            section = doc.get("section", "")
            category = doc.get("category", "GENERAL")
            summary = doc.get("summary", "")
            steps = doc.get("protocol_steps", [])
            keywords = doc.get("keywords", [])
            citation = doc.get("citations", doc_name)

            # Chunk 1: Overview & Symptoms chunk
            overview_text = f"{doc_name} {section} {category} {' '.join(keywords)} {summary}"
            self.chunks.append({
                "chunk_id": f"{doc_id}-OVERVIEW",
                "doc_id": doc_id,
                "document": doc_name,
                "section": section,
                "category": category,
                "citation": citation,
                "content_type": "OVERVIEW",
                "text": overview_text,
                "summary": summary,
                "steps": steps
            })

            # Chunk 2: Step-by-Step Clinical Procedure chunk
            steps_text = f"{category} {section} {' '.join(steps)}"
            self.chunks.append({
                "chunk_id": f"{doc_id}-PROCEDURE",
                "doc_id": doc_id,
                "document": doc_name,
                "section": section,
                "category": category,
                "citation": citation,
                "content_type": "PROCEDURE",
                "text": steps_text,
                "summary": summary,
                "steps": steps
            })

        if self.use_transformer and self.embed_model is not None:
            # Dense neural embeddings
            texts = [c["text"] for c in self.chunks]
            embeddings = self.embed_model.encode(texts, normalize_embeddings=True)
            self.chunk_vectors = [emb.tolist() for emb in embeddings]
        else:
            # High-performance Vector Space TF-IDF with L2 normalization
            # Build vocabulary & document frequency
            num_chunks = len(self.chunks)
            doc_freq: Dict[str, int] = {}
            chunk_token_lists = []

            for chunk in self.chunks:
                tokens = set(self._tokenize(chunk["text"]))
                chunk_token_lists.append(self._tokenize(chunk["text"]))
                for t in tokens:
                    doc_freq[t] = doc_freq.get(t, 0) + 1

            self.vocabulary = {term: idx for idx, term in enumerate(sorted(doc_freq.keys()))}
            self.idf = {term: math.log((num_chunks + 1.0) / (freq + 1.0)) + 1.0 for term, freq in doc_freq.items()}

            # Encode all chunks into L2-normalized vector space
            self.chunk_vectors = []
            for tokens in chunk_token_lists:
                vec = self._vectorize_tokens(tokens)
                self.chunk_vectors.append(vec)

    def _vectorize_tokens(self, tokens: List[str]) -> List[float]:
        """Creates an L2-normalized TF-IDF vector."""
        vec = [0.0] * len(self.vocabulary)
        if not tokens:
            return vec

        term_counts: Dict[str, int] = {}
        for t in tokens:
            if t in self.vocabulary:
                term_counts[t] = term_counts.get(t, 0) + 1

        total_terms = len(tokens)
        sq_sum = 0.0

        for t, count in term_counts.items():
            idx = self.vocabulary[t]
            tf = count / total_terms
            idf_val = self.idf.get(t, 1.0)
            score = tf * idf_val
            vec[idx] = score
            sq_sum += score * score

        # L2 Normalize
        norm = math.sqrt(sq_sum)
        if norm > 0:
            vec = [v / norm for v in vec]
        return vec

    @staticmethod
    def _cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
        """Calculates cosine similarity between two unit vectors (dot product)."""
        if len(vec1) != len(vec2):
            return 0.0
        dot = sum(a * b for a, b in zip(vec1, vec2))
        return max(0.0, min(1.0, dot))

    def search(self, query: str, top_k: int = 3, category_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Executes vector similarity search against NASA medical corpus.
        Returns top-K matching protocols with similarity score and citations.
        """
        if not query.strip():
            return []

        # Vectorize query
        if self.use_transformer and self.embed_model is not None:
            query_vec = self.embed_model.encode([query], normalize_embeddings=True)[0].tolist()
        else:
            q_tokens = self._tokenize(query)
            query_vec = self._vectorize_tokens(q_tokens)

        scored_results: List[Tuple[float, Dict[str, Any]]] = []

        seen_docs = set()
        for i, chunk in enumerate(self.chunks):
            if category_filter and chunk["category"].upper() != category_filter.upper():
                continue

            sim = self._cosine_similarity(query_vec, self.chunk_vectors[i])
            
            # Boost score if category or document ID matches query directly
            query_lower = query.lower()
            if chunk["category"].lower() in query_lower:
                sim = min(1.0, sim + 0.15)
            if chunk["doc_id"].lower() in query_lower:
                sim = min(1.0, sim + 0.25)

            if sim > 0.05:
                scored_results.append((sim, chunk))

        scored_results.sort(key=lambda x: x[0], reverse=True)

        # Deduplicate by doc_id to provide unique top protocols
        deduped = []
        for score, chunk in scored_results:
            doc_id = chunk["doc_id"]
            if doc_id not in seen_docs:
                seen_docs.add(doc_id)
                deduped.append({
                    "doc_id": chunk["doc_id"],
                    "document": chunk["document"],
                    "section": chunk["section"],
                    "category": chunk["category"],
                    "citation": chunk["citation"],
                    "summary": chunk["summary"],
                    "steps": chunk["steps"],
                    "similarity_score": round(score, 4),
                    "matched_chunk": chunk["chunk_id"]
                })
                if len(deduped) >= top_k:
                    break

        return deduped

    def get_by_id(self, protocol_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves exact protocol by document ID."""
        for doc in self.corpus:
            if doc["id"].lower() == protocol_id.lower():
                return doc
        return None
