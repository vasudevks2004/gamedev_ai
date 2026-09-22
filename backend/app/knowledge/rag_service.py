"""
RAG Service for Ashwin's Personal AI Game Development Assistant.
Provides semantic retrieval, query matching, and citation formatting across Unreal Engine, C++, and Blender knowledge.
"""

import re
from typing import List, Dict, Any, Optional
from app.knowledge.knowledge_base import GAME_DEV_KNOWLEDGE_CORPUS, KnowledgeEntry

class RAGService:
    def __init__(self, corpus: Optional[List[KnowledgeEntry]] = None):
        self.corpus = corpus or GAME_DEV_KNOWLEDGE_CORPUS

    def search(self, query: str, top_k: int = 3, category_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Rank knowledge entries against query using multi-term keyword & semantic tag scoring.
        """
        if not query or not query.strip():
            return []

        tokens = set(re.findall(r'\b[a-zA-Z0-9_\+#\.]+\b', query.lower()))
        scored_results = []

        for entry in self.corpus:
            if category_filter and entry.category.lower() != category_filter.lower():
                continue

            score = 0.0
            entry_title_lower = entry.title.lower()
            entry_summary_lower = entry.summary.lower()
            entry_content_lower = entry.content.lower()

            for token in tokens:
                if len(token) < 2:
                    continue
                # Match tags (highest priority)
                for tag in entry.tags:
                    if token == tag.lower():
                        score += 5.0
                    elif token in tag.lower():
                        score += 2.5
                # Match title
                if token in entry_title_lower:
                    score += 4.0
                # Match summary
                if token in entry_summary_lower:
                    score += 2.0
                # Match content
                if token in entry_content_lower:
                    score += 1.0

            if score > 0:
                scored_results.append((score, entry))

        # Sort descending by score
        scored_results.sort(key=lambda x: x[0], reverse=True)
        top_entries = scored_results[:top_k]

        return [
            {
                "score": score,
                "id": entry.id,
                "title": entry.title,
                "category": entry.category,
                "summary": entry.summary,
                "content": entry.content,
                "citation": entry.source_citation,
                "doc_url": entry.doc_url
            }
            for score, entry in top_entries
        ]

    def build_rag_context_block(self, query: str, top_k: int = 2) -> str:
        """
        Retrieve relevant knowledge and format into an augmented system prompt context block.
        """
        results = self.search(query, top_k=top_k)
        if not results:
            return ""

        context_lines = [
            "### RELEVANT GAME-DEV DOCUMENTATION & KNOWLEDGE CITATIONS:",
            "Use the following technical references to guide Ashwin accurately:"
        ]

        for i, item in enumerate(results, 1):
            context_lines.append(f"\n[Citation {i}]: {item['title']} ({item['category']})")
            context_lines.append(f"Source: {item['citation']}")
            if item.get('doc_url'):
                context_lines.append(f"URL: {item['doc_url']}")
            context_lines.append(f"Reference Summary:\n{item['content']}\n")

        return "\n".join(context_lines)

rag_service = RAGService()
