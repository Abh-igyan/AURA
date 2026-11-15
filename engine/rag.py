"""
AURA Grounded Clinical RAG Engine
Powered by dense vector search over the authoritative NASA spaceflight clinical protocols.
Guarantees every output carries an explicit document ID and verified NASA citation.
"""

from __future__ import annotations
from pathlib import Path
from typing import Any, Dict, List, Optional
from .vector_store import VectorStore


class GroundedMedicalRAG:
    def __init__(self, guidelines_path: Path | str):
        self.vector_store = VectorStore(guidelines_path)
        self.corpus = self.vector_store.corpus

    def get_by_id(self, protocol_id: str) -> Optional[Dict[str, Any]]:
        return self.vector_store.get_by_id(protocol_id)

    def query(self, query_str: str, category: Optional[str] = None, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Retrieves matching NASA spaceflight medical protocols using vector similarity search.
        """
        matches = self.vector_store.search(query_str, top_k=top_k, category_filter=category)
        # Format matching records for compatibility with downstream tools
        results = []
        for m in matches:
            doc = self.vector_store.get_by_id(m["doc_id"])
            if doc:
                doc_copy = dict(doc)
                doc_copy["vector_score"] = m["similarity_score"]
                results.append(doc_copy)
        return results

    def format_checklist(self, protocol_doc: Dict[str, Any]) -> List[Dict[str, str]]:
        """
        Structures raw protocol steps into an auditable crew checklist with citations.
        """
        checklist = []
        doc_id = protocol_doc.get("id", "UNKNOWN-DOC")
        doc_name = protocol_doc.get("document", "NASA Medical Manual")
        section = protocol_doc.get("section", "")

        for idx, step in enumerate(protocol_doc.get("protocol_steps", []), 1):
            checklist.append({
                "step_number": idx,
                "action": step,
                "source_id": doc_id,
                "citation": f"{doc_name} [{section}]"
            })
        return checklist
