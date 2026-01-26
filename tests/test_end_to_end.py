# -*- coding: utf-8 -*-
"""
Test End-to-End del Agentic RAG (Día 6).
Verifica el flujo completo: Orchestrator -> Planner -> Retrieval -> Evaluator -> (Corrective) -> Synthesis
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.graph.workflow import run_agentic_rag


def test_end_to_end():
    """Test del sistema completo."""
    
    print("\n" + "="*80)
    print("TEST: End-to-End Agentic RAG - Día 6")
    print("="*80)
    
    # Query verificada compleja
    query = "¿Cuál es la suma total de todos los avales bancarios en el sistema?"
    
    print(f"\nQuery: {query}")
    print("Ejecutando workflow completo...")
    
    result = run_agentic_rag(query)
    
    print("\n" + "="*80)
    print("RESPUESTA FINAL GENERADA:")
    print("="*80)
    print(result.get('answer', 'Sin respuesta'))
    
    print("\n" + "="*80)
    print("FUENTES CITADAS:")
    print("="*80)
    for source in result.get('sources', []):
        archivo = source.get('archivo')
        paginas = source.get('paginas')
        print(f"- {archivo} (Pags: {paginas})")
    
    # Metadata final
    meta = result.get('metadata', {})
    print("\n" + "="*80)
    print("METADATA:")
    print(f"- Complexity: {meta.get('complexity')}")
    print(f"- Eval Score: {meta.get('evaluation_score')}")
    print(f"- Retries: {meta.get('retry_count')}")
    
    print("\n✅ Test completado (Revisar calidad de respuesta)")


if __name__ == "__main__":
    test_end_to_end()
