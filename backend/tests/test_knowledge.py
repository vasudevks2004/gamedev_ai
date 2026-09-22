import pytest
from app.knowledge.knowledge_base import GAME_DEV_KNOWLEDGE_CORPUS
from app.knowledge.rag_service import rag_service

def test_knowledge_corpus_integrity():
    assert len(GAME_DEV_KNOWLEDGE_CORPUS) >= 8
    categories = {e.category for e in GAME_DEV_KNOWLEDGE_CORPUS}
    assert "Unreal Engine" in categories
    assert "C++" in categories
    assert "Blender" in categories
    
    for entry in GAME_DEV_KNOWLEDGE_CORPUS:
        assert entry.id
        assert entry.title
        assert len(entry.tags) > 0
        assert entry.summary
        assert entry.content
        assert entry.source_citation

def test_rag_search_unreal():
    results = rag_service.search("Enhanced Input mapping context", top_k=2)
    assert len(results) > 0
    top = results[0]
    assert "enhanced input" in top["title"].lower() or "input" in top["title"].lower()
    assert top["category"] == "Unreal Engine"

def test_rag_search_cpp():
    results = rag_service.search("smart pointer tobjectptr memory", top_k=2)
    assert len(results) > 0
    top = results[0]
    assert "pointer" in top["title"].lower() or top["category"] == "C++"

def test_rag_search_blender():
    results = rag_service.search("blender unit scale fbx export 0.01", top_k=2)
    assert len(results) > 0
    top = results[0]
    assert top["category"] == "Blender"

def test_rag_context_block_formatting():
    context_block = rag_service.build_rag_context_block("How do I setup replication in UE5?")
    assert "RELEVANT GAME-DEV DOCUMENTATION" in context_block
    assert "Citation 1" in context_block
    assert "Source:" in context_block
