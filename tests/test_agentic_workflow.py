# -*- coding: utf-8 -*-
"""
Test básico del workflow agentic RAG.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.graph.workflow import run_agentic_rag


def test_basic_workflow():
    """Test simple del workflow."""
    
    print("\n" + "="*80)
    print("TEST: Agentic RAG - Día 1 Setup")
    print("="*80)
    
    # Test query simple
    result = run_agentic_rag("¿Cuál es el importe total de los avales?")
    
    print(f"\nQuery: ¿Cuál es el importe total de los avales?")
    print(f"\nRespuesta: {result['answer']}")
    print(f"Confidence: {result['confidence']}")
    print(f"Sources: {len(result['sources'])}")
    print(f"\nMetadata: {result['metadata']}")
    
    print("\n" + "="*80)
    print("✅ Workflow básico funciona - Día 1 completado")
    print("="*80)


if __name__ == "__main__":
    test_basic_workflow()
