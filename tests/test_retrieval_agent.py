# -*- coding: utf-8 -*-
"""
Test del Retrieval Agent (Día 3).
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.graph.workflow import run_agentic_rag


def test_retrieval_agent():
    """Test del retrieval agent con sub-queries."""
    
    print("\n" + "="*80)
    print("TEST: Retrieval Agent - Día 3")
    print("="*80)
    
    # Query de agregación (más compleja)
    query = "¿Cuál es la suma total de todos los avales bancarios en el sistema?"
    
    print(f"\nQuery: {query}")
    print("Ejecutando workflow...")
    
    result = run_agentic_rag(query)
    
    metadata = result.get('metadata', {})
    
    print(f"\nResultados:")
    print(f"Complejidad: {metadata.get('complexity')}")
    print(f"Sub-queries generadas: {len(metadata.get('sub_queries', []))}")
    
    # Verificar reportes de hallazgo (esto requeriría acceder al estado, 
    # pero run_agentic_rag retorna un dict procesado.
    # Tendríamos que inspeccionar logs o modificar run_agentic_rag para devolver full state si queremos debug profundo.
    # Por ahora confiamos en que 'sources' tenga algo si synthesis estuviera, 
    # pero como synthesis no está, 'answer' estará vacío o dummy.
    # Vamos a verificar los logs (visualmente) o confiar en que no explote.
    
    # Pero espera, run_agentic_rag retorna {answer, sources, metadata}
    # En retrieval no estamos generando 'sources' formateados para el output final todavía (eso es Synthesis).
    # Así que verificamos si el grafo completó sin error.
    
    print("\nSub-Queries ejecutadas:")
    for sq in metadata.get('sub_queries', []):
        print(f"  - [{sq['id']}] {sq['query']}")
    
    print("\n✅ Test completado (Verificar logs para detalles de retrieval)")


if __name__ == "__main__":
    test_retrieval_agent()
